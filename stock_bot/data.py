"""Market-data collection.

Downloads daily OHLC data for each index from Yahoo Finance (via ``yfinance``)
and caches it to ``data/raw`` so repeated runs do not re-hit the API.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import yfinance as yf

from .config import Config


# Extra calendar days fetched *before* ``start_date`` so the previous trading
# day's close (the "Thursday" reference) is always available for the earliest
# Friday in the study window.
_LOOKBACK_BUFFER_DAYS = 10


def _raw_path(cfg: Config, name: str) -> Path:
    return Path(cfg.data_dir) / "raw" / f"{name}.csv"


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """yfinance returns a (field, ticker) column MultiIndex for one symbol.

    Reduce it to plain ``Open``/``High``/.../``Close`` columns.
    """
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    return df


def download_index(cfg: Config, name: str, ticker: str, *, use_cache: bool = True) -> pd.DataFrame:
    """Return a daily OHLC DataFrame for one index, indexed by date.

    Columns: ``Open``, ``High``, ``Low``, ``Close``, ``Volume`` (date index).
    """
    cache = _raw_path(cfg, name)
    if use_cache and cache.exists():
        df = pd.read_csv(cache, parse_dates=["Date"], index_col="Date")
        return df

    fetch_start = (
        dt.date.fromisoformat(cfg.start_date) - dt.timedelta(days=_LOOKBACK_BUFFER_DAYS)
    ).isoformat()
    fetch_end = (
        dt.date.fromisoformat(cfg.resolved_end_date()) + dt.timedelta(days=1)
    ).isoformat()

    raw = yf.download(
        ticker,
        start=fetch_start,
        end=fetch_end,
        interval="1d",
        auto_adjust=False,
        progress=False,
    )
    if raw is None or raw.empty:
        raise RuntimeError(f"No data returned for {name} ({ticker}).")

    df = _flatten_columns(raw)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index).normalize()
    df.index.name = "Date"
    df = df[~df.index.duplicated(keep="last")].sort_index()

    cache.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache)
    return df


def load_all(cfg: Config, *, use_cache: bool = True) -> dict[str, pd.DataFrame]:
    """Download (or load cached) data for every configured index."""
    out: dict[str, pd.DataFrame] = {}
    for name, ticker in cfg.indices.items():
        out[name] = download_index(cfg, name, ticker, use_cache=use_cache)
    return out
