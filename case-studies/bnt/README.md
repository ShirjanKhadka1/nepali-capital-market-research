# Bottlers Nepal (Terai) — BNT (NEPSE) — Inputs + skeleton, NOT a valuation

> Moved here from `nepal-market-research` on 7 Nov 2026 (content merge
> approved by the owner; that repo is retained for history with a
> pointer to this repo). Figures, status, and open questions are
> unchanged by the move.

**Status: Inputs + skeleton.** The verified inputs below are now also
in machine-readable form in `data/bnt-fy2081-82.csv` (see
`data/SOURCES.md` for the source and gap list), and a documented
research-model skeleton — assumptions table plus sensitivity tables
computed only from these inputs, arithmetic shown — lives in
`model/` (`README.md`, `assumptions.md`, `sensitivity.md`).
No DCF, no target price, and no valuation conclusion has been built
in this study. Anyone who quotes this folder as a valuation is
misquoting it.

## Source
39th annual report, FY 2081/82 (year ended 16 Jul 2025), standalone figures.
NEPSE ticker BNT — not the NYSE company of the same letters.

Single source for these figures (Round 3, R7, 29 Oct 2026):
`data/bnt-verified-figures.md` — values here match it exactly.
Page reference for every figure: TO VERIFY (no copy of the 39th
annual report PDF is on file; see that file's verification status).

## Verified inputs (all NPR, unless stated)
- Revenue: 7,527,297,984 (−14.2% vs prior year)
- EBIT: 407,359,078
- Depreciation & amortisation: 650,871,600
- Profit before tax: 218,422,271
- Tax — current: 53,371,085; prior-period adjustment: 763,054,705;
  deferred: 15,934,615
- Net loss: −613,938,134 (the Rs 763M prior-period tax adjustment is the
  entire reason for the loss — without it, the year would not be a loss year)
- EPS: −507
- Operating cash flow: 1,497,212,819
- Capex: 197,522,182
- Borrowings: 2,344,466,783, all current, nil non-current
- Cash: 36,531,377
- Shares outstanding: 1,210,000
- Current lease liability: 32,042,935 (open item: working capital or debt?)
- Dividend for FY 2081/82: nil

## Open questions (undecided — do not treat any of these as decided)
1. FCFF bridge gap of ~Rs 81M between OCF-minus-capex (~Rs 1,299.7M) and the
   EBIT bridge (~Rs 1,218.7M) — likely cash taxes / interest classification,
   not yet proved.
2. NOPAT tax rate: 25% statutory vs 24.4% effective — not yet chosen.
3. WACC weights, current vs target capital structure, thin-trading beta caveat.
4. Terminal growth: any rate near nominal GDP needs a reconvergence thesis,
   given revenue fell 14.2% — not yet argued.

## What would complete this study
A 3-statement forecast with stated drivers, a WACC with stated weights, and a
terminal value with a stated growth thesis — each checked against the figures
above, with every change from these inputs explained. Until then: inputs +
skeleton only, not a valuation.
