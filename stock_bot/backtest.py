"""Back-testing of the dropping-Friday -> Monday trade (Step 6).

Two **policies** are evaluated on every *dropping* Friday (a Friday whose close
fell below its Thursday close), each closed out on the next trading day
("Monday"):

* **Policy 1 - long**  : buy the Friday, sell on Monday (profit if it rebounds).
* **Policy 2 - short** : short-sell the Friday, buy to cover on Monday
  (profit if the drop continues).

Four buy/sell price pairs are tried for both policies:

    friday_open  -> monday_open
    friday_open  -> monday_close
    friday_close -> monday_open
    friday_close -> monday_close

Trading fees (default 0.5% each leg, Step 7) are charged on both legs.

Fee model (``e`` = entry/Friday price, ``x`` = exit/Monday price):

* long  capital multiplier = (x / e) * (1 - buy_fee) * (1 - sell_fee)
      (buy at entry pays buy_fee; sell at exit pays sell_fee)
* short capital multiplier = 1 + (1 - sell_fee) - (x / e) * (1 + buy_fee)
      (short-sell at entry pays sell_fee; buy to cover at exit pays buy_fee)

With no price move and equal fees both reduce to ``1 - buy_fee - sell_fee``
(the ~1% round-trip cost), and long/short returns are mirror images of the
price move.

For each policy two tests are produced:

* **independent** - a fresh ``initial_capital`` is risked every dropping Friday.
* **continuous**  - ``initial_capital`` is committed on the first dropping
  Friday and fully reinvested (compounded) on every subsequent one.
"""

from __future__ import annotations

import pandas as pd

from .config import Config

# (label, friday entry column, monday exit column)
STRATEGIES: list[tuple[str, str, str]] = [
    ("open_to_open", "friday_open", "monday_open"),
    ("open_to_close", "friday_open", "monday_close"),
    ("close_to_open", "friday_close", "monday_open"),
    ("close_to_close", "friday_close", "monday_close"),
]

SIDES: tuple[str, ...] = ("long", "short")


def _net_multiplier(entry: pd.Series, exit_: pd.Series, cfg: Config, side: str) -> pd.Series:
    """Per-trade capital multiplier after round-trip fees for ``side``."""
    ratio = exit_ / entry
    if side == "long":
        return ratio * (1.0 - cfg.buy_fee) * (1.0 - cfg.sell_fee)
    if side == "short":
        return 1.0 + (1.0 - cfg.sell_fee) - ratio * (1.0 + cfg.buy_fee)
    raise ValueError(f"Unknown side: {side!r} (expected 'long' or 'short').")


def dropping_trades(fridays_with_drops: pd.DataFrame) -> pd.DataFrame:
    """Tradeable dropping Fridays: a drop *and* a valid Monday to close into."""
    df = fridays_with_drops
    mask = df["is_drop"] & df["monday_date"].notna()
    return df[mask].sort_values("friday_date").reset_index(drop=True)


def build_trade_ledger(fridays_with_drops: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Per-trade net returns for every dropping Friday, strategy and policy."""
    trades = dropping_trades(fridays_with_drops)
    ledger = pd.DataFrame(
        {
            "friday_date": trades["friday_date"],
            "monday_date": trades["monday_date"],
            "drop_rate": trades["drop_rate"],
        }
    )
    for side in SIDES:
        for label, entry_col, exit_col in STRATEGIES:
            mult = _net_multiplier(trades[entry_col], trades[exit_col], cfg, side)
            ledger[f"{side}_{label}_net_return"] = mult - 1.0
    return ledger


def independent_test(fridays_with_drops: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Independent (non-compounding) test for both policies."""
    trades = dropping_trades(fridays_with_drops)
    rows = []
    for side in SIDES:
        for label, entry_col, exit_col in STRATEGIES:
            if trades.empty:
                rows.append(
                    {
                        "policy": side,
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
            ret = _net_multiplier(trades[entry_col], trades[exit_col], cfg, side) - 1.0
            profit = cfg.initial_capital * ret
            rows.append(
                {
                    "policy": side,
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
    """Continuous (compounding) test for both policies."""
    trades = dropping_trades(fridays_with_drops)
    rows = []
    for side in SIDES:
        for label, entry_col, exit_col in STRATEGIES:
            if trades.empty:
                rows.append(
                    {
                        "policy": side,
                        "strategy": label,
                        "n_trades": 0,
                        "final_capital": cfg.initial_capital,
                        "total_return": 0.0,
                    }
                )
                continue
            mult = _net_multiplier(trades[entry_col], trades[exit_col], cfg, side)
            final = cfg.initial_capital * float(mult.prod())
            rows.append(
                {
                    "policy": side,
                    "strategy": label,
                    "n_trades": int(len(trades)),
                    "final_capital": final,
                    "total_return": final / cfg.initial_capital - 1.0,
                }
            )
    return pd.DataFrame(rows)
