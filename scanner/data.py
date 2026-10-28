"""Data loading for the NEPSE scanner. Exchange: NEPSE, always.

Two honest inputs, and nothing else:
1. CSV files you supply yourself (from NEPSE's own published data, your
   broker's export, or any source you can name on the same page).
2. A live fetcher that DOES NOT EXIST YET — see NepseLiveFetcher below.

The fetcher is deliberately a stub. Research on 28 Oct 2026 found NO
documented, free, public NEPSE OHLCV API that this scanner may call:
- NEPSE's own site (nepalstock.com.np) serves its pages through internal,
  token-protected endpoints; third-party libraries reverse-engineer that
  token flow. That is undocumented access, not a public API — not wired in.
- The NEPSE-licensed Market Data Provider (MDP, data.smartwealthpro.com)
  is a paid, licensed feed — not free.
- Nepalytix advertises an "open finance data hub" but publishes no public
  API documentation found on 28 Oct 2026; its bulk/API access sits on an
  Enterprise tier. Claim = TO VERIFY, not a usable endpoint.
- Nepse Alpha publishes no public API (third-party listing: "API: No").
- Chukul is a login/phone-registered app with paid packages; no public API.

Until a documented free endpoint is verified, any live price must come
from a CSV you provide. The stub raises an error naming exactly what is
missing instead of returning a stale or invented price. Never present a
stale price as fresh, and never invent a price to fill a gap.
"""

import csv
from dataclasses import dataclass


class NepseDataError(Exception):
    """Raised for any data problem: missing file, bad row, missing endpoint."""


@dataclass
class Candle:
    date: str       # ISO date, YYYY-MM-DD
    close: float
    high: float
    low: float
    volume: float


def _parse_float(row, field, where):
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError):
        raise NepseDataError(f"{where}: bad or missing {field}")
    if value != value or value in (float("inf"), float("-inf")):
        raise NepseDataError(f"{where}: non-finite {field}")
    return value


def load_csv(path):
    """Load one symbol's candles from a CSV with columns:
    date, close, high, low, volume. Rows must be in date order, strictly
    increasing, unique dates, close > 0. Bad rows raise NepseDataError —
    they are never silently skipped, because a skipped row would silently
    shift every moving average after it.
    """
    candles = []
    try:
        fh = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise NepseDataError(f"cannot open {path}: {exc}") from exc
    with fh:
        reader = csv.DictReader(fh)
        required = {"date", "close", "high", "low", "volume"}
        if reader.fieldnames is None or not required.issubset(
                {f.strip() for f in reader.fieldnames}):
            raise NepseDataError(
                f"{path}: expected columns date, close, high, low, volume")
        for n, raw in enumerate(reader, start=2):
            row = {(k.strip() if k else k): (v.strip() if isinstance(v, str) else v)
                   for k, v in raw.items()}
            if not row.get("date"):
                raise NepseDataError(f"{path} line {n}: missing date")
            candle = Candle(
                date=row["date"],
                close=_parse_float(row, "close", f"{path} line {n}"),
                high=_parse_float(row, "high", f"{path} line {n}"),
                low=_parse_float(row, "low", f"{path} line {n}"),
                volume=_parse_float(row, "volume", f"{path} line {n}"),
            )
            if candle.close <= 0:
                raise NepseDataError(f"{path} line {n}: close must be > 0")
            if candle.high < candle.low:
                raise NepseDataError(f"{path} line {n}: high < low")
            candles.append(candle)
    if not candles:
        raise NepseDataError(f"{path}: no data rows")
    dates = [c.date for c in candles]
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise NepseDataError(
            f"{path}: dates must be strictly increasing and unique")
    return candles


def load_multi_csv(path):
    """Load many symbols from one CSV with columns:
    symbol, sector, date, close, high, low, volume.
    Returns {symbol: {"sector": str, "candles": [Candle, ...]}}.
    Each symbol's rows must be in date order; symbols may interleave.
    """
    groups = {}
    try:
        fh = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise NepseDataError(f"cannot open {path}: {exc}") from exc
    with fh:
        reader = csv.DictReader(fh)
        required = {"symbol", "sector", "date", "close", "high", "low", "volume"}
        if reader.fieldnames is None or not required.issubset(
                {f.strip() for f in reader.fieldnames}):
            raise NepseDataError(
                f"{path}: expected columns symbol, sector, date, close, "
                "high, low, volume")
        for n, raw in enumerate(reader, start=2):
            row = {(k.strip() if k else k): (v.strip() if isinstance(v, str) else v)
                   for k, v in raw.items()}
            symbol = row.get("symbol")
            if not symbol or not row.get("date"):
                raise NepseDataError(f"{path} line {n}: missing symbol or date")
            candle = Candle(
                date=row["date"],
                close=_parse_float(row, "close", f"{path} line {n}"),
                high=_parse_float(row, "high", f"{path} line {n}"),
                low=_parse_float(row, "low", f"{path} line {n}"),
                volume=_parse_float(row, "volume", f"{path} line {n}"),
            )
            if candle.close <= 0:
                raise NepseDataError(f"{path} line {n}: close must be > 0")
            entry = groups.setdefault(symbol, {"sector": row.get("sector", ""),
                                               "candles": []})
            if entry["sector"] == "" and row.get("sector"):
                entry["sector"] = row["sector"]
            entry["candles"].append(candle)
    for symbol, entry in groups.items():
        dates = [c.date for c in entry["candles"]]
        if dates != sorted(dates) or len(set(dates)) != len(dates):
            raise NepseDataError(
                f"{path}: {symbol} dates must be strictly increasing and unique")
    if not groups:
        raise NepseDataError(f"{path}: no data rows")
    return groups


