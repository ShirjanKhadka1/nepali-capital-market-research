# Nepal data handling — fiscal years, dates, holidays, and CSV format

> Research only. Not investment advice. Exchange: NEPSE, always.
> Nothing here invents a calendar, a holiday, or a price. Anything not
> sourced below is labelled TO VERIFY.

## 1. Bikram Sambat (BS) / AD fiscal years

Nepal's fiscal year runs roughly mid-July to mid-July and is named by
the BS year in which it starts. Example from the programme's own records:
Bottlers Nepal (Terai)'s FY 2081/82 (39th annual report) ended
16 July 2025 — so FY 2081/82 covers approximately mid-July 2024 to
16 July 2025. Always state both the BS fiscal year and the AD dates
when you quote a Nepal figure; a bare "FY 2081/82" without AD dates is
ambiguous to an international reader, and a bare AD year without the BS
year is ambiguous to a Nepal reader.

**BS ↔ AD conversion: TO VERIFY per date.** BS months do not align
neatly with AD months, and conversion tables differ by source. Do not
hand-compute a BS date from an AD date (or vice versa) in a report:
use a named, verifiable converter or calendar source, cite it on the
same page, and flag any converted date whose converter is not cited as
TO VERIFY. No conversion table is included in this guide, deliberately
— a table copied without a source would be exactly the invented data
this programme refuses to publish.

## 2. NEPSE holiday calendar: check, never hardcode

NEPSE trading days, festival closures (e.g. Dashain), and any special
closures are set by NEPSE/SEBON notices. This guide does **not** list
holiday dates: a hardcoded list goes stale and then silently corrupts
every "trading days since" calculation built on it. Before any scan or
study that depends on trading days:

- Check the current NEPSE/SEBON notice for the period in question.
- Record the notice (source + date) alongside the study.
- Treat any period containing an unconfirmed closure as TO VERIFY for
  day-count purposes.

The scanner itself does not need a holiday calendar: it works on the
dates actually present in the CSV. A missing trading day in the CSV is
a gap in the data, not a day to interpolate — never fill it.

## 3. What a valid scanner CSV must contain (exact spec)

The scanner accepts only user-supplied CSV. There is no live NEPSE feed
(see `../research/indicator-source-teardown-2026-10-28.md` and the
toolkit's `DATA_SOURCES.md`: no documented free public NEPSE OHLCV API
was verified as of 28 Oct 2026; the paid licensed feed is the owner's
funding decision only and is not started).

**Single-symbol file** (`scanner/data.py: load_csv`):
columns `date, close, high, low, volume`. Encoding UTF-8 (BOM tolerated).
Rows in date order, strictly increasing, unique dates, `close > 0`,
`high >= low`. Any bad row raises an error — bad rows are never
silently skipped, because a skipped row would silently shift every
moving average after it.

**Multi-symbol file** (`load_multi_csv` / `load_multi_csv_report`):
columns `symbol, sector, date, close, high, low, volume`. Symbols may
interleave. In the lenient scan loader, a symbol with ANY bad row is
dropped as a whole and the reason is recorded; other symbols are
unaffected. A file-level problem (missing file, wrong columns, zero
usable rows) still raises, because then there is no scan at all.

**Corporate actions — TO VERIFY per source.** Bonus shares, rights
issues, and splits change prices without changing value. The scanner
does NOT adjust for them. If your CSV is unadjusted (the usual case for
raw exports), a bonus/split date looks like a price crash and a
crossover computed across it is meaningless. State on the same page as
any scan whether the CSV is adjusted or unadjusted; if you do not know,
label the scan's crossovers TO VERIFY around action dates and do not
quote a "since cross %" across one.

## 4. Labelling rule (applies to every Nepal output)

Every Nepal figure carries: exchange (NEPSE), BS fiscal year where
relevant, AD period, source, and retrieval date — or UNKNOWN/TO VERIFY.
NEPSE tickers are never confused with other exchanges' tickers
(NEPSE BNT ≠ NYSE BNT).

## 5. Intraday trading — UPCOMING, not live (28 Oct 2026)

Nepal is about to try intraday trading practice. As far as
programme records show, intraday trading is NOT yet live: no
launch date, no rules, and no intraday data feed are recorded
here, and none are invented. The scanner remains daily-CSV-only,
and no intraday signal is claimed anywhere in this programme.
When SEBON/NEPSE formally announces intraday trading, that
announcement (with its date) is what would unlock any intraday
work — until then, intraday stays labelled UPCOMING / TO VERIFY.
