> **SUPERSEDED (Round 3) — do not use the numbers below as current.**
> The canonical programme map is
> [`finance-research-agents/ops/SYSTEM-MAP.md`](https://github.com/ShirjanKhadka1/finance-research-agents/blob/main/ops/SYSTEM-MAP.md),
> and current counts live in each repo's generated `status.json`
> (produced by `scripts/generate_status.py`, checked by `scripts/check_numbers.py`).
> This file is kept in place, unchanged except for this banner and for
> count claims replaced by pointers below, so its history is preserved.
> Any number still visible below is historical, not current.

# Integration — nepali-capital-market-research

## Role in the system
The market layer for Nepal. Company research (nepal-market-research)
answers "this company"; this repo answers "this market" — structure,
participants, instruments, and how it actually works.

## Connections
- Agent: nepali-capital-market-researcher (in `agents/` here, and linked
  from finance-research-agents).
- Templates: market-review, instrument-comparison (in `templates/` here).
- Scanner: NEPSE EMA/SMA crossover scanner (in `scanner/` here — current generated count in `status.json`) — the executable engine for this repo; its teardown of public reference sites is in `research/`.
- Playbook: adapted — market reviews use the same "no deleted sections"
  rule as company reports.
- Sibling repos: nepal-market-research (companies inside this market),
  finance-research-agents (world-market-researcher for global context).
## Workflow
Structure guide → participant map → sourced facts → mechanism →
risks → Reality Checker pass. See `guides/market-structure.md`.
