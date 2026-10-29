"""Tests for the NEPSE scanner. Run from scanner/: python3 -m pytest tests/ -v

Known-series expectations were computed by hand / from the definitions in
indicators.py's docstring, not by copying another library's output:
- SMA: plain mean.
- RSI on a steadily rising series must be 100 (no down days).
- RSI on a flat series is 50 by convention (no gain, no loss).
- Bollinger on a flat series: upper == lower == price (sd = 0).
- Stochastic on a flat series: 50 by convention (range = 0).
"""

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import Candle, NepseDataError, NepseLiveFetcher, load_csv, load_multi_csv
from indicators import (
    adx,
    atr,
    bollinger,
    ema,
    find_crosses,
    latest_cross,
    macd,
    rsi,
    since_cross_pct,
    sma,
    stochastic,
    volume_ratio,
)
from scanner import analyse, scan


def candles_from_closes(closes, start_day=1):
    out = []
    for i, c in enumerate(closes):
        out.append(Candle(date=f"2026-01-{start_day + i:02d}", close=c,
                          high=c * 1.01, low=c * 0.99, volume=1000.0))
    return out


# --- SMA / EMA -----------------------------------------------------------

def test_sma_known_values():
    assert sma([1, 2, 3, 4, 5], 3) == [None, None, 2.0, 3.0, 4.0]


def test_sma_too_few_points_all_none():
    assert sma([1, 2], 5) == [None, None]


def test_ema_seed_is_sma():
    result = ema([10, 20, 30], 3)
    assert result[2] == pytest.approx(20.0)


def test_ema_rejects_non_numeric_and_nan():
    with pytest.raises(ValueError):
        ema([1, "x", 3], 2)
    with pytest.raises(ValueError):
        ema([1, float("nan"), 3], 2)


# --- Crossovers ----------------------------------------------------------

def test_bullish_cross_detected_and_since_cross_pct():
    # Fast EMA(2) starts below slow EMA(3) after a fall, then rises above.
    closes = [100, 90, 80, 70, 80, 90, 100, 110]
    fast = ema(closes, 2)
    slow = ema(closes, 3)
    cross = latest_cross(fast, slow, "bullish")
    assert cross is not None
    assert closes[cross["index"]] > 0
    pct = since_cross_pct(closes, cross["index"])
    assert pct == pytest.approx((closes[-1] - closes[cross["index"]])
                                / closes[cross["index"]])


def test_no_cross_on_flat_series():
    closes = [50.0] * 30
    assert find_crosses(ema(closes, 5), ema(closes, 10)) == []


def test_bearish_cross_detected():
    closes = [70, 80, 90, 100, 90, 80, 70, 60]
    cross = latest_cross(ema(closes, 2), ema(closes, 3), "bearish")
    assert cross is not None and cross["direction"] == "bearish"


def test_since_cross_pct_out_of_range_is_none():
    assert since_cross_pct([100, 110], 5) is None
    assert since_cross_pct([100, 110], -1) is None


# --- RSI / MACD / Bollinger / ATR / Stochastic / ADX ---------------------

def test_rsi_rising_series_is_100():
    result = rsi([100 + i for i in range(20)], 14)
    assert result[-1] == pytest.approx(100.0)


def test_rsi_flat_series_is_50():
    result = rsi([50.0] * 20, 14)
    assert result[-1] == pytest.approx(50.0)


def test_rsi_too_few_points_is_none():
    assert rsi([100, 101, 102], 14) == [None, None, None]


def test_macd_rising_series_positive():
    line, sig, _ = macd([100 + i for i in range(60)])
    assert line[-1] > 0 and sig[-1] is not None and sig[-1] > 0


def test_bollinger_flat_series_bands_equal_price():
    mid, upper, lower = bollinger([42.0] * 30, 20, 2.0)
    assert mid[-1] == pytest.approx(42.0)
    assert upper[-1] == pytest.approx(42.0)
    assert lower[-1] == pytest.approx(42.0)


