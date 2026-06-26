"""Back-testing of the "buy a dropping Friday, sell on Monday" strategy (Step 6).

A trade buys one index entry point on a *dropping* Friday and sells it on the
next trading day ("Monday").  Four buy/sell combinations are evaluated:

    friday_open  -> monday_open
    friday_open  -> monday_close
    friday_close -> monday_open
    friday_close -> monday_close

Trading fees of ``buy_fee`` and ``sell_fee`` (default 0.5% each, Step 7) are
applied to both legs, so a single trade multiplies capital by::

    (sell_price / buy_price) * (1 - buy_fee) * (1 - sell_fee)

Two tests are produced:

* **independent** - a fresh ``initial_capital`` is risked every dropping Friday;
  results are aggregated (total/average profit, win rate).
* **continuous**  - ``initial_capital`` is committed on the first dropping
  Friday and fully reinvested on every subsequent one (compounding).
"""

from __future__ import annotations

import pandas as pd

from .config import Config

# (label, friday buy column, monday sell column)
STRATEGIES: list[tuple[str, str, str]] = [
    ("open_to_open", "friday_open", "monday_open"),
    ("open_to_close", "friday_open", "monday_close"),
    ("close_to_open", "friday_close", "monday_open"),
    ("close_to_close", "friday_close", "monday_close"),
]


def _net_multiplier(buy: pd.Series, sell: pd.Series, cfg: Config) -> pd.Series:
    """Per-trade capital multiplier after round-trip fees."""
    return (sell / buy) * (1.0 - cfg.buy_fee) * (1.0 - cfg.sell_fee)


def dropping_trades(fridays_with_drops: pd.DataFrame) -> pd.DataFrame:
    """Tradeable dropping Fridays: a drop *and* a valid Monday to sell into."""
    df = fridays_with_drops
    mask = df["is_drop"] & df["monday_date"].notna()
    return df[mask].sort_values("friday_date").reset_index(drop=True)


def build_trade_ledger(fridays_with_drops: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Per-trade ledger across all four strategies for every dropping Friday."""
    trades = dropping_trades(fridays_with_drops)
    ledger = pd.DataFrame(
        {
            "friday_date": trades["friday_date"],
            "monday_date": trades["monday_date"],
            "drop_rate": trades["drop_rate"],
        }
    )
    for label, buy_col, sell_col in STRATEGIES:
        mult = _net_multiplier(trades[buy_col], trades[sell_col], cfg)
        ledger[f"{label}_net_return"] = mult - 1.0
    return ledger


def independent_test(fridays_with_drops: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Independent (non-compounding) test: $X risked every dropping Friday."""
    trades = dropping_trades(fridays_with_drops)
    rows = []
    for label, buy_col, sell_col in STRATEGIES:
        if trades.empty:
            rows.append(
                {
                    "strategy": label,
                    "n_trades": 0,
                    "total_profit": 0.0,
                    "avg_net_return": float("nan"),
                    "win_rate": float("nan"),
                    "best_trade": float("nan"),
                    "worst_trade": float("nan"),
                }
            )
            continue
        mult = _net_multiplier(trades[buy_col], trades[sell_col], cfg)
        ret = mult - 1.0
        profit = cfg.initial_capital * ret
        rows.append(
            {
                "strategy": label,
                "n_trades": int(len(trades)),
                "total_profit": float(profit.sum()),
                "avg_net_return": float(ret.mean()),
                "win_rate": float((ret > 0).mean()),
                "best_trade": float(ret.max()),
                "worst_trade": float(ret.min()),
            }
        )
    return pd.DataFrame(rows)


def continuous_test(fridays_with_drops: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Continuous (compounding) test: reinvest capital on each dropping Friday."""
    trades = dropping_trades(fridays_with_drops)
    rows = []
    for label, buy_col, sell_col in STRATEGIES:
        if trades.empty:
            rows.append(
                {
                    "strategy": label,
                    "n_trades": 0,
                    "final_capital": cfg.initial_capital,
                    "total_return": 0.0,
                }
            )
            continue
        mult = _net_multiplier(trades[buy_col], trades[sell_col], cfg)
        final = cfg.initial_capital * float(mult.prod())
        rows.append(
            {
                "strategy": label,
                "n_trades": int(len(trades)),
                "final_capital": final,
                "total_return": final / cfg.initial_capital - 1.0,
            }
        )
    return pd.DataFrame(rows)
