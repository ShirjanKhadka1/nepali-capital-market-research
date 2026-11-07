# `data/` — Bottlers Nepal (Terai), FY 2081/82 verified inputs

**Status, 29 Oct 2026: this folder now holds ONE dataset** —
`bnt-fy2081-82.csv`, the FY 2081/82 figures for Bottlers Nepal (Terai)
(NEPSE ticker BNT — not the NYSE company of the same letters) that were
already verified on file. Nothing else has been added, and no figure
without a named source is in the file. Empty cells mean "not verified on
file", not zero — the one genuine zero (non-current borrowings) is
entered as `0` and flagged as such in the CSV notes.

## What is here

- `bnt-fy2081-82.csv` — one row per figure, FY 2081/82 with the prior-year
  comparative where the same report printed one. Every row names its
  source in its own `source` column.
- `SOURCES.md` — the full source citation, the verification basis (and
  its limit), and the explicit gap list. Read it before reusing any figure.

## What is NOT here

- No other company, no other year, no market prices, no forecasts.
- No WACC, beta, ERP/CRP, terminal growth rate, or exit multiple — those
  anchors live in the sprint ledger under other sources and with their
  own caveats (including an unverified beta vintage); they are NOT
  annual-report figures and so they are NOT in this dataset. See
  `../model/assumptions.md` for how they are handled (listed, not used).
- No unaudited FY 2082/83 quarterly figures — those are normalisation
  evidence in the ledger, not audited annual-report data, so they stay
  out of this dataset.

> Educational research only. Not investment advice, not a recommendation
> to buy or sell any security. This dataset is inputs, not a valuation.