def load_multi_csv_report(path):
    """Lenient twin of load_multi_csv() for scans: returns
    (groups, failures). A symbol with ANY bad row is dropped as a whole
    — a half-loaded symbol would silently shift its moving averages —
    and the reason is recorded in failures. Other symbols are unaffected.
    A file-level problem (missing file, wrong columns, zero usable rows)
    still raises NepseDataError, because then there is no scan at all.
    """
    try:
        raw_groups = load_multi_csv(path)
        return raw_groups, []
    except NepseDataError:
        pass  # fall through to per-symbol isolation below
    # Re-parse row by row, isolating failures per symbol.
    groups = {}
    failures = {}
    try:
        fh = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise NepseDataError(f"cannot open {path}: {exc}") from exc
    with fh:
        reader = csv.DictReader(fh)
        required = {"symbol", "sector", "date", "close", "high", "low",
                    "volume"}
        if reader.fieldnames is None or not required.issubset(
                {f.strip() for f in reader.fieldnames}):
            raise NepseDataError(
                f"{path}: expected columns symbol, sector, date, close, "
                "high, low, volume")
        rows_by_symbol = {}
        for n, raw in enumerate(reader, start=2):
            row = {(k.strip() if k else k):
                   (v.strip() if isinstance(v, str) else v)
                   for k, v in raw.items()}
            symbol = row.get("symbol") or f"(missing symbol, line {n})"
            try:
                if not row.get("symbol") or not row.get("date"):
                    raise NepseDataError(f"line {n}: missing symbol/date")
                candle = Candle(
                    date=row["date"],
                    close=_parse_float(row, "close", f"line {n}"),
                    high=_parse_float(row, "high", f"line {n}"),
                    low=_parse_float(row, "low", f"line {n}"),
                    volume=_parse_float(row, "volume", f"line {n}"),
                )
                if candle.close <= 0:
                    raise NepseDataError(f"line {n}: close must be > 0")
                if candle.high < candle.low:
                    raise NepseDataError(f"line {n}: high < low")
            except NepseDataError as exc:
                failures[symbol] = str(exc)
                continue
            rows_by_symbol.setdefault(symbol, {"sector": row.get("sector", ""),
                                               "candles": []})
            if rows_by_symbol[symbol]["sector"] == "" and row.get("sector"):
                rows_by_symbol[symbol]["sector"] = row["sector"]
            rows_by_symbol[symbol]["candles"].append(candle)
    for symbol, entry in rows_by_symbol.items():
        dates = [c.date for c in entry["candles"]]
        if dates != sorted(dates) or len(set(dates)) != len(dates):
            failures[symbol] = "dates not strictly increasing/unique"
            continue
        if symbol in failures:
            continue  # a bad row anywhere drops the whole symbol
        groups[symbol] = entry
    for symbol in failures:
        groups.pop(symbol, None)
    return groups, [{"symbol": s, "reason": r}
                    for s, r in sorted(failures.items())]


class NepseLiveFetcher:
    """Placeholder for a live NEPSE data source. NOT implemented.

    Implementing it requires, in this order:
    1. A documented, free, public NEPSE OHLCV endpoint (URL + terms),
       verified by reading its own documentation — not by guessing a URL
       or copying another site's internal API calls.
    2. Confirmation that its terms allow this use.
    3. A freshness rule: any quote older than the last trading session
       must be labelled STALE, never returned as fresh.

    Until then, fetch() raises NepseDataError. Use load_csv /
    load_multi_csv with data you sourced yourself, and name the source.
    """

    def fetch(self, symbol):
        raise NepseDataError(
            "No live NEPSE data source is wired in: no documented, free, "
            "public NEPSE OHLCV API was verified on 28 Oct 2026 "
            "(see research/indicator-source-teardown-2026-10-28.md). "
            f"Provide {symbol} as a CSV instead, and name its source.")
