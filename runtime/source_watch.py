#!/usr/bin/env python3
"""Watch official program-card sources for content changes without mutating cards.

Unlike the transport-only health check, this tool hashes the official page
body and compares it against the last observed digest. A `CHANGED` result is
a human-review signal only: the tool never edits knowledge cards, and a
transport failure is never evidence that a program changed or closed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
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
DEFAULT_STATE_PATH = ROOT / "reports" / "source-watch-state.yaml"


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


def content_digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def fetch_content(url: str, timeout: int = 15) -> dict[str, Any]:
    request = Request(
        url,
        headers={"User-Agent": "funding-intelligence-source-watch/1.0"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return {
                "state": "FETCHED",
                "http_status": response.status,
                "digest": content_digest(response.read()),
                "error": None,
            }
    except HTTPError as error:
        return {
            "state": "HTTP_ERROR",
            "http_status": error.code,
            "digest": None,
            "error": str(error),
        }
    except (URLError, TimeoutError, OSError) as error:
        return {
            "state": "UNREACHABLE",
            "http_status": None,
            "digest": None,
            "error": str(error),
        }


def classify_change(previous: Any, fetch: dict[str, Any]) -> str:
    """Classify a fetch against the stored digest without inventing evidence."""

    if fetch["state"] != "FETCHED":
        return fetch["state"]
    if not previous:
        return "NEW"
    if str(previous) == fetch["digest"]:
        return "UNCHANGED"
    return "CHANGED"


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"state_version": 1, "sources": {}}
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sources = value.get("sources") if isinstance(value, dict) else None
    return {"state_version": 1, "sources": sources if isinstance(sources, dict) else {}}


def build_checks(state_path: Path, timeout: int = 15) -> list[dict[str, Any]]:
    state = load_state(state_path)
    sources = state["sources"]
    checks: list[dict[str, Any]] = []
    for path in card_paths():
        card = load_yaml(path)
        status = card.get("status") or {}
        source = status.get("official_source")
        program_id = card.get("id")
        record: dict[str, Any] = {
            "program_id": program_id,
            "program": card.get("name"),
            "source": source,
            "card_path": str(path.relative_to(ROOT)),
            "card_last_checked": str(status.get("last_checked")) if status.get("last_checked") is not None else None,
        }
        if not source:
            record.update({"state": "MISSING_SOURCE", "http_status": None, "digest": None, "error": "status.official_source is missing"})
        else:
            fetch = fetch_content(str(source), timeout)
            record.update(fetch)
            record["change"] = classify_change(sources.get(str(program_id), {}).get("digest") if isinstance(sources.get(str(program_id)), dict) else None, fetch)
        checks.append(record)
    return checks


def report_from_checks(checks: list[dict[str, Any]], checked_at: str | None = None) -> dict[str, Any]:
    checks.sort(key=lambda item: str(item.get("program_id")))
    changed = [item for item in checks if item.get("change") == "CHANGED"]
    return {
        "source_watch_version": 1,
        "checked_at": checked_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "source_count": len(checks),
        "changed_count": len(changed),
        "summary": {
            "unchanged": sum(item.get("change") == "UNCHANGED" for item in checks),
            "new": sum(item.get("change") == "NEW" for item in checks),
            "changed": len(changed),
            "transport_failed": sum(item.get("change") in {"UNREACHABLE", "HTTP_ERROR"} for item in checks),
            "missing_source": sum(item.get("state") == "MISSING_SOURCE" for item in checks),
        },
        "checks": checks,
    }


def update_state(state_path: Path, checks: list[dict[str, Any]]) -> None:
    """Persist observed digests for fetched sources only; never touches cards."""

    state = load_state(state_path)
    sources = state["sources"]
    for item in checks:
        if item.get("state") == "FETCHED" and item.get("digest"):
            sources[str(item["program_id"])] = {
                "digest": item["digest"],
                "observed_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(yaml.safe_dump({"state_version": 1, "sources": sources}, allow_unicode=True, sort_keys=True), encoding="utf-8")


def render_summary(report: dict[str, Any]) -> str:
    lines = [
        "# Funding Intelligence official-source watch",
        "",
        f"Checked at: `{report['checked_at']}`",
        f"Sources checked: **{report['source_count']}**",
        f"Content changes: **{report['changed_count']}**",
        "",
        "| Program | State | Change | HTTP | Source |",
        "|---|---|---|---:|---|",
    ]
    for item in report["checks"]:
        source = item.get("source") or "missing"
        change = item.get("change") or "—"
        lines.append(
            f"| {item.get('program_id')} | `{item['state']}` | `{change}` | {item.get('http_status') or '—'} | {source} |"
        )
    lines.extend([
        "",
        "`CHANGED` means the official page body differs from the last observed digest. It is a human-review signal, not a status change: review the page, then update the card's `status` and `pathway` metadata by hand.",
        "`UNREACHABLE` and `HTTP_ERROR` are transport outcomes. They are not evidence that a program changed or closed.",
        "This tool never mutates knowledge cards. Digests are stored outside Git in the state file.",
    ])
    return "\n".join(lines) + "\n"


def self_test() -> int:
    fetch_ok = {"state": "FETCHED", "http_status": 200, "digest": "digest-a", "error": None}
    if classify_change(None, fetch_ok) != "NEW":
        print("ERROR: first observation was not classified as NEW", file=sys.stderr)
        return 1
    if classify_change("digest-a", fetch_ok) != "UNCHANGED":
        print("ERROR: identical digest was not classified as UNCHANGED", file=sys.stderr)
        return 1
    if classify_change("digest-b", fetch_ok) != "CHANGED":
        print("ERROR: different digest was not classified as CHANGED", file=sys.stderr)
        return 1
    if classify_change(None, {"state": "UNREACHABLE", "http_status": None, "digest": None, "error": "x"}) != "UNREACHABLE":
        print("ERROR: transport failure was not preserved as UNREACHABLE", file=sys.stderr)
        return 1
    if content_digest(b"stable") != content_digest(b"stable") or content_digest(b"stable") == content_digest(b"changed"):
        print("ERROR: content digest is not stable or not discriminating", file=sys.stderr)
        return 1
    report = report_from_checks(
        [
            {"program_id": "synthetic-card", "state": "FETCHED", "change": "CHANGED", "http_status": 200, "source": "https://example.com"},
            {"program_id": "synthetic-card-2", "state": "FETCHED", "change": "UNCHANGED", "http_status": 200, "source": "https://example.com/2"},
        ],
        checked_at="2026-09-11T00:00:00+00:00",
    )
    if report["changed_count"] != 1 or report["summary"]["unchanged"] != 1:
        print("ERROR: source-watch report summary miscounted changes", file=sys.stderr)
        return 1
    try:
        json.dumps(report)
    except TypeError as error:
        print(f"ERROR: source-watch report is not JSON serializable: {error}", file=sys.stderr)
        return 1
    print("OK: source-watch self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE_PATH, help="digest state file (kept outside Git)")
    parser.add_argument("--update-state", action="store_true", help="persist observed digests for fetched sources")
    parser.add_argument("--output", type=Path, help="write YAML or JSON report based on file extension")
    parser.add_argument("--summary", type=Path, help="write Markdown summary")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    checks = build_checks(args.state, args.timeout)
    report = report_from_checks(checks)
    if args.output:
        if args.output.suffix.lower() == ".json":
            args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            args.output.write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")
    else:
        print(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), end="")
    if args.summary:
        args.summary.write_text(render_summary(report), encoding="utf-8")
    if args.update_state:
        update_state(args.state, checks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
