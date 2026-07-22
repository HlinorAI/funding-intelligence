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
PROJECT_PATHS = sorted((ROOT / "tests" / "cases").glob("*.yaml"))

DECISION_VALUES = {"NOW", "NEXT", "LATER", "VERIFY_FIRST", "BUILD_FIRST", "DO_NOT_APPLY"}
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
CREDENTIAL_PATTERNS = (
    re.compile(r"(?:ghp_|github_pat_|sk-[A-Za-z0-9]|AKIA[0-9A-Z]{16})"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?:api[_-]?key|secret|password)\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/"),
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


def validate_public_tracking(errors: list[str]) -> None:
    files = tracked_files()
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
        for pattern in CREDENTIAL_PATTERNS:
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
    validate_public_tracking(errors)
    validate_generated_reports(report_schema, route_schema, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: schemas validated {len(PROGRAM_CARD_PATHS)} program cards, {len(PROJECT_PATHS)} projects, public reports, route verification, issue forms, and tracked-file privacy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
