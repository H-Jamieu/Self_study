"""Identify "Fridays", "Mondays", drops, and Friday->Monday price changes.

Definitions (per the project brief):

* **Friday** - a trading day that is either
    a) an actual calendar Friday, or
    b) the last trading day before a market break of ``holiday_min_days`` or
       more non-trading calendar days (i.e. the eve of a holiday season).
* **Thursday** - the trading day immediately preceding a Friday; its close is
  the reference used to decide whether the Friday "dropped".
* **Monday** - the next trading day following a Friday.
"""

from __future__ import annotations

import pandas as pd

from .config import Config

_WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def build_daily(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Enrich the raw OHLC frame with neighbour-day context.

    Adds previous/next trading-day columns and the gap (in non-trading calendar
    days) to the next trading day.  Operates on the *full* frame (including the
    pre-start buffer) so neighbour lookups are correct at the window edges.
    """
    out = df.sort_index().copy()
    idx = out.index

    out["weekday"] = idx.weekday
    out["weekday_name"] = [_WEEKDAY_NAMES[w] for w in idx.weekday]

    out["prev_date"] = idx.to_series().shift(1).values
    out["prev_close"] = out["Close"].shift(1)

    next_date = idx.to_series().shift(-1)
    out["next_date"] = next_date.values
    out["next_open"] = out["Open"].shift(-1)
    out["next_close"] = out["Close"].shift(-1)

    # Non-trading calendar days between this day and the next trading day.
    # e.g. Fri -> Mon = 2 (Sat, Sun); Thu -> Mon (Fri holiday) = 3.
    gap = (pd.to_datetime(next_date.values) - idx).days
    out["non_trading_days_after"] = (gap - 1).astype("Int64")

    return out


def identify_fridays(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Return the table of Fridays within the study window (Step 2 + 4).

    One row per Friday with its type, the reference Thursday close, the Friday
    OHLC, and the following Monday's open/close.
    """
    daily = build_daily(df, cfg)

    is_weekday_friday = daily["weekday"] == 4
    is_holiday_eve = daily["non_trading_days_after"] >= cfg.holiday_min_days
    is_friday = is_weekday_friday | is_holiday_eve

    fri = daily[is_friday].copy()

    # Restrict to the study window (Fridays on/after the start date).
    start = pd.Timestamp(cfg.start_date)
    fri = fri[fri.index >= start]

    fri["friday_type"] = [
        "weekday_friday" if w else "holiday_eve" for w in (fri["weekday"] == 4)
    ]

    table = pd.DataFrame(
        {
            "friday_date": fri.index,
            "friday_type": fri["friday_type"].values,
            "weekday": fri["weekday_name"].values,
            "thursday_date": pd.to_datetime(fri["prev_date"].values),
            "thursday_close": fri["prev_close"].values,
            "friday_open": fri["Open"].values,
            "friday_close": fri["Close"].values,
            "non_trading_days_after": fri["non_trading_days_after"].values,
            "monday_date": pd.to_datetime(fri["next_date"].values),
            "monday_open": fri["next_open"].values,
            "monday_close": fri["next_close"].values,
        }
    ).reset_index(drop=True)

    return table


def add_drop_columns(fridays: pd.DataFrame) -> pd.DataFrame:
    """Step 3: condition Friday close on the Thursday close.

    ``drop_rate`` = friday_close / thursday_close - 1 (negative => a drop).
    ``is_drop``   = True when the Friday closed below its Thursday.
    """
    out = fridays.copy()
    out["drop_rate"] = out["friday_close"] / out["thursday_close"] - 1.0
    out["is_drop"] = out["drop_rate"] < 0
    return out


def friday_to_monday_changes(fridays: pd.DataFrame) -> pd.DataFrame:
    """Step 5: Friday->Monday percentage changes for all four price pairs."""
    out = fridays.copy()
    out = out[out["monday_date"].notna()].copy()

    out["open_to_open"] = out["monday_open"] / out["friday_open"] - 1.0
    out["open_to_close"] = out["monday_close"] / out["friday_open"] - 1.0
    out["close_to_open"] = out["monday_open"] / out["friday_close"] - 1.0
    out["close_to_close"] = out["monday_close"] / out["friday_close"] - 1.0

    cols = [
        "friday_date",
        "friday_type",
        "drop_rate",
        "is_drop",
        "monday_date",
        "open_to_open",
        "open_to_close",
        "close_to_open",
        "close_to_close",
    ]
    return out[[c for c in cols if c in out.columns]].reset_index(drop=True)
