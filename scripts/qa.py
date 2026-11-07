"""Quality-gate entry point (Phase 4) for nepali-capital-market-research.

Stdlib only. Gates, in order (fail fast — stop at the first failure):
  tests        pytest scanner/tests/ -q (113 tests)
  lint         ruff check scanner/ (repo's ruff.toml; mypy is deliberately
               NOT run — scanner/ uses a dual script/package import mode
               that mypy rejects, measured 28 Oct 2026)
  counts       scripts/generate_status.py --root . then
               scripts/check_numbers.py --root . (test counts, case
               studies, datasets vs status.json + READMEs)
  licence      scripts/qa_licence.py (SOURCES licence table + no AGPL content)
  secrets      scripts/qa_secrets.py (tree + git history)
  links        scripts/qa_links.py (internal must resolve; external best-effort)
  fresh-clone  scripts/qa_fresh_clone.py (clone + scanner CLI smoke < 60 s)

Note: this repo has no internal Markdown links (cross-references are
code spans, not links), so the link gate checks the 4 external URLs
best-effort and 0 internal links — that is the honest count, not a
skipped check.

Dev tools come from requirements-dev.txt (pinned pytest/ruff, identical
to CI).

Usage:
  python scripts/qa.py [--only GATE] [--skip GATE,...] [--offline]
                       [--list]
Exit 0 only when every run gate passes. Prints a per-gate PASS/FAIL
summary at the end.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def _tool(name):
    binary = shutil.which(name)
    if binary:
        return [binary]
    return [sys.executable, "-m", name]


def _run(cmd, cwd=ROOT):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          check=False, timeout=900)


def _show(proc):
    out = proc.stdout.strip()
    if out:
        print(out)
    if proc.stderr.strip():
        print(proc.stderr.strip()[-1000:])


def gate_tests(_args):
    proc = _run([sys.executable, "-m", "pytest", "scanner/tests/", "-q"])
    _show(proc)
    return proc.returncode


def gate_lint(_args):
    proc = _run(_tool("ruff") + ["check", "scanner/"])
    _show(proc)
    return proc.returncode


def gate_counts(_args):
    gen = _run([sys.executable, "scripts/generate_status.py", "--root", ".",
                "--repo", "nepali-capital-market-research"])
    if gen.returncode != 0:
        _show(gen)
        return gen.returncode
    proc = _run([sys.executable, "scripts/check_numbers.py", "--root", "."])
    _show(proc)
    return proc.returncode


def _script_gate(name):
    def gate(args):
        cmd = [sys.executable, str(SCRIPTS / name)]
        if name == "qa_links.py" and args.offline:
            cmd.append("--offline")
        proc = _run(cmd)
        _show(proc)
        return proc.returncode
    return gate


GATES = [
    ("tests", gate_tests),
    ("lint", gate_lint),
    ("counts", gate_counts),
    ("licence", _script_gate("qa_licence.py")),
    ("secrets", _script_gate("qa_secrets.py")),
    ("links", _script_gate("qa_links.py")),
    ("fresh-clone", _script_gate("qa_fresh_clone.py")),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default=None, help="run a single gate by name")
    parser.add_argument("--skip", default="", help="comma-separated gates to skip")
    parser.add_argument("--offline", action="store_true",
                        help="link gate: skip external checks")
    parser.add_argument("--list", action="store_true",
                        help="list gate names and exit")
    args = parser.parse_args()
    if args.list:
        for name, _gate in GATES:
            print(name)
        return 0
    skipped = {s.strip() for s in args.skip.split(",") if s.strip()}
    selected = [(n, g) for n, g in GATES
                if (args.only is None or n == args.only) and n not in skipped]
    if args.only and not any(n == args.only for n, _g in GATES):
        print(f"unknown gate: {args.only} (see --list)")
        return 2
    results = []
    for name, gate in selected:
        print(f"\n=== gate: {name} ===")
        try:
            code = gate(args)
        except Exception as exc:  # noqa: BLE001 — a crashing gate is a FAIL
            print(f"gate {name} raised {type(exc).__name__}: {exc}")
            code = 1
        status = "PASS" if code == 0 else "FAIL"
        print(f"[{status}] {name}")
        results.append((name, code))
        if code != 0:
            break
    print("\n=== qa summary ===")
    for name, code in results:
        print(f"  {'PASS' if code == 0 else 'FAIL'}  {name}")
    for name, _g in GATES:
        if name not in {r[0] for r in results}:
            print(f"  SKIP  {name} (stopped at first failure)")
    failed = [n for n, c in results if c != 0]
    if failed:
        print(f"qa FAILED at gate: {failed[0]}")
        return 1
    print("qa PASSED: all gates green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
