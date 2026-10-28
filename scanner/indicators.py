"""Zero-dependency technical indicators for NEPSE (Nepal Stock Exchange) research.

Research only. Not investment advice, never a buy/sell recommendation.
Every indicator here describes what past prices DID. None of them predicts
what a price WILL do. On thinly traded NEPSE stocks a signal can be an
artefact of one trade, a circuit limit, or a stale price — see README.md.

Conventions (standard textbook definitions, stated so results are checkable):
- SMA(n): simple mean of the last n closes, first value at index n-1.
- EMA(n): seeded with the SMA of the first n closes, then
  EMA = close * (2 / (n + 1)) + EMA_prev * (1 - 2 / (n + 1)).
- RSI(14): Wilder smoothing. First value at index 14 (needs 15 closes).
  Flat series (no gains and no losses) returns 50.0, not an error.
- MACD(12, 26, 9): EMA12 - EMA26; signal = EMA9 of the MACD line,
  seeded with the SMA of the first 9 MACD values.
- Bollinger(20, 2): SMA20 middle band, population standard deviation.
- ATR(14): Wilder smoothing of the true range.
- Stochastic(14, 3): %K over 14 bars, %D = SMA3 of %K.
- ADX(14): Wilder smoothing of +DM / -DM / true range, first ADX value
  is the mean of the first 14 DX values (available at index 27).
- A series shorter than an indicator's warm-up returns None for that
  indicator, never a made-up number.

All functions reject non-finite values (None, NaN, inf, strings, bools)
with ValueError, and reject non-positive prices where a ratio needs one.
"""

import math

__all__ = [
    "sma", "ema", "rsi", "macd", "bollinger", "atr", "stochastic", "adx",
    "volume_ratio", "find_crosses", "latest_cross", "since_cross_pct",
]


def _check(values, name="values"):
    if not isinstance(values, (list, tuple)) or len(values) == 0:
        raise ValueError(f"{name}: expected a non-empty list of numbers")
    out = []
    for v in values:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError(f"{name}: non-numeric value {v!r}")
        if not math.isfinite(v):
            raise ValueError(f"{name}: non-finite value {v!r}")
        out.append(float(v))
    return out


def _check_prices(values):
    out = _check(values, "closes")
    for v in out:
        if v <= 0:
            raise ValueError("closes: prices must be > 0")
    return out


def sma(values, period):
    """Simple moving average. Returns list with None until index period-1."""
    vals = _check(values)
    if period < 1:
        raise ValueError("period must be >= 1")
    out = [None] * len(vals)
    window = 0.0
    for i, v in enumerate(vals):
        window += v
        if i >= period:
            window -= vals[i - period]
        if i >= period - 1:
            out[i] = window / period
    return out


def ema(values, period):
    """Exponential moving average, SMA-seeded. None until index period-1."""
    vals = _check(values)
    if period < 1:
        raise ValueError("period must be >= 1")
    out = [None] * len(vals)
    if len(vals) < period:
        return out
    k = 2.0 / (period + 1)
    out[period - 1] = sum(vals[:period]) / period
    for i in range(period, len(vals)):
        out[i] = vals[i] * k + out[i - 1] * (1 - k)
    return out


def rsi(closes, period=14):
    """Wilder RSI. First value at index `period` (needs period+1 closes)."""
    vals = _check_prices(closes)
    if period < 1:
        raise ValueError("period must be >= 1")
    out = [None] * len(vals)
    if len(vals) < period + 1:
        return out
    gains = [max(vals[i] - vals[i - 1], 0.0) for i in range(1, len(vals))]
    losses = [max(vals[i - 1] - vals[i], 0.0) for i in range(1, len(vals))]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    idx = period  # first close index with a full window of changes
    if avg_loss == 0:
        out[idx] = 100.0 if avg_gain > 0 else 50.0
    else:
        out[idx] = 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)
    for i in range(period + 1, len(vals)):
        avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        if avg_loss == 0:
            out[i] = 100.0 if avg_gain > 0 else 50.0
        else:
            out[i] = 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)
    return out


