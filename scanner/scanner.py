"""Crossover scan over NEPSE candles. Research only, never a recommendation.

A "bullish cross" here means only this: on the cross date, the fast average
moved from at or below the slow average to above it. It is a description
of past prices, not a prediction and not a buy signal. The falsifiers that
matter most on NEPSE — thin trading, circuit limits, stale prices — are
flagged in the row, not hidden: see `thin_volume` and the README.
"""

from datetime import date as _date

try:
    from indicators import (adx, atr, bollinger, ema, find_crosses, latest_cross,
                        macd, rsi, since_cross_pct, sma, stochastic,
                        volume_ratio)
except ImportError:  # running as scanner.cli package
    from .indicators import (adx, atr, bollinger, ema, find_crosses, latest_cross,
                            macd, rsi, since_cross_pct, sma, stochastic,
                            volume_ratio)

DEFAULT_FAST = 20
DEFAULT_SLOW = 50


def _parse_iso(text):
    year, month, day = (int(p) for p in text.split("-"))
    return _date(year, month, day)


def analyse(candles, fast_period=DEFAULT_FAST, slow_period=DEFAULT_SLOW):
    """Full indicator snapshot for one symbol. Returns a dict; any
    indicator without enough data is None, never invented."""
    if not candles:
        raise ValueError("analyse: empty candle list")
    dates = [c.date for c in candles]
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise ValueError("analyse: dates must be strictly increasing "
                         "and unique")
    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    volumes = [c.volume for c in candles]
    fast = ema(closes, fast_period)
    slow = ema(closes, slow_period)
    macd_line, signal_line, _hist = macd(closes)
    _mid, upper, lower = bollinger(closes)
    stoch_k, stoch_d = stochastic(highs, lows, closes)
    rsi_s = rsi(closes)
    atr_s = atr(highs, lows, closes)
    adx_s = adx(highs, lows, closes)
    cross = latest_cross(fast, slow, "bullish")
    cross_date = None
    days_since = None
    since_pct = None
    if cross is not None:
        cross_date = candles[cross["index"]].date
        days_since = (_parse_iso(candles[-1].date)
                      - _parse_iso(cross_date)).days
        since_pct = since_cross_pct(closes, cross["index"])
    vol_ratio = volume_ratio(volumes)
    result = {
        "ltp": closes[-1],
        "last_date": candles[-1].date,
        "fast": fast[-1],
        "slow": slow[-1],
        "fast_period": fast_period,
        "slow_period": slow_period,
        "cross_date": cross_date,
        "days_since_cross": days_since,
        "since_cross_pct": since_pct,
        "all_crosses": find_crosses(fast, slow),
        "sma20": sma(closes, 20)[-1],
        "rsi14": rsi_s[-1],
        "macd": macd_line[-1],
        "macd_signal": signal_line[-1],
        "bollinger_upper": upper[-1],
        "bollinger_lower": lower[-1],
        "atr14": atr_s[-1],
        "stoch_k": stoch_k[-1],
        "stoch_d": stoch_d[-1],
        "adx14": adx_s[-1],
        "volume_ratio_20d": vol_ratio,
        # Falsifier flags: True means "treat this row with extra suspicion".
        "thin_volume": vol_ratio is not None and vol_ratio < 0.5,
        "no_cross": cross is None,
        "trailing_flat_days": _trailing_flat_days(closes),
        "last_day_move_pct": _last_day_move_pct(closes),
    }
    label, reasons = signal_label(result)
    result["signal_label"] = label
    result["signal_reasons"] = reasons
    return result


def _trailing_flat_days(closes):
    """Consecutive trailing bars with an unchanged close (circuit-limit
    days and untraded days both look like this)."""
    n = 1
    for i in range(len(closes) - 1, 0, -1):
        if closes[i] == closes[i - 1]:
            n += 1
        else:
            break
    return n if len(closes) > 1 else 0


def _last_day_move_pct(closes):
    if len(closes) < 2 or closes[-2] == 0:
        return None
    return (closes[-1] - closes[-2]) / closes[-2]


def signal_label(row):
    """Signal-vs-noise label for a crossed row. Returns (label, reasons).

    Tiers, in order — a row is only as strong as its weakest check:
    - NOISE: thin volume, or a long flat tail (stale / circuit-locked),
      or the cross itself is unconfirmed by any other reading.
    - WEAK: a cross with no confirmation at all.
    - WATCH: cross + volume at/above its 20-day average, trend unconfirmed.
    - CONFIRMED: cross + volume >= 1.5x average AND ADX >= 25 (a real
      trend, not just a fast average twitching above a slow one).
    "CONFIRMED" still means only "confirmed as a past-price pattern" —
    never a prediction, never a buy signal. No label is ever printed
    without its reasons.
    """
    if row["cross_date"] is None:
        return "NO SIGNAL", ["no bullish cross in this history"]
    reasons = []
    if row["thin_volume"]:
        reasons.append("volume below 0.5x its 20-day average (thin trading)")
    if row.get("trailing_flat_days", 0) >= 5:
        reasons.append(f"last {row['trailing_flat_days']} closes identical "
                       "(circuit-limit or stale-price tail)")
    if reasons:
        return "NOISE", reasons
    vol = row["volume_ratio_20d"]
    adx_v = row["adx14"]
    if vol is not None and vol >= 1.5 and adx_v is not None and adx_v >= 25:
        return "CONFIRMED (pattern only)", [
            f"volume {vol:.2f}x 20-day average",
            f"ADX {adx_v:.1f} (>= 25, trending)"]
    if vol is not None and vol >= 1.0:
        return "WATCH", [f"volume {vol:.2f}x 20-day average",
                         "trend strength unconfirmed (ADX < 25 or unknown)"]
    return "WEAK", ["cross only — no volume or trend confirmation"]


def scan(groups, fast_period=DEFAULT_FAST, slow_period=DEFAULT_SLOW,
         only_crossed=True):
    """Scan {symbol: {'sector', 'candles'}}. With only_crossed=True (the
    default, matching the screenshot's crossover list), only symbols whose
    latest bullish cross is still the most recent cross state — i.e. fast
    is currently above slow and a bullish cross exists — are returned.
    With only_crossed=False every symbol is returned, crossed or not.

    A symbol that fails analysis is SKIPPED, not fatal: use scan_report()
    to see the failure reasons. scan() itself never raises for one bad
    symbol — that is the failure-isolation rule (see README).
    """
    rows, _failures = scan_report(groups, fast_period, slow_period,
                                  only_crossed)
    return rows


def scan_report(groups, fast_period=DEFAULT_FAST, slow_period=DEFAULT_SLOW,
                only_crossed=True):
    """Like scan(), plus a failures list: [{'symbol', 'reason'}].
    Every failure is logged with a reason, never swallowed, and never
    poisons the other symbols."""
    rows = []
    failures = []
    for symbol in sorted(groups):
        entry = groups[symbol]
        try:
            row = analyse(entry["candles"], fast_period, slow_period)
        except Exception as exc:  # per-symbol isolation: log, continue
            failures.append({"symbol": symbol, "reason": str(exc)})
            continue
        row["symbol"] = symbol
        row["sector"] = entry.get("sector", "")
        if only_crossed and (row["cross_date"] is None
                             or row["fast"] is None or row["slow"] is None
                             or row["fast"] <= row["slow"]):
            continue
        rows.append(row)
    return rows, failures
