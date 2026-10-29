"""Tests for the R6 loader-only NEPSE bridge. Run from scanner/:
python3 -m pytest tests/test_nepse_bridge.py -v

Nothing here touches a live feed or a real NEPSE price. The example
CSV is synthetic by construction and labelled as such.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import NepseDataError
from nepse_bridge import (
    SYNTHETIC_MARKER,
    load_user_csv,
    load_user_csv_single,
)

EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "examples")
SYNTHETIC = os.path.join(EXAMPLES, "nepse_user_supplied_SYNTHETIC.csv")
DEMO = os.path.join(EXAMPLES, "demo_prices.csv")


def test_synthetic_example_loads_and_is_labelled():
    assert SYNTHETIC_MARKER in os.path.basename(SYNTHETIC)
    with open(SYNTHETIC, encoding="utf-8") as fh:
        header = fh.readline()
    assert "symbol" in header
    groups, source = load_user_csv(
        SYNTHETIC, "SYNTHETIC example file, invented for format testing")
    assert set(groups) == {"SYNTHETIC-A", "SYNTHETIC-B"}
    assert len(groups["SYNTHETIC-A"]["candles"]) == 5
    assert source.startswith("SYNTHETIC")


def test_source_is_mandatory():
    with pytest.raises(NepseDataError):
        load_user_csv(SYNTHETIC, "")
    with pytest.raises(NepseDataError):
        load_user_csv(SYNTHETIC, "   ")
    with pytest.raises(NepseDataError):
        load_user_csv_single(DEMO, "")


def test_single_symbol_loader_loads_single_format():
    # The AAPL example file is single-symbol format (date, close,
    # high, low, volume) — labelled example data, not NEPSE prices.
    aapl = os.path.join(EXAMPLES, "aapl-daily-closes-2024-2025.csv")
    candles, source = load_user_csv_single(
        aapl, "AAPL example file shipped with the scanner (NASDAQ, "
        "not NEPSE)")
    assert len(candles) == 502
    assert candles[0].date == "2024-01-02"
    assert source.startswith("AAPL example")
