"""Named close-based setups for the NEPSE scanner. Research only,
never a recommendation.

A "match" here means only this: the symbol's past closes satisfy the
stated rule. It is a description of past prices, not a prediction and
never a buy/sell/hold label. Every setup is defined on daily closes
only, with its exact rule in its docstring and in scanner/README.md,
so any match can be recomputed by hand from the CSV.

Discipline adapted from day-trader-skill (MIT, commit 3d0f4ef) —
scanner rule table, universe hygiene, coverage reporting, and the
two-stage confirm pattern (cheap necessary condition first, exact
check second). The adaptation is NEPSE/daily-closes only: no
intraday bars, no US-universe endpoints, no execution, no "buy"
language. See scanner/SOURCES_MERGE_2026-11-07.md.

Two-stage confirmation (see scan_setups)
-----------------------------------------
Stage 1 is a cheap necessary condition, evaluated per setup from the
shared per-symbol indicator snapshot (one analyse() call per symbol,
reused across all five setups) or from a tail slice of the closes —
O(1) per setup once the snapshot exists. Stage 2 is the exact rule
recomputed from the raw closes. Stage 1 cannot reject a true match:
each stage-1 condition is implied by its setup's exact rule (the
proof is in the function's comment), and for the RSI setups stage 1
checks the same value stage 2 recomputes. What stage 1 saves is
stage-2 work on symbols that cannot match.

Confirmations are capped (max_confirmations, default 50). When the
cap is hit, the remaining candidates are listed as "unconfirmed" and
the result is explicitly PARTIAL — an unconfirmed candidate is never
reported as a match and never silently dropped.

Standard library only.
"""

try:
    from indicators import rsi, sma
    from scanner import analyse, coverage_summary
except ImportError:  # running as scanner.setups package
    from .indicators import rsi, sma
    from .scanner import analyse, coverage_summary


SETUP_ORDER = [
    "breakout_20d",
    "bull_flag",
    "reclaim_ma20",
    "oversold",
    "oversold_bounce",
]

SETUP_DEFINITIONS = {
    "breakout_20d": "Latest close above the highest close of the prior "
                    "20 closes (needs 21 closes).",
    "bull_flag": "Close rose at least 10% over the 10 sessions ending "
                 "6 bars ago, then the last 5 closes span at most 5% "
                 "(needs 16 closes).",
    "reclaim_ma20": "Latest close above its 20-day moving average "
                    "while the prior close was at or below its 20-day "
                    "moving average (needs 21 closes).",
    "oversold": "Wilder RSI-14 below 30 on the latest close "
                "(needs 15 closes).",
    "oversold_bounce": "Wilder RSI-14 below 30 at least once in the "
                       "last 5 sessions and the latest close above the "
                       "prior close (needs 15 closes).",
}


def _closes_of(candles):
    return [c.close for c in candles]


def breakout_20d(closes):
    """Close above the prior 20 closes. Returns None (no match / too
    few closes) or {"breakout_level", "close", "above_level_pct"}.

    Needs 21 closes: the level is the max of closes[-21:-1] and the
    close tested is closes[-1]. A close exactly equal to the level is
    not a breakout.
    """
    if len(closes) < 21:
        return None
    level = max(closes[-21:-1])
    close = closes[-1]
    if close <= level:
        return None
    return {
        "breakout_level": level,
        "close": close,
        "above_level_pct": close / level - 1,
    }


