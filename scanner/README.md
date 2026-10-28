# NEPSE EMA/SMA Scanner — research only

**Exchange: NEPSE (Nepal Stock Exchange). Not investment advice, never a
buy/sell recommendation.** A crossover describes what past prices did.
It does not predict what a price will do, and on NEPSE it is often noise.
Read the falsifiers below before you trust any row this scanner prints.

Zero dependencies. Python 3.10+ standard library only.

## Run it

```bash
cd scanner
python3 cli.py --csv examples/demo_prices.csv
python3 cli.py --csv examples/demo_prices.csv --detail DEMO
python3 cli.py --csv my_prices.csv --fast 10 --slow 30 --all
```

CSV format (multi-symbol): `symbol,sector,date,close,high,low,volume`,
one row per symbol per trading day, dates strictly increasing per symbol.
See `examples/demo_prices.csv`. Your CSV's source must be named wherever
results are shared — a scan over unsourced prices is an unsourced scan.
The exact spec (single- and multi-symbol files, validation rules, what
counts as a bad row) plus BS/AD fiscal years, the holiday-calendar rule,
and the corporate-action warning are in
`../guides/nepal-data-handling.md` — read it before running a scan on
real prices. Single-symbol files use `date,close,high,low,volume`.

Tests: `python3 -m pytest tests/ -v` (40 tests, all passing on 28 Oct 2026;
pytest itself is a test-only dependency, the scanner needs none).

## What each indicator means

| Indicator | Meaning | Default |
|---|---|---|
| EMA Fast / Slow + crossover | Fast average crossing above slow = bullish cross. The scan prints the cross date, calendar days since the cross, and "Since cross" = (LTP − close on cross date) / close on cross date | EMA(20) / EMA(50), change with `--fast` / `--slow` |
| SMA(20) | Plain 20-day mean close; a slower, smoother trend line than EMA | 20 |
| RSI(14) | Wilder momentum, 0–100. High = strong recent gains, low = strong recent losses. Flat series = 50 by convention | 14 |
| MACD(12/26/9) | EMA12 − EMA26, with a 9-period signal line. Positive = short average above long average | 12/26/9 |
| Bollinger(20, 2σ) | SMA20 ± 2 population standard deviations. Wide bands = volatile past; narrow = quiet past | 20, 2σ |
| ATR(14) | Wilder average true range — typical daily price movement including gaps | 14 |
| Stochastic %K/%D (14,3) | Where the close sits inside the last 14 days' high–low range, smoothed over 3 days | 14, 3 |
| ADX(14) | Trend strength, 0–100, direction-free. Above ~25 is conventionally called a strong trend — a convention, not a fact | 14 |
| Volume vs 20-day average | Today's volume divided by the mean of the previous 20 days' volumes. Below 0.5 flags `thin_volume` | 20 |

Definitions are fixed in `indicators.py`'s docstring (EMA seeded with SMA,
Wilder smoothing for RSI/ATR/ADX, population σ for Bollinger) so any
result can be recomputed by hand.

## Why NEPSE needs extra suspicion

These are the falsifiers that break textbook indicators on NEPSE, and
what this scanner does about each:

1. **Thin trading.** Many NEPSE stocks trade a handful of shares on some
   days. A crossover printed on near-zero volume is one trade, not a
   trend. Check `volume_ratio_20d` / the `thin_volume` flag first.
2. **Circuit limits.** NEPSE price bands cap daily moves, so a stock can
   sit at its limit for days. RSI then pins near an extreme, Bollinger
   bands compress, and ATR understates the real risk — the market is
   not allowed to show its full range.
3. **Stale prices.** A "last traded price" from days ago is not a current
   price. This scanner never labels a price fresh: it reports the last
   date in the CSV, and the CSV's own date is the freshness claim. If
   your CSV is a week old, every signal in it is a week old.
4. **Short history.** ADX needs 28 bars before its first value; EMA(50)
   needs 50. Indicators without enough data return `n/a`, never a
   made-up number. A cross that "happened" before the slow average even
   existed is not reported as a cross — that warm-up limitation is real
   and is covered by a test (the first demo series failed exactly this
   way and was extended).
5. **Since-cross % is backward-looking.** A stock up 38% since its cross
   has already moved 38%. That number says nothing about the next move,
   and chasing it is the most common way a scanner misleads.

## Signal vs noise labelling

Every crossed row gets a label, always with its reasons (`--detail`
shows them). CONFIRMED means only "the past-price pattern is confirmed
by volume and trend" — never a prediction, never a buy signal:

| Label | Rule |
|---|---|
| NO SIGNAL | No bullish cross in history |
| NOISE | Thin volume (< 0.5x 20-day average) OR >= 5 trailing identical closes (circuit-limit / stale tail) |
| WEAK | Cross only, no confirmation |
| WATCH | Cross + volume >= 1.0x average, trend unconfirmed |
| CONFIRMED (pattern only) | Cross + volume >= 1.5x AND ADX >= 25 |

