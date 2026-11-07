# Sources — `bnt-fy2081-82.csv`

## Primary source (every row unless its `source` column says otherwise)

**Bottlers Nepal (Terai) Ltd, 39th annual report, FY 2081/82
(year ended 16 July 2025), standalone figures.**

NEPSE ticker BNT. This is not the NYSE-listed company that shares the
letters "BNT". All amounts are in Nepalese rupees (NPR) unless the row
says otherwise (EPS is NPR per share; shares outstanding is a share count).

## Verification basis — stated plainly, including its limit

These figures were **already verified on file before this Phase 11 task**,
in two places that agree with each other:

1. The valuation-week verified-inputs ledger prepared during the
   30-day finance sprint (Days 8–12), which records each figure as
   verified from the 39th annual report, FY 2081/82, and retires
   superseded figures so stale numbers cannot leak in.
2. The case-study README already in this repo
   (`../README.md`), which carries the
   same FY 2081/82 figures under the same source citation.

This Phase 11 task **transcribed those on-file figures into CSV form and
re-checked the internal arithmetic** (D&A split, year-on-year changes,
EPS denominators, working-capital change — all shown in
`../model/sensitivity.md`). It did **not** re-audit the figures against
the annual-report PDF itself: no copy of the 39th annual report PDF is
on file in this repo or in the sprint workspace to re-check against.
Anyone who wants a second audit should open the 39th annual report and
tick each CSV row back to it; that re-audit is an open contribution
(see Gaps, item 1).

Two precision notes:

- The current lease liability is Rs 32,042,935 as carried in the
  case-study README; the ledger rounds it to Rs 32.0M. The CSV uses the
  precise README figure and the difference is rounding only.
- The prior-period tax adjustment (Rs 763,054,705) is a tax line, not an
  operating item. It is kept as its own row and is never netted into
  EBIT, EBITDA, or OCF in this dataset.

## Also verified on file, deliberately NOT in the CSV

These are real, but their source is not the 39th annual report, so mixing
them into the CSV would misstate provenance. They are recorded here so
they are not lost, and so nobody re-adds them without their source:

- **Dividend for FY 2081/82: nil** — board decision 26 Nov 2025,
  per the verified-inputs ledger. (Corollary on file: the FY 2081/82
  audited accounts did include the 50% BNT dividend for FY 2080/81 —
  Rs 50 × 1,098,472 BNL-held shares ≈ Rs 54.9M — relevant only to a
  BNL-side restatement, not to BNT's own FY 2081/82 figures.)
- **BNL's stake in BNT: 90.78% (1,098,472 of 1,210,000 shares)** —
  from BNT's 32nd annual report, FY 2074/75, per the ledger. Eight years
  old at the FY 2081/82 anchor date: the ledger flags it as the best
  verified anchor, not gospel, and notes the 39th annual report's
  shareholding note as the tie-breaker. Not in the CSV because it is
  not a FY 2081/82 annual-report figure.

## Explicit gaps — figures NOT verified, so NOT included

1. **Second audit against the 39th annual report PDF** — not done in
   this task (no PDF on file). Open contribution.
2. **Prior-year comparatives for PBT, tax lines, capex, borrowings,
   cash, lease liability, and shares** — blank in the CSV. They may
   exist in the report, but they are not verified on file, so they
   are left blank rather than filled from memory.
3. **Any FY 2082/83 figure, audited or unaudited** — the 40th annual
   report had not been published as of the ledger date (16 Oct 2026).
   The unaudited FY 2082/83 quarterlies in the ledger are normalisation
   evidence only and are excluded here by design.
4. **Market prices, market capitalisation, and enterprise value** —
   NEPSE closes are market data with their own thin-trading caveats
   (see `../model/assumptions.md`); they are not annual-report data
   and are not in this dataset.
5. **Segment, volume, pricing, or capacity detail** — not verified on
   file; a forecast driver cannot be sourced from this dataset alone.
6. **Any figure from an unverified source, estimate, or interpolation**
   — excluded by rule, not by oversight. If it is not in the CSV or
   listed above with its source, it is not claimed anywhere in this repo.
