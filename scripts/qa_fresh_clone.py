"""Fresh-clone install test (Phase 4 quality gate): a clean clone must
run the scanner smoke command fast.

Stdlib only. Clones the repo to a fresh temp dir (from --url, default
the local repo path, so the check works offline) and runs
``python scanner/cli.py --csv scanner/examples/demo_prices.csv``
there with a timer. Fails if the command exits non-zero or takes 60
seconds or more.

Usage: python3 scripts/qa_fresh_clone.py [--root REPO_ROOT]
       [--url URL_OR_PATH] [--timeout SECONDS]
Exit 0 only when the fresh clone runs the smoke command inside the
time budget.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

COMMAND = [sys.executable, "scanner/cli.py", "--csv",
           "scanner/examples/demo_prices.csv"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",
                        default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--url", default=None,
                        help="clone source (default: the local repo path)")
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()
    root = Path(args.root)
    src = args.url or str(root)
    tmp = Path(tempfile.mkdtemp(prefix="qa-fresh-clone-"))
    try:
        clone = subprocess.run(
            ["git", "clone", "--quiet", src, str(tmp / "repo")],
            capture_output=True, text=True, check=False, timeout=120)
        if clone.returncode != 0:
            print(f"FAIL: git clone failed: {clone.stderr.strip()[-500:]}")
            return 1
        start = time.monotonic()
        try:
            run = subprocess.run(
                COMMAND, cwd=tmp / "repo", capture_output=True, text=True,
                check=False, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(f"FAIL: fresh-clone smoke exceeded {args.timeout:.0f}s")
            return 1
        elapsed = time.monotonic() - start
        if run.returncode != 0:
            print(f"FAIL: fresh-clone smoke exited {run.returncode}:")
            print((run.stdout + run.stderr)[-2000:])
            return 1
        if elapsed >= args.timeout:
            print(f"FAIL: fresh-clone smoke took {elapsed:.1f}s "
                  f"(budget {args.timeout:.0f}s)")
            return 1
        print(f"PASS: fresh-clone smoke ran in {elapsed:.1f}s "
              f"(budget {args.timeout:.0f}s)")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
