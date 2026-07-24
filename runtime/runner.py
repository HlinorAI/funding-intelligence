#!/usr/bin/env python3
"""Deterministic local evaluator for the Funding Intelligence knowledge base."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROGRAM_DIR = ROOT / "knowledge" / "programs"
ACTIVE_STATES = {"OPEN", "ROLLING", "ACTIVE"}
UNCERTAIN_STATES = {"VERIFY", "WATCH", "UPCOMING", "BD-ONLY"}
BLOCKED_STATES = {"CLOSED", "HOLD"}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected mapping in {path}")
    return value


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def truthy(data: dict[str, Any], *path: str) -> bool:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return False
        current = current.get(key)
    if isinstance(current, str):
        return current.strip().lower() in {"true", "yes", "present", "verified", "confirmed"}
    return bool(current)


def number(data: dict[str, Any], *path: str) -> float:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return 0
        current = current.get(key, 0)
    if isinstance(current, bool):
        return 1.0 if current else 0.0
    try:
        return float(current or 0)
    except (TypeError, ValueError):
        return 0.0


def normalize_stage(project: dict[str, Any]) -> str:
    raw = project.get("stage", "UNKNOWN")
    if isinstance(raw, list):
        return str(raw[0]) if raw else "UNKNOWN"
    return str(raw)


def project_goals(project: dict[str, Any]) -> list[str]:
    needs = project.get("needs") or {}
    explicit = [str(goal).lower() for goal in as_list(needs.get("goals"))]
    if explicit:
        return explicit
    goals: list[str] = []
    if truthy(needs, "funding") or number(needs, "funding") > 0:
        goals.append("funding")
    if truthy(needs, "partnerships"):
        goals.append("partnerships")
    if truthy(needs, "accelerator"):
        goals.append("accelerator")
    return goals


def program_affiliation_state(project: dict[str, Any], program_id: str | None) -> str | None:
    """Normalize a project's public relationship with a program into a routing state."""

    if not program_id:
        return None
    records = [
        affiliation
        for affiliation in as_list(project.get("program_affiliations"))
        if isinstance(affiliation, dict) and str(affiliation.get("program_id")) == program_id
    ]
    for affiliation in records:
        if str(affiliation.get("status", "")).lower() == "current":
            return "current"
    for affiliation in records:
        status = str(affiliation.get("status", "")).lower()
        outcome = str(affiliation.get("outcome", "")).lower()
        if status in {"previous", "alumni"} and outcome in {"accepted", "completed", "graduated", "successful"}:
            return "previous_successful"
    for affiliation in records:
        status = str(affiliation.get("status", "")).lower()
        outcome = str(affiliation.get("outcome", "")).lower()
        if status == "rejected" or outcome == "rejected":
            return "rejected"
    if records:
        return "unknown"
    return None


def current_program_affiliation(project: dict[str, Any], program_id: str | None) -> str | None:
    """Backward-compatible helper for the current-affiliation hard gate."""

    return "current" if program_affiliation_state(project, program_id) == "current" else None


def text_tokens(project: dict[str, Any]) -> set[str]:
    product = project.get("product") or {}
    values = []
    for value in as_list(project.get("sector")) + as_list(project.get("geography")):
        values.append(str(value))
    for key in ("description", "customers"):
        values.extend(str(value) for value in as_list(product.get(key)))
    values.extend(str(value) for value in as_list(product.get("technology")))
    return {token.lower().replace("-", "_") for token in values}


def project_ecosystems(project: dict[str, Any]) -> set[str]:
    product = project.get("product") or {}
    constraints = project.get("constraints") or {}
    values = as_list(product.get("ecosystems")) + as_list(constraints.get("native_ecosystems")) + as_list(constraints.get("target_ecosystems"))
    return {str(value).lower() for value in values}


def project_fit(project: dict[str, Any], card: dict[str, Any]) -> tuple[bool, str]:
    if ecosystem_match(project, card):
        return True, "ecosystem"
    routing = card.get("routing") or {}
    verticals = {str(value).lower() for value in as_list(routing.get("verticals"))}
    project_values = text_tokens(project)
    if verticals & project_values:
        return True, "vertical"
    return False, "none"


def ecosystem_match(project: dict[str, Any], card: dict[str, Any]) -> bool:
    ecosystem = str(card.get("ecosystem", "")).lower()
    name = str(card.get("name", "")).lower()
    project_values = project_ecosystems(project)
    return any(value in ecosystem or ecosystem in value or value in name for value in project_values)


