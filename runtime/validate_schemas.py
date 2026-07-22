#!/usr/bin/env python3
"""Validate public project, program, report, route, and repository contracts."""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"

PROGRAM_CARD_PATHS = sorted((ROOT / "knowledge" / "programs").glob("*.yaml"))
PROGRAM_CARD_PATHS += sorted((ROOT / "knowledge" / "packs").glob("*/programs/*.yaml"))
AI_PROGRAM_CARD_PATHS = sorted((ROOT / "knowledge" / "packs" / "ai" / "programs").glob("*.yaml"))
PROJECT_PATHS = sorted((ROOT / "tests" / "cases").glob("*.yaml"))
EXAMPLE_DIR = ROOT / "examples" / "example-ai-startup"
EXAMPLE_PROJECT_PATH = EXAMPLE_DIR / "project.yaml"
EXAMPLE_EXPECTED_PATH = EXAMPLE_DIR / "expected-report.yaml"

DECISION_VALUES = {"NOW", "NEXT", "LATER", "VERIFY_FIRST", "BUILD_FIRST", "DO_NOT_APPLY", "APPLY_AGAIN_AFTER_CHANGE"}
RESOURCE_TYPES = {
    "startup_program",
    "cloud_credits",
    "technical_support",
    "enterprise_bd",
    "accelerator",
    "venture_investment",
    "founder_network",
    "community",
}
SUPPORT_RESOURCES = {"startup_program", "cloud_credits", "technical_support", "enterprise_bd", "community"}
CAPITAL_RESOURCES = {"accelerator", "venture_investment", "founder_network"}
ALLOWED_FORM_TYPES = {"markdown", "input", "textarea", "dropdown", "checkboxes"}

PRIVATE_PATH_PATTERNS = (
    re.compile(r"^evidence/hlinor(?:/|$)"),
    re.compile(r"^tests/live(?:/|$)"),
    re.compile(r"^tests/expected/hlinor\.yaml$"),
    re.compile(r"^history/(applications|feedback)\.yaml$"),
    re.compile(r"^reports(?:/|$)"),
)


