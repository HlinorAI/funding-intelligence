"""Local privacy gate for detecting and redacting credential-like input."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

try:
    from runtime.validate_schemas import credential_patterns
except ImportError:
    from validate_schemas import credential_patterns


def scan_text(value: str, source: str = "input") -> list[dict[str, Any]]:
    """Return locations of sensitive-looking values without returning their contents."""

    findings: list[dict[str, Any]] = []
    patterns = credential_patterns()
    for line_number, line in enumerate(value.splitlines(), start=1):
        for pattern_index, pattern in enumerate(patterns):
            if pattern.search(line):
                findings.append({"source": source, "line": line_number, "pattern": pattern_index})
    return findings


def redact_text(value: str) -> str:
    """Replace detected credential-like spans before a document is shared or stored."""

    redacted = value
    for pattern in credential_patterns():
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="files to scan; contents are never printed")
    args = parser.parse_args()
    findings: list[dict[str, Any]] = []
    for path in args.paths:
        try:
            findings.extend(scan_text(path.read_text(encoding="utf-8"), str(path)))
        except (OSError, UnicodeDecodeError) as error:
            print(f"ERROR: cannot scan {path}: {error}", file=sys.stderr)
            return 2
    if findings:
        for finding in findings:
            print(
                f"BLOCKED: {finding['source']}:{finding['line']} "
                f"matched sensitive pattern {finding['pattern']}",
                file=sys.stderr,
            )
        return 1
    print(f"OK: privacy scan passed for {len(args.paths)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
