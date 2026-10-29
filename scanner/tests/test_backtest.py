"""Tests for the walk-forward backtest. Run from scanner/:
python3 -m pytest tests/ -v

Labels here are PATTERN ONLY: a "win" means only "the price moved in
the direction of the past cross over the horizon". It is never a buy,
sell, or hold signal, and no test asserts that a pattern predicts
anything — the tests pin the arithmetic and the no-lookahead property.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest import backtest, backtest_csv, summarize, walk_forward_events
from data import Candle
from indicators import ema, find_crosses


def candles_from_closes(closes):
    out = []
    for i, c in enumerate(closes):
        out.append(
            Candle(
                date=f"2026-01-{i + 1:02d}",
                close=c,
                high=c * 1.01,
                low=c * 0.99,
                volume=1000.0,
            )
        )
    return out


# Series: flat 20, flat 10, then a gradual rise. EMA(3) crosses EMA(5)
# upward on the second rising bar (index 11, close 14).
RISE = [20] * 5 + [10] * 5 + [12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
# Mirror image: flat 10, flat 20, then a gradual fall.
FALL = [10] * 5 + [20] * 5 + [18, 16, 14, 12, 10, 8, 6, 4]
# Rise then reversal: the bullish cross is followed by a fall.
REVERSAL = [20] * 5 + [10] * 5 + [12, 14, 16, 14, 12, 10, 8]
# Flat after the jump: the bullish cross scores exactly 0.
FLAT_AFTER = [20] * 5 + [10] * 5 + [20] * 6


def test_bullish_win_forward_return_is_hand_checked():
    events, excluded = walk_forward_events(candles_from_closes(RISE), 3, 5, 2)
    assert excluded == 0
    assert len(events) == 1
    event = events[0]
    assert event["index"] == 11
    assert event["date"] == "2026-01-12"
    assert event["direction"] == "bullish"
    assert event["close_at_signal"] == 14
    assert event["close_at_horizon"] == 18
    # Forward return is (18 - 14) / 14, computed from the series itself.
    assert event["forward_return"] == pytest.approx(2 / 7)
    assert event["outcome"] == "win"


def test_bearish_win_uses_flipped_sign():
    events, _excluded = walk_forward_events(candles_from_closes(FALL), 3, 5, 2)
    assert len(events) == 1
    event = events[0]
    assert event["direction"] == "bearish"
    assert event["close_at_signal"] == 16
    assert event["close_at_horizon"] == 12
    assert event["forward_return"] == pytest.approx(-0.25)
    # Bearish "win" means only: the price fell after a bearish cross.
    assert event["outcome"] == "win"


def test_bullish_loss_stays_in_the_record():
    events, excluded = walk_forward_events(candles_from_closes(REVERSAL), 3, 5, 3)
    assert len(events) == 1
    assert events[0]["direction"] == "bullish"
    assert events[0]["close_at_signal"] == 14
    assert events[0]["close_at_horizon"] == 12
    assert events[0]["forward_return"] == pytest.approx(-1 / 7)
    assert events[0]["outcome"] == "loss"
    # The later bearish cross has no full 3-bar outcome: counted, not
    # silently dropped and not scored on a partial horizon.
    assert excluded == 1


def test_flat_outcome_is_neither_win_nor_loss():
    events, _excluded = walk_forward_events(candles_from_closes(FLAT_AFTER), 3, 5, 2)
    assert len(events) == 1
    assert events[0]["forward_return"] == 0.0
    assert events[0]["outcome"] == "flat"


def test_cross_near_series_end_is_excluded_not_scored():
    short = [20] * 5 + [10] * 5 + [12, 14, 16]
    events, excluded = walk_forward_events(candles_from_closes(short), 3, 5, 5)
    assert events == []
    assert excluded == 1


def test_no_lookahead_signal_matches_prefix_computation():
    """A cross at t computed from the full series must equal the cross
    computed from the prefix ending at t: the signal uses only data up
    to t. Appending future bars must not change any earlier signal."""
    closes = RISE
    full_fast = ema(closes, 3)
    full_slow = ema(closes, 5)
    full_crosses = find_crosses(full_fast, full_slow)
    assert full_crosses  # the test would be vacuous without a cross
    for cross in full_crosses:
        t = cross["index"]
        prefix_crosses = find_crosses(ema(closes[: t + 1], 3), ema(closes[: t + 1], 5))
        assert cross in prefix_crosses
    # And the backtest's own events carry the same signals.
    events, _excluded = walk_forward_events(candles_from_closes(closes), 3, 5, 2)
    assert [(e["index"], e["direction"]) for e in events] == [
        (c["index"], c["direction"])
        for c in full_crosses
        if c["index"] + 2 < len(closes)
    ]


def test_forward_return_matches_series_for_every_event():
    closes = RISE + [32, 34, 30, 26, 22]
    events, _excluded = walk_forward_events(candles_from_closes(closes), 3, 5, 4)
    assert events
    for event in events:
        i = event["index"]
        assert event["forward_return"] == pytest.approx(closes[i + 4] / closes[i] - 1)


def test_naive_baseline_uses_same_walk_forward_windows():
    # Hand-checked on RISE with fast 3 / slow 5 / horizon 2: warm-up
    # index is 4, so windows run t = 4 through t = 17 (t + 2 < 20),
    # 14 windows in total; the expected rates below are recomputed
    # from the series itself, not copied from the module's output.
    result = backtest(candles_from_closes(RISE), 3, 5, 2)
    naive = result["metrics"]["naive"]
    assert naive["n_windows"] == 14
    windows = [RISE[t + 2] / RISE[t] - 1 for t in range(4, len(RISE) - 2)]
    assert naive["positive_rate"] == pytest.approx(
        sum(1 for r in windows if r > 0) / len(windows)
    )
    assert naive["mean_forward_return"] == pytest.approx(sum(windows) / len(windows))
    assert naive["mae_no_change"] == pytest.approx(
        sum(abs(r) for r in windows) / len(windows)
    )
    bullish = result["metrics"]["bullish"]
    assert bullish["n_events"] == 1
    assert bullish["wins"] == 1 and bullish["losses"] == 0
    assert bullish["hit_rate"] == 1.0
    assert bullish["hit_rate_lift"] == pytest.approx(1.0 - naive["positive_rate"])


def test_negative_lift_is_reported_not_hidden():
    result = backtest(candles_from_closes(REVERSAL), 3, 5, 3)
    bullish = result["metrics"]["bullish"]
    assert bullish["hit_rate"] == 0.0
    assert bullish["hit_rate_lift"] < 0
    assert result["metrics"]["combined"]["hit_rate"] == 0.0


def test_no_events_still_reports_naive_baseline():
    flat = candles_from_closes([50] * 30)
    result = backtest(flat, 3, 5, 2)
    assert result["events"] == []
    assert result["metrics"]["bullish"] is None
    assert result["metrics"]["bearish"] is None
    assert result["metrics"]["combined"] is None
    assert result["metrics"]["naive"]["n_windows"] == 24
    assert result["metrics"]["naive"]["positive_rate"] == 0.0


def test_summarize_rejects_bad_horizon():
    with pytest.raises(ValueError):
        summarize([], [10, 11, 12], 0, 0)


def test_backtest_rejects_bad_inputs():
    with pytest.raises(ValueError):
        backtest([], 3, 5, 2)
    with pytest.raises(ValueError):
        backtest(candles_from_closes(RISE), 3, 5, 0)
    with pytest.raises(ValueError):
        backtest(candles_from_closes(RISE), 0, 5, 2)
    shuffled = candles_from_closes(RISE)
    shuffled[3], shuffled[4] = shuffled[4], shuffled[3]
    with pytest.raises(ValueError):
        backtest(shuffled, 3, 5, 2)


def test_backtest_csv_round_trips_through_load_csv(tmp_path):
    path = tmp_path / "prices.csv"
    path.write_text("date,close,high,low,volume\n")
    with path.open("a") as fh:
        for i, c in enumerate(RISE):
            fh.write(f"2026-01-{i + 1:02d},{c},{c * 1.01},{c * 0.99},1000\n")
    result = backtest_csv(str(path), 3, 5, 2)
    assert len(result["events"]) == 1
    assert result["events"][0]["outcome"] == "win"
    assert result["metrics"]["bullish"]["hit_rate"] == 1.0
