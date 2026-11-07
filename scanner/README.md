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

Tests: `python3 -m pytest tests/ -v` (113 tests, all passing on 7 Nov 2026; generated count in `../status.json`, checked by `../scripts/check_numbers.py`;
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

## Coverage reporting — a scan is PARTIAL when anything failed

`scan_with_coverage()` (in `scanner.py`; the CLI uses it on every
run) returns the rows plus explicit coverage accounting:

```python
{"universe": N, "scanned": N, "failed": N, "usable": N,
 "failed_symbols": [...]}
```

- **universe:** symbols in the input. **scanned:** symbols attempted
  (always == universe — a scan never silently skips a symbol it was
  given). **failed:** symbols whose analysis raised and were excluded.
  **usable:** symbols analysed successfully (scanned − failed). A
  symbol that analysed fine but matched no rule still counts as
  usable — "usable" is about the data, not the match.
  **failed_symbols:** the failed symbols, sorted, so the gap is
  nameable, not just countable.

If any symbol failed, the result is explicitly PARTIAL and says so in
plain language: "PARTIAL: 2 of 10 symbols failed and were excluded
from the scan: SYM1, SYM2. Rows below cover only the 8 usable
symbols." A scan with failures is never presented as complete. When
nothing failed the note says "Complete: all N symbols scanned, no
failures." `scan_setups()` reports the same coverage shape. The
discipline (coverage counts + PARTIAL flag) is adapted from
day-trader-skill (MIT, commit 3d0f4ef); see `SOURCES_MERGE_2026-11-07.md`.

## Named setups — daily closes only

`setups.py` implements five close-based setups. A match means only
"the symbol's past closes satisfy the stated rule" — never a
recommendation, never a prediction. Each match entry carries the exact
rule values that triggered (breakout level, RSI value, ...), so any
match can be recomputed by hand from the CSV.

| Setup | Exact rule |
|---|---|
| `breakout_20d` | Latest close above the highest close of the prior 20 closes (needs 21 closes). A close exactly equal to the level is not a breakout |
| `bull_flag` | Close rose at least 10% over the 10 sessions ending 6 bars ago (closes[−16] → closes[−6]), then the last 5 closes span at most 5% ((max − min) / min). Needs 16 closes. Both thresholds inclusive |
| `reclaim_ma20` | Latest close above its 20-day moving average while the prior close was at or below its 20-day moving average (needs 21 closes) |
| `oversold` | Wilder RSI-14 below 30 on the latest close (reuses `indicators.rsi`; needs 15 closes). RSI exactly 30 is not oversold |
| `oversold_bounce` | Wilder RSI-14 below 30 at least once in the last 5 sessions AND the latest close above the prior close (needs 15 closes) |

Run them with `scan_setups(groups)` — it returns
`{"matches", "coverage", "partial", "capped", "unconfirmed",
"failures", "note", "max_confirmations", "confirmations_used"}`.
`matches` maps each setup name to its matching symbols with their
rule values. A symbol with too few closes for a setup simply does
not match it — that is not a failure.

## Two-stage confirmation

`scan_setups()` confirms in two stages, adapted from the
day-trader-skill pattern:

1. **Cheap necessary condition first.** Evaluated per setup from the
   shared per-symbol indicator snapshot (one `analyse()` call per
   symbol, reused across all five setups) or from a tail slice of the
   closes — O(1) per setup once the snapshot exists. Each stage-1
   condition is implied by its setup's exact rule (the proof is in
   `setups.py`), so stage 1 never creates a false negative; for the
   RSI setups stage 1 checks the same value stage 2 recomputes.
2. **Expensive exact check second.** The rule is recomputed from the
   raw closes, and only confirmed matches are reported.

Confirmations are capped: `max_confirmations` (default 50). When the
cap is hit, the remaining candidates are listed as `unconfirmed`,
`capped` is True, and the result is PARTIAL with a plain-language
note naming the cap. An unconfirmed candidate is never reported as a
match and never silently dropped.

