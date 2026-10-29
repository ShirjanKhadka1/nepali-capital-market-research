"""Walk-forward backtest of crossover signal patterns. Research only.

A "signal" here is a PATTERN ONLY: a fast EMA crossing a slow EMA on a
past date. It is never a buy, sell, or hold recommendation, and this
module never prints one. What it reports is what happened AFTER past
crosses, on a horizon the caller chooses — wins and losses alike.

Walk-forward discipline (no lookahead)
--------------------------------------
The signal at time ``t`` uses only data up to ``t``. That is a property
of the indicators, not a promise: ``indicators.ema`` at index ``i`` is
computed from closes up to ``i`` only, and ``find_crosses`` compares
the fast/slow pair at ``i`` with the previous non-None state. So a
cross recorded at ``t`` is identical whether it is computed from the
full series or from the prefix ending at ``t`` — a test pins this.
The outcome (the close ``horizon`` bars later) is by definition future
data, but it is only ever used to SCORE the signal, never to form it.

Metrics (all defined here, no hidden choices)
---------------------------------------------
For a signal at index ``t`` with horizon ``h``:

- ``forward_return = close[t + h] / close[t] - 1``.
- Bullish signal: win if ``forward_return > 0``, loss if ``< 0``,
  flat if ``== 0``. Bearish signal: the signs flip (win if ``< 0``).
- ``hit_rate = wins / n_events`` (flats count as events, not wins).
- ``mean_forward_return`` / ``median_forward_return``: mean / median
  of the events' forward returns, signs as observed.
- ``mae_no_change``: mean ``|forward_return|`` over events — the mean
  absolute error of a naive no-change forecast (predicting the price
  stays at ``close[t]``) on exactly the signal windows.
- Naive baseline, same walk-forward discipline: every eligible window
  (any index ``t`` at or after the slow average's warm-up with
  ``t + h`` in range) is scored the same way, with no signal at all.
  ``naive_positive_rate`` is the share of those windows with a
  positive forward return; ``naive_negative_rate`` the share with a
  negative one; ``naive_mean_forward_return`` and
  ``naive_mae_no_change`` are the corresponding means.
- ``hit_rate_lift``: signal hit rate minus the matching naive rate
  (positive rate for bullish signals, negative rate for bearish).
  A negative lift is a loss for the pattern and stays in the record;
  it is not edited out, averaged away, or re-labelled.
- ``excluded``: crosses too close to the end of the series to have a
  full ``h``-bar outcome. They are counted, not silently dropped, and
  never scored on a partial horizon.

Limitations, stated not hidden
------------------------------
- A cross that happens before the slow average is defined cannot be
  recorded (inherited from ``indicators`` / ``scanner`` warm-up).
- Crosses are rare: on a short series the event count is small and a
  hit rate over a handful of events proves nothing. The result dict
  always carries ``n_events`` next to every rate for that reason.
- This module scores past patterns only. It says nothing about the
  next cross, the next price, or any market — including NEPSE. An
  example series from another market (e.g. AAPL) is an example of the
  METHOD, never evidence about NEPSE.
- No live feed: input is a user-supplied CSV (see ``data.load_csv``).
  Name the CSV's source wherever results are shared.

Standard library only.
"""

import statistics

try:
    from data import load_csv
    from indicators import ema, find_crosses
except ImportError:  # running as scanner.backtest package
    from .data import load_csv
    from .indicators import ema, find_crosses

DEFAULT_FAST = 20
DEFAULT_SLOW = 50
DEFAULT_HORIZON = 5


def _closes_and_dates(candles):
    if not candles:
        raise ValueError("backtest: empty candle list")
    dates = [c.date for c in candles]
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise ValueError("backtest: dates must be strictly increasing and unique")
    return [c.close for c in candles], dates


def walk_forward_events(
    candles, fast_period=DEFAULT_FAST, slow_period=DEFAULT_SLOW, horizon=DEFAULT_HORIZON
):
    """All crossover events with their walk-forward outcomes.

    Returns (events, excluded): ``events`` is a list of dicts with
    index, date, direction, close_at_signal, close_at_horizon,
    horizon_date, forward_return, and outcome ("win"/"loss"/"flat").
    ``excluded`` counts crosses with no full ``horizon``-bar outcome.
    Signals use only data up to their own index (see module docstring).
    """
    if horizon < 1:
        raise ValueError("backtest: horizon must be >= 1")
    if fast_period < 1 or slow_period < 1:
        raise ValueError("backtest: periods must be >= 1")
    closes, dates = _closes_and_dates(candles)
    fast = ema(closes, fast_period)
    slow = ema(closes, slow_period)
    events = []
    excluded = 0
    for cross in find_crosses(fast, slow):
        i = cross["index"]
        if i + horizon >= len(closes):
            excluded += 1
            continue
        forward = closes[i + horizon] / closes[i] - 1
        if cross["direction"] == "bullish":
            outcome = "win" if forward > 0 else "loss" if forward < 0 else "flat"
        else:
            outcome = "win" if forward < 0 else "loss" if forward > 0 else "flat"
        events.append(
            {
                "index": i,
                "date": dates[i],
                "direction": cross["direction"],
                "close_at_signal": closes[i],
                "close_at_horizon": closes[i + horizon],
                "horizon_date": dates[i + horizon],
                "forward_return": forward,
                "outcome": outcome,
            }
        )
    return events, excluded


