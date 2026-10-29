# Example series for the walk-forward backtest — NOT NEPSE data

This file documents the example CSV used by `backtest.py`. It is an
example of the METHOD, not evidence about NEPSE, and must never be
presented as Nepali market data.

- **Symbol:** AAPL (Apple Inc., NASDAQ)
- **File:** `aapl-daily-closes-2024-2025.csv` (single-symbol format:
  `date,close,high,low,volume`)
- **Date range:** 2024-01-02 to 2025-12-31 (502 trading days)
- **Source:** Yahoo Finance chart API, public endpoint
  `query1.finance.yahoo.com/v8/finance/chart/AAPL` (interval `1d`,
  USD, exchange NMS as returned in the response metadata)
- **Fetched:** 29 Oct 2026, one polite request, saved unchanged apart
  from rounding prices to 2 decimals for the CSV
- **Rows:** 502 data rows, no missing closes/highs/lows/volumes,
  dates strictly increasing and unique (checked at fetch time)

Why AAPL and not a NEPSE series: no documented, free, public NEPSE
OHLCV API was verified (see `../research/indicator-source-teardown-2026-10-28.md`
and `data.py`), so no NEPSE series is invented to fill the gap. AAPL is
a free public series used only to demonstrate and test the backtest
arithmetic. Backtest results on it say nothing about NEPSE stocks.

Run it (from `scanner/`):

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from backtest import backtest_csv
r = backtest_csv('examples/aapl-daily-closes-2024-2025.csv')
print(r['metrics'])
for e in r['events']: print(e)
"
```
