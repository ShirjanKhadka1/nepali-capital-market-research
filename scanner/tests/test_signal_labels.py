"""Signal-vs-noise labels, pinned across edge cases. Research only.

The labels are the scanner's most-read output, so this file proves they
do not drift at the edges: low volume, identical closes, missing/bad
data via the lenient loader, and the tier boundaries. Every label is
pattern-only — none is ever a buy/sell label, and that is asserted
directly, not assumed. No scanner behaviour is changed by this file.

Follows the existing test files' layout (sys.path insert, synthetic
series only, no live NEPSE data, exchange NEPSE where relevant).
"""

import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import Candle, NepseDataError, load_multi_csv, load_multi_csv_report
from scanner import analyse, scan_report, signal_label

ALLOWED_LABELS = {"NO SIGNAL", "NOISE", "WEAK", "WATCH",
                  "CONFIRMED (pattern only)"}


def mk(closes, volumes=None, start="2026-01-01"):
    base = datetime.date.fromisoformat(start)
    out = []
    for i, c in enumerate(closes):
        d = (base + datetime.timedelta(days=i)).isoformat()
        out.append(Candle(date=d, close=c, high=c * 1.01, low=c * 0.99,
                          volume=(volumes[i] if volumes else 1000.0)))
    return out


def crossed_closes():
    """100 bars: fall 50, then rise 50. The cross lands after the
    EMA(50) warm-up, so it is recorded (default 20/50 periods)."""
    return ([200 - 1.0 * i for i in range(50)]
            + [151 + 1.5 * i for i in range(50)])


def assert_pattern_only(label):
    assert label in ALLOWED_LABELS
    lowered = label.lower()
    assert "buy" not in lowered and "sell" not in lowered
    assert "hold" not in lowered and "target" not in lowered


# --- End-to-end: the same crossed series, four different labels -----------

def test_crossed_series_default_volume_is_watch():
    row = analyse(mk(crossed_closes()))
    assert row["cross_date"] is not None
    assert row["volume_ratio_20d"] == pytest.approx(1.0)
    assert row["signal_label"] == "WATCH"
    assert_pattern_only(row["signal_label"])
    assert row["signal_reasons"]


def test_crossed_series_low_volume_is_noise_not_confirmed():
    closes = crossed_closes()
    volumes = [1000.0] * 99 + [10.0]  # last-day volume collapses
    row = analyse(mk(closes, volumes))
    assert row["cross_date"] is not None
    assert row["thin_volume"] is True
    assert row["volume_ratio_20d"] == pytest.approx(0.01)
    assert row["signal_label"] == "NOISE"
    assert any("thin trading" in r for r in row["signal_reasons"])


def test_crossed_series_high_volume_and_trend_is_confirmed_pattern_only():
    closes = crossed_closes()
    volumes = [1000.0] * 99 + [3000.0]
    row = analyse(mk(closes, volumes))
    assert row["cross_date"] is not None
    assert row["volume_ratio_20d"] == pytest.approx(3.0)
    assert row["adx14"] is not None and row["adx14"] >= 25
    assert row["signal_label"] == "CONFIRMED (pattern only)"
    assert_pattern_only(row["signal_label"])
    # "Confirmed" still describes a past-price pattern, never a trade.
    assert "pattern only" in row["signal_label"]


def test_crossed_series_identical_close_tail_is_noise():
    # Rise, then 8 identical closes: the trailing run is 9 (the last
    # rising bar also closed at the tail price), past the >= 5 rule.
    closes = crossed_closes() + [crossed_closes()[-1]] * 8
    row = analyse(mk(closes))
    assert row["cross_date"] is not None
    assert row["trailing_flat_days"] == 9
    assert row["signal_label"] == "NOISE"
    assert any("identical" in r for r in row["signal_reasons"])


def test_fully_identical_closes_is_no_signal():
    row = analyse(mk([77.0] * 60))
    assert row["cross_date"] is None
    assert row["trailing_flat_days"] == 60
    assert row["signal_label"] == "NO SIGNAL"


# --- Tier boundaries, unit level -------------------------------------------

@pytest.mark.parametrize("vol,adx,expected", [
    (1.5, 25.0, "CONFIRMED (pattern only)"),  # both thresholds inclusive
    (1.49, 30.0, "WATCH"),                    # volume just below 1.5
    (2.0, 24.9, "WATCH"),                     # ADX just below 25
    (1.0, 10.0, "WATCH"),                     # volume floor for WATCH
    (0.99, 10.0, "WEAK"),                     # volume below WATCH floor
    (None, None, "WEAK"),                     # no confirmation available
])
def test_label_tier_boundaries(vol, adx, expected):
    row = {"cross_date": "2026-01-10", "thin_volume": False,
           "trailing_flat_days": 0, "volume_ratio_20d": vol, "adx14": adx}
    label, reasons = signal_label(row)
    assert label == expected
    assert reasons
    assert_pattern_only(label)


