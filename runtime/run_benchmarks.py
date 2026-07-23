#!/usr/bin/env python3
"""Run completed public decision-quality benchmark cases without rewriting expectations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from runner import build_report, load_yaml  # noqa: E402
from verify_route import find_cards, verify_route  # noqa: E402


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def route_reasons(route: dict[str, Any]) -> list[str]:
    reasons = as_list(route.get("why"))
    reasons.extend(as_list((route.get("decision_trace") or {}).get("why")))
    reasons.extend(as_list((route.get("eligibility") or {}).get("notes")))
    return [str(reason) for reason in reasons]


def check_reason(case_id: str, route_id: str, route: dict[str, Any], expected: dict[str, Any], errors: list[str]) -> None:
    haystack = "\n".join(route_reasons(route))
    for fragment in expected.get("reason_contains", []):
        if fragment not in haystack:
            errors.append(f"{case_id}:{route_id}: expected reason fragment not found: {fragment}")


def run_case(path: Path) -> list[str]:
    case = load_yaml(path)
    case_id = str(case.get("case_id", path.stem))
    if case.get("status") != "complete":
        return []
    project = case["project"]
    expected = case["expected"]
    errors: list[str] = []

    report = build_report(project)
    if report["classification"]["stage"] != expected["classification"]["stage"]:
        errors.append(f"{case_id}: classification stage mismatch")
    if set(report["classification"]["sectors"]) != set(expected["classification"]["sectors"]):
        errors.append(f"{case_id}: classification sectors mismatch")
    if report["gate"]["passed"] != expected["runner"]["gate_passed"]:
        errors.append(f"{case_id}: runner gate mismatch")
    runner_routes = {
        item["program_id"]: item
        for item in as_list(report.get("opportunities")) + as_list(report.get("do_not_apply"))
    }
    for route_id, route_expected in expected["runner"]["routes"].items():
        actual = runner_routes.get(route_id)
        if actual is None:
            errors.append(f"{case_id}: runner route missing: {route_id}")
            continue
        if actual.get("decision") != route_expected.get("decision"):
            errors.append(
                f"{case_id}:{route_id}: runner decision expected {route_expected.get('decision')}, got {actual.get('decision')}"
            )
        check_reason(case_id, route_id, actual, route_expected, errors)

    cards = {str(card.get("id")): card for card in find_cards()}
    verifier_routes: dict[str, dict[str, Any]] = {}
    for route_id in expected["verifier"]["routes"]:
        card = cards.get(route_id)
        if card is None:
            errors.append(f"{case_id}: verifier card missing: {route_id}")
            continue
        verifier_routes[route_id] = verify_route(project, card, {}, False)
    for route_id, route_expected in expected["verifier"]["routes"].items():
        actual = verifier_routes.get(route_id)
        if actual is None:
            continue
        if actual.get("decision") != route_expected.get("decision"):
            errors.append(
                f"{case_id}:{route_id}: verifier decision expected {route_expected.get('decision')}, got {actual.get('decision')}"
            )
        if route_expected.get("readiness") and actual.get("project_readiness") != route_expected["readiness"]:
            errors.append(
                f"{case_id}:{route_id}: readiness expected {route_expected['readiness']}, got {actual.get('project_readiness')}"
            )
        check_reason(case_id, route_id, actual, route_expected, errors)
    for route_id, forbidden_decisions in expected.get("forbidden", {}).items():
        actual_decisions = {
            runner_routes.get(route_id, {}).get("decision"),
            verifier_routes.get(route_id, {}).get("decision"),
        }
        invalid = actual_decisions.intersection(forbidden_decisions)
        if invalid:
            errors.append(f"{case_id}:{route_id}: forbidden decisions observed: {sorted(invalid)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, action="append", help="run only this benchmark case")
    args = parser.parse_args()
    paths = args.case or sorted((ROOT / "benchmarks" / "cases").glob("*.yaml"))
    errors = [error for path in paths for error in run_case(path)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: checked {len(paths)} decision-quality benchmark case(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
