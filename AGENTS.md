# AGENTS.md

## Cursor Cloud specific instructions

This repository is a **Python stock-analysis bot** (`stock_bot` package). It
studies whether buying a major index on a "dropping Friday" and selling the next
trading day is profitable, across S&P 500, Nasdaq, Dow Jones and Hang Seng.
(It previously contained C++ exercises; those were retired.)

### Environment
- Python 3.12 with a virtualenv at `.venv` (created with `python3 -m venv`; the
  system needs the `python3.12-venv` apt package, already handled at setup time).
- Dependencies are in `requirements.txt` (`pandas`, `yfinance`). Activate the
  venv before running: `source .venv/bin/activate`.

### Run / build / test
- Run the full analysis: `python -m stock_bot` (writes tables to `output/`).
- Force fresh market data: `python -m stock_bot --no-cache`.
- There is no separate build step and no automated test suite yet. "Lint" is a
  syntax/unused-import check: `python -m pyflakes stock_bot` and
  `python -m py_compile stock_bot/*.py`.

### Gotchas (non-obvious)
- **Network dependency:** data comes live from Yahoo Finance via `yfinance`.
  A bare `curl` to Yahoo often returns HTTP 429; `yfinance` handles the required
  cookies/crumb, so use it rather than raw HTTP. Downloads are cached under
  `data/raw/` (git-ignored); delete that dir or pass `--no-cache` to refresh.
- **Date-dependent output:** the study window ends at "today", so `output/`
  tables and back-test numbers change as new trading days arrive. The committed
  `output/` is a point-in-time snapshot; re-run to regenerate.
- **"Since Trump came to power"** defaults to `2025-01-20` (2nd term) in
  `stock_bot/config.py`; override with `--start-date`.
- Each market uses its **own** trading calendar, so "Friday" (incl. holiday-eve)
  detection differs per index (e.g. Hong Kong holidays for `^HSI`).
