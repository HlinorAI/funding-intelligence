"""Run the repository's reproducible local validation gate."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
PYTHON_MODULES = [
    "runtime/__init__.py",
    "runtime/project_contract.py",
    "runtime/freshness.py",
    "runtime/ingest.py",
    "runtime/runner.py",
    "runtime/verify_route.py",
    "runtime/validate_schemas.py",
    "runtime/render_report.py",
    "runtime/run_benchmarks.py",
    "runtime/health_check.py",
    "runtime/source_watch.py",
    "runtime/validate_workflows.py",
    "runtime/privacy.py",
    "runtime/check.py",
]


def commands(skip_tests: bool = False) -> list[tuple[str, list[str]]]:
    result: list[tuple[str, list[str]]] = []
    if not skip_tests:
        result.append(("pytest regression suite", [sys.executable, "-m", "pytest", "-q"]))
    result.extend(
        [
            ("runner regression suite", [sys.executable, "runtime/runner.py", "--check-all"]),
            ("decision-quality benchmarks", [sys.executable, "runtime/run_benchmarks.py"]),
            ("Python compilation", [sys.executable, "-m", "py_compile", *PYTHON_MODULES]),
            ("health-check self-test", [sys.executable, "runtime/health_check.py", "--self-test"]),
            ("source-watch self-test", [sys.executable, "runtime/source_watch.py", "--self-test"]),
            ("workflow validator self-test", [sys.executable, "runtime/validate_workflows.py", "--self-test"]),
            ("workflow validation", [sys.executable, "runtime/validate_workflows.py"]),
            ("schema and public-safety validation", [sys.executable, "runtime/validate_schemas.py"]),
        ]
    )
    return result


def run_check(label: str, command: Sequence[str]) -> bool:
    print(f"==> {label}")
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode:
        print(f"FAILED: {label} (exit {result.returncode})", file=sys.stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-tests", action="store_true", help="skip pytest and run contract checks only")
    args = parser.parse_args()
    for label, command in commands(skip_tests=args.skip_tests):
        if not run_check(label, command):
            return 1
    print("OK: Funding Intelligence validation gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