def _summarize_direction(events, direction):
    """Hit-rate block for one direction; None if it has no events."""
    subset = [e for e in events if e["direction"] == direction]
    if not subset:
        return None
    returns = [e["forward_return"] for e in subset]
    wins = sum(1 for e in subset if e["outcome"] == "win")
    losses = sum(1 for e in subset if e["outcome"] == "loss")
    flats = sum(1 for e in subset if e["outcome"] == "flat")
    return {
        "n_events": len(subset),
        "wins": wins,
        "losses": losses,
        "flats": flats,
        "hit_rate": wins / len(subset),
        "mean_forward_return": sum(returns) / len(returns),
        "median_forward_return": statistics.median(returns),
        "mae_no_change": sum(abs(r) for r in returns) / len(returns),
        "best_forward_return": max(returns),
        "worst_forward_return": min(returns),
    }


def summarize(events, closes, horizon, warmup_index):
    """Metrics for ``events`` plus the naive baseline over all windows.

    ``closes`` is the full close series; ``warmup_index`` is the first
    index where the slow average is defined (``slow_period - 1``), so
    the baseline only covers windows the signal could have covered.
    """
    if horizon < 1:
        raise ValueError("backtest: horizon must be >= 1")
    bullish = _summarize_direction(events, "bullish")
    bearish = _summarize_direction(events, "bearish")
    combined = None
    if events:
        wins = sum(1 for e in events if e["outcome"] == "win")
        combined = {
            "n_events": len(events),
            "wins": wins,
            "losses": sum(1 for e in events if e["outcome"] == "loss"),
            "flats": sum(1 for e in events if e["outcome"] == "flat"),
            "hit_rate": wins / len(events),
        }
    windows = [
        closes[t + horizon] / closes[t] - 1
        for t in range(warmup_index, len(closes) - horizon)
    ]
    naive = None
    if windows:
        naive = {
            "n_windows": len(windows),
            "positive_rate": (sum(1 for r in windows if r > 0) / len(windows)),
            "negative_rate": (sum(1 for r in windows if r < 0) / len(windows)),
            "mean_forward_return": sum(windows) / len(windows),
            "mae_no_change": sum(abs(r) for r in windows) / len(windows),
        }
    result = {
        "bullish": bullish,
        "bearish": bearish,
        "combined": combined,
        "naive": naive,
    }
    if bullish is not None and naive is not None:
        result["bullish"]["hit_rate_lift"] = (
            bullish["hit_rate"] - naive["positive_rate"]
        )
    if bearish is not None and naive is not None:
        result["bearish"]["hit_rate_lift"] = (
            bearish["hit_rate"] - naive["negative_rate"]
        )
    return result


def backtest(
    candles, fast_period=DEFAULT_FAST, slow_period=DEFAULT_SLOW, horizon=DEFAULT_HORIZON
):
    """Full walk-forward backtest for one symbol's candles.

    Returns {"events", "excluded", "metrics", "fast_period",
    "slow_period", "horizon"}.
    """
    events, excluded = walk_forward_events(candles, fast_period, slow_period, horizon)
    closes, _dates = _closes_and_dates(candles)
    metrics = summarize(events, closes, horizon, slow_period - 1)
    return {
        "events": events,
        "excluded": excluded,
        "metrics": metrics,
        "fast_period": fast_period,
        "slow_period": slow_period,
        "horizon": horizon,
    }


def backtest_csv(
    path, fast_period=DEFAULT_FAST, slow_period=DEFAULT_SLOW, horizon=DEFAULT_HORIZON
):
    """Backtest a single-symbol CSV (columns date, close, high, low,
    volume — see ``data.load_csv``). The CSV's source must be named
    wherever results are shared."""
    return backtest(load_csv(path), fast_period, slow_period, horizon)
