"""Command-line entry point: ``python -m stock_bot``.

Runs the full pipeline and prints a readable summary of every result table.
"""

from __future__ import annotations

import argparse

import pandas as pd

from .config import Config
from .pipeline import run


def _print_df(title: str, df: pd.DataFrame) -> None:
    print(f"\n=== {title} ===")
    with pd.option_context(
        "display.max_rows", None,
        "display.width", 200,
        "display.float_format", lambda v: f"{v:,.4f}",
    ):
        print(df.to_string(index=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Friday-drop / next-day stock analysis bot")
    parser.add_argument("--start-date", default=None, help="Study start date (YYYY-MM-DD).")
    parser.add_argument("--end-date", default=None, help="Study end date (YYYY-MM-DD).")
    parser.add_argument("--buy-fee", type=float, default=None, help="Buy fee fraction (default 0.005).")
    parser.add_argument("--sell-fee", type=float, default=None, help="Sell fee fraction (default 0.005).")
    parser.add_argument("--no-cache", action="store_true", help="Force re-download of market data.")
    args = parser.parse_args(argv)

    overrides: dict[str, object] = {}
    if args.start_date:
        overrides["start_date"] = args.start_date
    if args.end_date:
        overrides["end_date"] = args.end_date
    if args.buy_fee is not None:
        overrides["buy_fee"] = args.buy_fee
    if args.sell_fee is not None:
        overrides["sell_fee"] = args.sell_fee

    cfg = Config(**overrides)

    print("Stock analysis bot")
    print(f"  window : {cfg.start_date} -> {cfg.resolved_end_date()}")
    print(f"  fees   : buy {cfg.buy_fee:.3%} / sell {cfg.sell_fee:.3%}")
    print(f"  capital: {cfg.initial_capital:.2f}")

    results = run(cfg, use_cache=not args.no_cache)

    for name in cfg.indices:
        res = results[name]
        _print_df(f"{name}: Fridays (with drop conditioning)", res["fridays"])
        _print_df(f"{name}: Friday -> Monday changes", res["changes"])
        _print_df(f"{name}: Independent test (dropping Fridays, long & short)", res["independent"])
        _print_df(f"{name}: Continuous test (dropping Fridays, long & short)", res["continuous"])

    _print_df("SUMMARY - Independent test (all markets)", results["_summary"]["independent"])
    _print_df("SUMMARY - Continuous test (all markets)", results["_summary"]["continuous"])

    print("\nOutput tables written to:", cfg.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
