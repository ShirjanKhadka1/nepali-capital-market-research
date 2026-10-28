# Indicator & data-source teardown — NEPSE reference sites, 28 Oct 2026

**Purpose:** what the four reference sites publicly show, what data source
they publicly state, and whether any of them offers a documented, free,
public API this scanner may call. **No code was copied from any of them.
No paywalled or login-locked data was accessed. No login or paywall was
bypassed.** Anything not found in public pages is marked TO VERIFY, not
filled in by guessing.

**Ownership note:** Chart Nepali is NOT the user's site — it is someone
else's site. It is listed here only as a public reference, exactly like
the other three.

**Headline finding:** as of 28 Oct 2026, NONE of the four publishes a
documented, free, public OHLCV API that this scanner can call. That is
why `scanner/data.py` ships a CSV loader plus a fetcher stub that raises
an error, instead of a live feed. The one licensed route (NEPSE's Market
Data Provider) is paid; the unofficial routes work by reverse-engineering
NEPSE's internal token flow, which is undocumented access, not a public
API, and is deliberately NOT wired in.

## 1. Nepalytix (nepalytix.com) — PUBLIC

What it publicly shows:
- Real-time NEPSE analytics, live prices, indices, sector movement,
  broker flow, floorsheet records, AI-powered signals (breakout alerts,
  trend shifts, reversal patterns), portfolio tracking, company
  financials (EPS, BVPS, dividend history), and valuation tools (DCF,
  P/E) — per its homepage and app-store listing.
- An "open finance data hub": its homepage says daily floorsheet, broker
  data, technical feeds and historical financials are "freely accessible"
  for students, quant researchers and AI builders.

What data source it publicly states:
- NEPSE market data generally; no specific upstream feed or endpoint is
  named on the public pages found. Its pricing page puts API and bulk
  data access on an Enterprise tier (custom pricing, for institutions),
  with "Custom screeners and scan logic" and "Custom alerts and signal
  engine" also on that tier.

Public API? **No documentation found (TO VERIFY).** The "open data hub"
claim could not be turned into a URL, an endpoint, or terms of use from
public pages on 28 Oct 2026. Until Nepalytix itself publishes API docs,
treat the claim as marketing, not as a usable endpoint.

What this scanner takes from it: the indicator set (price + volume +
broker/floorsheet context) and the "sourced figures" discipline — NOT its
signals, which are proprietary and unverifiable from outside.

## 2. Chart Nepali (chartnepali.com) — PUBLIC, not the user's site

What it publicly shows:
- Live NEPSE and sector sub-index charts, daily market summary, breadth
  and turnover analytics, dividend and corporate-action tracking,
  portfolio and weighted-average-cost tools, and a searchable profile
  for every listed company (per its business listing).
- A chart room with NEPSE candles (index, every sub-index, every listed
  company, daily and intraday) and, since 4 Oct 2026, a Pine Script
  editor under every chart: TradingView Pine Script v5/v6 pasted by the
  user runs in the user's own browser on the visible bars. Saving a
  script asks the user to sign in; running one does not.

What data source it publicly states:
- "25+ years of Nepal Stock Exchange (NEPSE) data" (its business
  listing). No upstream feed, endpoint, or licence is named publicly.

Public API? **No documentation found (TO VERIFY).** The chart room is a
logged-in web product (the user holds a chart-room login); its internal
chart-data calls were NOT inspected, copied, or reused.

What this scanner takes from it: the chart-room idea that indicators
must run on the user's own visible data, and Pine Script as proof that
standard indicators (any TradingView study) are the common language of
NEPSE charting — NOT its data feed, which is not public.

## 3. Chukul (chukul.com) — PUBLIC pages; product is login/paid

What it publicly shows:
- An "AI-based algorithm" for NEPSE trend prediction, per its app-store
  listing (developer: Pi Tech Public Limited). Method as publicly
  described: historical data + technical indicators + fundamental
  indicators + data science / AI, generating daily buy/sell signals and
  reports, with candlestick patterns as "the fuel of the system" — e.g.
  a Bullish Engulfing candle is presented with a probability of average
  return, and a Bearish Engulfing candle the reverse.
- Public blog analysis uses trend lines, chart patterns (e.g. Inverse
  Head & Shoulders), RSI breakouts, and rising turnover, with an
  explicit invalidation level and an education-only disclaimer.

