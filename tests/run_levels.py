"""Checks every level with plain CPython (same Python version as Pyodide):
- the reference solution passes its checker
- the untouched starter code fails, with a message
- meta.json has everything the website needs
Run: python3 tests/run_levels.py [day numbers...]
"""
import json
import signal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "python"))

from factory.checker import run_check  # noqa: E402

LEVELS = ROOT / "src" / "levels"
META_KEYS = {"day", "title", "topic", "floor", "briefing", "hints", "machine", "bonus"}
TIMEOUT = 10


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def check(code, check_src):
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(TIMEOUT)
    try:
        return json.loads(run_check(code, check_src))
    finally:
        signal.alarm(0)


def main(days):
    failures = 0
    dirs = sorted(LEVELS.glob("day*"))
    if days:
        dirs = [d for d in dirs if int(d.name[3:]) in days]
    for d in dirs:
        problems = []
        meta = json.loads((d / "meta.json").read_text())
        missing = META_KEYS - meta.keys()
        if missing:
            problems.append(f"meta.json missing {sorted(missing)}")
        if len(meta.get("hints", [])) != 3:
            problems.append("needs exactly 3 hints")
        if not (d / "lesson.md").read_text().strip():
            problems.append("empty lesson.md")
        check_src = (d / "check.py").read_text()
        try:
            sol = check((d / "solution.py").read_text(), check_src)
            if not sol["passed"]:
                problems.append(f"solution FAILED: {sol['message']}")
        except Timeout:
            problems.append("solution timed out")
        try:
            start = check((d / "starter.py").read_text(), check_src)
            if start["passed"]:
                problems.append("starter code PASSES (it should fail)")
            elif not start["message"]:
                problems.append("starter fails without a message")
        except Timeout:
            problems.append("starter timed out (infinite loop?)")
        status = "ok " if not problems else "FAIL"
        print(f"{status} {d.name}: {meta.get('title', '?')}")
        for p in problems:
            print(f"     - {p}")
        failures += bool(problems)
    print(f"\n{len(dirs) - failures}/{len(dirs)} levels ok")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main({int(a) for a in sys.argv[1:]}))