def macd(closes, fast=12, slow=26, signal=9):
    """Returns (macd_line, signal_line, histogram), each None until warmed up."""
    vals = _check_prices(closes)
    fast_e = ema(vals, fast)
    slow_e = ema(vals, slow)
    line = [None] * len(vals)
    for i in range(len(vals)):
        if fast_e[i] is not None and slow_e[i] is not None:
            line[i] = fast_e[i] - slow_e[i]
    # Signal: EMA of the MACD line, seeded with SMA of first `signal` values.
    sig = [None] * len(vals)
    defined = [(i, v) for i, v in enumerate(line) if v is not None]
    if len(defined) >= signal:
        k = 2.0 / (signal + 1)
        first_idx = defined[signal - 1][0]
        sig[first_idx] = sum(v for _, v in defined[:signal]) / signal
        prev = sig[first_idx]
        for i, v in defined[signal:]:
            prev = v * k + prev * (1 - k)
            sig[i] = prev
    hist = [None] * len(vals)
    for i in range(len(vals)):
        if line[i] is not None and sig[i] is not None:
            hist[i] = line[i] - sig[i]
    return line, sig, hist


def bollinger(closes, period=20, mult=2.0):
    """Returns (middle, upper, lower). Population standard deviation."""
    vals = _check_prices(closes)
    mid = sma(vals, period)
    upper = [None] * len(vals)
    lower = [None] * len(vals)
    for i in range(len(vals)):
        if mid[i] is None:
            continue
        window = vals[i - period + 1:i + 1]
        mean = mid[i]
        var = sum((x - mean) ** 2 for x in window) / period
        sd = math.sqrt(var)
        upper[i] = mean + mult * sd
        lower[i] = mean - mult * sd
    return mid, upper, lower


def _true_range(highs, lows, closes):
    tr = [highs[0] - lows[0]]
    for i in range(1, len(highs)):
        tr.append(max(highs[i] - lows[i],
                        abs(highs[i] - closes[i - 1]),
                        abs(lows[i] - closes[i - 1])))
    return tr


def atr(highs, lows, closes, period=14):
    """Wilder ATR. First value at index `period` (needs period+1 bars)."""
    h = _check(highs, "highs")
    l = _check(lows, "lows")
    c = _check_prices(closes)
    if not (len(h) == len(l) == len(c)):
        raise ValueError("highs, lows, closes must have equal length")
    if period < 1:
        raise ValueError("period must be >= 1")
    out = [None] * len(c)
    if len(c) < period + 1:
        return out
    tr = _true_range(h, l, c)
    out[period] = sum(tr[1:period + 1]) / period
    for i in range(period + 1, len(c)):
        out[i] = (out[i - 1] * (period - 1) + tr[i]) / period
    return out


def stochastic(highs, lows, closes, period=14, smooth=3):
    """Returns (%K, %D). %D = SMA(smooth) of %K."""
    h = _check(highs, "highs")
    l = _check(lows, "lows")
    c = _check_prices(closes)
    if not (len(h) == len(l) == len(c)):
        raise ValueError("highs, lows, closes must have equal length")
    k = [None] * len(c)
    for i in range(len(c)):
        if i < period - 1:
            continue
        hi = max(h[i - period + 1:i + 1])
        lo = min(l[i - period + 1:i + 1])
        k[i] = 50.0 if hi == lo else 100.0 * (c[i] - lo) / (hi - lo)
    d = [None] * len(c)
    defined = [(i, v) for i, v in enumerate(k) if v is not None]
    for j in range(smooth - 1, len(defined)):
        idx = defined[j][0]
        d[idx] = sum(v for _, v in defined[j - smooth + 1:j + 1]) / smooth
    return k, d


