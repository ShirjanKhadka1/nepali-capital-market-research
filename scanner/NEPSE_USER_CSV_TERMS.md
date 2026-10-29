# NEPSE data bridge — terms audit and user-supplied CSV format (Round 3, R6)

**Verdict first: LOADER ONLY. No real NEPSE price dataset is published
with this round, and no real-NEPSE backtest or walk-forward re-run was
possible.** The loader in `nepse_bridge.py` loads a CSV you supply, in
the format below, and refuses to run without a named source. A tiny
synthetic example (`examples/nepse_user_supplied_SYNTHETIC.csv`) exists
for format testing only — its prices are invented and labelled
SYNTHETIC in the file itself, never real NEPSE prices.

Research only. Never a buy/sell/hold recommendation. NEPSE intraday
trading is UPCOMING, not live — nothing here claims otherwise.

## 1. Terms audit — public website shirjankhadka.com.np (fetched 29 Oct 2026)

Pages read as public page text: homepage (`/`), the NEPSE portfolio
tracker page (`/nepse-portfolio/`), its linked Data Use & Terms page
(`/data-terms.html`), and the privacy page (`/privacy.html`). The
site's repository/internals were not touched. No bulk data was
scraped; only page text was read.

### Source A — the site's own Data Use & Terms (effective 1 October 2026)

Quoted verbatim (the parts that decide this round):

> "Prices, indices, floorsheets and corporate-action notices are
> compiled from public sources: the official NEPSE website and
> disclosures, company notices mirrored by market portals (ShareSansar,
> MeroLagani, Arthasansar and others), and Nepal Rastra Bank
> publications. Every corporate-action record we publish as verified
> is backed by the official NEPSE notice PDF."

> "We respect the terms of every upstream source. If a source forbids
> redistribution, we replace it, seek permission, or publish only
> derived values with attribution."

> "You may quote figures, share links, and screenshot charts for
> personal, educational, or journalistic use with attribution
> ("Source: Nepse Decode, shirjankhadka.com.np"). Bulk re-scraping of
> this site's data files to republish a competing feed is not
> permitted — if you need bulk access, email us and we'll talk."

> "Please don't hammer the site with automated requests. Data files
> are sharded and CDN-cached for normal browsing; aggressive scraping
> may get rate-limited."

**Permission verdict — BULK REDISTRIBUTION NOT PERMITTED.** Quoting
individual figures with attribution is allowed; copying the site's
data files (or a price series derived from them in bulk) into this
repo as a dataset would be exactly the bulk re-scraping / competing
feed the terms forbid. No emailed bulk-access permission is on file,
and none was sought by this round (seeking it is the owner's
decision, not a worker's). So no dataset from this site is published
here — not raw, and not as a bulk derived series either, because the
bulk act itself is what the terms restrict.

### Source B — the site's portfolio tracker page (attribution on the page)

> "Live quotes via our own 15-minute market snapshot; figures may be
> delayed — see our data terms."

> "Prices come from the latest daily batch — during market hours they
> can lag the live market, and a holding with no price in the latest
> batch shows as – and is left out of the totals rather than guessed."

> "NEPSE publishes no free official real-time API, so community
> mirrors and batch data may be delayed."

This corroborates the known state (no free official real-time API)
and adds a delay caveat, but it names no upstream licence that would
permit redistribution, so it changes nothing in the verdict.

### Source C — upstream sources named by the site (NEPSE, ShareSansar, MeroLagani, Arthasansar, NRB)

**No redistribution permission established for any of them.**

- NEPSE (nepalstock.com.np): no documented free public OHLCV API
  exists (research 28 Oct 2026, re-confirmed this round by the
  site's own statement above); the exchange's homepage renders only
  "Loading..." and its prices appear only through an internal
  token-protected flow, which is undocumented access and is NOT
  wired in. The licensed route (NEPSE Market Data Provider) is paid
  and NOT started — the owner's funding decision only.
- ShareSansar / MeroLagani / Arthasansar / NRB publications: the
  site's terms page names them as compilation sources but publishes
  no licence or redistribution terms for them, and this round found
  no permission statement from them. Absence of a permission is not
  permission — so no series sourced from them is republished here.

### Source D — homepage and privacy page

The homepage text fetch returns the portfolio shell only (no data
attribution, no licence language — the page is JavaScript-rendered
and the text fetch does not execute it). The privacy page covers
personal data only ("This site links to external websites (market
data sources, LinkedIn, and others). Their privacy practices are
their own") — it contains no data-redistribution terms. Neither page
grants anything; both are recorded here so the audit does not
over-claim what was seen.

### What WOULD change the verdict

1. Written bulk-access permission from the site owner (email route
   the terms page itself names), or
2. a documented free public NEPSE OHLCV endpoint whose own terms
   allow redistribution, or
3. a paid NEPSE Market Data Provider licence (owner's funding
   decision).

Until one of those exists, this bridge stays loader-only.

## 2. User-supplied CSV format (the only real-NEPSE input this scanner accepts)

Multi-symbol file, one row per symbol per trading day:

```
symbol,sector,date,close,high,low,volume
BNT,Manufacturing & Processing,2026-10-12,11888,11900,11800,50
```

Single-symbol file:

```
date,close,high,low,volume
2026-10-12,11888,11900,11800,50
```

Rules (enforced by `data.load_csv` / `data.load_multi_csv`, wrapped by
`nepse_bridge.load_user_csv` / `load_user_csv_single`):

- Dates ISO (`YYYY-MM-DD`), strictly increasing and unique per symbol.
- `close > 0`, `high >= low`, all numerics finite. A bad row raises
  `NepseDataError` — it is never silently skipped, because a skipped
  row would silently shift every moving average after it.
- A **source must be named** on every load (`source` argument). The
  source string must travel with any published result. A scan over
  unsourced prices is an unsourced scan.
- Thin-trading flag: the scanner flags `thin_volume` (< 0.5x 20-day
  average volume) and trailing flat days in its output rows. A close
  set by a handful of trades (e.g. the ledger's BNT 11,888 close on
  2 trades / 50 shares) is a stale-price risk, not a market price —
  say so wherever it is used.
- Nepal frictions reminder (user-supplied 28 Oct 2026, applied at
  analysis time, never baked into prices): broker 0.36/0.33/0.31/
  0.27/0.24% (min Rs 10), SEBON 0.015%, DP Rs 25/scrip, CGT 5%
  ≤365 days / 3.75% >365 days, circuit ±15%, settlement T+2
  (broker 58 offers T+1).

## 3. What was NOT done (so nobody has to re-check)

- No bulk scrape of shirjankhadka.com.np or any portal. Only public
  page text was read.
- No unofficial token-flow library was wired in, in this scanner or
  in the toolkit.
- No live NEPSE feed was invented, and no NEPSE price was fabricated
  to fill a gap. The synthetic example is labelled SYNTHETIC.
- No real-NEPSE backtest or walk-forward re-run: with no permitted
  dataset, both analyses were re-run on the EXISTING labelled
  example data instead (see `R6-EXAMPLE-DATA-RESULTS.md` in this
  folder, on the same branch).
