# R6 results on EXISTING labelled example data — NO real-NEPSE run was possible

**Plain statement first: no real-NEPSE backtest and no real-NEPSE
walk-forward re-run was possible in this round.** No permitted real
NEPSE price dataset exists (see `NEPSE_USER_CSV_TERMS.md`: the
public site's terms forbid bulk re-scraping to republish a competing
feed, no bulk-access permission is on file, and no documented free
public NEPSE OHLCV API exists). Both analyses below were therefore
re-run on the EXISTING labelled example data shipped with this
scanner — AAPL daily closes, a US equity, NOT NEPSE — and the
results say nothing about NEPSE, about AAPL's future, or about any
security. Research only, never a buy/sell/hold recommendation.

## Data (labelled, existing, untouched)

- File: `examples/aapl-daily-closes-2024-2025.csv` (shipped before
  this round; not created, edited, or re-sourced here).
- Series: AAPL (NASDAQ) daily closes, **2024-01-02 → 2025-12-31,
  n = 502 bars**, first close 185.64, last close 271.86.
- Method note: the scanner backtest and the toolkit walk-forward
  below use the same file, so the two analyses are comparable with
  each other but neither generalises beyond this one series and
  period.

## 1. Scanner crossover backtest (re-run 29 Oct 2026)

Method: `backtest.backtest_csv` with default EMA(20)/EMA(50) crosses,
forward returns at horizons 5 and 20 bars. A "win" means only that
the price moved in the cross's direction over the horizon. 95%
confidence intervals are Wilson score intervals for the hit rate —
with n = 3 and n = 2 they are extremely wide, which is itself the
finding: **5 events cannot support any claim about the pattern**.

| Horizon | Direction | n | Wins / losses / flats | Hit rate | 95% CI | Mean fwd return | Median | Lift vs naive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 bars | Bullish | 3 | 1 / 2 / 0 | 33.3% | 6.2% – 79.2% | +0.47% | −0.46% | −23.1 pts |
| 5 bars | Bearish | 2 | 1 / 1 / 0 | 50.0% | 9.5% – 90.5% | +1.62% | +1.62% | +6.5 pts |
| 20 bars | Bullish | 3 | 2 / 1 / 0 | 66.7% | 20.8% – 93.9% | −1.87% | +1.00% | −1.9 pts |
| 20 bars | Bearish | 2 | 1 / 1 / 0 | 50.0% | 9.5% – 90.5% | −6.05% | −6.05% | +18.6 pts |

Naive baselines (same walk-forward discipline, all eligible
windows): h = 5: n = 448 windows, 56.5% positive / 43.5% negative,
mean +0.59%. h = 20: n = 433 windows, 68.6% positive / 31.4%
negative, mean +2.45%. Excluded (crosses too close to the series
end for a full horizon): 0 at both horizons.

Reading, wins AND losses: the bullish 5-bar pattern lost to naive
by 23.1 points; the bearish 20-bar lift (+18.6 pts) comes with a
negative mean return (−6.05%) on just 2 events and a CI spanning
9.5%–90.5% — it is noise, not an edge, and is reported as such,
not hidden. These numbers reproduce the previously recorded
backtest on this file exactly (same 5 events); the CIs are new.

## 2. Toolkit walk-forward model comparison (re-run 29 Oct 2026)

Method: `toolkit.predictive.compare_models_walk_forward` on the
same 502 closes, `train_size = 251`, horizons (1, 3, 5), default
four-model set only (naive, moving_average_5, linear_trend,
exp_smoothing_0.3). At each origin the model sees only data up to
that origin. MAE/RMSE in US dollars per share.

| Horizon | n_test | Naive MAE | Best fitted MAE | Best model | Beats naive? |
| --- | --- | --- | --- | --- | --- |
| h = 1 | 251 | 2.8474 | 4.5180 (exp_smoothing_0.3) | naive | No |
| h = 3 | 249 | 5.6394 | 6.5891 (exp_smoothing_0.3) | naive | No |
| h = 5 | 247 | 7.7088 | 7.9284 (exp_smoothing_0.3) | naive | No |

Full h = 1 ranking: naive 2.8474 / 4.3117 (MAE/RMSE),
exp_smoothing_0.3 4.5180 / 6.2247, moving_average_5 4.9345 /
6.9123, linear_trend 22.7787 / 26.2165. Full h = 3: naive 5.6394 /
8.1204, exp_smoothing_0.3 6.5891 / 8.8699, moving_average_5 7.0780 /
9.4096, linear_trend 23.4342 / 26.8982. Full h = 5: naive 7.7088 /
10.3697, exp_smoothing_0.3 7.9284 / 10.5098, moving_average_5
8.4038 / 10.9391, linear_trend 24.1026 / 27.5718.

Reading: **naive wins at every horizon** — the same conclusion as
the previously recorded real-data walk-forward (AAPL 251 closes,
2025-10-29 → 2026-10-28, where naive MAE was 3.766 / 6.977 / 9.229
at h = 1 / 3 / 5), on a different series and period, so the two
runs corroborate the direction but are not the same run and their
numbers must not be mixed. MAE grows with horizon for every model,
including naive. One symbol, one 24-month period, closes only, no
transaction costs — this is NOT a statement about general model
accuracy, about AAPL, or about any NEPSE security.

## What a real-NEPSE re-run would require

One of: (a) written bulk-access permission from shirjankhadka.com.np
(the route its own terms page names), (b) a documented free public
NEPSE OHLCV endpoint whose terms allow redistribution, or (c) a
paid NEPSE Market Data Provider licence (owner's funding decision).
Until then, the loader-only bridge stands, and any future re-run
must report liquid names only, flag thin trading per symbol, and
show wins AND losses with the naive baseline, CIs, and n — the
same discipline as above.
