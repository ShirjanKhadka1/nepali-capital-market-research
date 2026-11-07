# BNT verified figures — single source (Round 3, R7)

**Bottlers Nepal (Terai) Ltd, NEPSE ticker BNT** (not the NYSE
company of the same letters). **39th annual report, FY 2081/82,
year ended 16 July 2025, standalone figures, NPR** unless stated.

This file is the programme's single source for the BNT figures.
It moved here from `nepal-market-research` on 7 Nov 2026 (content
merge approved by the owner; that repo is retained for history with
a pointer to this repo). The other two places that carry them — both
in `finance-research-agents` —

- `finance-research-agents/docs/worked-example/bottlers-nepal-terai-bnt-research-note.md`
- `finance-research-agents/examples/bottlers-nepal-terai-initiation-example.md`

— must match this file's values and carry a provenance line
pointing here. **No valuation, DCF, target price, or recommendation
is built from these figures anywhere in this programme** — valuation
from verified inputs alone is stated openly as impossible (see
`../model/README.md`).

## Verification status — read before quoting any number below

**No copy of the 39th annual report PDF is on file** in this repo,
in the sprint workspace, or in `~/workspace/user/files/` (checked
29 Oct 2026; the only PDFs there are unrelated). Every figure below
was therefore verified **against the sprint's verified-inputs ledger
(prepared 2026-10-16, consolidating sprint-week verification) and
against the machine-readable transcription in
`bnt-fy2081-82.csv` + `SOURCES.md`**, which agree with each
other and with both downstream repos. The ledger attributes each
figure to the 39th annual report, but **no page number is recorded
for any figure in any on-file source**. Accordingly:

- **Source column below = "39th annual report FY 2081/82 via
  2026-10-16 ledger"** (or "via case-study README" for the lease
  liability, whose precise figure comes from the case-study README
  while the ledger rounds it — see the note).
- **Page reference = TO VERIFY for every figure.** A second audit
  that ticks each row back to the report PDF, page by page, is an
  open contribution (see `SOURCES.md`, gap 1). Until that audit
  lands, no figure here may be cited with a page number, and no
  downstream repo may invent one. This file does not launder the
  ledger's attribution into a page reference.

The R7 cross-check (29 Oct 2026) compared all three repos figure by
figure: **no numeric mismatch was found** on any row below. The
only harmonisation made was precision, not value: the worked
example's rounded "Rs 32.0M" lease-liability mention now also
states the precise Rs 32,042,935, matching this file and the CSV.
All arithmetic tie-outs below were recomputed from these values
and pass (see "Arithmetic checks").

## Figures

| Item | FY 2081/82 | FY 2080/81 | Unit | Source | Page ref |
| --- | --- | --- | --- | --- | --- |
| Revenue from operations | 7,527,297,984 | 8,771,297,424 | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Profit from operations (EBIT face label) | 407,359,078 | 721,109,708 | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Depreciation & amortisation (646,041,660 + 4,829,940) | 650,871,600 | — (not frozen) | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Profit before tax | 218,422,271 | — | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Current tax | 53,371,085 | — | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Deferred tax | 15,934,615 | — | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Prior-period tax adjustment | 763,054,705 | — | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Net profit / (loss) | −613,938,134 | 339,681,626 | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| EPS (as reported, rounded) | −507 | 281 | NPR/share | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Operating cash flow | 1,497,212,819 | 1,108,364,321 | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Capex (PPE acquisition) | 197,522,182 | — | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Working capital ex-cash/ex-borrowings | 1,478,090,828 | 1,937,911,582 | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Borrowings — total, all current | 2,344,466,783 | — | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Borrowings — non-current | 0 (nil, stated explicitly) | — | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Cash and cash equivalents | 36,531,377 | — | NPR | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |
| Current lease liability | 32,042,935 | — | NPR | Case-study README (ledger rounds to Rs 32.0M) | TO VERIFY |
| Shares outstanding | 1,210,000 | — | shares | 39th annual report FY 2081/82 via 2026-10-16 ledger | TO VERIFY |

Derived, arithmetic only (not report lines):

| Item | Value | Arithmetic |
| --- | --- | --- |
| Revenue change | −14.2% | 7,527,297,984 / 8,771,297,424 − 1 = −14.18% |
| EBIT change | −43.5% | 407,359,078 / 721,109,708 − 1 = −43.51% |
| EBITDA (EBIT + D&A) | 1,058,230,678 (margin 14.06%) | 407,359,078 + 650,871,600 |
| Working-capital change | −459,820,754 (release) | 1,478,090,828 − 1,937,911,582 |
| OCF − capex | 1,299,690,637 | 1,497,212,819 − 197,522,182 |
| Net debt (borrowings − cash, lease in WC) | 2,307,935,406 | 2,344,466,783 − 36,531,377 |
| Profit ex-prior-period adjustment | 149,116,571 | −613,938,134 + 763,054,705 |
| PBT tie-out | −613,938,134 | 218,422,271 − 69,305,700 (current + deferred tax) − 763,054,705 |

## Open items (undecided — carried, not resolved, by this file)

1. **Page references: TO VERIFY for every figure** (no PDF on file).
2. **Current lease liability: working capital or debt?** The ledger
   places it inside working capital; counting it as debt moves net
   debt by Rs 32,042,935 (to 2,339,978,341). Undecided.
3. **~Rs 81M FCFF bridge gap** between OCF − capex (~Rs 1,299.7M)
   and the EBIT bridge (~Rs 1,218.7M) — cash taxes / interest
   classification, unproved.
4. **NOPAT tax: 25% statutory (Rs 305.52M) vs 24.4% effective
   (Rs 307.96M)** — ΔRs 2.44M, immaterial, not chosen.
5. **BNL's 90.78% stake (1,098,472 of 1,210,000 shares)** is from
   BNT's 32nd annual report, FY 2074/75 — 8 years old at the anchor
   date. It is NOT a FY 2081/82 figure and is NOT in the table above;
   its tie-breaker is the 39th annual report's shareholding note —
   TO VERIFY with the page audit.
6. **Dividend for FY 2081/82: nil** (board decision 26 Nov 2025, per
   ledger) — recorded here, not in the audited-figures table, because
   its source is the board decision, not the report's statements.

## Arithmetic checks (recomputed 29 Oct 2026, all pass)

Revenue −14.18% → −14.2%; EBIT −43.51% → −43.5%; D&A split sums
exactly; EPS −507.39 → −507 and 280.73 → 281 as reported;
current + deferred tax = 69,305,700; PBT − tax − adjustment =
reported net loss exactly; WC change = −459,820,754 exactly.
