#!/usr/bin/env python3
"""Route verifier with independent program, endpoint, fit and readiness states."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

from runner import ROOT, evaluate, load_yaml, program_affiliation_state, project_fit, text_tokens


UNKNOWN = {None, "", "UNKNOWN", "unknown", "TODO", "NOT_PROVIDED", "not_provided"}


def known(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        return value not in UNKNOWN and value.strip().lower() not in {"false", "no", "none"}
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return value not in UNKNOWN


def find_cards() -> list[dict[str, Any]]:
    paths = list((ROOT / "knowledge" / "programs").glob("*.yaml"))
    paths.extend((ROOT / "knowledge" / "packs").glob("*/programs/*.yaml"))
    return [load_yaml(path) for path in sorted(paths)]


def load_pack(evidence_dir: Path | None) -> dict[str, Any]:
    if not evidence_dir or not evidence_dir.exists():
        return {}
    return {path.stem: load_yaml(path) for path in sorted(evidence_dir.glob("*.yaml"))}


def pack_value(project: dict[str, Any], pack: dict[str, Any], section: str, key: str) -> Any:
    if section in pack and isinstance(pack[section], dict):
        return pack[section].get(key)
    return None


def evidence_value(project: dict[str, Any], pack: dict[str, Any], key: str) -> Any:
    evidence = project.get("evidence") or {}
    if key in evidence:
        return evidence[key]
    mapping = {
        "site": [("company", "website"), ("product", "website")],
        "github": [("deployment", "repository"), ("technical-proof", "repository")],
        "live_demo": [("technical-proof", "working_demo")],
        "live_deployment": [("deployment", "status")],
        "users": [("traction", "users")],
        "pilots": [("customers", "pilots")],
        "revenue": [("traction", "revenue")],
        "metrics": [("traction", "usage_metrics")],
        "legal_entity": [("company", "legal_entity")],
        "funding_stage": [("funding-needs", "funding_stage")],
        "funding_history": [("company", "current_funding")],
        "api_use_case": [("product", "api_use_case")],
        "customer_problem": [("product", "problem"), ("customers", "customer_problem_interviews")],
        "customer": [("product", "customer")],
        "team": [("company", "team_size")],
        "aws_account": [("funding-needs", "aws_account")],
        "provider_org_id": [("funding-needs", "provider_referral")],
        "milestones": [("milestones", "status")],
        "product": [("product", "product")],
    }
    for section, field in mapping.get(key, []):
        value = pack_value(project, pack, section, field)
        if value is not None:
            return value
    if key == "funding_stage":
        return project.get("stage")
    if key == "geography":
        return project.get("geography")
    return None


def proof_status(project: dict[str, Any], pack: dict[str, Any], requirement: str) -> dict[str, Any]:
    text = requirement.lower()
    if "api use case" in text:
        field = "api_use_case"
    elif "aws account" in text:
        field = "aws_account"
    elif "provider org" in text:
        field = "provider_org_id"
    elif "customer/problem" in text:
        field = "customer_problem"
    elif "funding stage" in text:
        field = "funding_stage"
    elif "concise application" in text:
        field = "application"
    elif "company-owned software product" in text or "product and ai workload" in text or "product and company details" in text:
        field = "product"
    elif "website" in text or "site" in text:
        field = "site"
    elif "github" in text or "repo" in text:
        field = "github"
    elif "demo" in text or "prototype" in text or "working mvp" in text:
        field = "live_demo"
    elif "pilot" in text or "customer" in text or "integrator" in text:
        field = "pilots"
    elif "user" in text or "usage" in text or "traction" in text:
        field = "users"
    elif "revenue" in text:
        field = "revenue"
    elif "milestone" in text or "budget" in text:
        field = "milestones"
    elif "api" in text or "workload" in text or "architecture" in text or "technology" in text:
        field = "product"
    elif "team" in text or "developer" in text or "founder" in text:
        field = "team"
    elif "headquarter" in text:
        field = "geography"
    elif "private" in text or "incorporated" in text or "legal" in text:
        field = "legal_entity"
    elif "funding" in text:
        field = "funding_history"
    else:
        field = "unmapped"
    value = evidence_value(project, pack, field)
    return {
        "requirement": requirement,
        "field": field,
        "status": "PASS" if known(value) else "MISSING",
        "value": value if known(value) else "UNKNOWN",
    }


def live_check(url: str, timeout: int = 15) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "funding-intelligence-route-verifier/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return {"state": "PASS", "http_status": response.status, "final_url": response.geturl()}
    except HTTPError as error:
        return {"state": "FAIL", "http_status": error.code, "error": str(error)}
    except (URLError, TimeoutError, OSError) as error:
        return {"state": "FAIL", "error": str(error)}


def get_program_status(card: dict[str, Any], verified_at_override: str | None = None) -> dict[str, Any]:
    status = card.get("status") or {}
    verification = card.get("verification") or {}
    source_verified = verification.get("source_verified") is True
    return {
        "value": status.get("state", "UNKNOWN"),
        "verified_at": verified_at_override or (str(verification.get("verified_at")) if source_verified and verification.get("verified_at") else None),
        "source": status.get("official_source"),
        "source_verified": source_verified,
        "verified_via": verification.get("verified_via"),
    }


def get_endpoint_status(card: dict[str, Any], live: bool, verified_at_override: str | None = None) -> tuple[dict[str, Any], str | None]:
    status = card.get("status") or {}
    verification = card.get("verification") or {}
    endpoint = verification.get("actual_endpoint") or status.get("official_source")
    source_verified = verification.get("source_verified") is True
    source_verified_at = verified_at_override or (str(verification.get("verified_at")) if source_verified and verification.get("verified_at") else None)
    if not endpoint:
        return {"value": "MISSING", "transport": "NOT_RUN", "transport_error": None, "verified_at": None}, None
    if not live:
        return {
            "value": "AVAILABLE" if source_verified else "UNKNOWN",
            "transport": "NOT_RUN",
            "transport_error": None,
            "verified_at": source_verified_at,
        }, endpoint
    probe = live_check(endpoint)
    if probe.get("state") == "PASS":
        return {
            "value": "AVAILABLE",
            "transport": "PASS",
            "http_status": probe.get("http_status"),
            "final_url": probe.get("final_url"),
            "transport_error": None,
            "verified_at": dt.date.today().isoformat(),
        }, endpoint
    if source_verified:
        return {
            "value": "AVAILABLE",
            "transport": "UNREACHABLE",
            "transport_error": probe.get("error", f"HTTP {probe.get('http_status')}"),
            "verified_at": source_verified_at,
        }, endpoint
    return {
        "value": "UNREACHABLE",
        "transport": "UNREACHABLE",
        "transport_error": probe.get("error", f"HTTP {probe.get('http_status')}"),
        "verified_at": None,
    }, endpoint


def project_fit_state(project: dict[str, Any], card: dict[str, Any], evaluation: dict[str, Any]) -> dict[str, Any]:
    if not evaluation["gate"]["project_fit"]:
        return {"value": "NONE", "basis": [], "score": evaluation["score"]}
    routing = card.get("routing") or {}
    native_signals = {str(value).lower() for value in routing.get("native_signals", [])}
    tokens = text_tokens(project)
    basis = evaluation["decision_trace"]["positive"]
    if native_signals and not native_signals & tokens:
        return {"value": "WEAK", "basis": basis + ["required native signal is absent"], "score": evaluation["score"]}
    return {"value": "STRONG" if native_signals & tokens else "POSSIBLE", "basis": basis, "score": evaluation["score"]}


def readiness_state(card: dict[str, Any], fit: dict[str, Any], missing: list[str], affiliation_state: str | None = None) -> str:
    if affiliation_state in {"current", "previous_successful"}:
        return "INELIGIBLE"
    if affiliation_state == "rejected":
        return "REAPPLY_AFTER_CHANGE"
    if affiliation_state == "unknown":
        return "UNKNOWN"
    if fit["value"] == "NONE":
        return "INELIGIBLE"
    if fit["value"] == "WEAK":
        return "BUILD_FIRST"
    policy = card.get("decision_policy") or {}
    mode = policy.get("readiness_mode")
    if mode == "access":
        return "UNKNOWN"
    if missing and mode == "eligibility":
        return "INCOMPLETE"
    if missing and mode == "build_proof":
        return "BUILD_FIRST"
    if missing:
        return "INCOMPLETE"
    return "READY"


def decision_for(project: dict[str, Any], card: dict[str, Any], program_status: dict[str, Any], endpoint_status: dict[str, Any], fit: dict[str, Any], readiness: str) -> str:
    affiliation_state = program_affiliation_state(project, str(card.get("id")))
    if affiliation_state in {"current", "previous_successful"}:
        return "DO_NOT_APPLY"
    if affiliation_state == "rejected":
        return "APPLY_AGAIN_AFTER_CHANGE"
    if affiliation_state == "unknown":
        return "VERIFY_FIRST"
    if fit["value"] == "NONE" or program_status["value"] in {"CLOSED", "HOLD"}:
        return "DO_NOT_APPLY"
    if endpoint_status["value"] == "MISSING":
        return "NO_ACTIONABLE_ENDPOINT"
    policy = card.get("decision_policy") or {}
    if fit["value"] == "WEAK" and policy.get("weak_fit"):
        return policy["weak_fit"]
    if readiness == "UNKNOWN" and policy.get("access_unknown"):
        return policy["access_unknown"]
    if readiness == "INCOMPLETE" and policy.get("missing_eligibility"):
        return policy["missing_eligibility"]
    if readiness == "BUILD_FIRST":
        return policy.get("missing_proof", "BUILD_FIRST")
    if endpoint_status["value"] in {"UNKNOWN", "UNREACHABLE"}:
        return "VERIFY_FIRST"
    if readiness == "READY":
        return "NOW"
    return "VERIFY_FIRST"


def verify_route(project: dict[str, Any], card: dict[str, Any], pack: dict[str, Any], live: bool, verified_at_override: str | None = None) -> dict[str, Any]:
    evaluation = evaluate(project, card)
    program_status = get_program_status(card, verified_at_override)
    endpoint_status, endpoint = get_endpoint_status(card, live, verified_at_override)
    proofs = [proof_status(project, pack, item) for item in card.get("required_evidence", [])]
    missing = [item["requirement"] for item in proofs if item["status"] != "PASS"]
    fit = project_fit_state(project, card, evaluation)
    affiliation_state = program_affiliation_state(project, str(card.get("id")))
    readiness = readiness_state(card, fit, missing, affiliation_state)
    decision = decision_for(project, card, program_status, endpoint_status, fit, readiness)
    policy = card.get("decision_policy") or {}
    next_action = dict(card.get("next_action") or {})
    next_action["action"] = decision
    return {
        "program": card.get("name"),
        "program_id": card.get("id"),
        "program_status": program_status,
        "endpoint_status": endpoint_status,
        "project_fit": dict(fit),
        "project_readiness": readiness,
        "status": program_status["value"],
        "actual_endpoint": endpoint,
        "eligibility": {
            "state": readiness,
            "passed": [item["requirement"] for item in proofs if item["status"] == "PASS"],
            "missing": missing,
            "notes": [
                (card.get("verification") or {}).get("status_check", "Confirm official eligibility and endpoint"),
                f"Decision policy: {policy or 'default'}",
                *( [f"Affiliation state: {affiliation_state}"] if affiliation_state else [] ),
            ],
        },
        "resource_type": card.get("resource_type", card.get("mechanism", [])),
        "required_proof": proofs,
        "hlinor_fit": {**fit, "basis": list(fit.get("basis", []))},
        "next_action": next_action,
        "stop_condition": card.get("stop_condition", "Not specified"),
        "verified_at": endpoint_status.get("verified_at") or program_status.get("verified_at"),
        "decision": decision,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--route", action="append", help="route id; repeatable")
    parser.add_argument("--all-ai", action="store_true", help="verify all AI-routed cards")
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--live", action="store_true", help="perform HTTP checks of actual endpoints")
    parser.add_argument("--verified-at", help="override source snapshot date")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="assert the expected five-route Hlinor shape")
    args = parser.parse_args()
    project = load_yaml(args.project)
    cards = find_cards()
    if args.route:
        selected = [card for card in cards if card.get("id") in set(args.route)]
    elif args.all_ai:
        tokens = text_tokens(project)
        selected = [card for card in cards if set(str(value).lower() for value in (card.get("routing") or {}).get("verticals", [])) & tokens]
    else:
        parser.error("use --route ID or --all-ai")
    if not selected:
        raise SystemExit("No matching routes")
    pack = load_pack(args.evidence_dir)
    report = {
        "verification_version": 2,
        "project": project.get("name", "UNKNOWN"),
        "mode": "live" if args.live else "source_snapshot",
        "routes": [verify_route(project, card, pack, args.live, args.verified_at) for card in selected],
    }
    if args.check:
        route_ids = {item["program_id"] for item in report["routes"]}
        expected = {"aws-activate", "microsoft-for-startups", "nvidia-inception", "openai-for-startups", "y-combinator"}
        if route_ids != expected:
            raise AssertionError(f"expected AI routes {sorted(expected)}, got {sorted(route_ids)}")
        decisions = {item["decision"] for item in report["routes"]}
        if decisions != {"COMPLETE_ELIGIBILITY_DATA", "BUILD_NVIDIA_USE_CASE", "VERIFY_ACCESS_PATH", "BUILD_FIRST"}:
            raise AssertionError(f"unexpected route decisions: {sorted(decisions)}")
        if any(not item["actual_endpoint"] or not item["resource_type"] for item in report["routes"]):
            raise AssertionError("route contract is incomplete")
        print(f"OK: checked {len(report['routes'])} route records with independent states")
        return 0
    rendered = json.dumps(report, indent=2, ensure_ascii=False) if args.output and args.output.suffix == ".json" else yaml.safe_dump(report, allow_unicode=True, sort_keys=False)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