def credential_patterns() -> tuple[re.Pattern[str], ...]:
    """Build credential signatures without storing complete token prefixes in source."""

    provider_prefixes = (
        "".join(("gh", "p_")),
        "".join(("github_", "pat_")),
        "".join(("sk", "-")),
        "AKIA",
    )
    provider_tokens = "|".join(
        (
            re.escape(provider_prefixes[0]),
            re.escape(provider_prefixes[1]),
            f"{re.escape(provider_prefixes[2])}[A-Za-z0-9]",
            f"{re.escape(provider_prefixes[3])}[0-9A-Z]{{16}}",
        )
    )
    private_key_marker = "".join(("-" * 5, "BEGIN "))
    private_key_suffix = "".join((" KEY", "-" * 5))
    credential_fields = "|".join(
        (
            "".join(("api", r"[_-]?", "key")),
            "".join(("sec", "ret")),
            "".join(("pass", "word")),
        )
    )
    private_path_roots = "|".join(("Users", "home"))
    return (
        re.compile(f"(?:{provider_tokens})"),
        re.compile(f"{re.escape(private_key_marker)}[A-Z ]*{re.escape(private_key_suffix)}"),
        re.compile(f"(?:{credential_fields})" + r"\s*[:=]\s*\S+", re.IGNORECASE),
        re.compile(f"/(?:{private_path_roots})/" + r"[A-Za-z0-9_.-]+/"),
    )


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def normalize_dates(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: normalize_dates(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_dates(item) for item in value]
    return value


def schema(name: str) -> dict[str, Any]:
    value = normalize_dates(load_yaml(SCHEMA_DIR / name))
    Draft202012Validator.check_schema(value)
    return value


def validate_document(value: Any, schema_value: dict[str, Any], path: Path, errors: list[str]) -> None:
    validator = Draft202012Validator(schema_value)
    for error in sorted(validator.iter_errors(value), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "$"
        errors.append(f"{path.relative_to(ROOT)}:{location}: {error.message}")


def validate_program_card(path: Path, card_schema: dict[str, Any], errors: list[str]) -> None:
    card = normalize_dates(load_yaml(path))
    validate_document(card, card_schema, path, errors)
    if not isinstance(card, dict):
        return

    status = card.get("status") or {}
    if not status.get("official_source"):
        errors.append(f"{path.relative_to(ROOT)}: status.official_source is required")
    if not status.get("last_checked"):
        errors.append(f"{path.relative_to(ROOT)}: status.last_checked is required")
    if "verification" in card:
        verification = card.get("verification") or {}
        for field in ("verified_at", "source_verified", "actual_endpoint"):
            if field not in verification:
                errors.append(f"{path.relative_to(ROOT)}: verification.{field} is required when verification is present")

    route_requirements = card.get("evidence_requirements")
    if path in AI_PROGRAM_CARD_PATHS:
        if not isinstance(route_requirements, dict):
            errors.append(f"{path.relative_to(ROOT)}: evidence_requirements is required for AI pack cards")
        else:
            mechanisms = {str(value) for value in card.get("mechanism", [])}
            missing_routes = sorted(mechanisms - set(route_requirements))
            if missing_routes:
                errors.append(f"{path.relative_to(ROOT)}: missing evidence_requirements for mechanisms {missing_routes}")
    if isinstance(route_requirements, dict):
        for route, requirements in route_requirements.items():
            if not isinstance(requirements, list) or not requirements or not all(isinstance(item, str) and item.strip() for item in requirements):
                errors.append(f"{path.relative_to(ROOT)}: evidence_requirements.{route} must be a non-empty string list")

    resource_types = card.get("resource_type")
    if resource_types is not None:
        unknown = sorted(set(resource_types) - RESOURCE_TYPES) if isinstance(resource_types, list) else []
        if unknown:
            errors.append(f"{path.relative_to(ROOT)}: unknown resource_type values: {unknown}")
        families = set()
        if isinstance(resource_types, list):
            if set(resource_types) & SUPPORT_RESOURCES:
                families.add("support")
            if set(resource_types) & CAPITAL_RESOURCES:
                families.add("capital")
        if len(families) > 1:
            errors.append(f"{path.relative_to(ROOT)}: resource_type mixes support and capital resources")


def validate_expected_fixtures(errors: list[str]) -> None:
    for path in sorted((ROOT / "tests" / "expected").glob("*.yaml")):
        if path.name == "hlinor.yaml":
            continue
        value = normalize_dates(load_yaml(path))
        if not isinstance(value, dict):
            errors.append(f"{path.relative_to(ROOT)}: expected fixture must be a mapping")
            continue
        if not isinstance(value.get("decision"), str) or value["decision"] not in DECISION_VALUES:
            errors.append(f"{path.relative_to(ROOT)}: decision must be a known runner decision")
        if "must_include" in value and not isinstance(value["must_include"], (str, list)):
            errors.append(f"{path.relative_to(ROOT)}: must_include must be a string or list")
        if not isinstance(value.get("must_not_be_now"), bool):
            errors.append(f"{path.relative_to(ROOT)}: must_not_be_now must be boolean")
        if not isinstance(value.get("gate_passed"), bool):
            errors.append(f"{path.relative_to(ROOT)}: gate_passed must be boolean")


def validate_issue_forms(errors: list[str]) -> None:
    directory = ROOT / ".github" / "ISSUE_TEMPLATE"
    forms = sorted(directory.glob("*.yml"))
    if not forms:
        errors.append(".github/ISSUE_TEMPLATE: at least one issue form is required")
        return
    for path in forms:
        value = normalize_dates(load_yaml(path))
        relative = path.relative_to(ROOT)
        if path.name == "config.yml":
            if not isinstance(value, dict) or not isinstance(value.get("blank_issues_enabled"), bool):
                errors.append(f"{relative}: blank_issues_enabled must be boolean")
            continue
        if not isinstance(value, dict):
            errors.append(f"{relative}: issue form must be a mapping")
            continue
        for field in ("name", "description", "body"):
            if field not in value:
                errors.append(f"{relative}: missing required field {field}")
        body = value.get("body")
        if not isinstance(body, list):
            continue
        ids: list[str] = []
        for index, item in enumerate(body):
            if not isinstance(item, dict):
                errors.append(f"{relative}: body[{index}] must be a mapping")
                continue
            item_type = item.get("type")
            if item_type not in ALLOWED_FORM_TYPES:
                errors.append(f"{relative}: body[{index}] has unknown type {item_type!r}")
            item_id = item.get("id")
            if item_type != "markdown":
                if not isinstance(item_id, str) or not item_id:
                    errors.append(f"{relative}: body[{index}] requires a non-empty id")
                elif item_id in ids:
                    errors.append(f"{relative}: duplicate body id {item_id}")
                else:
                    ids.append(item_id)


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True)
    return [item for item in result.stdout.decode().split("\0") if item]


def validate_credential_scanner(errors: list[str]) -> None:
    """Regression-test credential detection and guard against scanner self-matches."""

    provider_prefixes = (
        "".join(("gh", "p_")),
        "".join(("github_", "pat_")),
        "".join(("sk", "-")),
        "AKIA",
    )
    examples = (
        ("provider token 1", provider_prefixes[0] + "synthetic"),
        ("provider token 2", provider_prefixes[1] + "synthetic"),
        ("provider token 3", provider_prefixes[2] + "A"),
        ("provider token 4", provider_prefixes[3] + "A" * 16),
        ("private key marker", "".join(("-" * 5, "BEGIN ", "RSA ", "PRIVATE KEY", "-" * 5))),
        ("credential assignment", "".join(("api", "_key: synthetic"))),
        ("private path", "/" + "Users" + "/example/private/file"),
    )
    patterns = credential_patterns()
    for label, example in examples:
        if not any(pattern.search(example) for pattern in patterns):
            errors.append(f"credential scanner regression: did not detect {label}")

    source = Path(__file__).read_text(encoding="utf-8")
    if any(pattern.search(source) for pattern in patterns):
        errors.append("credential scanner regression: validator source matches its own signatures")


def validate_public_tracking(errors: list[str]) -> None:
    files = tracked_files()
    patterns = credential_patterns()
    for path in files:
        if any(pattern.search(path) for pattern in PRIVATE_PATH_PATTERNS):
            errors.append(f"tracked private path: {path}")
        absolute = ROOT / path
        if not absolute.is_file():
            continue
        try:
            text = absolute.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in patterns:
            if pattern.search(text):
                errors.append(f"credential or private-path pattern in tracked file {path}: {pattern.pattern}")


def validate_yaml_syntax(errors: list[str]) -> None:
    for relative in tracked_files():
        path = ROOT / relative
        if path.suffix.lower() not in {".yaml", ".yml"} or any(pattern.search(relative) for pattern in PRIVATE_PATH_PATTERNS):
            continue
        try:
            load_yaml(path)
        except Exception as error:
            errors.append(f"{relative}: invalid YAML: {error}")


def validate_generated_reports(report_schema: dict[str, Any], route_schema: dict[str, Any], errors: list[str]) -> None:
    sys.path.insert(0, str(ROOT / "runtime"))
    from runner import build_report, load_yaml as runner_load_yaml

    for project_path in PROJECT_PATHS:
        report = normalize_dates(build_report(runner_load_yaml(project_path)))
        validate_document(report, report_schema, project_path.with_name(f"{project_path.stem}.generated-report.yaml"), errors)

    command = [
        sys.executable,
        str(ROOT / "runtime" / "verify_route.py"),
        str(ROOT / "tests" / "cases" / "web3.yaml"),
        "--route",
        "base-funding-ladder",
    ]
    process = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    validate_document(normalize_dates(yaml.safe_load(process.stdout)), route_schema, ROOT / "tests" / "cases" / "web3.route-verification.yaml", errors)

    sample_path = ROOT / "examples" / "sample_report.yaml"
    if sample_path.exists():
        validate_document(normalize_dates(load_yaml(sample_path)), route_schema, sample_path, errors)


def validate_public_example(
    project_schema: dict[str, Any], report_schema: dict[str, Any], route_schema: dict[str, Any], errors: list[str]
) -> None:
    required_files = [
        EXAMPLE_PROJECT_PATH,
        EXAMPLE_EXPECTED_PATH,
        *(EXAMPLE_DIR / "evidence").glob("*.yaml"),
    ]
    missing_files = [path for path in required_files if not path.exists()]
    for path in missing_files:
        errors.append(f"public example missing file: {path.relative_to(ROOT)}")
    if missing_files or not EXAMPLE_PROJECT_PATH.exists():
        return

    project = normalize_dates(load_yaml(EXAMPLE_PROJECT_PATH))
    validate_document(project, project_schema, EXAMPLE_PROJECT_PATH, errors)
    sys.path.insert(0, str(ROOT / "runtime"))
    from runner import build_report, load_yaml as runner_load_yaml

    generated_report = normalize_dates(build_report(runner_load_yaml(EXAMPLE_PROJECT_PATH)))
    validate_document(generated_report, report_schema, EXAMPLE_PROJECT_PATH.with_name("generated-report.yaml"), errors)

    expected = normalize_dates(load_yaml(EXAMPLE_EXPECTED_PATH))
    if not isinstance(expected, dict):
        errors.append(f"{EXAMPLE_EXPECTED_PATH.relative_to(ROOT)}: expected report must be a mapping")
        return
    runner_expectation = expected.get("runner") or {}
    generated_opportunities = {item["program_id"]: item for item in generated_report["opportunities"]}
    if generated_report["project"] != expected.get("project"):
        errors.append(f"{EXAMPLE_EXPECTED_PATH.relative_to(ROOT)}: project does not match generated report")
    primary = generated_report["opportunities"][0]["decision"] if generated_report["opportunities"] else None
    if primary != runner_expectation.get("primary_decision"):
        errors.append(f"{EXAMPLE_EXPECTED_PATH.relative_to(ROOT)}: primary runner decision changed")
    if generated_report["gate"]["passed"] != runner_expectation.get("gate_passed"):
        errors.append(f"{EXAMPLE_EXPECTED_PATH.relative_to(ROOT)}: runner gate result changed")
    for route in runner_expectation.get("opportunities", []):
        program_id = route.get("program_id")
        actual = generated_opportunities.get(program_id)
        if actual is None:
            errors.append(f"{EXAMPLE_EXPECTED_PATH.relative_to(ROOT)}: missing generated route {program_id}")
        elif actual["decision"] != route.get("decision"):
            errors.append(f"{EXAMPLE_EXPECTED_PATH.relative_to(ROOT)}: decision changed for {program_id}")
    if runner_expectation.get("must_not_be_now") and any(item["decision"] == "NOW" for item in generated_report["opportunities"]):
        errors.append(f"{EXAMPLE_EXPECTED_PATH.relative_to(ROOT)}: an unverified opportunity reached NOW")

    command = [
        sys.executable,
        str(ROOT / "runtime" / "verify_route.py"),
        str(EXAMPLE_PROJECT_PATH),
        "--all-ai",
        "--evidence-dir",
        str(EXAMPLE_DIR / "evidence"),
    ]
    process = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    route_report = normalize_dates(yaml.safe_load(process.stdout))
    validate_document(route_report, route_schema, EXAMPLE_EXPECTED_PATH, errors)
    expected_decisions = (expected.get("verifier") or {}).get("decisions") or {}
    actual_decisions = {item["program_id"]: item["decision"] for item in route_report.get("routes", [])}
    if len(route_report.get("routes", [])) != (expected.get("verifier") or {}).get("route_count"):
        errors.append(f"{EXAMPLE_EXPECTED_PATH.relative_to(ROOT)}: verifier route count changed")
    for program_id, decision in expected_decisions.items():
        if actual_decisions.get(program_id) != decision:
            errors.append(f"{EXAMPLE_EXPECTED_PATH.relative_to(ROOT)}: verifier decision changed for {program_id}")


def main() -> int:
    errors: list[str] = []
    project_schema = schema("project.schema.yaml")
    program_schema = schema("program-card.schema.yaml")
    route_schema = schema("route-verification.schema.yaml")
    report_schema = schema("report.schema.yaml")

    for path in PROGRAM_CARD_PATHS:
        validate_program_card(path, program_schema, errors)
    for path in PROJECT_PATHS:
        validate_document(normalize_dates(load_yaml(path)), project_schema, path, errors)
    validate_expected_fixtures(errors)
    validate_issue_forms(errors)
    validate_yaml_syntax(errors)
    validate_credential_scanner(errors)
    validate_public_tracking(errors)
    validate_generated_reports(report_schema, route_schema, errors)
    validate_public_example(project_schema, report_schema, route_schema, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: schemas validated {len(PROGRAM_CARD_PATHS)} program cards, {len(PROJECT_PATHS)} projects, public reports, route verification, issue forms, and tracked-file privacy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