What data source it publicly states:
- None named publicly. Access requires a registered user with a valid
  phone number; basic features are free to registered users and further
  packages are paid (a user review cites a NPR 2,499 minimum — TO VERIFY
  against Chukul's own current pricing, not relied on here).

Public API? **None found (TO VERIFY).** No public API documentation.

What this scanner takes from it: candlestick-pattern context and the
discipline of stating an invalidation level — i.e. what would prove a
reading wrong. It does NOT take Chukul's buy/sell signals: a probability
quoted without its sample, base rate, and out-of-sample test is a claim,
not evidence, and this scanner's house rules forbid presenting signals
as recommendations.

Caution, stated plainly: Chukul's listing language ("guarantees a novice
user a safe landing", "predicts the perfect time to buy") is marketing
overclaim. No indicator guarantees anything on NEPSE or anywhere else.
This scanner never uses that language.

## 4. Nepse Alpha (nepsealpha.com) — PUBLIC pages; no public API

What it publicly shows:
- Live market data, advanced charting, technical indicators (moving
  averages, RSI, MACD, Bollinger Bands), portfolio tracking, stock
  screening, company financials and research insights, per third-party
  listings and its own marketing. A similarly named AI product
  (NepseAlphaAI) advertises sentiment analysis and sector rotation —
  whether it is the same operator is TO VERIFY and is NOT assumed here.

What data source it publicly states:
- None named publicly on the pages found.

Public API? **No.** A third-party software listing answers "Does Nepse
Alpha provide API?" with "No", and no free trial is offered. TO VERIFY
against Nepse Alpha's own current terms, but there is nothing public to
wire in today.

What this scanner takes from it: the standard indicator set (MA, RSI,
MACD, Bollinger) — the same set every NEPSE platform converges on, which
is why this scanner implements exactly those, plus ATR, Stochastic,
ADX, and volume comparison.

## 5. The wider NEPSE data landscape (context, also public)

These are NOT among the four references, but they decide the fetcher
question, so they are recorded here:

- **NEPSE official site (nepalstock.com.np):** the authoritative source
  for prices, but its data endpoints are internal and token-protected.
  Third-party Python libraries (e.g. `nepse-data-api`, `nepseman-api`
  on PyPI) wrap that flow with token/WASM handling. Those libraries are
  public code, but the endpoint they call is NEPSE's internal API, not a
  documented public API. Using it would mean depending on undocumented
  access that NEPSE can change or block at any time. NOT wired in.
- **Market Data Provider / MDP (data.smartwealthpro.com):** officially
  licensed by NEPSE, real-time prices, corporate actions, financials,
  with docs, SDKs and an API playground — but a paid, licensed feed for
  businesses (50+ businesses cited). NOT free. This is the legitimate
  route if live data is ever funded; it is NOT started here (no paid
  service, per the programme's rule).
- **Other NEPSE charting tools seen in passing (NepseIQ, Nepsense,
  ShareRocketPro, NChartPro, Shikhar Signals, Hamro Share):** all show
  the same convergent indicator set — RSI, MACD, SMA/EMA crossovers,
  Bollinger, volume, support/resistance, plus broker/floorsheet flow.
  None of them changes the fetcher conclusion: no documented free public
  OHLCV API was found among them either. Their scanner vocabularies
  confirm the indicator list; they do not supply a feed.

## 6. What this scanner therefore implements (and why)

| Indicator | Why it is in | NEPSE falsifier to check alongside it |
|---|---|---|
| SMA / EMA + crossover, since-cross % | The screenshot's scanner; every reference site's core | Cross on one thin trade, or at a circuit limit, is noise |
| RSI(14) | All four references | Overbought can stay overbought in a circuit-driven run |
| MACD(12/26/9) | All four references | Lags; whipsaws in sideways, low-volume stocks |
| Bollinger(20, 2σ) | All four references | Bands widen on one block trade, not on a trend |
| ATR(14) | Volatility sizing; gap/circuit context | Circuit limits cap true range — ATR understates risk |
| Stochastic(14,3) | Standard momentum; cited for NEPSE traders | Meaningless in a flat, untraded series (returns 50) |
| ADX(14) | Trend-strength filter; cited for NEPSE traders | Needs 28 bars before its first value; useless on short history |
| Volume vs 20-day average | Every reference site's volume screen | The single most useful NEPSE check: no volume = no signal |

Deliberately NOT implemented as signals: no buy/sell labels, no
"probability of rise" (Chukul-style), no AI forecast, no price targets.
A scanner that labels a thinly traded hydro stock a "buy" on a crossover
alone would be exactly the dishonesty this programme refuses.

## 7. TO VERIFY before any deployment or live-data step

1. Whether Nepalytix publishes API docs or terms for its "open data hub"
   (re-check its site/docs, not its marketing page).
2. Whether NEPSE publishes any official public data API or data-use
   terms (re-check nepse.org.np / nepalstock.com.np documentation).
3. MDP pricing/terms, IF live data is ever funded — user decision, never
   started without his explicit say-so.
4. The screenshot's Fast/Slow periods (UNKNOWN) and the six symbols'
   real cross-date closes, before any screenshot figure is ever quoted
   as a computed result.
5. Chukul's current pricing and whether NepseAlphaAI shares Nepse
   Alpha's operator — both irrelevant to the scanner, recorded so they
   are not assumed later.

## Sources consulted (public pages, 28 Oct 2026)

- nepalytix.com (homepage, pricing) and its app-store listing
- chartnepali.com/pine-script and ChartNepali's business listing
- chukul.com blog (28 Oct 2026 breakout post) and Chukul's app-store listing
- Nepse Alpha third-party listings (SaaSworthy, SourceForge comparison)
- pypi.org/project/nepse-data-api, pypi.org/project/nepseman-api,
  data.smartwealthpro.com (MDP), nepseiq.com, nepsense.com,
  sharerocketpro.com, nchartpro.com, shikharsignals.com (context only)

## 8. How a scanner is actually used — and the better version (usage analysis)

Listing features is not understanding use. This section works out, from
the reference sites' own public descriptions, how a NEPSE crossover
scanner is used in practice, where it misleads, and what this scanner
does differently. No reference site's code or signals were used.

### 8.1 What a crossover signal means in practice

A trader opens a crossover list (like the screenshot's) to answer one
question: "what has started moving, and is it still moving?" The list
itself answers only the first half: fast average above slow average,
with a date and a since-cross gain. Everything traders actually do next
is a filter the list does NOT apply for them:

1. **Volume confirmation.** Is today's volume actually above normal, or
   did one small trade print a new average? Every reference site shows
   volume next to price for this reason; none of the public scanner
   lists found here applies a volume gate to the list itself. This
   scanner does: volume below 0.5x its 20-day average flags the row
   `thin_volume`, and the signal label drops to NOISE.
2. **Trend confirmation.** Is there a trend at all, or is the market
   chopping sideways and crossing back and forth? ADX exists for this
   question. A cross with ADX below 25 in a sideways stock is a whipsaw
   waiting to happen — the classic NEPSE false signal, because
   low-liquidity stocks spend long stretches going nowhere and then
   gap. This scanner requires ADX >= 25 plus volume >= 1.5x for its
   strongest tier, and even that tier is labelled "pattern only".
3. **Multiple timeframes.** A daily cross that contradicts the weekly
   trend is weaker than one that agrees with it. This scanner is daily
   only (its CSV is daily bars); multi-timeframe confirmation is a
   documented TO VERIFY extension, not a faked feature — the code does
   not pretend weekly data exists when only daily bars were supplied.
4. **Waiting for confirmation.** Practitioners commonly wait for the
   cross to survive 2–3 closes, or for price to stay above the fast
   average, before acting — because a single close above the average
   reverses the next day more often than not. This scanner does not
   impose a waiting rule (that would be a trading rule, and this is
   research code), but it prints `days_since_cross` and
   `trailing_flat_days` so the reader can see whether the cross is
   fresh, old, or frozen at a circuit limit.
5. **The exit / invalidation.** Chukul's public blog states this
   discipline best: name the level that proves the reading wrong
   (their example: invalidation at NEPSE 2560). A scanner without an
   invalidation level is a story, not a plan. This scanner's equivalent
   is structural: every row carries its falsifiers (thin volume, flat
   tail, last-day move, ADX) so the reader can invalidate it.

### 8.2 Where false signals come from on NEPSE specifically

- **Whipsaw in sideways, thin stocks:** fast and slow averages cross
  repeatedly while price goes nowhere. Guard: ADX filter + volume gate.
- **One block trade / single-day spike:** one large print drags the
  fast average over the slow one for a day. Guard: trailing-flat and
  last-day-move flags; a spike that reverts the next day leaves no
  sustained cross (tested: a +30% single bar in a flat series produces
  no cross at all).
- **Circuit-limit days:** price pinned at its limit for days makes RSI
  pin at an extreme, Bollinger bands compress, and ATR understate risk.
  Guard: `trailing_flat_days` (>= 5 flags NOISE) and the README's
  circuit-limit warning.
- **Unadjusted corporate actions:** bonus shares, rights and splits
  change the price mechanically. A price series that is not adjusted
  for them will show fake crashes and fake crosses. Guard: none in
  code can fix bad input — the CSV's source and adjustment status must
  be named wherever results are shared. This is a data rule, stated in
  the README, not a code claim.
- **Stale prices presented as fresh:** a last-traded price from days
  ago displayed without its date. Guard: the scanner always prints the
  last date in the CSV, and the live fetcher refuses to return any
  price rather than return a stale one as fresh.
- **Survivorship / cherry-picked "since cross" gains:** a list sorted
  by since-cross gain shows only winners. Guard: the CLI prints every
  crossed symbol, and `--all` prints uncrossed ones too; since-cross %
  is labelled backward-looking everywhere it appears.

### 8.3 Signal vs noise labelling (the better version)

| Label | Rule | What it means |
|---|---|---|
| NO SIGNAL | No bullish cross in history | Nothing to discuss |
| NOISE | Thin volume (< 0.5x) OR >= 5 trailing identical closes | Do not use this row; the cross is an artefact until proven otherwise |
| WEAK | Cross only, no confirmation | A cross happened; nothing else supports it |
| WATCH | Cross + volume >= 1.0x average | Volume supports it; trend strength does not (yet) |
| CONFIRMED (pattern only) | Cross + volume >= 1.5x AND ADX >= 25 | The past-price pattern is confirmed by volume and trend — still NOT a prediction or a buy signal |

No label is printed without its reasons (`--detail` shows them). A label
is a summary of checks, not a verdict on the stock.
