# Case-study seed template — copy this to start a new study

> Educational research only. Not investment advice, not a
> recommendation to buy, sell, or hold any security.
> No number in a study built from this template is presented
> as verified unless its source is named on the same page.
> Exchange is always stated. For NEPSE companies, state
> NEPSE explicitly — a NEPSE ticker is never confused with
> another exchange's ticker of the same letters
> (NEPSE BNT ≠ NYSE BNT).

## Why this file lives here, not in `case-studies/`

`case-studies/` is reserved for real studies: per
`case-studies/README.md`, a new study is added only when its
first verified inputs are collected — not as an empty folder
with a name on it. This template therefore lives in `templates/`. Copy
it into `case-studies/<company>/README.md` only when the
first sourced inputs below are actually filled in. Until
then, the study does not exist, and nothing may cite it.

The new study's `data/` folder stays empty until a dataset meets
the standard in `case-studies/<company>/data/README.md` (named
public source, period, licence/terms for reuse, retrieval date).
This template invents no dataset and does not fill `data/`.

## Cover — mandatory status label (first thing on the page)

Every study carries exactly ONE of these labels, on its
cover, above all analysis. The label is the study's status;
it is not decoration, and it is never upgraded without the
evidence the next label requires.

- **Inputs only:** verified figures collected, analysis not
  yet built.
- **In progress:** analysis underway, gaps listed in the
  study README.
- **Completed:** analysis built, checked, and reviewed —
  with the checker named.

### The Completed rule (non-negotiable)

**Completed requires ALL inputs sourced + dated.** That
means, in the Sourced inputs table below:

- every input row has a source (publisher + publication),
  a period, and a page/section;
- every input row has a retrieval date;
- no input the conclusion depends on is labelled
  UNKNOWN or TO VERIFY.

Completed additionally requires: the analysis is actually
built (not sketched), it has been checked against the inputs
above with every change from those inputs explained, the
checker is named on the page, and any open question that
remains is listed as a limitation — not silently dropped. A
conclusion that depends on an unresolved open question
cannot be Completed.

**A study starts at Inputs only.** Copying this template
does not make a study In progress, and collecting inputs
does not make it Completed. The existing Bottlers Nepal
(Terai) study (`case-studies/bnt/README.md`) is the worked
example of correct labelling: it is Inputs + skeleton, is
titled "NOT a valuation", and stays there until new sourced
evidence exists. Do not upgrade it by editing its label.

Copy this cover block into the new study, with one label
kept and the other two deleted:

```text
# <Company name> — <TICKER> (NEPSE) — <Inputs only / In progress / Completed>

**Status: <Inputs only / In progress / Completed>.**
**Checker (Completed only): <name, or TO VERIFY — not Completed until named>.**
**This study is / is not a valuation:** <delete as applicable;
a study is not a valuation until the valuation is actually
built and checked — see "What would complete this study">.
```

## Study identity

- **Company:** [name]
- **Ticker (exchange always stated):** [TICKER] (NEPSE)
- **Period:** [BS fiscal year, e.g. FY ____/____] covering
  [AD start date] to [AD end date] — both BS and AD dates,
  or TO VERIFY. A bare BS year without AD dates, or a bare
  AD year without the BS year, is ambiguous: see
  `../guides/nepal-data-handling.md` in this repo (same rule applies here).
- **Source publication:** [e.g. annual report number + year]
- **Date started:** [YYYY-MM-DD] | **Author:** [name]

## Sourced inputs

One row per input. No row without a source + period +
page/section + retrieval date may be used in any analysis.
Anything not yet sourced goes in Open questions, not here,
and is labelled TO VERIFY — never filled with a plausible
figure.

| Input | Figure (with currency/unit) | Source (publisher + publication) | Period | Page/section | Retrieved |
|---|---|---|---|---|---|
| [e.g. Revenue] | [figure, or TO VERIFY] | [source, or TO VERIFY] | [period, or TO VERIFY] | [page/section, or TO VERIFY] | [YYYY-MM-DD, or TO VERIFY] |
| [e.g. Operating cash flow] | | | | | |
| [e.g. Shares outstanding] | | | | | |
| [e.g. Dividend for the period] | | | | | |

Rules for this table:

1. Every figure: source + period + page/section, on the
   same page as the figure (repo rule 1).
2. Every number carries its currency/unit, or UNKNOWN.
3. No professional experience is claimed that is actually
   coursework or a personal project (repo rule 3).
4. No investment recommendation. A study may say "the
   market price implies X" — it may not say "buy this"
   (repo rule 4).
5. Price data, if used at all: state the CSV source, its
   period, and whether it is adjusted or unadjusted for
   corporate actions (bonus, rights, splits). There is no
   live NEPSE feed claim: CSV-only, user-supplied data.
   A scan across an unadjusted action date is labelled
   TO VERIFY around that date; never fill a missing
   trading day by interpolation. See `../guides/nepal-data-handling.md`
   in this repo for the CSV spec and
   the holiday-calendar rule (check the current
   NEPSE/SEBON notice; never hardcode holiday dates).

## Evidence status

Summarise, in words, what is actually evidenced — not what
is hoped for:

- **Verified inputs:** [list, or "none yet"]
- **Inputs still TO VERIFY:** [list]
- **Analysis built so far:** [none / partial — which
  sections / complete — with checker named]
- **What is NOT claimed:** [e.g. no DCF, no target price,
  no valuation conclusion — until built and checked]

## Open questions (undecided — do not treat any as decided)

Number each open question. An open question is not answered
by restating it, and a study's conclusion may not quietly
assume an answer to one.

1. [Question — what is unknown, and what evidence would
   settle it]
2. [Question]
3. [Question]

## What would complete this study

List the concrete artefacts that would move this study to
Completed, each with its own check:

- [ ] A 3-statement forecast with stated drivers, checked
      against the sourced inputs above.
- [ ] A WACC (where applicable) with stated weights and
      stated caveats (e.g. thin-trading beta where relevant).
- [ ] A terminal value (where applicable) with a stated
      growth thesis — any rate near nominal GDP needs a
      reconvergence thesis where revenue has fallen, argued
      explicitly, not assumed.
- [ ] Checker named, check recorded, every change from the
      inputs above explained.

Until every box is checked and the Completed rule above is
met, the cover label stays where the evidence puts it.

## Status-change checklist

- Inputs only → In progress: analysis has actually started
  AND every gap is listed above as an open question.
- In progress → Completed: the Completed rule above is met
  in full — all inputs sourced + dated, analysis built,
  checked, checker named. If any part fails, the label
  stays In progress (or drops back to Inputs only if the
  analysis is withdrawn).
- Never move a label because a study "looks finished",
  because a deadline passed, or because a template was
  copied. The label follows the evidence, not the effort.
