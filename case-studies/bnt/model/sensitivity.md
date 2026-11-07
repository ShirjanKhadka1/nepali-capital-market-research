# Sensitivity tables — computed ONLY from verified FY 2081/82 inputs

> **Research model, NOT a valuation and NOT investment advice.**
> Every table below shows its arithmetic in full. All inputs are from
> `../data/bnt-fy2081-82.csv` (39th annual report, FY 2081/82, year
> ended 16 Jul 2025). No forecast year, no discount rate, no terminal
> value, and no market price enters any table. Where a table shows a
> range, the range is the undecided choice itself — the study picks
> nothing.

Base inputs used throughout: Revenue 7,527,297,984; EBIT 407,359,078;
D&A 650,871,600; OCF 1,497,212,819; Capex 197,522,182; Net loss
−613,938,134; Prior-period tax adjustment 763,054,705; Borrowings
2,344,466,783 (all current); Cash 36,531,377; Lease liability
32,042,935; Shares 1,210,000; Working capital 1,478,090,828
(prior year 1,937,911,582).

## Table 1 — Base-year margins and cash conversion (single-point arithmetic)

| Measure | Arithmetic | Result |
|---|---|---|
| EBITDA | 407,359,078 + 650,871,600 | **1,058,230,678** |
| EBITDA margin | 1,058,230,678 / 7,527,297,984 | **14.06%** (ledger: 14.1%) |
| EBIT margin | 407,359,078 / 7,527,297,984 | **5.41%** |
| Net margin (reported) | −613,938,134 / 7,527,297,984 | **−8.16%** |
| OCF margin | 1,497,212,819 / 7,527,297,984 | **19.89%** |
| Capex intensity | 197,522,182 / 7,527,297,984 | **2.62%** |
| OCF − capex | 1,497,212,819 − 197,522,182 | **1,299,690,637** (~Rs 1,299.7M) |
| OCF / capex | 1,497,212,819 / 197,522,182 | **7.58x** |

Reading (not a conclusion): the year's cash generation (OCF) is far
stronger than its reported earnings — the wedge is the Rs 763M tax
adjustment plus Rs 650.9M of non-cash D&A. That wedge is exactly why
Table 3 exists.

## Table 2 — NOPAT sensitivity to the undecided tax rate

The study has NOT chosen a NOPAT tax rate. Both rates on file are
shown; neither is endorsed.

| Tax rate | Arithmetic | NOPAT |
|---|---|---|
| 25% statutory | 407,359,078 × (1 − 0.25) = 407,359,078 × 0.75 | **305,519,309** (305,519,308.5 before rounding; ledger: 305.52M) |
| 24.4% effective (as used in the Day 8 build, per ledger) | 407,359,078 × (1 − 0.244) = 407,359,078 × 0.756 | **307,963,463** (307,963,462.97 before rounding; ledger: 307.96M) |
| Difference | 307,963,463 − 305,519,309 | **2,444,154** |

Note: the 24.4% rate is reproduced exactly as the ledger states it for
the Day 8 build. It is NOT derived here from current + deferred tax
(53,371,085 + 15,934,615 = 69,305,700), because that sum sits alongside
the Rs 763M prior-period adjustment and does not by itself produce
24.4%. Deriving a different "effective" rate from those lines would be
inventing a definition — so the table shows the ledger's rate as a
stated input and leaves the choice open.

## Table 3 — The FCFF bridge gap, reproduced (unresolved)

Two routes to a free-cash-flow-like figure, from the same verified
inputs, do not agree. The gap is the study's biggest open item.

| Route | Arithmetic | Result |
|---|---|---|
| Cash route: OCF − capex | 1,497,212,819 − 197,522,182 | **1,299,690,637** |
| EBIT route: NOPAT (25%) + D&A − capex − ΔWC | 305,519,309 + 650,871,600 − 197,522,182 − (−459,820,754) | **1,218,689,481** (~Rs 1,218.7M) |
| ΔWC (working-capital change) | 1,478,090,828 − 1,937,911,582 | **−459,820,754** (a release, so subtracting it adds back) |
| **Gap** | 1,299,690,637 − 1,218,689,481 | **81,001,157** (~Rs 81M) |

Using the 24.4% NOPAT instead moves the EBIT route to
307,963,463 + 650,871,600 − 197,522,182 + 459,820,754 = 1,221,133,635,
and the gap to 78,557,002 (~Rs 78.6M) — the tax choice explains
Rs 2.4M of the gap and nothing more. The remaining ~Rs 79–81M is
attributed on file to cash taxes / interest classification, but that
is a hypothesis, not a proof. **No FCFF figure from this table may be
used as "the" FCFF until the gap is reconciled from the statements.**

## Table 4 — Debt sensitivity to the lease-liability classification

Also undecided. Both treatments are shown; neither is endorsed.

| Treatment | Arithmetic | Net debt |
|---|---|---|
| Borrowings − cash (lease stays in working capital, per ledger) | 2,344,466,783 − 36,531,377 | **2,307,935,406** |
| Borrowings + lease − cash (lease counted as debt) | 2,344,466,783 + 32,042,935 − 36,531,377 | **2,339,978,341** |
| Difference | 2,339,978,341 − 2,307,935,406 | **32,042,935** |

Context arithmetic (not a leverage conclusion): borrowings / revenue =
2,344,466,783 / 7,527,297,984 = 31.15%; net debt (lease in WC) /
EBITDA = 2,307,935,406 / 1,058,230,678 = 2.18x. These ratios describe
FY 2081/82 only; with all borrowings current, they describe a
maturity profile, not a target capital structure.

## Table 5 — Reported vs ex-adjustment earnings (normalisation shown, not chosen)

| Measure | Arithmetic | Result |
|---|---|---|
| Reported net loss | As reported | **−613,938,134** |
| Prior-period tax adjustment | As reported | **763,054,705** |
| Net profit ex-adjustment | −613,938,134 + 763,054,705 | **149,116,571** |
| Ex-adjustment EPS (derived, NOT reported) | 149,116,571 / 1,210,000 | **123.24** |
| Reported EPS (check) | −613,938,134 / 1,210,000 = −507.38 | **−507** (as reported) |

The ex-adjustment line is arithmetic, not a restated account: it shows
that the reported loss is entirely attributable to the adjustment, but
it does not decide whether a forecast should normalise the adjustment
away. That decision is open (assumption B4).

## What these tables deliberately do NOT contain

- No sensitivity to a discount rate, because no WACC is computed here
  (assumptions C1–C4: unverified beta vintage, thin-traded price).
- No sensitivity to terminal growth or an exit multiple, because no
  terminal value is computed here (assumptions C5–C6).
- No share-price, market-cap, or enterprise-value sensitivity, because
  no market price enters this folder (assumption C7).
- No forecast-year sensitivity, because there is no forecast year.

Adding any of those would require closing the gaps in
`assumptions.md` section D with sourced figures — not extending these
tables by assumption.
