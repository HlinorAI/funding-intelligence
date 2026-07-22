#!/usr/bin/env python3
"""Render deterministic runner and route-verification YAML as a human report."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


DECISION_GROUPS = {
    "NOW": {"NOW"},
    "BUILD_FIRST": {"BUILD_FIRST", "BUILD_NVIDIA_USE_CASE"},
    "VERIFY_ACCESS_PATH": {"VERIFY_ACCESS_PATH", "COMPLETE_ELIGIBILITY_DATA", "VERIFY_FIRST"},
    "DO_NOT_APPLY": {"DO_NOT_APPLY"},
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return value


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def text(value: Any, fallback: str = "unknown") -> str:
    if value is None or value == "":
        return fallback
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or fallback
    return str(value)


def bullets(values: list[Any], fallback: str = "No recorded items.") -> list[str]:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    return [f"- {value}" for value in cleaned] or [f"- {fallback}"]


def route_index(report: dict[str, Any], verification: dict[str, Any]) -> dict[str, dict[str, Any]]:
    routes: dict[str, dict[str, Any]] = {}
    for item in as_list(report.get("opportunities")) + as_list(report.get("do_not_apply")):
        if isinstance(item, dict) and item.get("program_id"):
            routes[str(item["program_id"])] = {"runner": item}
    for item in as_list(verification.get("routes")):
        if isinstance(item, dict) and item.get("program_id"):
            routes.setdefault(str(item["program_id"]), {})["verification"] = item
    return routes


def effective_route(route: dict[str, Any]) -> dict[str, Any]:
    runner = route.get("runner") or {}
    verifier = route.get("verification") or {}
    merged = dict(runner)
    merged.update({key: value for key, value in verifier.items() if value is not None})
    merged["decision"] = verifier.get("decision") or runner.get("decision") or "UNKNOWN"
    merged["program"] = verifier.get("program") or runner.get("program") or runner.get("name") or "Unknown route"
    merged["program_id"] = verifier.get("program_id") or runner.get("program_id")
    merged["decision_source"] = "route verification" if verifier.get("decision") else "runner"
    merged["verified_route"] = bool(verifier)
    return merged


def route_group(decision: str) -> str:
    for group, values in DECISION_GROUPS.items():
        if decision in values:
            return group
    return "OTHER"


def route_reason(route: dict[str, Any]) -> list[str]:
    fit = route.get("project_fit") or {}
    if route.get("verified_route"):
        reasons = as_list(fit.get("basis"))
        reasons.extend(as_list((route.get("eligibility") or {}).get("notes")))
    else:
        reasons = as_list(route.get("why"))
        reasons.extend(as_list((route.get("decision_trace") or {}).get("why")))
        reasons.extend(as_list(fit.get("basis")))
    return list(
        dict.fromkeys(
            str(item)
            for item in reasons
            if item and not str(item).startswith("Decision policy:")
        )
    )


def route_missing(route: dict[str, Any]) -> list[str]:
    missing = [] if route.get("verified_route") else as_list(route.get("missing"))
    eligibility = route.get("eligibility") or {}
    missing.extend(as_list(eligibility.get("missing")))
    required_proof = route.get("required_proof") or []
    for proof in required_proof:
        if isinstance(proof, dict) and proof.get("status") not in {None, "PASS"}:
            missing.append(proof.get("requirement", "Unspecified proof"))
    return list(dict.fromkeys(str(item) for item in missing if item))


def route_next_action(route: dict[str, Any]) -> str:
    action = route.get("next_action") or {}
    if isinstance(action, dict):
        deliverable = action.get("deliverable")
        if deliverable:
            return str(deliverable)
        if action.get("action"):
            return str(action["action"])
    return "No next action recorded."


def render_route(route: dict[str, Any]) -> list[str]:
    decision = text(route.get("decision"))
    lines = [f"### {text(route.get('program'))}", "", f"- Decision: `{decision}`", f"- Decision source: {text(route.get('decision_source'))}"]
    if route.get("resource_type"):
        lines.append(f"- Resource: {text(route.get('resource_type'))}")
    if route.get("score") is not None:
        lines.append(f"- Score: {route['score']}")
    if route.get("program_status"):
        status = route["program_status"]
        lines.append(f"- Program status: `{text(status.get('value'))}`; checked {text(status.get('verified_at'))}")
    elif route.get("status"):
        lines.append(f"- Program status: `{text(route.get('status'))}`; checked {text(route.get('last_checked'))}")
    if route.get("endpoint_status"):
        endpoint = route["endpoint_status"]
        lines.append(f"- Endpoint: `{text(endpoint.get('value'))}`; transport `{text(endpoint.get('transport'))}`")
    reasons = route_reason(route)
    lines.extend(["", "Why it is here:"] + bullets(reasons[:5]))
    missing = route_missing(route)
    lines.extend(["", "Missing proof:"] + bullets(missing))
    lines.extend(["", f"Next action: {route_next_action(route)}"])
    if route.get("stop_condition"):
        lines.append(f"Stop condition: {route['stop_condition']}")
    return lines + [""]


def source_lines(routes: list[dict[str, Any]]) -> list[str]:
    seen: set[tuple[str, str]] = set()
    lines: list[str] = []
    for route in routes:
        status = route.get("program_status") or {}
        source = status.get("source") or route.get("official_source")
        checked = status.get("verified_at") or route.get("last_checked") or route.get("verified_at")
        if not source:
            continue
        key = (str(source), text(checked))
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- [{text(route.get('program'))}]({source}) — checked {text(checked)}")
    return lines or ["- No official source recorded in the supplied reports."]


def timeline(report: dict[str, Any], routes: list[dict[str, Any]]) -> dict[str, list[str]]:
    plan = report.get("execution_plan") or {}
    next_actions = [route_next_action(route) for route in routes if route_group(text(route.get("decision"))) != "DO_NOT_APPLY"]
    return {
        "14 days": list(dict.fromkeys(next_actions + as_list(plan.get("days_7"))))[:7],
        "30 days": list(dict.fromkeys(as_list(plan.get("days_30")) + [item for route in routes for item in route_missing(route)]))[:7],
        "60 days": list(dict.fromkeys(as_list(plan.get("days_90"))))[:7],
    }


def render(report: dict[str, Any], verification: dict[str, Any]) -> str:
    routes = [effective_route(route) for route in route_index(report, verification).values()]
    routes.sort(key=lambda route: (route_group(text(route.get("decision"))) == "DO_NOT_APPLY", -float(route.get("score") or 0)))
    grouped = {group: [route for route in routes if route_group(text(route.get("decision"))) == group] for group in DECISION_GROUPS}
    project = text(report.get("project") or verification.get("project"))
    classification = report.get("classification") or {}
    lines = [
        f"# Opportunity Report: {project}",
        "",
        "> Human-readable rendering of deterministic runner and route-verification results.",
        "",
        "## Executive summary",
        "",
        f"- Stage: {text(classification.get('stage'))}",
        f"- Sectors: {text(classification.get('sectors'))}",
        f"- Goals: {text(classification.get('goals'))}",
        f"- Runner gate passed: `{text((report.get('gate') or {}).get('passed'))}`",
        "",
    ]
    if grouped["NOW"]:
        lines.append("There are routes with a current actionable decision, subject to human eligibility review.")
    else:
        lines.append("There is no route that should be treated as an unconditional immediate application.")
    lines.append("")

    section_titles = {
        "NOW": "NOW",
        "BUILD_FIRST": "BUILD_FIRST",
        "VERIFY_ACCESS_PATH": "VERIFY_ACCESS_PATH",
        "DO_NOT_APPLY": "DO_NOT_APPLY",
    }
    for group, title in section_titles.items():
        lines.extend([f"## {title}", ""])
        if grouped[group]:
            for route in grouped[group]:
                lines.extend(render_route(route))
        else:
            lines.extend(["No routes in this category.", ""])

    missing = list(dict.fromkeys(as_list(report.get("missing_proof")) + [item for route in routes for item in route_missing(route)]))
    lines.extend(["## Missing evidence", ""] + bullets(missing))

    lines.extend(["", "## Execution plan", ""])
    for horizon, actions in timeline(report, routes).items():
        lines.extend([f"### {horizon}", ""] + bullets(actions))
        lines.append("")

    lines.extend(["## Sources and verification dates", ""] + source_lines(routes))
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="runner report YAML")
    parser.add_argument("route_verification", type=Path, help="route-verification report YAML")
    parser.add_argument("--output", type=Path, help="write Markdown instead of stdout")
    args = parser.parse_args()
    rendered = render(load_yaml(args.report), load_yaml(args.route_verification))
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
