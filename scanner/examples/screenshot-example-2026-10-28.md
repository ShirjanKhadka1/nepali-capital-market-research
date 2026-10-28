# Screenshot example — Crossover Scanner, 28 Oct 2026

**Status: screenshot example ONLY. These are NOT live prices, NOT today's
market data, and NOT outputs of this scanner.**

Source: a screenshot sent by the user on 28 Oct 2026 showing a "Crossover
Scanner" list of Hydro Power stocks on NEPSE. The screenshot shows LTP,
Fast, Slow, "Since cross" and a cross date for each symbol. The Fast/Slow
periods are NOT shown in the screenshot, so they are UNKNOWN here — do not
assume 20/50. The "Since cross" percentages are the screenshot's own
reported figures; they cannot be recomputed from the screenshot because
the close on each cross date is not shown. They are reproduced here so
the scanner's output format can be compared column-for-column, nothing more.

| Symbol | Sector (NEPSE) | LTP | Fast | Slow | Since cross | Cross date |
|---|---|---|---|---|---|---|
| PHCL | Hydro Power | 371.00 | 350.06 | 331.99 | +21.72% | 14 Sep (44d ago) |
| MHNL | Hydro Power | 271.10 | 260.71 | 254.70 | +5.49% | 14 Sep (44d ago) |
| GHL | Hydro Power | 331.00 | 309.09 | 279.11 | +37.97% | 11 Sep (47d ago) |
| GVL | Hydro Power | 577.10 | 544.31 | 512.19 | +19.01% | 11 Sep (47d ago) |
| LEC | Hydro Power | 251.10 | 245.27 | 242.82 | +2.03% | 10 Sep (48d ago) |
| MBJC | Hydro Power | 336.20 | 321.88 | 302.85 | +20.07% | 9 Sep (49d ago) |

Reading notes (all TO VERIFY against real data before any use):
- "44d ago" etc. are calendar days from the screenshot date (28 Oct 2026),
  which is why this scanner reports `days_since_cross` as calendar days
  between the cross date and the last date in the CSV.
- A large "Since cross" (e.g. GHL +37.97%) describes a move that ALREADY
  happened. It is not evidence the move continues — that is exactly the
  falsifier this scanner's README warns about.
- For a live equivalent of this table, supply a real multi-symbol CSV
  (see `demo_prices.csv` for the format) and run `python3 cli.py --csv
  <file>`. Until a documented free NEPSE data endpoint is verified, there
  is no live feed behind this table.

## Synthetic demo (tested, reproducible)

`demo_prices.csv` is a 100-bar SYNTHETIC series for a fictional symbol
DEMO (Hydro Power): falls from 200 to 170, flat for 40 bars, then rises
3/day to 290. It exists only so the crossover maths can be tested
end-to-end. Its scan output (EMA20/EMA50) on 28 Oct 2026:

| Symbol | Sector | LTP | Fast | Slow | Since cross | Cross date |
|---|---|---|---|---|---|---|
| DEMO | Hydro Power | 290.00 | 262.03 | 232.19 | +51.83% | 2026-08-06 |

Run it: `cd scanner && python3 cli.py --csv examples/demo_prices.csv`
