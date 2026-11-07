"""Tests for named setups, coverage reporting, two-stage confirmation,
and the criteria-grammar screen. Run from scanner/:
python3 -m pytest tests/test_setups_screen.py -v

Series expectations were computed by hand from the rule definitions
in setups.py / screen.py, not by copying another library's output:
- breakout level is the max of the prior 20 closes (inclusive of the
  boundary: a close exactly equal to the level is not a breakout).
- bull_flag run is closes[-16] -> closes[-6] (10 steps); exactly +10%
  and exactly a 5% flag range both match (inclusive thresholds).
- reclaim_ma20 values are plain 20-day means, checked by hand.
- RSI on a steadily falling series is 0 (no gains at all).
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import Candle
from scanner import scan_with_coverage
from screen import screen
from setups import (
    SETUP_ORDER,
    breakout_20d,
    bull_flag,
    oversold,
    oversold_bounce,
    reclaim_ma20,
    scan_setups,
)


def candles_from_closes(closes, start_day=1):
    out = []
    for i, c in enumerate(closes):
        out.append(Candle(date=f"2026-01-{start_day + i:02d}", close=c,
                          high=c * 1.01, low=c * 0.99, volume=1000.0))
    return out


def groups_from(**series):
    return {sym: {"sector": "Test",
                  "candles": candles_from_closes(closes)}
            for sym, closes in series.items()}


# --- breakout_20d ----------------------------------------------------------

def test_breakout_20d_match_reports_level():
    hit = breakout_20d([100.0] * 20 + [101.0])
    assert hit is not None
    assert hit["breakout_level"] == pytest.approx(100.0)
    assert hit["close"] == pytest.approx(101.0)
    assert hit["above_level_pct"] == pytest.approx(0.01)


def test_breakout_20d_equal_to_level_is_not_a_breakout():
    assert breakout_20d([100.0] * 20 + [100.0]) is None


def test_breakout_20d_below_level_and_too_short():
    assert breakout_20d([100.0] * 20 + [99.0]) is None
    assert breakout_20d([100.0] * 20) is None


# --- bull_flag -------------------------------------------------------------

FLAG_RUN = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
FLAG_TAIL = [110.5, 111, 110.5, 109.5, 110]


def test_bull_flag_match_at_exact_thresholds():
    hit = bull_flag(FLAG_RUN + FLAG_TAIL)
    assert hit is not None
    assert hit["run_gain_pct"] == pytest.approx(0.10)
    assert hit["run_start"] == pytest.approx(100.0)
    assert hit["run_end"] == pytest.approx(110.0)
    assert hit["flag_low"] == pytest.approx(109.5)
    assert hit["flag_high"] == pytest.approx(111.0)
    assert hit["flag_range_pct"] == pytest.approx(1.5 / 109.5)


def test_bull_flag_run_under_10pct_is_not_a_match():
    weak_run = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 109]
    assert bull_flag(weak_run + FLAG_TAIL) is None


def test_bull_flag_range_over_5pct_is_not_a_match():
    wide_flag = [110, 116, 110, 110, 110]
    assert bull_flag(FLAG_RUN + wide_flag) is None


def test_bull_flag_too_short():
    assert bull_flag(FLAG_RUN + FLAG_TAIL[:4]) is None


# --- reclaim_ma20 ----------------------------------------------------------

def test_reclaim_ma20_match_reports_both_averages():
    hit = reclaim_ma20([100.0] * 19 + [90.0, 102.0])
    assert hit is not None
    assert hit["ma20"] == pytest.approx(99.6)
    assert hit["prev_ma20"] == pytest.approx(99.5)
    assert hit["close"] == pytest.approx(102.0)
    assert hit["prev_close"] == pytest.approx(90.0)


def test_reclaim_ma20_already_above_is_not_a_reclaim():
    assert reclaim_ma20([100.0] * 19 + [105.0, 104.0]) is None


def test_reclaim_ma20_still_below_and_too_short():
    assert reclaim_ma20([100.0] * 19 + [90.0, 95.0]) is None
    assert reclaim_ma20([100.0] * 20) is None


# --- oversold --------------------------------------------------------------

def test_oversold_steady_decline_is_zero_rsi():
    closes = [100.0 * 0.95 ** i for i in range(20)]
    hit = oversold(closes)
    assert hit is not None
    assert hit["rsi14"] == pytest.approx(0.0)


def test_oversold_flat_and_rising_are_not_oversold():
    assert oversold([100.0] * 20) is None
    assert oversold([100.0 * 1.02 ** i for i in range(20)]) is None


def test_oversold_too_short():
    assert oversold([100.0 * 0.95 ** i for i in range(14)]) is None


# --- oversold_bounce -------------------------------------------------------

def test_oversold_bounce_decline_then_one_up_close():
    closes = [100.0 * 0.95 ** i for i in range(16)]
    closes.append(closes[-1] * 1.02)
    hit = oversold_bounce(closes)
    assert hit is not None
    assert hit["rsi14"] < 30
    assert hit["min_rsi_5d"] < 30
    assert hit["close"] > hit["prev_close"]


def test_oversold_bounce_no_up_close_is_not_a_bounce():
    closes = [100.0 * 0.95 ** i for i in range(20)]
    assert oversold_bounce(closes) is None


def test_oversold_bounce_rsi_recovered_is_not_a_bounce():
    closes = [100.0 * 0.95 ** i for i in range(15)]
    for _ in range(10):  # long rally: RSI above 30 for the last 5 sessions
        closes.append(closes[-1] * 1.10)
    assert oversold_bounce(closes) is None


def test_oversold_bounce_too_short():
    assert oversold_bounce([100.0 * 0.95 ** i for i in range(14)]) is None


# --- scan_with_coverage ----------------------------------------------------

def test_scan_with_coverage_complete_when_nothing_fails():
    groups = groups_from(GOOD=[100.0] * 30)
    result = scan_with_coverage(groups, only_crossed=False)
    assert result["coverage"] == {
        "universe": 1, "scanned": 1, "failed": 0, "usable": 1,
        "failed_symbols": [],
    }
    assert result["partial"] is False
    assert result["note"].startswith("Complete:")
    assert len(result["rows"]) == 1


def test_scan_with_coverage_partial_names_failed_symbol():
    groups = groups_from(GOOD=[100.0] * 30)
    groups["BAD"] = {"sector": "Test", "candles": []}
    result = scan_with_coverage(groups, only_crossed=False)
    assert result["coverage"]["universe"] == 2
    assert result["coverage"]["scanned"] == 2
    assert result["coverage"]["failed"] == 1
    assert result["coverage"]["usable"] == 1
    assert result["coverage"]["failed_symbols"] == ["BAD"]
    assert result["partial"] is True
    assert "PARTIAL" in result["note"]
    assert "BAD" in result["note"]
    assert [r["symbol"] for r in result["rows"]] == ["GOOD"]


def test_scan_with_coverage_empty_universe():
    result = scan_with_coverage({}, only_crossed=False)
    assert result["coverage"]["universe"] == 0
    assert result["coverage"]["usable"] == 0
    assert result["partial"] is False
    assert result["rows"] == []


# --- scan_setups: integration + two-stage confirmation ---------------------

def test_scan_setups_finds_breakout_and_reports_coverage():
    groups = groups_from(
        BRK=[100.0] * 20 + [101.0],
        FLAT=[100.0] * 30,
        BAD=[],
    )
    result = scan_setups(groups)
    assert set(result["matches"]) == set(SETUP_ORDER)
    brk = result["matches"]["breakout_20d"]
    assert [m["symbol"] for m in brk] == ["BRK"]
    assert brk[0]["breakout_level"] == pytest.approx(100.0)
    assert brk[0]["sector"] == "Test"
    assert result["matches"]["bull_flag"] == []
    assert result["matches"]["oversold"] == []
    assert result["coverage"]["failed"] == 1
    assert result["coverage"]["failed_symbols"] == ["BAD"]
    assert result["coverage"]["usable"] == 2
    assert result["partial"] is True
    assert "PARTIAL" in result["note"]


def test_scan_setups_complete_when_nothing_fails():
    groups = groups_from(BRK=[100.0] * 20 + [101.0])
    result = scan_setups(groups)
    assert result["partial"] is False
    assert result["capped"] is False
    assert result["unconfirmed"] == []
    assert result["note"].startswith("Complete:")


def test_scan_setups_subset_only_runs_wanted_setups():
    groups = groups_from(
        DOWN=[100.0 * 0.95 ** i for i in range(20)])
    result = scan_setups(groups, setups=["oversold"])
    assert list(result["matches"]) == ["oversold"]
    assert len(result["matches"]["oversold"]) == 1


def test_scan_setups_unknown_setup_raises():
    with pytest.raises(ValueError):
        scan_setups({}, setups=["not_a_setup"])


def test_scan_setups_confirmation_cap_marks_partial():
    # Series matches breakout_20d only: the prior close (102) sits above
    # its 20-day average (100.1), so reclaim_ma20 does not match, and
    # the run gain is 0, so bull_flag does not match. But bull_flag's
    # cheap stage-1 check (last-5 range 3% <= 5%) and oversold_bounce's
    # (last close above prior close) still pass, so each symbol yields
    # 4 candidates: breakout, bull_flag, reclaim, oversold_bounce.
    series = [100.0] * 19 + [102.0, 103.0]
    groups = groups_from(**{f"BRK{i}": series for i in range(5)})
    result = scan_setups(groups, max_confirmations=6)
    assert [m["symbol"] for m in result["matches"]["breakout_20d"]] == [
        "BRK0", "BRK1"]
    assert result["confirmations_used"] == 6
    assert result["capped"] is True
    assert result["partial"] is True
    assert len(result["unconfirmed"]) == 14  # 20 candidates - 6 confirmed
    assert result["unconfirmed"][0] == {
        "setup": "reclaim_ma20", "symbol": "BRK1"}
    assert "PARTIAL" in result["note"]
    assert "confirmation cap (6)" in result["note"]


def test_scan_setups_zero_cap_confirms_nothing():
    groups = groups_from(BRK=[100.0] * 20 + [101.0])
    result = scan_setups(groups, max_confirmations=0)
    assert result["matches"]["breakout_20d"] == []
    assert result["confirmations_used"] == 0
    assert result["partial"] is True
    # BRK passes stage 1 for breakout, bull_flag (last-5 range 1%),
    # reclaim, and oversold_bounce (last close above prior close)
    # alike, so all four are unconfirmed, in setup order.
    assert result["unconfirmed"] == [
        {"setup": "breakout_20d", "symbol": "BRK"},
        {"setup": "bull_flag", "symbol": "BRK"},
        {"setup": "reclaim_ma20", "symbol": "BRK"},
        {"setup": "oversold_bounce", "symbol": "BRK"},
    ]


def test_scan_setups_stage1_never_rejects_exact_match():
    # Every series below matches its setup exactly; the two-stage scan
    # must find all of them (stage 1 is necessary, never a false no).
    groups = groups_from(
        BRK=[100.0] * 20 + [101.0],
        FLAG=FLAG_RUN + FLAG_TAIL,
        RECL=[100.0] * 19 + [90.0, 102.0],
        DOWN=[100.0 * 0.95 ** i for i in range(20)],
    )
    closes = [100.0 * 0.95 ** i for i in range(16)]
    closes.append(closes[-1] * 1.02)
    groups["BOUNCE"] = {"sector": "Test",
                        "candles": candles_from_closes(closes)}
    result = scan_setups(groups)
    assert result["partial"] is False
    # BRK matches breakout AND reclaim (close above its average, prior
    # close on it); RECL matches breakout too (102 > prior max 100) and
    # oversold_bounce (its RSI dipped to 0 on the 90 bar, inside the
    # last 5 sessions, and the last close rose).
    assert [m["symbol"] for m in result["matches"]["breakout_20d"]] == [
        "BRK", "RECL"]
    assert [m["symbol"] for m in result["matches"]["bull_flag"]] == [
        "FLAG"]
    assert [m["symbol"] for m in result["matches"]["reclaim_ma20"]] == [
        "BRK", "RECL"]
    assert [m["symbol"] for m in result["matches"]["oversold"]] == [
        "BOUNCE", "DOWN"]
    assert [m["symbol"] for m in result["matches"]["oversold_bounce"]] == [
        "BOUNCE", "RECL"]


# --- screen: criteria grammar + audit log ----------------------------------

ROWS = [
    {"symbol": "A", "rsi14": 25.0, "ltp": 100.0},
    {"symbol": "B", "rsi14": 45.0, "ltp": 200.0},
    {"symbol": "C", "rsi14": None, "ltp": 150.0},
    {"symbol": "D", "rsi14": 20.0, "ltp": 90.0},
]


def test_screen_lt_removes_high_rsi_and_none():
    result = screen(ROWS, [{"field": "rsi14", "op": "<", "value": 30}])
    assert [r["symbol"] for r in result["rows"]] == ["A", "D"]
    assert result["audit"] == [{
        "clause": {"field": "rsi14", "op": "<", "value": 30},
        "removed": 2, "remaining": 2,
    }]


def test_screen_clauses_apply_in_order_and_audit_each():
    result = screen(ROWS, [
        {"field": "rsi14", "op": "<", "value": 30},
        {"field": "ltp", "op": ">=", "value": 95},
    ])
    assert [r["symbol"] for r in result["rows"]] == ["A"]
    assert [a["removed"] for a in result["audit"]] == [2, 1]
    assert [a["remaining"] for a in result["audit"]] == [2, 1]


def test_screen_each_operator():
    assert [r["symbol"] for r in screen(
        ROWS, [{"field": "ltp", "op": ">", "value": 150}])["rows"]] == ["B"]
    assert [r["symbol"] for r in screen(
        ROWS, [{"field": "ltp", "op": ">=", "value": 150}])["rows"]] == [
        "B", "C"]
    assert [r["symbol"] for r in screen(
        ROWS, [{"field": "ltp", "op": "<=", "value": 100}])["rows"]] == [
        "A", "D"]
    assert [r["symbol"] for r in screen(
        ROWS, [{"field": "rsi14", "op": "==", "value": 25.0}])["rows"]] == [
        "A"]


def test_screen_between_is_inclusive():
    result = screen(ROWS, [{"field": "ltp", "op": "between",
                            "value": [100, 150]}])
    assert [r["symbol"] for r in result["rows"]] == ["A", "C"]


def test_screen_empty_criteria_returns_all_rows():
    result = screen(ROWS, [])
    assert result["rows"] == ROWS
    assert result["audit"] == []


def test_screen_unknown_operator_raises():
    with pytest.raises(ValueError):
        screen(ROWS, [{"field": "ltp", "op": "!=", "value": 100}])


def test_screen_unknown_field_raises():
    with pytest.raises(ValueError):
        screen(ROWS, [{"field": "nope", "op": ">", "value": 1}])


def test_screen_malformed_between_raises():
    with pytest.raises(ValueError):
        screen(ROWS, [{"field": "ltp", "op": "between", "value": [150]}])
    with pytest.raises(ValueError):
        screen(ROWS, [{"field": "ltp", "op": "between",
                       "value": [150, 100]}])
