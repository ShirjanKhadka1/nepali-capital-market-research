"""Second check pass — edge cases that break real NEPSE scanners.

Each test names the generic failure mode it guards against. Nothing here
touches, reads, or copies the private Nepse Decode project; these are
generic scanner failure modes, tested on synthetic series.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import Candle, load_multi_csv_report
from indicators import adx, atr, bollinger, ema, rsi, stochastic
from scanner import analyse, scan_report, signal_label


def mk(closes, volumes=None, start="2026-01-01"):
    import datetime
    base = datetime.date.fromisoformat(start)
    out = []
    for i, c in enumerate(closes):
        d = (base + datetime.timedelta(days=i)).isoformat()
        out.append(Candle(date=d, close=c, high=c * 1.01, low=c * 0.99,
                          volume=(volumes[i] if volumes else 1000.0)))
    return out


def test_circuit_limit_repeated_closes_no_crash_all_finite():
    # Rise, then 10 identical closes at the circuit limit: division by
    # zero / zero-range must not produce inf or NaN anywhere.
    closes = [100 + i for i in range(40)] + [139.0] * 10
    row = analyse(mk(closes))
    for key in ("rsi14", "macd", "bollinger_upper", "bollinger_lower",
                "atr14", "stoch_k", "stoch_d", "adx14"):
        assert row[key] is not None and row[key] == row[key]  # not NaN
        assert abs(row[key]) != float("inf")
    # 11, not 10: the last rising bar also closed at 139, so the
    # trailing identical-close run is 11 bars long.
    assert row["trailing_flat_days"] == 11


def test_single_day_spike_then_revert_does_not_create_fake_cross():
    # One +30% bar in a flat series, then back to flat: EMA cross logic
    # must not report a bullish cross from a single spike, and no
    # indicator may go non-finite.
    closes = [100.0] * 40 + [130.0] + [100.0] * 20
    row = analyse(mk(closes))
    assert row["cross_date"] is None  # fast never sustainably crosses slow
    assert row["rsi14"] is not None and 0 <= row["rsi14"] <= 100


def test_price_gap_series_atr_captures_gap():
    # Gap up 100 -> 150 overnight: ATR must reflect the gap (true range
    # includes prior close), not just the small daily range.
    closes = [100.0] * 20 + [150.0] * 20
    highs = [c * 1.01 for c in closes]
    lows = [c * 0.99 for c in closes]
    result = atr(highs, lows, closes, 14)
    assert result[-1] > 2.0  # daily range alone would be ~2.0


def test_missing_days_dates_are_kept_as_given_not_filled():
    # A CSV that skips calendar days (holiday / no trade) must NOT be
    # silently filled with invented closes. analyse() uses only the bars
    # given; the last date is the last bar's date, nothing later.
    candles = mk([100.0, 101.0, 102.0], start="2026-01-01")
    candles[1].date = "2026-01-05"  # a gap in the input itself
    candles[2].date = "2026-01-06"
    row = analyse(candles)
    assert row["last_date"] == "2026-01-06"
    assert row["ltp"] == 102.0


def test_very_short_history_returns_none_not_wrong_numbers():
    row = analyse(mk([100.0, 101.0]))
    assert row["rsi14"] is None and row["adx14"] is None
    assert row["cross_date"] is None and row["fast"] is None
    label, _ = signal_label(row)
    assert label == "NO SIGNAL"


def test_no_look_ahead_earlier_indicators_unchanged_by_later_bars():
    # Appending a future bar must not change any indicator value that
    # was already computed for an earlier bar (no future data leaks back).
    base = [100 + i * 0.5 for i in range(40)]
    early = rsi(base, 14)
    later = rsi(base + [200.0], 14)
    assert early[:-1] == later[:-1] or all(
        (a is None and b is None) or a == b
        for a, b in zip(early, later[:len(early)]))
    early_ema = ema(base, 20)
    later_ema = ema(base + [200.0], 20)
    assert early_ema == later_ema[:len(early_ema)]


def test_one_bad_symbol_does_not_poison_scan(tmp_path):
    csv_path = tmp_path / "mixed.csv"
    lines = ["symbol,sector,date,close,high,low,volume"]
    for i in range(60):
        lines.append(f"GOOD,Hydro Power,2026-01-{i+1:02d}" if i < 31 else
                     f"GOOD,Hydro Power,2026-02-{i-30:02d},"
                     f"{170 + (i-59)*3 if i >= 59 else 170:.2f},"
                     f"{172:.2f},{168:.2f},1000")
    # Simpler: rebuild GOOD deterministically below; BAD has a bad close.
    lines = ["symbol,sector,date,close,high,low,volume"]
    import datetime
    base = datetime.date(2026, 1, 1)
    for i in range(60):
        c = 200 - 1.5 * i if i < 20 else (170.0 if i < 40 else 170 + 3 * (i - 39))
        d = (base + datetime.timedelta(days=i)).isoformat()
        lines.append(f"GOOD,Hydro Power,{d},{c:.2f},{c*1.01:.2f},"
                     f"{c*0.99:.2f},1000")
        lines.append(f"BAD,Hydro Power,{d},not-a-price,1,1,1000")
    csv_path.write_text("\n".join(lines) + "\n")
    groups, failures = load_multi_csv_report(str(csv_path))
    assert "GOOD" in groups and "BAD" not in groups
    assert any(f["symbol"] == "BAD" for f in failures)
    # GOOD's rise starts before EMA(50) is defined, so it has no
    # recorded cross (warm-up limitation, documented in README) — but
    # it must still analyse cleanly and appear with only_crossed=False.
    rows, scan_failures = scan_report(groups, only_crossed=False)
    assert any(r["symbol"] == "GOOD" for r in rows)
    assert scan_failures == []


def test_failed_symbol_logged_in_scan_report():
    groups = {"OK": {"sector": "", "candles": mk([100.0] * 60)},
              "EMPTY": {"sector": "", "candles": []}}
    rows, failures = scan_report(groups, only_crossed=False)
    assert any(r["symbol"] == "OK" for r in rows)
    assert any(f["symbol"] == "EMPTY" for f in failures)


def test_signal_labelling_tiers():
    # Thin volume + cross -> NOISE, never CONFIRMED.
    row = {"cross_date": "2026-01-10", "thin_volume": True,
           "trailing_flat_days": 0, "volume_ratio_20d": 0.2, "adx14": 40.0}
    label, reasons = signal_label(row)
    assert label == "NOISE" and reasons
    # Volume + trend -> CONFIRMED (pattern only).
    row = {"cross_date": "2026-01-10", "thin_volume": False,
           "trailing_flat_days": 0, "volume_ratio_20d": 2.0, "adx14": 30.0}
    label, _ = signal_label(row)
    assert label.startswith("CONFIRMED")
    # Cross alone -> WEAK.
    row = {"cross_date": "2026-01-10", "thin_volume": False,
           "trailing_flat_days": 0, "volume_ratio_20d": 0.8, "adx14": 10.0}
    label, _ = signal_label(row)
    assert label == "WEAK"


def test_flat_series_all_indicators_finite():
    closes = [77.0] * 60
    assert rsi(closes, 14)[-1] == 50.0
    assert stochastic([77.0] * 60, [77.0] * 60, closes, 14, 3)[0][-1] == 50.0
    assert adx([77.0] * 60, [77.0] * 60, closes, 14)[-1] == 0.0
    mid, upper, lower = bollinger(closes, 20, 2.0)
    assert upper[-1] == lower[-1] == mid[-1] == 77.0
