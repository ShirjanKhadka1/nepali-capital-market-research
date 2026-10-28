# Contributing

Thank you for contributing. Keep changes small, sourced, and checkable.

## Running tests

```bash
cd scanner && python3 -m pytest tests/ -v
```

All tests must pass before submitting.

## Proposing a Markdown change

1. Open an issue first for anything bigger than a typo, or comment on
   an existing issue asking to be picked up.
2. Fork, branch `docs/issue-<number>-<slug>` for docs or
   `fix/issue-<number>-<slug>` for a fix, and make the smallest change
   that does the job.
3. For a new template or checklist item, follow the format of the
   existing templates in the repo and keep the standard sections intact
   — if a section does not apply, write why, rather than deleting it.
4. Cite a source for every new number, with its period, on the same page.
   Unsourced numbers will not be merged, however plausible they look.

## Scanner changes

The scanner runs on user-supplied CSV only — there is no live NEPSE
feed, and none may be claimed. Every new indicator needs a test with
known values and an edge-case test (short history, flat series, bad data).

## House rules (all contributions)

- Research and education only: never investment advice, never a buy/sell/
  hold recommendation, never guaranteed returns.
- Every number sourced with its period, or labelled UNKNOWN / TO VERIFY.
- No fake metrics, no invented features, no live NEPSE feed claim.
- No credentials anywhere. No paywalled scraping.
