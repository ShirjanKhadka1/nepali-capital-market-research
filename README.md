# 🇳🇵 Nepali Capital Market Research — one repo

One repo for researching Nepal's capital market as a whole — not just one
company, and not just NEPSE equities: the market's structure, its
participants, its instruments, and how it actually works for an investor,
a researcher, or a business looking to raise capital.

> Research only, not investment advice. Every number in this repo cites
> its source and period, or is labelled TO VERIFY. Nothing here is a
> recommendation to buy, sell, or invest in any security or instrument.

## What this repo is

| Folder | What is inside |
|---|---|
| `agents/` | The Nepali Capital Market Researcher agent (Markdown, free, local — copy it into your own AI tool) |
| `guides/` | Market structure guide: how NEPSE, brokers, merchant bankers, mutual funds, bonds, and regulation fit together |
| `templates/` | Market review template, instrument comparison template, participant map template |
| `scanner/` | NEPSE EMA/SMA crossover scanner (Python, zero dependencies, 40/40 tests): EMA/SMA crossovers, RSI, MACD, Bollinger, ATR, Stochastic, ADX, volume checks, with signal-vs-noise labels. Runs on a user-supplied CSV — no live NEPSE feed exists (no documented free public NEPSE OHLCV API verified). See `scanner/README.md`. |
| `research/` | Teardown of public NEPSE reference sites (Nepalytix, Chart Nepali, Chukul, Nepse Alpha) and their data sources — public information only, no code copied, no paywalled data accessed. |

## Quick start — use the agent (free, local)

```bash
# No install needed — copy the agent file into any AI tool
# agents/nepali-capital-market-researcher.md
```

Then:

```
Activate Nepali Capital Market Researcher mode. Explain [part of Nepal's
capital market] with sources and dates, and tell me what is still
unverified. No recommendation.
```

## The market, in one page (read this before any detail)

Nepal's capital market is bank-dominated, retail-heavy, and still
developing in depth: equities on NEPSE are the most visible part, but the
market also includes government and corporate bonds, debentures, mutual
funds, and a growing merchant-banking and issue-management ecosystem.
Regulation sits with SEBON (Securities Board of Nepal); trading, clearing,
and settlement run through NEPSE and its related institutions; brokers are
the access point for most retail investors.

That paragraph is a map, not a dataset. Every specific claim about size,
growth, listings, or returns in this repo must be sourced in the file that
makes it — if it is not sourced there, treat it as TO VERIFY, however
plausible it sounds.

## How to use this repo

1. **Learn the structure first** (`guides/market-structure.md`) — before
   any company or instrument, understand who does what.
2. **Pick one slice** — one instrument, one participant type, or one
   market segment — and research it with the agent + template.
3. **Source everything** — annual reports, SEBON/NEPSE publications, and
   issuer filings first; news second; social media never as a sole source.
4. **Label status honestly** — Inputs only / In progress / Completed,
   exactly as in the main finance pack.

## Related repos (same author, same rules)

- `finance-research-agents/` — the full agent pack (this repo's agent is
  the capital-market specialist inside that system).
- `nepal-market-research/` — company case studies (starting with Bottlers
  Nepal (Terai), inputs only).
- `nepali-business-opportunities/` — business opportunities inside Nepal,
  scored with a framework, not asserted.

## License

MIT.
