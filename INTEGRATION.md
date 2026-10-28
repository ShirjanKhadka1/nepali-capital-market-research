# Integration — nepali-capital-market-research

## Role in the system
The market layer for Nepal. Company research (nepal-market-research)
answers "this company"; this repo answers "this market" — structure,
participants, instruments, and how it actually works.

## Connections
- Agent: nepali-capital-market-researcher (in `agents/` here, and linked
  from finance-research-agents).
- Templates: market-review, instrument-comparison (in `templates/` here).
- Playbook: adapted — market reviews use the same "no deleted sections"
  rule as company reports.
- Sibling repos: nepal-market-research (companies inside this market),
  finance-research-agents (world-market-researcher for global context).
## Workflow
Structure guide → participant map → sourced facts → mechanism →
risks → Reality Checker pass. See `guides/market-structure.md`.