def bull_flag(closes):
    """+10% run over 10 sessions, then a 5-close flag within a 5%
    range. Returns None or {"run_gain_pct", "run_start", "run_end",
    "flag_low", "flag_high", "flag_range_pct"}.

    Needs 16 closes. The run is closes[-16] -> closes[-6] (10 steps
    of change); the flag is the last 5 closes, whose range is
    (max - min) / min. Both thresholds are inclusive: exactly +10%
    and exactly a 5% range both match.
    """
    if len(closes) < 16:
        return None
    run_start = closes[-16]
    run_end = closes[-6]
    if run_start <= 0:
        return None
    run_gain = run_end / run_start - 1
    if run_gain < 0.10:
        return None
    flag = closes[-5:]
    flag_low = min(flag)
    flag_high = max(flag)
    if flag_low <= 0:
        return None
    flag_range = (flag_high - flag_low) / flag_low
    if flag_range > 0.05:
        return None
    return {
        "run_gain_pct": run_gain,
        "run_start": run_start,
        "run_end": run_end,
        "flag_low": flag_low,
        "flag_high": flag_high,
        "flag_range_pct": flag_range,
    }


def reclaim_ma20(closes):
    """Close crosses back above its 20-day moving average. Returns
    None or {"ma20", "prev_ma20", "close", "prev_close"}.

    Needs 21 closes so the 20-day average exists at both the latest
    and the prior bar. Match: closes[-1] > ma20[-1] and
    closes[-2] <= ma20[-2]. A prior close exactly on its average
    counts as "at or below".
    """
    if len(closes) < 21:
        return None
    ma = sma(closes, 20)
    if ma[-1] is None or ma[-2] is None:
        return None
    if closes[-1] <= ma[-1] or closes[-2] > ma[-2]:
        return None
    return {
        "ma20": ma[-1],
        "prev_ma20": ma[-2],
        "close": closes[-1],
        "prev_close": closes[-2],
    }


def oversold(closes):
    """Wilder RSI-14 below 30 on the latest close (reuses
    indicators.rsi). Returns None or {"rsi14"}.

    Needs 15 closes (the first RSI value is at index 14). RSI
    exactly 30 is not oversold.
    """
    if len(closes) < 15:
        return None
    value = rsi(closes)[-1]
    if value is None or value >= 30:
        return None
    return {"rsi14": value}


def oversold_bounce(closes):
    """RSI-14 below 30 within the last 5 sessions and the latest
    close above the prior close. Returns None or {"rsi14",
    "min_rsi_5d", "close", "prev_close"}.

    Needs 15 closes. "Within the last 5 sessions" is the last 5
    defined RSI values (indices -5..-1); a session with no defined
    RSI yet cannot count.
    """
    if len(closes) < 15 or len(closes) < 2:
        return None
    if closes[-1] <= closes[-2]:
        return None
    series = rsi(closes)
    recent = [v for v in series[-5:] if v is not None]
    if not recent or min(recent) >= 30:
        return None
    return {
        "rsi14": series[-1],
        "min_rsi_5d": min(recent),
        "close": closes[-1],
        "prev_close": closes[-2],
    }


SETUP_FUNCTIONS = {
    "breakout_20d": breakout_20d,
    "bull_flag": bull_flag,
    "reclaim_ma20": reclaim_ma20,
    "oversold": oversold,
    "oversold_bounce": oversold_bounce,
}


def _stage1_passes(name, row, closes):
    """Cheap necessary condition for `name`. Must be implied by the
    exact rule — a symbol that matches exactly always passes stage 1,
    so stage 1 never creates a false negative.

    - breakout_20d: close > max(prior 20) implies close > mean of the
      last 20 closes (each prior close is below it), and that mean is
      row["sma20"].
    - bull_flag: the flag window IS the last 5 closes, so a match
      implies their range is within 5%.
    - reclaim_ma20: the exact rule requires closes[-1] > ma20[-1],
      and ma20[-1] is row["sma20"].
    - oversold: stage 1 checks row["rsi14"] < 30 — the same value
      stage 2 recomputes from the raw closes.
    - oversold_bounce: the exact rule requires closes[-1] >
      closes[-2].
    """
    if name == "breakout_20d":
        return (row["sma20"] is not None
                and closes[-1] > row["sma20"])
    if name == "bull_flag":
        if len(closes) < 5:
            return False
        flag = closes[-5:]
        return (max(flag) - min(flag)) / min(flag) <= 0.05
    if name == "reclaim_ma20":
        return (row["sma20"] is not None
                and closes[-1] > row["sma20"])
    if name == "oversold":
        return row["rsi14"] is not None and row["rsi14"] < 30
    if name == "oversold_bounce":
        return len(closes) >= 2 and closes[-1] > closes[-2]
    raise ValueError(f"scan_setups: unknown setup {name!r}")