def evidence_score(project: dict[str, Any]) -> int:
    evidence = project.get("evidence") or {}
    checks = [
        truthy(evidence, "site"),
        truthy(evidence, "github"),
        truthy(evidence, "live_demo"),
        truthy(evidence, "live_deployment"),
        number(evidence, "users") > 0,
        truthy(evidence, "metrics"),
        number(evidence, "pilots") > 0,
        number(evidence, "partners") > 0,
        number(evidence, "revenue") > 0 or truthy(evidence, "revenue"),
    ]
    return min(20, round(sum(checks) / len(checks) * 20))


def mechanism_score(project: dict[str, Any], card: dict[str, Any]) -> tuple[int, list[str]]:
    needs = project.get("needs") or {}
    goals = set(project_goals(project))
    mechanisms = {str(value).lower() for value in as_list(card.get("mechanism"))}
    stage = normalize_stage(project).lower()
    score = 5
    reasons: list[str] = []
    goal_map = {
        "funding": {"proposal_grant", "retro", "investment", "incentive", "subsidy"},
        "partnerships": {"bd"},
        "partner": {"bd"},
        "accelerator": {"accelerator", "investment"},
        "distribution": {"bd", "incentive", "accelerator"},
        "technical_support": {"bd", "subsidy", "accelerator"},
    }
    desired = set().union(*(goal_map.get(goal, set()) for goal in goals))
    if desired & mechanisms:
        score = 15
        reasons.append("goal matches mechanism")
    else:
        score = 2
        reasons.append("goal does not match mechanism")
    if stage in {"idea", "prototype"} and mechanisms & {"retro", "incentive"}:
        score = max(0, score - 5)
        reasons.append("early stage is weak for ship-first or incentive route")
    if stage in {"mainnet", "revenue"} and mechanisms & {"retro", "incentive", "bd"}:
        score = min(15, score + 2)
    return score, reasons


def gates(project: dict[str, Any], card: dict[str, Any]) -> dict[str, bool]:
    status = card.get("status") or {}
    next_action = card.get("next_action") or {}
    affiliation_state = program_affiliation_state(project, str(card.get("id")))
    return {
        "project_fit": project_fit(project, card)[0],
        "status_verified": status.get("needs_verification") is False and status.get("state") in ACTIVE_STATES,
        "application_endpoint_exists": bool(status.get("official_source")),
        "mechanism_identified": bool(as_list(card.get("mechanism"))),
        "evidence_requirements_known": bool(as_list(card.get("required_evidence"))),
        "next_action_exists": bool(next_action.get("action") and next_action.get("deliverable")),
        "affiliation_verified": affiliation_state != "unknown",
        "not_already_affiliated": affiliation_state not in {"current", "previous_successful"},
    }