def test_flat_tail_boundary_five_is_noise_four_is_not():
    base = {"cross_date": "2026-01-10", "thin_volume": False,
            "volume_ratio_20d": 2.0, "adx14": 30.0}
    label, _ = signal_label({**base, "trailing_flat_days": 5})
    assert label == "NOISE"
    label, _ = signal_label({**base, "trailing_flat_days": 4})
    assert label == "CONFIRMED (pattern only)"


def test_thin_volume_beats_confirmed_level_volume_and_trend():
    row = {"cross_date": "2026-01-10", "thin_volume": True,
           "trailing_flat_days": 0, "volume_ratio_20d": 2.0, "adx14": 40.0}
    label, _ = signal_label(row)
    assert label == "NOISE"


def test_no_cross_beats_any_volume_and_trend():
    row = {"cross_date": None, "thin_volume": False,
           "trailing_flat_days": 0, "volume_ratio_20d": 3.0, "adx14": 40.0}
    label, reasons = signal_label(row)
    assert label == "NO SIGNAL"
    assert reasons


def test_no_label_is_ever_a_buy_sell_or_hold_label():
    rows = [
        {"cross_date": None, "thin_volume": False, "trailing_flat_days": 0,
         "volume_ratio_20d": 3.0, "adx14": 40.0},
        {"cross_date": "2026-01-10", "thin_volume": True,
         "trailing_flat_days": 0, "volume_ratio_20d": 0.2, "adx14": 40.0},
        {"cross_date": "2026-01-10", "thin_volume": False,
         "trailing_flat_days": 9, "volume_ratio_20d": 2.0, "adx14": 40.0},
        {"cross_date": "2026-01-10", "thin_volume": False,
         "trailing_flat_days": 0, "volume_ratio_20d": 0.8, "adx14": 10.0},
        {"cross_date": "2026-01-10", "thin_volume": False,
         "trailing_flat_days": 0, "volume_ratio_20d": 1.2, "adx14": 10.0},
        {"cross_date": "2026-01-10", "thin_volume": False,
         "trailing_flat_days": 0, "volume_ratio_20d": 2.0, "adx14": 30.0},
    ]
    labels = {signal_label(r)[0] for r in rows}
    assert labels == {"NO SIGNAL", "NOISE", "WEAK", "WATCH",
                      "CONFIRMED (pattern only)"}
    for label in labels:
        assert_pattern_only(label)


# --- Missing / bad data through the lenient loader --------------------------

def test_lenient_loader_drops_bad_symbol_keeps_good_label(tmp_path):
    # GOOD: the crossed series above, as CSV rows. BAD: one bad close.
    lines = ["symbol,sector,date,close,high,low,volume"]
    base = datetime.date(2026, 1, 1)
    for i, c in enumerate(crossed_closes()):
        d = (base + datetime.timedelta(days=i)).isoformat()
        lines.append(f"GOOD,Hydro Power,{d},{c:.2f},{c * 1.01:.2f},"
                     f"{c * 0.99:.2f},1000")
        lines.append(f"BAD,Hydro Power,{d},not-a-price,1,1,1000")
    csv_path = tmp_path / "mixed.csv"
    csv_path.write_text("\n".join(lines) + "\n")
    # Strict loader: the whole file fails on the bad row.
    with pytest.raises(NepseDataError):
        load_multi_csv(str(csv_path))
    # Lenient loader: BAD is dropped with a reason, GOOD survives whole.
    groups, failures = load_multi_csv_report(str(csv_path))
    assert "GOOD" in groups and "BAD" not in groups
    assert any(f["symbol"] == "BAD" for f in failures)
    rows, scan_failures = scan_report(groups)
    assert len(rows) == 1 and rows[0]["symbol"] == "GOOD"
    assert rows[0]["signal_label"] == "WATCH"
    assert_pattern_only(rows[0]["signal_label"])
    assert scan_failures == []


def test_empty_symbol_is_a_logged_failure_not_a_poisoned_scan():
    groups = {"OK": {"sector": "", "candles": mk(crossed_closes())},
              "EMPTY": {"sector": "", "candles": []}}
    rows, failures = scan_report(groups)
    assert any(r["symbol"] == "OK" for r in rows)
    assert any(f["symbol"] == "EMPTY" for f in failures)
    for row in rows:
        assert_pattern_only(row["signal_label"])
