"""Integrity tests for the Bottlers Nepal (Terai) case-study dataset.

The dataset moved here from nepal-market-research on 7 Nov 2026
(content merge approved by the owner). These tests guard the move:
they check the CSV parses, carries the verified FY 2081/82 figures
from case-studies/bnt/data/bnt-verified-figures.md, and keeps the
"inputs + skeleton, NOT a valuation" labelling intact.

Stdlib only (csv, pathlib). No valuation is computed here.
"""

import csv
from pathlib import Path

CASE_STUDY = Path(__file__).resolve().parents[2] / "case-studies" / "bnt"
CSV_PATH = CASE_STUDY / "data" / "bnt-fy2081-82.csv"

EXPECTED_COLUMNS = [
    "item",
    "fy_2081_82_npr",
    "fy_2080_81_npr",
    "unit",
    "source",
    "notes",
]

# Spot values from case-studies/bnt/data/bnt-verified-figures.md
# (39th annual report, FY 2081/82, via the 2026-10-16 ledger).
EXPECTED_VALUES = {
    "revenue_from_operations": 7527297984,
    "profit_from_operations_ebit": 407359078,
    "operating_cash_flow": 1497212819,
    "borrowings_total": 2344466783,
    "borrowings_non_current": 0,
    "shares_outstanding": 1210000,
}


def _rows():
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == EXPECTED_COLUMNS
        return list(reader)


def test_csv_parses_with_expected_columns_and_row_count():
    rows = _rows()
    assert len(rows) == 18


def test_key_figures_match_verified_figures_file():
    by_item = {r["item"]: r for r in _rows()}
    for item, value in EXPECTED_VALUES.items():
        assert item in by_item, f"missing row: {item}"
        assert int(by_item[item]["fy_2081_82_npr"]) == value


def test_explicit_nil_is_zero_not_missing():
    by_item = {r["item"]: r for r in _rows()}
    row = by_item["borrowings_non_current"]
    assert row["fy_2081_82_npr"].strip() == "0"
    assert "Nil" in row["notes"]


def test_every_row_names_a_source_and_a_value():
    for row in _rows():
        assert row["item"].strip()
        assert row["unit"].strip()
        assert row["source"].strip()
        assert row["fy_2081_82_npr"].strip(), f"no FY 2081/82 value: {row['item']}"


def test_study_still_labelled_inputs_plus_skeleton_not_a_valuation():
    readme = (CASE_STUDY / "README.md").read_text(encoding="utf-8")
    assert "Inputs + skeleton" in readme
    assert "NOT a valuation" in readme