def adx(highs, lows, closes, period=14):
    """Wilder ADX. First value at index 2*period - 1 (27 for period 14).

    Included because it implements cleanly with Wilder smoothing and no
    extra dependencies: +DM/-DM, smoothed true range, DI+/DI-, DX, then
    ADX as the mean of the first `period` DX values, Wilder-smoothed after.
    """
    h = _check(highs, "highs")
    l = _check(lows, "lows")
    c = _check_prices(closes)
    if not (len(h) == len(l) == len(c)):
        raise ValueError("highs, lows, closes must have equal length")
    if period < 1:
        raise ValueError("period must be >= 1")
    out = [None] * len(c)
    if len(c) < 2 * period:
        return out
    tr = _true_range(h, l, c)
    plus_dm = [0.0] * len(c)
    minus_dm = [0.0] * len(c)
    for i in range(1, len(c)):
        up = h[i] - h[i - 1]
        down = l[i - 1] - l[i]
        plus_dm[i] = up if up > down and up > 0 else 0.0
        minus_dm[i] = down if down > up and down > 0 else 0.0
    sm_tr = sum(tr[1:period + 1]) / period
    sm_plus = sum(plus_dm[1:period + 1]) / period
    sm_minus = sum(minus_dm[1:period + 1]) / period
    dx = [None] * len(c)

    def _dx(i):
        di_p = 100.0 * sm_plus / sm_tr if sm_tr else 0.0
        di_m = 100.0 * sm_minus / sm_tr if sm_tr else 0.0
        denom = di_p + di_m
        return 0.0 if denom == 0 else 100.0 * abs(di_p - di_m) / denom

    dx[period] = _dx(period)
    for i in range(period + 1, len(c)):
        sm_tr = (sm_tr * (period - 1) + tr[i]) / period
        sm_plus = (sm_plus * (period - 1) + plus_dm[i]) / period
        sm_minus = (sm_minus * (period - 1) + minus_dm[i]) / period
        dx[i] = _dx(i)
    defined_dx = [v for v in dx if v is not None]
    first = 2 * period - 1
    out[first] = sum(defined_dx[:period]) / period
    for i in range(first + 1, len(c)):
        out[i] = (out[i - 1] * (period - 1) + dx[i]) / period
    return out


def volume_ratio(volumes, period=20):
    """Last volume / mean of the previous `period` volumes. None if too few."""
    vols = _check(volumes, "volumes")
    if period < 1:
        raise ValueError("period must be >= 1")
    if len(vols) < period + 1:
        return None
    mean_prev = sum(vols[-period - 1:-1]) / period
    if mean_prev == 0:
        return None
    return vols[-1] / mean_prev


def find_crosses(fast, slow):
    """Indices where fast crosses slow. Each item: {'index', 'direction'}.

    'bullish' = fast moves from <= slow to > slow.
    'bearish' = fast moves from >= slow to < slow.
    Equal values alone never count as a cross.
    """
    if len(fast) != len(slow):
        raise ValueError("fast and slow must have equal length")
    crosses = []
    prev = None  # -1 fast below, 0 equal/unknown, +1 fast above
    for i in range(len(fast)):
        if fast[i] is None or slow[i] is None:
            continue
        cur = 1 if fast[i] > slow[i] else (-1 if fast[i] < slow[i] else 0)
        if prev is not None and cur != 0 and prev != 0 and cur != prev:
            crosses.append({"index": i,
                            "direction": "bullish" if cur == 1 else "bearish"})
        if cur != 0:
            prev = cur
    return crosses


def latest_cross(fast, slow, direction="bullish"):
    """Most recent cross of the given direction, or None."""
    for c in reversed(find_crosses(fast, slow)):
        if c["direction"] == direction:
            return c
    return None


def since_cross_pct(closes, cross_index):
    """(last close - close on cross date) / close on cross date, as a decimal.

    Returns None if the cross index is out of range or the cross close is 0.
    """
    vals = _check_prices(closes)
    if cross_index < 0 or cross_index >= len(vals):
        return None
    base = vals[cross_index]
    if base == 0:
        return None
    return (vals[-1] - base) / base