## Criteria grammar — an auditable screen

`screen.py` filters rows (e.g. `analyse()` rows) by a list of
field/operator/value clauses, applied in order:

```python
from screen import screen
result = screen(rows, [
    {"field": "rsi14", "op": "<", "value": 30},
    {"field": "ltp", "op": ">=", "value": 100},
])
result["rows"]    # rows that survived every clause, in input order
result["audit"]   # [{"clause": ..., "removed": N, "remaining": N}, ...]
```

Operators: `>`, `>=`, `<`, `<=`, `==`, `between` (inclusive
`[lo, hi]`). The audit log records, per clause in order, how many
names that clause removed and how many remained — replay the clauses
in order and the counts reproduce, so a screen is auditable. A row
whose field value is `None` ("no data for this indicator") never
matches a numeric clause, so it is removed by that clause and the
removal is counted. Errors are loud: an unknown operator, a malformed
`between` value, a field missing from a row, or an incomparable value
all raise `ValueError` naming the problem — a typo in a field name
never silently empties a screen. The idea (clauses + per-clause audit
log) is adapted from FinceptTerminal's screener (AGPL-3.0, commit
7716ee8); the grammar and implementation are written from scratch,
no Fincept code copied. See `SOURCES_MERGE_2026-11-07.md`.

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
   `n/a`, never inf, NaN, or a crash. Final count: **57/57 tests pass** (40 original + 17 signal-label tests).

## Walk-forward backtest (29 Oct 2026)

`backtest.py` scores past crossover patterns walk-forward: a signal at
time `t` uses only data up to `t` (EMA at `i` uses closes up to `i`;
a test proves a cross at `t` is identical on the prefix ending at `t`).
The outcome — the close `horizon` bars later — only ever scores the
signal, never forms it. Labels are PATTERN ONLY: a "win" means only
"the price moved in the direction of the past cross over the horizon".
Never a buy/sell/hold recommendation, never a prediction, and never
evidence about NEPSE.

Run it on your own single-symbol CSV:

```bash
cd scanner
python3 -c "
import sys; sys.path.insert(0, '.')
from backtest import backtest_csv
r = backtest_csv('my_prices.csv')  # defaults: EMA(20)/EMA(50), horizon 5
print(r['metrics'])
for e in r['events']: print(e)
"
```

Metrics (defined in `backtest.py`'s docstring): hit rate (wins /
events, flats counted as events), mean/median forward return, mean
absolute error of a no-change forecast on the signal windows, and the
naive baseline — the same scoring over EVERY eligible window after
slow-average warm-up, with no signal at all. `hit_rate_lift` is the
signal hit rate minus the matching naive rate. Crosses too close to
the series end for a full horizon are counted as `excluded`, never
scored on a partial horizon.

### Example result — AAPL, NOT NEPSE data

Series: AAPL daily closes, 2024-01-02 to 2025-12-31, 502 bars, fetched
once 29 Oct 2026 from the Yahoo Finance chart API (see
`examples/aapl-example-2026-10-29.md` for symbol, range, source, and
fetch date). It demonstrates the method only; it says nothing about
NEPSE. Defaults EMA(20)/EMA(50); only 5 crosses in 502 bars, so every
rate below rests on a handful of events and proves nothing on its own.

| Horizon | Direction | Events | Wins | Losses | Hit rate | Naive rate | Lift | Mean fwd return |
|---|---|---|---|---|---|---|---|---|
| 5 bars | Bullish | 3 | 1 | 2 | 33.3% | 56.5% (448 windows) | −23.1 pts | +0.47% |
| 5 bars | Bearish | 2 | 1 | 1 | 50.0% | 43.5% (448 windows) | +6.5 pts | +1.62% |
| 5 bars | Combined | 5 | 2 | 3 | 40.0% | — | — | — |
| 20 bars | Bullish | 3 | 2 | 1 | 66.7% | 68.6% (433 windows) | −1.9 pts | −1.87% |
| 20 bars | Bearish | 2 | 1 | 1 | 50.0% | 31.4% (433 windows) | +18.6 pts | −6.05% |
| 20 bars | Combined | 5 | 3 | 2 | 60.0% | — | — | — |