def scan_setups(groups, setups=None, max_confirmations=50):
    """Two-stage named-setup scan over {symbol: {'sector', 'candles'}}.

    Returns {"matches", "coverage", "partial", "capped",
    "unconfirmed", "failures", "note", "max_confirmations",
    "confirmations_used"}.

    - "matches": {setup name: [{symbol, sector, ...rule values}]}.
      A symbol appears only if its exact rule matched; the rule
      values that triggered are in the entry.
    - "coverage": {"universe", "scanned", "failed", "usable",
      "failed_symbols"} (see scanner.coverage_summary).
    - "partial": True if any symbol failed OR the confirmation cap
      was hit. "capped": True only for the cap. "unconfirmed":
      [{"setup", "symbol"}] candidates never exactly checked because
      the cap was reached — never reported as matches, never silently
      dropped.
    - "note": the coverage outcome in plain language.

    A symbol whose analysis raises is a failure (counted, listed,
    never fatal to the rest). A symbol with too few closes for a
    setup simply does not match it — that is not a failure.
    """
    wanted = list(SETUP_ORDER if setups is None else setups)
    for name in wanted:
        if name not in SETUP_FUNCTIONS:
            raise ValueError(f"scan_setups: unknown setup {name!r}")
    if max_confirmations < 0:
        raise ValueError("scan_setups: max_confirmations must be >= 0")
    matches = {name: [] for name in wanted}
    failures = []
    candidates = []  # (setup, symbol, sector, closes) in scan order
    for symbol in sorted(groups):
        entry = groups[symbol]
        try:
            row = analyse(entry["candles"])
        except Exception as exc:  # per-symbol isolation: log, continue
            failures.append({"symbol": symbol, "reason": str(exc)})
            continue
        closes = _closes_of(entry["candles"])
        for name in wanted:
            if _stage1_passes(name, row, closes):
                candidates.append((name, symbol,
                                   entry.get("sector", ""), closes))
    unconfirmed = []
    confirmations = 0
    for name, symbol, sector, closes in candidates:
        if confirmations >= max_confirmations:
            unconfirmed.append({"setup": name, "symbol": symbol})
            continue
        confirmations += 1
        try:
            hit = SETUP_FUNCTIONS[name](closes)
        except Exception as exc:  # exact check failed: log, continue
            failures.append({"symbol": symbol,
                             "reason": f"{name}: {exc}"})
            continue
        if hit is None:
            continue
        entry = {"symbol": symbol, "sector": sector}
        entry.update(hit)
        matches[name].append(entry)
    coverage = coverage_summary(groups, failures)
    capped = bool(unconfirmed)
    partial = coverage["failed"] > 0 or capped
    if partial:
        parts = []
        if coverage["failed"]:
            parts.append(f"{coverage['failed']} of "
                         f"{coverage['universe']} symbols failed and "
                         f"were excluded")
        if capped:
            parts.append(f"{len(unconfirmed)} candidate(s) were not "
                         f"confirmed because the confirmation cap "
                         f"({max_confirmations}) was reached")
        note = ("PARTIAL: " + "; ".join(parts) + ". Matches below cover "
                "only the symbols that were scanned and confirmed.")
    else:
        note = (f"Complete: all {coverage['universe']} symbols scanned, "
                f"no failures, all {confirmations} candidate(s) confirmed.")
    return {
        "matches": matches,
        "coverage": coverage,
        "partial": partial,
        "capped": capped,
        "unconfirmed": unconfirmed,
        "failures": failures,
        "note": note,
        "max_confirmations": max_confirmations,
        "confirmations_used": confirmations,
    }