def evaluate(project: dict[str, Any], card: dict[str, Any]) -> dict[str, Any]:
    status = card.get("status") or {}
    state = str(status.get("state", "VERIFY"))
    project_tokens = text_tokens(project)
    route_fit, fit_kind = project_fit(project, card)
    evidence = project.get("evidence") or {}
    constraints = project.get("constraints") or {}
    mechanisms = {str(value).lower() for value in as_list(card.get("mechanism"))}
    reasons: list[str] = []
    missing: list[str] = []
    penalties: dict[str, int] = {}

    strategic = 25 if route_fit else (10 if "web3" in project_tokens and state not in BLOCKED_STATES else 5)
    technical = 20 if route_fit and (truthy(evidence, "live_deployment") or truthy(project, "product", "technology")) else 6
    evidence_points = evidence_score(project)
    mechanism, mechanism_reasons = mechanism_score(project, card)
    readiness = 10
    if not truthy(evidence, "live_demo") and not truthy(evidence, "live_deployment"):
        readiness -= 4
        missing.append("live demo or deployment")
    if number(project, "needs", "funding") > 0 and not truthy(project, "readiness", "budget"):
        readiness -= 2
        missing.append("milestone budget")
    if not truthy(project, "readiness", "milestones"):
        readiness -= 2
        missing.append("measurable milestones")
    access = min(10, int(number(project, "access", "champions") * 5 + number(project, "access", "warm_intros") * 2 + number(evidence, "partners") * 2))
    if access == 0:
        missing.append("champion or warm introduction")

    if state in BLOCKED_STATES:
        penalties["closed_program"] = -25
        reasons.append(f"status is {state}")
    if not route_fit:
        penalty_name = "no_native_fit" if card.get("ecosystem") else "no_vertical_fit"
        penalties[penalty_name] = -20
        missing.append("target/native ecosystem or vertical fit")
    if not route_fit and as_list(constraints.get("target_ecosystems")):
        penalties["wrong_stage"] = -20
        reasons.append("target ecosystem does not match this card")
    if mechanisms & {"retro", "incentive"} and not truthy(evidence, "live_deployment"):
        penalties["no_proof"] = -15
        missing.append("shipped deployment and measurable usage")
    if mechanism < 5:
        penalties["mechanism_mismatch"] = -15
    if truthy(constraints, "generic_multichain") and not route_fit:
        penalties["generic_multichain"] = -20
    if not truthy(project, "readiness", "milestones"):
        penalties["no_milestones"] = -10
    if "bd" in mechanisms and not truthy(project, "distribution", "plan"):
        penalties["no_distribution_plan"] = -10

    affiliation_state = program_affiliation_state(project, str(card.get("id")))
    if affiliation_state in {"current", "previous_successful"}:
        reasons.append(f"project already has {affiliation_state.replace('_', ' ')} {card.get('name')} affiliation")
        penalties["already_affiliated"] = -100
    elif affiliation_state == "rejected":
        reasons.append(f"project has a previous rejected {card.get('name')} application")
        penalties["previous_rejection"] = -5
    elif affiliation_state == "unknown":
        reasons.append(f"project {card.get('name')} affiliation outcome is unknown")
        missing.append("verified program affiliation status")

    raw_score = strategic + technical + evidence_points + mechanism + max(0, readiness) + access + sum(penalties.values())
    score = max(0, min(100, raw_score))
    gate = gates(project, card)
    gate["passed"] = all(gate.values())

    if affiliation_state in {"current", "previous_successful"}:
        decision = "DO_NOT_APPLY"
    elif affiliation_state == "rejected":
        decision = "APPLY_AGAIN_AFTER_CHANGE"
    elif affiliation_state in {"unknown", None}:
        decision = "VERIFY_FIRST"
    elif state in BLOCKED_STATES:
        decision = "DO_NOT_APPLY"
    elif not gate["project_fit"]:
        decision = "DO_NOT_APPLY"
    elif not gate["status_verified"]:
        decision = "VERIFY_FIRST"
    elif not truthy(evidence, "live_demo") and not truthy(evidence, "live_deployment"):
        decision = "BUILD_FIRST"
    elif score >= 80:
        decision = "NOW"
    elif score >= 65:
        decision = "NEXT"
    elif score >= 50:
        decision = "LATER"
    else:
        decision = "DO_NOT_APPLY"

    if route_fit:
        reasons.append(f"{fit_kind} matches project routing")
    if evidence_points >= 12:
        reasons.append("structured evidence is present")
    reasons.extend(mechanism_reasons)
    positive: list[str] = []
    negative: list[str] = []
    if route_fit:
        positive.append(f"{fit_kind} fit")
    if evidence_points >= 12:
        positive.append("structured evidence")
    if mechanism >= 10:
        positive.append("goal/mechanism fit")
    for key, value in penalties.items():
        negative.append(f"{key} ({value})")
    negative.extend(sorted(set(missing)))
    trace = {
        "program": card.get("name"),
        "considered": route_fit,
        "rejected": decision == "DO_NOT_APPLY",
        "score": score,
        "positive": positive,
        "negative": negative,
        "decision": decision,
        "why": reasons[:5],
    }
    return {
        "program_id": card.get("id"),
        "program": card.get("name"),
        "status": state,
        "score": score,
        "decision": decision,
        "mechanism": as_list(card.get("mechanism")),
        "resource_type": as_list(card.get("resource_type")),
        "components": {
            "strategic_fit": strategic,
            "technical_fit": technical,
            "evidence": evidence_points,
            "mechanism_fit": mechanism,
            "readiness": max(0, readiness),
            "access": access,
            "penalties": penalties,
        },
        "gate": gate,
        "why": reasons[:5],
        "missing": sorted(set(missing)),
        "next_action": card.get("next_action") or {},
        "stop_condition": card.get("stop_condition", "Not specified"),
        "decision_trace": trace,
        "official_source": status.get("official_source"),
        "last_checked": str(status.get("last_checked")) if status.get("last_checked") is not None else None,
    }


