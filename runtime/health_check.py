#!/usr/bin/env python3
"""Check official program-card URLs without mutating the knowledge base."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROGRAM_DIR = ROOT / "knowledge" / "programs"
PACK_DIR = ROOT / "knowledge" / "packs"
ACTIONABLE_STATES = {"NOT_FOUND", "SERVER_ERROR", "HTTP_ERROR", "MISSING_SOURCE"}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return value


def card_paths() -> list[Path]:
    paths = sorted(PROGRAM_DIR.glob("*.yaml"))
    paths.extend(sorted(PACK_DIR.glob("*/programs/*.yaml")))
    return paths


def classify_http(status: int) -> str:
    if 200 <= status < 400:
        return "HEALTHY"
    if status == 404:
        return "NOT_FOUND"
    if status >= 500:
        return "SERVER_ERROR"
    return "HTTP_ERROR"


def probe(url: str, timeout: int = 15) -> dict[str, Any]:
    request = Request(
        url,
        headers={"User-Agent": "funding-intelligence-health-check/1.0"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return {
                "state": classify_http(response.status),
                "http_status": response.status,
                "final_url": response.geturl(),
                "error": None,
            }
    except HTTPError as error:
        return {
            "state": classify_http(error.code),
            "http_status": error.code,
            "final_url": error.geturl(),
            "error": str(error),
        }
    except (URLError, TimeoutError, OSError) as error:
        return {
            "state": "UNREACHABLE",
            "http_status": None,
            "final_url": None,
            "error": str(error),
        }


def check_card(path: Path, timeout: int = 15) -> dict[str, Any]:
    card = load_yaml(path)
    status = card.get("status") or {}
    source = status.get("official_source")
    last_checked = status.get("last_checked")
    result: dict[str, Any] = {
        "program_id": card.get("id"),
        "program": card.get("name"),
        "source": source,
        "card_path": str(path.relative_to(ROOT)),
        "card_last_checked": str(last_checked) if last_checked is not None else None,
    }
    if not source:
        result.update({"state": "MISSING_SOURCE", "http_status": None, "final_url": None, "error": "status.official_source is missing"})
    else:
        result.update(probe(str(source), timeout))
    result["needs_review"] = result["state"] in ACTIONABLE_STATES
    return result


def build_report(timeout: int = 15, checked_at: str | None = None) -> dict[str, Any]:
    checks = [check_card(path, timeout) for path in card_paths()]
    checks.sort(key=lambda item: str(item.get("program_id")))
    actionable = [item for item in checks if item["needs_review"]]
    return {
        "health_check_version": 1,
        "checked_at": checked_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "source_count": len(checks),
        "actionable_count": len(actionable),
        "summary": {
            "healthy": sum(item["state"] == "HEALTHY" for item in checks),
            "unreachable": sum(item["state"] == "UNREACHABLE" for item in checks),
            "needs_review": len(actionable),
        },
        "checks": checks,
    }


def render_summary(report: dict[str, Any]) -> str:
    lines = [
        "# Funding Intelligence program-card health check",
        "",
        f"Checked at: `{report['checked_at']}`",
        f"Sources checked: **{report['source_count']}**",
        f"Actionable findings: **{report['actionable_count']}**",
        "",
        "| Program | State | HTTP | Source | Needs review |",
        "|---|---|---:|---|---|",
    ]
    for item in report["checks"]:
        source = item.get("source") or "missing"
        lines.append(
            f"| {item.get('program_id')} | `{item['state']}` | {item.get('http_status') or '—'} | {source} | {'yes' if item['needs_review'] else 'no'} |"
        )
    lines.extend([
        "",
        "`UNREACHABLE` means the check could not establish transport. It is not evidence that a program is closed. Knowledge cards are never changed by this job.",
    ])
    return "\n".join(lines) + "\n"


def self_test() -> int:
    cases = {
        200: "HEALTHY",
        302: "HEALTHY",
        404: "NOT_FOUND",
        403: "HTTP_ERROR",
        500: "SERVER_ERROR",
        503: "SERVER_ERROR",
    }
    for status, expected in cases.items():
        actual = classify_http(status)
        if actual != expected:
            print(f"ERROR: HTTP {status} classified as {actual}, expected {expected}", file=sys.stderr)
            return 1
    report = build_report(checked_at="2026-07-23T00:00:00+00:00")
    if report["health_check_version"] != 1 or not report["checks"]:
        print("ERROR: health-check report self-test produced no card records", file=sys.stderr)
        return 1
    try:
        json.dumps(report)
    except TypeError as error:
        print(f"ERROR: health-check report is not JSON serializable: {error}", file=sys.stderr)
        return 1
    print("OK: health-check self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write YAML or JSON report based on file extension")
    parser.add_argument("--summary", type=Path, help="write Markdown summary")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--fail-on-issues", action="store_true", help="return non-zero when actionable findings exist")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    report = build_report(timeout=args.timeout)
    if args.output:
        if args.output.suffix.lower() == ".json":
            args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            args.output.write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")
    else:
        print(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), end="")
    if args.summary:
        args.summary.write_text(render_summary(report), encoding="utf-8")
    return 1 if args.fail_on_issues and report["actionable_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
