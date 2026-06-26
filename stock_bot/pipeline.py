"""End-to-end pipeline tying together data, Fridays, changes and back-tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import backtest, data, fridays
from .config import Config


def _windowed_prices(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """OHLC restricted to the study window (drops the pre-start buffer)."""
    start = pd.Timestamp(cfg.start_date)
    end = pd.Timestamp(cfg.resolved_end_date())
    out = df.loc[(df.index >= start) & (df.index <= end), ["Open", "High", "Low", "Close", "Volume"]]
    return out.copy()


def analyse_market(name: str, df: pd.DataFrame, cfg: Config) -> dict[str, pd.DataFrame]:
    """Run the full analysis for a single index and return all result tables."""
    fri = fridays.identify_fridays(df, cfg)
    fri = fridays.add_drop_columns(fri)
    changes = fridays.friday_to_monday_changes(fri)
    trades = backtest.build_trade_ledger(fri, cfg)
    independent = backtest.independent_test(fri, cfg)
    continuous = backtest.continuous_test(fri, cfg)

    return {
        "prices": _windowed_prices(df, cfg),
        "fridays": fri,
        "changes": changes,
        "trades": trades,
        "independent": independent,
        "continuous": continuous,
    }


def _write(df: pd.DataFrame, path: Path, *, index: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)


def run(cfg: Config | None = None, *, use_cache: bool = True) -> dict[str, dict[str, pd.DataFrame]]:
    """Run the analysis for every configured index and write output tables."""
    cfg = cfg or Config()
    out_root = Path(cfg.output_dir)

    raw = data.load_all(cfg, use_cache=use_cache)

    results: dict[str, dict[str, pd.DataFrame]] = {}
    indep_rows = []
    cont_rows = []

    for name, df in raw.items():
        res = analyse_market(name, df, cfg)
        results[name] = res

        market_dir = out_root / name
        _write(res["prices"], market_dir / "prices.csv", index=True)
        _write(res["fridays"], market_dir / "fridays.csv")
        _write(res["changes"], market_dir / "fri_to_mon_changes.csv")
        _write(res["trades"], market_dir / "trades.csv")
        _write(res["independent"], market_dir / "independent_test.csv")
        _write(res["continuous"], market_dir / "continuous_test.csv")

        indep = res["independent"].copy()
        indep.insert(0, "market", name)
        indep_rows.append(indep)

        cont = res["continuous"].copy()
        cont.insert(0, "market", name)
        cont_rows.append(cont)

    summary_independent = pd.concat(indep_rows, ignore_index=True)
    summary_continuous = pd.concat(cont_rows, ignore_index=True)
    _write(summary_independent, out_root / "summary_independent.csv")
    _write(summary_continuous, out_root / "summary_continuous.csv")

    results["_summary"] = {
        "independent": summary_independent,
        "continuous": summary_continuous,
    }
    return results
