# Stock Analysis Bot — Friday-drop / next-trading-day study

A small, self-contained research tool that studies a simple market hypothesis:

> *If a major index **drops on a "Friday"**, what happens if you buy it and sell
> on the **next trading day ("Monday")**?*

It collects daily index data, classifies "Fridays", conditions them on the prior
("Thursday") close, measures Friday→Monday moves, and back-tests the trade with
realistic fees.

> This repository previously held C++ practice exercises; that work has been
> retired in favour of this analysis project.

## Markets covered

| Name       | Index                              | Yahoo ticker |
|------------|------------------------------------|--------------|
| `SP500`    | S&P 500                            | `^GSPC`      |
| `NASDAQ`   | Nasdaq Composite                   | `^IXIC`      |
| `DOW`      | Dow Jones Industrial Average       | `^DJI`       |
| `HANGSENG` | Hang Seng Index                    | `^HSI`       |

## Study window

Data is collected **"since Trump came to power"**, which defaults to
**2025-01-20** (the second-term inauguration), through the most recent trading
day. US markets were closed on 2025-01-20 (MLK Jr. Day), so the first observed
trading day is 2025-01-21. The start date is configurable (e.g. use
`--start-date 2017-01-20` for the first term).

## Definitions

* **Friday** — a trading day that is *either*
  1. an actual calendar Friday, *or*
  2. the last trading day before a market break of **≥ 2 non-trading calendar
     days** (the eve of a holiday season). Each market uses its **own** trading
     calendar, so Hong Kong holidays are detected independently of US ones.
* **Thursday** — the trading day immediately before a Friday. Its close is the
  reference used to decide whether the Friday "dropped".
* **Drop** — a Friday whose close is **below** its Thursday close
  (`drop_rate = friday_close / thursday_close − 1 < 0`).
* **Monday** — the next trading day after a Friday.

## Back-test (Step 6–7)

Only **dropping Fridays** are traded. Four buy→sell price pairs are evaluated:

`open→open`, `open→close`, `close→open`, `close→close`
(buy leg = Friday price, sell leg = Monday price).

Round-trip fees of **0.5% buy + 0.5% sell** are applied, so one trade multiplies
capital by:

```
(sell_price / buy_price) × (1 − 0.005) × (1 − 0.005)
```

Two tests are produced per market and strategy:

* **Independent** — a fresh \$100 is risked every dropping Friday; results are
  aggregated (total profit, average return, win rate, best/worst trade).
* **Continuous** — \$100 is committed on the first dropping Friday and fully
  reinvested (compounded) on every subsequent one.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m stock_bot                 # full analysis, prints tables, writes ./output
python -m stock_bot --no-cache      # force re-download of market data
python -m stock_bot --start-date 2017-01-20
python -m stock_bot --buy-fee 0.001 --sell-fee 0.001
```

## Outputs

Raw data is cached under `data/raw/` (git-ignored, re-downloadable). Result
tables are written under `output/`:

```
output/
  <MARKET>/
    prices.csv               # daily OHLC within the study window
    fridays.csv              # Step 2–4: Fridays, Thursday ref, drop, Monday OHLC
    fri_to_mon_changes.csv   # Step 5: open/close→open/close % changes
    trades.csv               # per-trade net returns (dropping Fridays)
    independent_test.csv      # Step 6: independent (non-compounding) results
    continuous_test.csv       # Step 6: continuous (compounding) results
  summary_independent.csv    # all markets × strategies
  summary_continuous.csv     # all markets × strategies
```

## Code layout

```
stock_bot/
  config.py     # tunables: indices, dates, fees, capital
  data.py       # download + cache daily OHLC from Yahoo Finance
  fridays.py    # Friday/Monday/Thursday logic, drops, Fri→Mon changes
  backtest.py   # fee model, independent & continuous tests
  pipeline.py   # orchestration + writing output tables
  __main__.py   # CLI (python -m stock_bot)
```

## Disclaimer

This is a back-testing / research exercise on historical data. It is **not**
financial advice. Past performance does not predict future results.