Every event, wins AND losses, at the 5-bar horizon:

| Signal date | Direction | Outcome | Forward return | Signal → horizon close |
|---|---|---|---|---|
| 2024-05-10 | Bullish | win | +3.73% | 183.05 → 189.87 (2024-05-17) |
| 2025-01-22 | Bearish | loss | +6.94% (price rose) | 223.83 → 239.36 (2025-01-29) |
| 2025-02-19 | Bullish | loss | −1.84% | 244.87 → 240.36 (2025-02-26) |
| 2025-03-11 | Bearish | win | −3.69% | 220.84 → 212.69 (2025-03-18) |
| 2025-07-09 | Bullish | loss | −0.46% | 211.14 → 210.16 (2025-07-16) |

Read honestly: at 5 bars the bullish pattern lost more often than it
won (1 win, 2 losses) and trailed its naive baseline by 23.1 points;
at 20 bars it won 2 of 3 yet still trailed the naive positive rate and
averaged −1.87% because its one loss (−12.10%) outweighed its wins.
A hit rate without its losses, its baseline, and its event count is a
claim, not evidence — this table keeps all three. No event was
excluded (0 at both horizons).

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
| `scanner.py` | Per-symbol analysis + the crossover scan + coverage reporting (`scan_with_coverage`) |
| `setups.py` | Five named close-based setups + two-stage confirmation scan (`scan_setups`) |
| `screen.py` | Criteria-grammar screen (`screen`) with per-clause audit log |
| `SOURCES_MERGE_2026-11-07.md` | Sources merged 7 Nov 2026: day-trader-skill (MIT) + FinceptTerminal (AGPL-3.0, ideas only) — adopted / adapted / rejected |
| `cli.py` | Command-line scan printing the screenshot's columns |
| `examples/demo_prices.csv` | 100-bar SYNTHETIC DEMO series (not market data) |
| `examples/screenshot-example-2026-10-28.md` | The six screenshot symbols, labelled as a screenshot example, NOT live prices |
| `tests/test_scanner.py` | 30 tests: known values, crossovers, boundaries, bad data |
| `tests/test_edge_cases.py` | 10 tests: gaps, flat/circuit-limit series, spikes, missing days, short history, failure isolation, look-ahead |
| `tests/test_signal_labels.py` | 17 tests: signal-vs-noise labels |
| `backtest.py` | Walk-forward crossover backtest (pattern only): events, hit rate, naive baseline, excluded count |
| `tests/test_backtest.py` | 13 tests: hand-checked wins/losses/flats, naive baseline, no-lookahead, near-end exclusion, CSV round-trip |
| `tests/test_setups_screen.py` | 35 tests: five named setups (positive, boundary, negative, short history), coverage + PARTIAL wording, confirmation cap, screen grammar + audit log |
| `tests/test_bnt_case_study.py` | 5 tests: BNT case-study CSV parses (18 rows, expected columns), key figures match the verified-figures file, explicit nil is 0 not missing, every row names a source, study still labelled Inputs + skeleton NOT a valuation |
| `examples/aapl-daily-closes-2024-2025.csv` | 502-bar AAPL daily example (Yahoo Finance chart API, fetched 29 Oct 2026) — NOT NEPSE data |
| `examples/aapl-example-2026-10-29.md` | Source note for the AAPL example: symbol, range, source, fetch date |

Status: **Live on GitHub** (public, main, since 28 Oct 2026); 113/113 tests verified locally 7 Nov 2026 (generated count in `../status.json`). A CI workflow (`.github/workflows/test.yml` in the parent repo, pytest on Python 3.10/3.11/3.12) is included with this update so the suite also runs publicly on GitHub.