## Failure handling — how this scanner refuses to fail like others

These are generic failure modes of NEPSE scanners, hardened against here
without inspecting any private project (Nepse Decode is private and
off-limits; nothing from it was opened, copied, or used):

- **Stale/missing data as fresh:** the live fetcher raises an error
  naming what is missing; the scanner always prints the CSV's last
  date, so staleness is visible, never hidden.
- **Thin-trading false crosses:** volume gate + NOISE label (above).
- **Division by zero on flat series:** RSI = 50, Stochastic = 50, ADX =
  0, Bollinger bands collapse to the price, volume ratio = None on a
  zero average — all tested on flat and circuit-limit series.
- **Look-ahead:** every indicator uses only bars up to its own index;
  tested by proving that appending a future bar changes no earlier
  indicator value.
- **Silent partial failures:** `load_multi_csv_report()` drops a symbol
  with ANY bad row as a whole (a half-loaded symbol would silently
  shift its averages) and logs the reason; `scan_report()` logs
  per-symbol analysis failures the same way. The CLI prints every
  failure and keeps scanning the rest. A failed symbol never poisons
  the scan, and a failure is never swallowed.
- **Demo vs live confusion:** the screenshot table and the DEMO series
  are labelled "screenshot example" / "SYNTHETIC" in their own files
  and in the README. No demo number is ever presented as market data.

## Second check pass (28 Oct 2026) — what it found and changed

After the first 30 tests passed, a second pass ran 10 more edge-case
tests (gaps, flat prices, circuit-limit repeated closes, missing days,
single-day spikes, very short history, one bad symbol, look-ahead).
Findings:

1. **Two test expectations were wrong, not the code:** a circuit-limit
   tail counted 11 identical closes (the last rising bar also closed at
   the limit price), and a test series crossed during EMA(50)'s warm-up
   so it correctly had no recorded cross. Both tests were corrected to
   assert the right property; the scanner was not changed to fit them.
2. **One real gap, fixed:** the first build's strict CSV loader aborted
   the whole scan on one bad symbol. Fixed with the lenient
   per-symbol loader above (strict loader kept for callers that want a
   hard failure).
3. **One real limitation, documented not hidden:** a cross that happens
   before the slow average is defined cannot be recorded, because the
   slow average does not exist yet. The demo series was extended from
   60 to 100 bars so its cross happens after warm-up; the README states
   the limitation.
4. **Confirmed clean:** flat series, circuit-limit tails, single-day
   spikes, price gaps, and 2-bar histories all produce finite values or
   `n/a`, never inf, NaN, or a crash. Final count: **40/40 tests pass.**

## What this scanner deliberately does NOT do

- No live data feed. Research on 28 Oct 2026 found no documented, free,
  public NEPSE OHLCV API (see
  `../research/indicator-source-teardown-2026-10-28.md`). The licensed
  NEPSE feed is paid; unofficial routes reverse-engineer NEPSE's
  internal token flow. `data.py`'s live fetcher therefore raises an
  error naming what is missing instead of returning a stale or invented
  price.
- No buy/sell labels, no "probability of rise", no price targets, no AI
  forecast. Other NEPSE products sell those; this programme does not,
  because a probability without its sample and out-of-sample test is a
  claim, not evidence.
- No data from the Nepse Decode repo or anything inside it. That project
  is private and is never used, linked, or referenced here.

## Files

| File | What it is |
|---|---|
| `indicators.py` | SMA, EMA, RSI, MACD, Bollinger, ATR, Stochastic, ADX, volume ratio, crossover detection |
| `data.py` | CSV loaders (single + multi-symbol) and the unimplemented live-fetcher stub |
| `scanner.py` | Per-symbol analysis + the crossover scan |
| `cli.py` | Command-line scan printing the screenshot's columns |
| `examples/demo_prices.csv` | 100-bar SYNTHETIC DEMO series (not market data) |
| `examples/screenshot-example-2026-10-28.md` | The six screenshot symbols, labelled as a screenshot example, NOT live prices |
| `tests/test_scanner.py` | 30 tests: known values, crossovers, boundaries, bad data |
| `tests/test_edge_cases.py` | 10 tests: gaps, flat/circuit-limit series, spikes, missing days, short history, failure isolation, look-ahead |

Status: **Live on GitHub** (public, main, since 28 Oct 2026); tests 40/40 verified locally 28 Oct 2026. A CI workflow (`.github/workflows/test.yml` in the parent repo, pytest on Python 3.10/3.11/3.12) is included with this update so the suite also runs publicly on GitHub.
