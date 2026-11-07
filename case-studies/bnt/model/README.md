# Research model — SKELETON ONLY

> **Research model, NOT a valuation and NOT investment advice.**
> No target price, no fair value, no buy/sell/hold conclusion is stated
> or implied anywhere in this folder. Nothing here is a recommendation.

## What this skeleton is

A documented shell that shows, with every step of arithmetic visible,
what can already be computed from the verified FY 2081/82 inputs in
`../data/bnt-fy2081-82.csv` — and where that computation stops. It exists
so the next contributor does not have to re-derive the base-year
arithmetic, and so nobody mistakes a base-year calculation for a
completed valuation.

## What it contains

- `assumptions.md` — the assumptions table: every input, its value,
  its source, and whether it is decided, undecided, or explicitly
  excluded. Undecided items are shown as open choices, never silently
  resolved.
- `sensitivity.md` — sensitivity tables computed **only** from the
  verified inputs, with the arithmetic written out in full. No hidden
  steps, no spreadsheet formulas to trust blindly, no forecast year.

## What it does NOT do — by design

- **No forecast.** There is no projected revenue, margin, capex, or
  working-capital year in this folder. A DCF needs forecast free cash
  flow; a single audited base year plus two undecided tax/WACC choices
  is not a forecast, and this skeleton does not pretend otherwise.
- **No WACC.** The ledger's WACC anchors (risk-free rate, beta, ERP/CRP,
  capital weights) come from other sources with their own caveats,
  including an unverified beta vintage and a thin-trading share price.
  They are listed in `assumptions.md` as *not used*, not computed into
  a discount rate here.
- **No terminal value.** No perpetual growth rate and no exit multiple
  is applied to any number in this folder. The ledger's growth and
  multiple anchors are listed as *not used*, with the reasons.
- **No market valuation.** No share price is multiplied by anything in
  this folder, so no market capitalisation or enterprise value is
  produced here. (The ledger's implied EV/EBITDA and EV/Sales figures
  are market-price arithmetic from a thin-traded close; reproducing
  them here would dress a price snapshot up as a valuation input.)
- **No normalisation decision.** The prior-period tax adjustment is
  shown stripped out as arithmetic, but whether a forecast should use
  reported, adjusted, or normalised earnings is left undecided.

## Honest finding (read this before building on the skeleton)

**A full valuation cannot be built from verified inputs alone, on the
evidence in this repo today.** What is missing is not more base-year
arithmetic — that part checks out, including the ~Rs 81M FCFF bridge
gap, which is reproduced below in `sensitivity.md` and remains
unexplained. What is missing is: (1) a resolved FCFF bridge (cash taxes
vs interest classification); (2) a chosen tax rate for NOPAT; (3) a
defensible WACC (beta vintage unverified, share price thin-traded);
(4) a terminal-growth thesis that survives the −14.2% revenue year;
(5) a forecast with stated drivers (no volume/price/capacity input is
verified on file); and (6) the FY 2082/83 audited outcome, including
what happened to the Rs 763M prior-period tax provision. Until those
are resolved with sources, the BNT study stays **Inputs + skeleton,
NOT a valuation** — and this folder must not be quoted as one.

## How to use it

1. Read `assumptions.md` first. Do not use a number whose status is
   "undecided" without deciding it openly and sourcing the decision.
2. Recompute any table in `sensitivity.md` by hand from
   `../data/bnt-fy2081-82.csv` — that is the point of showing the steps.
3. To advance the study, close one gap at a time with a sourced figure
   and update the assumptions table's status column. Do not close a gap
   by deleting it from the list.
