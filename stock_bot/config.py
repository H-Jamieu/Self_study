"""Central configuration for the stock-analysis bot.

All tunables live here so the analysis is easy to reproduce and adjust.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


# ---------------------------------------------------------------------------
# Indices under study.  Keys are friendly names used in output files/tables,
# values are the Yahoo Finance ticker symbols.
# ---------------------------------------------------------------------------
INDICES: dict[str, str] = {
    "SP500": "^GSPC",       # S&P 500
    "NASDAQ": "^IXIC",      # Nasdaq Composite
    "DOW": "^DJI",          # Dow Jones Industrial Average
    "HANGSENG": "^HSI",     # Hang Seng Index
}


@dataclass(frozen=True)
class Config:
    """Run configuration.

    ``start_date`` defaults to 2025-01-20, the date Donald Trump returned to
    power for his second term ("since Trump came to power").  US equity markets
    were actually closed that day (MLK Jr. Day), so the first observed trading
    day is 2025-01-21.  Override ``start_date`` if a different definition of
    "came to power" is desired (e.g. the first term, 2017-01-20).
    """

    start_date: str = "2025-01-20"
    end_date: str | None = None  # None => up to the most recent trading day

    indices: dict[str, str] = field(default_factory=lambda: dict(INDICES))

    # A "Friday" is the last trading day before a market break of at least this
    # many non-trading calendar days (a normal weekend = 2).  This unifies
    # "actual Fridays" with "last trading day before a >= 2 day holiday".
    holiday_min_days: int = 2

    # Round-trip trading fees (fraction of notional).
    buy_fee: float = 0.005
    sell_fee: float = 0.005

    # Starting capital for the back-tests (USD-equivalent points).
    initial_capital: float = 100.0

    # Output / cache locations (relative to repo root unless absolute).
    data_dir: str = "data"
    output_dir: str = "output"

    def resolved_end_date(self) -> str:
        return self.end_date or date.today().isoformat()
