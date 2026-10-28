# Good First Issues

Small, well-scoped tasks a new contributor can pick up. This is a list, not
a promise: no maintainer response time is promised, and no GitHub issue has
been created for these items. Open an issue first and ask to be assigned
before starting, so two people do not do the same task.

## 1. Extend no-lookahead coverage to the remaining scanner indicators

`scanner/tests/test_edge_cases.py` already has one no-lookahead test
(`test_no_look_ahead_earlier_indicators_unchanged_by_later_bars`), but it
covers only RSI and EMA: appending a future bar must not change any
indicator value already computed for an earlier bar. Extend the same
append-a-future-bar check, one indicator at a time, to the indicators in
`scanner/indicators.py` that it does not yet cover: SMA, MACD, Bollinger
bands, ATR, Stochastic, ADX, and volume ratio.

Acceptance: one indicator per contribution is fine; the new test follows
the existing test's pattern; the full scanner suite still passes
(`cd scanner && python3 -m pytest tests/ -v`); no indicator behaviour is
changed unless a genuine lookahead bug is proved by a failing test first.

## House rules

Research only, not investment advice; never a buy/sell recommendation.
No credentials, no private data, no paywalled scraping. The scanner stays
CSV-only — no live NEPSE feed claim.