def build_report(project: dict[str, Any]) -> dict[str, Any]:
    program_paths = sorted(PROGRAM_DIR.glob("*.yaml"))
    project_tokens = text_tokens(project)
    if project_tokens & {"ai", "artificial_intelligence", "agents", "agent_infrastructure"}:
        program_paths.extend(sorted((ROOT / "knowledge" / "packs" / "ai" / "programs").glob("*.yaml")))
    cards = [load_yaml(path) for path in program_paths]
    evaluations = [evaluate(project, card) for card in cards]
    evaluations.sort(key=lambda item: (item["decision"] == "DO_NOT_APPLY", -item["score"]))
    opportunities = [item for item in evaluations if item["decision"] != "DO_NOT_APPLY"][:7]
    rejected = [item for item in evaluations if item["decision"] == "DO_NOT_APPLY"]
    rejected.sort(key=lambda item: (item["gate"].get("not_already_affiliated", True), -item["score"]))
    do_not_apply = rejected[:10]
    evidence = project.get("evidence") or {}
    readiness = project.get("readiness") or {}
    all_gates = {
        "project_fit": False,
        "status_verified": False,
        "application_endpoint_exists": True,
        "mechanism_identified": True,
        "evidence_requirements_known": True,
        "next_action_exists": True,
    }
    if opportunities:
        all_gates = {key: all(item["gate"].get(key, False) for item in opportunities) for key in all_gates}
    all_gates["passed"] = all(all_gates.values())
    stage = project.get("stage", "UNKNOWN")
    goals = project_goals(project)
    plan_7 = [item["next_action"].get("deliverable") for item in opportunities[:3] if item["next_action"].get("deliverable")]
    plan_30 = ["Close missing proof: " + ", ".join(item["missing"][:3]) for item in opportunities[:3] if item["missing"]]
    plan_90 = [f"Re-score {item['program']} after status verification and new evidence" for item in opportunities[:3]]
    missing_proof = sorted({value for item in opportunities for value in item["missing"]})
    unknown_proof = {
        "pilots": "customer pilots",
        "revenue": "revenue evidence",
        "users": "user/usage evidence",
        "live_demo": "technical validation/demo",
        "live_deployment": "live deployment",
        "metrics": "usage metrics",
    }
    for field, label in unknown_proof.items():
        value = evidence.get(field)
        if value is None or (isinstance(value, str) and value.strip().lower() == "unknown"):
            missing_proof.append(label)
    if not truthy(evidence, "live_deployment"):
        missing_proof.append("live deployment")
    if not truthy(readiness, "milestones"):
        missing_proof.append("milestones")
    coverage_gaps: list[str] = []
    if not opportunities:
        coverage_gaps.append("No matching local program cards for the project's routing facts")
    if not project_ecosystems(project) and not opportunities:
        coverage_gaps.append("No target/native ecosystem provided; chain-specific cards are excluded")
    if any(token in text_tokens(project) for token in {"hardware", "industrial", "sme"}):
        coverage_gaps.append("Local knowledge base is currently Web3/ecosystem-heavy; generic AI, enterprise, deeptech and SME routes are not represented")
    return {
        "report_version": 1,
        "project": project.get("name", "UNKNOWN"),
        "classification": {
            "stage": normalize_stage(project),
            "stage_claims": as_list(project.get("stage_claims")) or as_list(project.get("stage")),
            "sectors": as_list(project.get("sector")),
            "goals": goals,
            "confidence": "high" if stage != "UNKNOWN" and goals else "low",
        },
        "gate": all_gates,
        "opportunities": opportunities,
        "do_not_apply": do_not_apply,
        "coverage_gaps": coverage_gaps,
        "missing_proof": sorted(set(missing_proof)),
        "execution_plan": {"days_7": plan_7, "days_30": plan_30, "days_90": plan_90},
    }


def check_expected(report: dict[str, Any], expected_path: Path) -> None:
    expected = load_yaml(expected_path)
    all_items = report["opportunities"] + report["do_not_apply"]
    decisions = {item["decision"] for item in all_items}
    programs = {item["program_id"] for item in all_items}
    decision_items = report["opportunities"] if expected.get("decision") != "DO_NOT_APPLY" else report["do_not_apply"]
    if expected.get("decision") and not any(item["decision"] == expected["decision"] for item in decision_items):
        raise AssertionError(f"{expected_path}: expected decision {expected['decision']}, got {decisions}")
    for program_id in as_list(expected.get("must_include")):
        if program_id not in programs:
            raise AssertionError(f"{expected_path}: missing program {program_id}")
    if expected.get("must_not_be_now") and any(item["decision"] == "NOW" for item in report["opportunities"]):
        raise AssertionError(f"{expected_path}: unverified route reached NOW")
    if expected.get("gate_passed") is not None and report["gate"]["passed"] != expected["gate_passed"]:
        raise AssertionError(f"{expected_path}: gate mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, nargs="?", help="project.yaml")
    parser.add_argument("--output", type=Path, help="write report instead of stdout")
    parser.add_argument("--format", choices=("yaml", "json"), default="yaml")
    parser.add_argument("--check-all", action="store_true", help="run all cases against tests/expected")
    args = parser.parse_args()
    if args.check_all:
        case_paths = sorted((ROOT / "tests" / "cases").glob("*.yaml")) + sorted((ROOT / "tests" / "live").glob("*.yaml"))
        expected_dir = ROOT / "tests" / "expected"
        for case_path in case_paths:
            report = build_report(load_yaml(case_path))
            check_expected(report, expected_dir / case_path.name)
        print(f"OK: checked {len(case_paths)} cases")
        return 0
    if not args.project:
        parser.error("project is required unless --check-all is used")
    report = build_report(load_yaml(args.project))
    rendered = json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" else yaml.safe_dump(report, allow_unicode=True, sort_keys=False)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
