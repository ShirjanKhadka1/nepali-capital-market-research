# Assumptions table — Bottlers Nepal (Terai), research-model skeleton

> **Research model, NOT a valuation and NOT investment advice.**
> Status meanings: **Verified** = on file with a named source (see
> `../data/SOURCES.md`). **Undecided** = a choice the study has not
> made — shown, not silently resolved. **Not used** = on file somewhere
> else but deliberately excluded from this skeleton, with the reason.

All amounts NPR unless stated. Base year: FY 2081/82, year ended
16 Jul 2025, 39th annual report.

## A. Base-year inputs (verified — used in `sensitivity.md`)

| # | Assumption / input | Value | Source | Status |
|---|---|---|---|---|
| A1 | Revenue | 7,527,297,984 | 39th annual report, via ledger | Verified |
| A2 | EBIT (Profit from Operations) | 407,359,078 | 39th annual report, via ledger | Verified |
| A3 | D&A | 650,871,600 (= 646,041,660 + 4,829,940) | 39th annual report, via ledger | Verified |
| A4 | PBT | 218,422,271 | 39th annual report, via ledger | Verified |
| A5 | Current tax / deferred tax | 53,371,085 / 15,934,615 | 39th annual report, via ledger | Verified |
| A6 | Prior-period tax adjustment | 763,054,705 | 39th annual report, via ledger | Verified |
| A7 | Net loss | −613,938,134; EPS −507 | 39th annual report, via ledger | Verified |
| A8 | OCF | 1,497,212,819 | 39th annual report, via ledger | Verified |
| A9 | Capex (PPE acquisition) | 197,522,182 | 39th annual report, via ledger | Verified |
| A10 | Working capital ex-cash/ex-borrowings | 1,478,090,828 (prior year 1,937,911,582) | 39th annual report, via ledger | Verified |
| A11 | Borrowings, all current; non-current nil | 2,344,466,783; 0 | 39th annual report, via ledger | Verified |
| A12 | Cash | 36,531,377 | 39th annual report, via ledger | Verified |
| A13 | Current lease liability | 32,042,935 | Case-study README (ledger: Rs 32.0M) | Verified (amount); treatment undecided — see B2 |
| A14 | Shares outstanding | 1,210,000 | 39th annual report, via ledger | Verified |

## B. Undecided — sensitivity shows the range, the study picks nothing

| # | Open choice | Options on file | Why it matters | Status |
|---|---|---|---|---|
| B1 | Tax rate for NOPAT | 25% statutory vs 24.4% effective (as used in the Day 8 build, per ledger) | Moves NOPAT by Rs 2,444,154 (see `sensitivity.md`, Table 2). Small in itself, but a forecast NOPAT needs a rate that is *argued*, not just picked. | Undecided |
| B2 | Lease liability: working capital or debt? | Inside WC per ledger; alternative is to count it as debt | Moves net debt by Rs 32,042,935 (Table 4). Immaterial to the bridge (ledger: 2.6% ceiling) but a debt schedule must classify it before any WACC weight is struck. | Undecided |
| B3 | FCFF bridge gap, ~Rs 81M | OCF − capex (Rs 1,299,690,637) vs EBIT bridge (Rs 1,218,689,481) | Likely cash taxes / interest classification, per the case-study README — not proved. No FCFF forecast can be built on an unreconciled bridge. | Undecided |
| B4 | Reported vs adjusted earnings | Reported net loss −613,938,134 vs ex-adjustment +149,116,571 | The adjustment is the entire loss story. Whether a forecast normalises it away is a judgement the study has not made. | Undecided |
| B5 | Current vs target capital structure | All borrowings are current; no target structure is stated on file | A WACC weight needs a target, not an accident of the balance-sheet date. "All current debt" is a fact about FY 2081/82, not a policy. | Undecided |

## C. Listed, NOT used — anchors from other sources, with their caveats

These appear in the sprint ledger. They are recorded here so a future
builder can see what exists — and why none of it is computed into a
discount rate, terminal value, or market value in this skeleton.

| # | Anchor | Value on file | Caveat | Treatment here |
|---|---|---|---|---|
| C1 | Risk-free rate | ~5.0% (PDMO FY 2081/82, 22 auctions; 8–11yr long end 5.00–5.49%) | Sensitivity band, not a point estimate | Not used — no WACC is computed |
| C2 | Beta (unlevered) | EM beverage-soft 0.50 anchor; US 0.56 cross-check (Jan 2026, 27 firms) | EM vintage **unverified**; BNT's own beta must not be regressed (thin trades) | Not used |
| C3 | ERP / CRP | Damodaran Jan 2026: CRP 4.66%, total ERP 8.89%; Jul 2026 refresh: mature ERP 4.20% | Layering a Nepal CRP on a mature-market ERP is itself a judgement trap, per the ledger | Not used |
| C4 | Capital weights | 86/14 market-value weights (equity Rs 14,384.48M at Rs 11,888 close × 1,210,000 shares; debt Rs 2,344.47M) | The Rs 11,888 close was set by 2 trades / 50 shares — thin-trade price; 120-day average fallbacks disagree slightly (11,696.53 vs 11,758.02, sources differ) | Not used |
| C5 | Terminal growth | Base ~7%, top ~8%, 9% prove-it ceiling (WB Nepal Development Update Oct 2026: FY26 nominal GDP ~7.1%) | Any rate near nominal GDP needs a reconvergence thesis after revenue fell 14.2%; flood figures are shock-specific and never belong in a perpetual rate | Not used |
| C6 | Exit multiples | Damodaran US Beverage (Soft) Jan 2026: EV/Sales 4.16x, P/S 3.57x | US multiple on a Nepal bottler; EM/global EV/EBITDA **unverified** on the web. Ledger rule: any exit multiple belongs on normalised, not depressed-LTM, EBITDA | Not used |
| C7 | Market closes / peer data | Ledger's Oct 2026 NEPSE closes and peer denominators | Thin/stale trading throughout (BNL stale since 9 Oct; UNL thin); unaudited quarterlies are not audited data | Not used |
| C8 | FY 2082/83 unaudited quarterlies | Q1–Q4 PAT on file in the ledger; LTM EPS 545, LTM P/E 21.83x at Rs 11,900 | Unaudited; FY 2081/82 audited stays the anchor. Normalisation evidence only | Not used |

## D. What a completed model would still need (gap list)

1. A reconciled FCFF bridge (close B3) with the cash-tax/interest
   classification proved from the statements.
2. A chosen, argued NOPAT tax rate (close B1).
3. A verified beta vintage and a defensible, non-thin-traded price
   for capital weights (close C2, C4) — or a stated reason to use
   book weights instead, argued openly.
4. A terminal-growth thesis that survives the −14.2% revenue year
   (close C5) and a normalised-EBITDA basis for any exit multiple
   (close C6).
5. Forecast drivers with sources: volume, pricing, capex intensity,
   working-capital days. None is verified on file today.
6. The FY 2082/83 audited outcome (40th annual report, not published
   as of the ledger date), including what happened to the Rs 763M
   prior-period tax provision.
7. A second audit of every CSV row back to the 39th annual report PDF
   (see `../data/SOURCES.md`).

Until D1–D7 are closed with sources, this remains a skeleton.
