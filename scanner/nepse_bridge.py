"""NEPSE user-supplied-CSV bridge (Round 3, R6) — LOADER ONLY.

There is NO live NEPSE feed and NO redistributed real NEPSE price
dataset in this repo, deliberately. See NEPSE_USER_CSV_TERMS.md for
the terms audit that forces this shape:

- shirjankhadka.com.np's own Data Use & Terms (effective 1 Oct 2026)
  permit quoting individual figures with attribution, but forbid
  bulk re-scraping of the site's data files to republish a competing
  feed without emailed bulk-access permission. No such permission is
  on file, so no price series from that site is copied here.
- No documented, free, public NEPSE OHLCV API exists (28 Oct 2026
  research, re-confirmed for this round); NEPSE's internal
  token-protected flow is undocumented access and is NOT wired in.

What this module does: load a CSV *you* supply, in the documented
format, and refuse to run without a named source. The source string
is mandatory — a scan over unsourced prices is an unsourced scan.

Format (multi-symbol, same as ``data.load_multi_csv``):
    symbol,sector,date,close,high,low,volume
one row per symbol per trading day, dates strictly increasing per
symbol. Single-symbol files use ``date,close,high,low,volume`` and
``load_user_csv_single``.

A tiny SYNTHETIC example lives at
``examples/nepse_user_supplied_SYNTHETIC.csv``. Its prices are
invented for format testing only, are labelled SYNTHETIC in the
file itself, and must never be presented as real NEPSE prices.
"""

try:
    from data import Candle, NepseDataError, load_csv, load_multi_csv
except ImportError:  # running as scanner.nepse_bridge package
    from .data import Candle, NepseDataError, load_csv, load_multi_csv

__all__ = ["NepseDataError", "Candle", "load_user_csv",
           "load_user_csv_single", "SYNTHETIC_MARKER"]


SYNTHETIC_MARKER = "SYNTHETIC"


def _require_source(source):
    if not isinstance(source, str) or not source.strip():
        raise NepseDataError(
            "nepse_bridge: a source must be named (e.g. 'NEPSE published "
            "data, session of 2026-10-29, transcribed by hand'). "
            "Unsourced prices are refused, not loaded.")
    return source.strip()


def load_user_csv(path, source):
    """Load a user-supplied multi-symbol NEPSE CSV.

    Returns (groups, source) where groups is the
    ``data.load_multi_csv`` mapping. ``source`` is recorded, never
    validated against the file — the caller asserts it, and it must
    travel with any result the scan produces.
    """
    source = _require_source(source)
    return load_multi_csv(path), source


def load_user_csv_single(path, source):
    """Load a user-supplied single-symbol NEPSE CSV.

    Returns (candles, source). Same source rule as load_user_csv.
    """
    source = _require_source(source)
    return load_csv(path), source
