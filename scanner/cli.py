"""CLI: run a NEPSE EMA/SMA crossover scan over a multi-symbol CSV.

Usage:
    python -m scanner.cli --csv examples/demo_prices.csv
    python -m scanner.cli --csv my_prices.csv --fast 10 --slow 30 --all
    python -m scanner.cli --csv my_prices.csv --detail DEMO

Columns printed match the screenshot's Crossover Scanner:
Symbol | Sector | LTP | Fast | Slow | Since cross | Cross date.
"Since cross" is (LTP - close on cross date) / close on cross date.

Research only. Not investment advice, never a buy/sell recommendation.
The CSV's source must be named wherever results are shared; a scan over
unsourced prices is an unsourced scan.
"""

import argparse
import sys

try:
    from data import NepseDataError, load_multi_csv, load_multi_csv_report
    from scanner import scan, scan_report
except ImportError:  # running as scanner.cli package
    from .data import (NepseDataError, load_multi_csv,
                       load_multi_csv_report)
    from .scanner import scan, scan_report


def _fmt(value, ndigits=2):
    return "n/a" if value is None else f"{value:.{ndigits}f}"


def _fmt_pct(value):
    if value is None:
        return "n/a"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True,
                        help="multi-symbol CSV: symbol,sector,date,close,"
                             "high,low,volume")
    parser.add_argument("--fast", type=int, default=20,
                        help="fast EMA period (default 20)")
    parser.add_argument("--slow", type=int, default=50,
                        help="slow EMA period (default 50)")
    parser.add_argument("--all", action="store_true",
                        help="show every symbol, not just crossed ones")
    parser.add_argument("--detail", metavar="SYMBOL",
                        help="also print the full indicator snapshot for SYMBOL")
    args = parser.parse_args(argv)
    # Lenient load: one bad symbol is reported and skipped, never fatal
    # to the whole scan. Strict load_multi_csv() is still available for
    # callers that want a hard failure on any bad row.
    groups, load_failures = load_multi_csv_report(args.csv)
    if not groups and load_failures:
        for f in load_failures:
            print(f"FAILED: {f['symbol']}: {f['reason']}", file=sys.stderr)
        print("error: no usable symbols in CSV", file=sys.stderr)
        return 2
    rows, scan_failures = scan_report(groups, args.fast, args.slow,
                                      only_crossed=not args.all)
    print("NEPSE Crossover Scanner — research only, not investment advice")
    print(f"Exchange: NEPSE | Fast EMA({args.fast}) / Slow EMA({args.slow}) "
          f"| Symbols scanned: {len(groups)} | Crossed: {len(rows)}")
    for f in load_failures + scan_failures:
        print(f"FAILED (skipped, reason logged): {f['symbol']}: "
              f"{f['reason']}")
    print(f"{'Symbol':<8}{'Sector':<14}{'LTP':>10}{'Fast':>10}{'Slow':>10}"
          f"{'Since cross':>13}{'Cross date':>13}")
    for r in rows:
        print(f"{r['symbol']:<8}{r['sector']:<14}{_fmt(r['ltp']):>10}"
              f"{_fmt(r['fast']):>10}{_fmt(r['slow']):>10}"
              f"{_fmt_pct(r['since_cross_pct']):>13}"
              f"{r['cross_date'] or 'n/a':>13}")
    if args.detail:
        detail = next((r for r in scan(groups, args.fast, args.slow,
                                       only_crossed=False)
                       if r["symbol"] == args.detail), None)
        if detail is None:
            print(f"error: symbol {args.detail} not in CSV", file=sys.stderr)
            return 2
        print(f"\nDetail — {args.detail} (NEPSE), last date "
              f"{detail['last_date']}:")
        for key in ("ltp", "fast", "slow", "sma20", "rsi14", "macd",
                    "macd_signal", "bollinger_upper", "bollinger_lower",
                    "atr14", "stoch_k", "stoch_d", "adx14",
                    "volume_ratio_20d"):
            print(f"  {key}: {_fmt(detail[key])}")
        print(f"  cross_date: {detail['cross_date'] or 'n/a'}")
        print(f"  days_since_cross: {detail['days_since_cross']}")
        print(f"  since_cross_pct: {_fmt_pct(detail['since_cross_pct'])}")
        print(f"  thin_volume (<0.5x 20d avg): {detail['thin_volume']}")
        print(f"  trailing_flat_days: {detail['trailing_flat_days']}")
        print(f"  last_day_move_pct: {_fmt_pct(detail['last_day_move_pct'])}")
        print(f"  signal_label: {detail['signal_label']}")
        for reason in detail['signal_reasons']:
            print(f"    - {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
