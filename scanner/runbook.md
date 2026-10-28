# Scanner runbook — data-first discipline for NEPSE

Research only, never a buy/sell recommendation. A scan describes what past
prices did. It does not predict what a price will do, and it never carries
a buy label.

Exchange: NEPSE (Nepal Stock Exchange).

## 1. Start with the data, not the signal

1. **CSV only.** The scanner runs on a user-supplied CSV — see
   `scanner/README.md` for the format. There is no live NEPSE feed in
   this repo, and no live feed is to be improvised: research on
   28 Oct 2026 found no documented, free, public NEPSE OHLCV API (see
   `research/indicator-source-teardown-2026-10-28.md`), and the licensed
   NEPSE feed is paid. Unofficial routes that reverse-engineer NEPSE's
   internal token flow are out of scope. If a live fetcher is needed,
   it stays an error naming what is missing — never a stale or invented
   price presented as fresh.
2. **Name the CSV's source wherever results are shared.** A scan over
   unsourced prices is an unsourced scan. Record, with the run:
   source publisher, period covered, last date in the CSV, and the date
   the CSV was obtained.
3. **Source / licence / freshness check (Data Scout-style), before any
   indicator is read:**
   - Source: who published these prices, and is that publisher the
     exchange, the issuer, or a third party?
   - Licence / terms: may these prices be reused and republished on
     the terms you are using them under? If the terms are unknown,
     say so — do not assume permission.
   - Freshness: what is the last date in the CSV, and how old is it
     relative to today? The scanner never labels a price fresh; the
     CSV's own last date is the freshness claim. A week-old CSV means
     week-old signals.
   - No paywalled data, no scraped data presented as official, no
     invented prices. If any of these checks fails, stop and label the
     run TO VERIFY — do not publish its rows as findings.

## 2. Read the scan in order: volume, then trend, then pattern

1. **Volume first.** Check `volume_ratio_20d` and the `thin_volume`
   flag before reading any crossover. A crossover on near-zero volume
   is one trade, not a trend.
2. **Trend confirmation second.** ADX is direction-free trend strength
   (see `scanner/README.md` for the convention: above ~25 is
   conventionally called strong, a convention, not a fact). A cross
   without ADX confirmation is unconfirmed, however clean it looks.
3. **Pattern last.** Only then read the crossover itself, with its
   cross date, days since the cross, and backward-looking "Since cross"
   figure — which says nothing about the next move.

## 3. Use the signal-vs-noise labels exactly as defined

| Label | Meaning in this runbook |
|---|---|
| NO SIGNAL | No bullish cross in history |
| NOISE | Thin volume (< 0.5x 20-day average) OR >= 5 trailing identical closes (circuit-limit / stale tail) |
| WEAK | Cross only, no confirmation |
| WATCH | Cross + volume >= 1.0x average, trend unconfirmed |
| CONFIRMED (pattern only) | Cross + volume >= 1.5x AND ADX >= 25 |

CONFIRMED means only "the past-price pattern is confirmed by volume and
trend". It is never a prediction, never a buy signal, and never a
probability of a rise. Do not upgrade it in prose: no "strong buy",
no price target, no "likely to rise".

## 4. NEPSE falsifiers to check on every run

- **Thin trading:** near-zero-volume days, flagged above.
- **Circuit limits:** repeated identical closes compress Bollinger
  bands and pin RSI; ATR understates the real risk.
- **Stale prices:** a last traded price from days ago is not a current
  price — check the CSV's last date.
- **Short history:** indicators without enough data return `n/a`,
  never a made-up number; a cross before the slow average existed is
  not a cross.
- **Since-cross % is backward-looking:** a stock already up since its
  cross has already moved. Chasing it is the most common way a scanner
  misleads.

## 5. What a run's output must carry

- CSV source, period, and last date (step 1).
- The label and its reasons for every crossed row (`--detail`).
- The falsifiers checked, and any that failed.
- The disclaimer: research only, NEPSE, no recommendation.

If any item is missing, the run is incomplete — label it so rather
than sharing a bare table of crosses.

## 6. Intraday — UPCOMING, not live (28 Oct 2026)

Nepal is about to try intraday trading practice, but as far as
programme records show it is NOT yet live. This scanner is
daily-CSV-only: it takes one row per trading day and makes no
intraday claim, uses no intraday feed, and produces no intraday
signal. No intraday launch date or rule is stated here. When
SEBON/NEPSE formally announces intraday trading (with a date),
that announcement is what would unlock intraday work — until
then, treat anything intraday as UPCOMING / TO VERIFY.
