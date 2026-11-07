# Sources merged into the NEPSE scanner — 2026-11-07

What was taken from two outside repos, what was changed, and what was
deliberately left out. Every file added or changed in this merge
records its source here; nothing was copied silently.

## Source repos (inspected from full local clones, read-only)

| Repo | URL | Commit | Licence |
|---|---|---|---|
| day-trader-skill | https://github.com/Jakeschincariol/day-trader-skill | `3d0f4ef` (2026-10-20), v2.0.0 | MIT |
| FinceptTerminal | https://github.com/Fincept-Corporation/FinceptTerminal | `7716ee8` (2026-10-26) | GNU AGPL-3.0-or-later |

## Licence rule (binding for this MIT repo)

- **day-trader-skill (MIT):** arithmetic and scanner discipline may be
  adapted, with attribution (repo + commit + "adapted from"). Done in
  `setups.py` and below.
- **FinceptTerminal (AGPL-3.0):** ideas and formulas ONLY. No Fincept
  code, text, layouts, command syntax, branding, or trade dress was
  copied into this repo. The criteria grammar in `screen.py` is an
  original implementation of the screener idea (field/operator/value
  clauses + per-clause audit log), written from scratch for this
  scanner's rows, and is attributed here and in the module docstring.

## Adopted / adapted into `scanner/`

| # | Capability | Source | What landed |
|---|---|---|---|
| D2 | Scanner rule table + universe hygiene + coverage reporting (scanned / failed / usable, PARTIAL flag) | day-trader-skill, adapted | `scanner.py`: `coverage_summary()` + `scan_with_coverage()`; `cli.py` prints the coverage note on every run; `setups.py`: `scan_setups()` reports the same coverage shape |
| D2 | Named setups on daily closes | day-trader-skill trader-scanner, adapted | `setups.py`: `breakout_20d`, `bull_flag`, `reclaim_ma20`, `oversold`, `oversold_bounce` — daily closes only, exact definitions in code + `scanner/README.md` |
| D2 | Two-stage confirmation (cheap necessary condition, expensive exact check, stated cap, PARTIAL when capped) | day-trader-skill, adapted | `setups.py`: `scan_setups()` — stage 1 from the shared per-symbol snapshot / tail slice, stage 2 exact recomputation from raw closes, `max_confirmations` (default 50), unconfirmed candidates listed, never reported as matches |
| F5 | Screener as criteria grammar (field/operator/value clauses, audit log of names removed per clause) | FinceptTerminal, idea only, reimplemented | `screen.py`: `screen()` with ops `>`, `>=`, `<`, `<=`, `==`, `between`; per-clause audit log; grammar documented in `scanner/README.md` |

Tests: `tests/test_setups_screen.py` (35 tests) covers every setup
(positive, boundary, negative, too-short history), coverage counts and
the PARTIAL wording, the confirmation cap (including cap 0), stage-1
never rejecting an exact match, and every screen operator plus the
audit log and its error cases.

## Explicitly rejected (with reason)

| # | Capability | Reason |
|---|---|---|
| R1 | Live trading / order execution (Fincept `src/trading/`, broker adapters; day-trader-skill trader-broker) | Real-money trading; this programme is research-only by user rule |
| R2 | Algo-trading / auto-execution, signals as orders | Out of scope; scanner outputs are "matches a rule" lists, never recommendations |
| R3 | US-universe endpoints (Yahoo as NEPSE coverage, NYSE holidays, PDT rules, TSLA examples as evidence) | Wrong market, wrong jurisdiction; NEPSE data stays CSV-only (user-supplied CSVs / synthetic example), no invented live feed |
| R4 | "Buy" / "sell" / "hold" language, price targets, probability-of-rise | A match is a past-price description, not a prediction; every setup result carries its rule values and no recommendation |
| R5 | Intraday bars / day-trading timeframes | NEPSE scanner is daily closes only; intraday data has no verified free source here |
| R6 | Fincept branding, layouts, command syntax, trade dress; paid-data dependence | AGPL + trademark/trade-dress assertions; ideas only |

## What did not change

- `indicators.py` is untouched: `oversold` / `oversold_bounce` reuse
  its Wilder RSI-14; `reclaim_ma20` reuses its SMA-20.
- `scan()` / `scan_report()` public API is unchanged; coverage is a
  new wrapper (`scan_with_coverage()`), not a breaking change.
- No live feed was added. `data.py`'s live fetcher remains a stub
  that raises; NEPSE prices still come only from user-supplied CSVs.