def test_bollinger_known_values():
    closes = list(range(1, 21))  # 1..20, mean 10.5, pop sd ~5.766
    mid, upper, lower = bollinger(closes, 20, 2.0)
    assert mid[-1] == pytest.approx(10.5)
    sd = math.sqrt(sum((x - 10.5) ** 2 for x in closes) / 20)
    assert upper[-1] == pytest.approx(10.5 + 2 * sd)
    assert lower[-1] == pytest.approx(10.5 - 2 * sd)


def test_atr_constant_range():
    highs = [110.0] * 20
    lows = [100.0] * 20
    closes = [105.0] * 20
    result = atr(highs, lows, closes, 14)
    assert result[-1] == pytest.approx(10.0)


def test_stochastic_flat_series_is_50():
    k, d = stochastic([50.0] * 20, [50.0] * 20, [50.0] * 20, 14, 3)
    assert k[-1] == pytest.approx(50.0)
    assert d[-1] == pytest.approx(50.0)


def test_stochastic_at_top_of_range_is_100():
    highs = [100.0] * 20
    lows = [90.0] * 20
    closes = [95.0] * 19 + [100.0]
    k, _ = stochastic(highs, lows, closes, 14, 3)
    assert k[-1] == pytest.approx(100.0)


def test_adx_strong_trend_high_flat_low():
    closes = [100 + i for i in range(60)]
    highs = [c + 1 for c in closes]
    lows = [c - 1 for c in closes]
    result = adx(highs, lows, closes, 14)
    assert result[-1] is not None and result[-1] > 25


def test_adx_flat_series_is_zero():
    result = adx([50.0] * 60, [50.0] * 60, [50.0] * 60, 14)
    assert result[-1] == pytest.approx(0.0)


def test_adx_too_few_points_all_none():
    result = adx([50.0] * 20, [50.0] * 20, [50.0] * 20, 14)
    assert all(v is None for v in result)


def test_volume_ratio_known_value():
    vols = [100.0] * 20 + [300.0]
    assert volume_ratio(vols, 20) == pytest.approx(3.0)


def test_volume_ratio_too_few_is_none():
    assert volume_ratio([100.0] * 10, 20) is None


# --- Data loading / fetcher stub -----------------------------------------

def test_load_csv_rejects_bad_row(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("date,close,high,low,volume\n2026-01-01,abc,1,1,1\n")
    with pytest.raises(NepseDataError):
        load_csv(str(bad))


def test_load_csv_rejects_duplicate_date(tmp_path):
    dup = tmp_path / "dup.csv"
    dup.write_text("date,close,high,low,volume\n2026-01-01,100,101,99,10\n"
                   "2026-01-01,101,102,100,10\n")
    with pytest.raises(NepseDataError):
        load_csv(str(dup))


def test_load_csv_rejects_missing_file():
    with pytest.raises(NepseDataError):
        load_csv("/nonexistent/nope.csv")


def test_live_fetcher_raises_and_names_what_is_missing():
    with pytest.raises(NepseDataError, match="No live NEPSE data source"):
        NepseLiveFetcher().fetch("NABIL")


def test_multi_csv_demo_file_loads():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    groups = load_multi_csv(os.path.join(here, "examples", "demo_prices.csv"))
    assert "DEMO" in groups and len(groups["DEMO"]["candles"]) == 100


# --- Scanner end-to-end ---------------------------------------------------

def test_scan_demo_cross_present_and_values_consistent():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    groups = load_multi_csv(os.path.join(here, "examples", "demo_prices.csv"))
    rows = scan(groups)
    assert len(rows) == 1
    row = rows[0]
    assert row["symbol"] == "DEMO"
    assert row["cross_date"] == "2026-08-06"
    assert row["ltp"] == pytest.approx(290.0)
    assert row["fast"] > row["slow"]
    assert row["since_cross_pct"] == pytest.approx((290.0 - 191.0) / 191.0)


def test_analyse_short_series_indicators_none_not_invented():
    row = analyse(candles_from_closes([100, 101, 102]))
    assert row["rsi14"] is None
    assert row["adx14"] is None
    assert row["bollinger_upper"] is None
    assert row["cross_date"] is None


def test_scan_only_crossed_false_includes_uncrossed():
    groups = {"FLAT": {"sector": "Hydro Power",
                       "candles": candles_from_closes([50.0] * 60)}}
    assert scan(groups) == []
    assert len(scan(groups, only_crossed=False)) == 1
