#!/usr/bin/env python3
"""Shared validation for the canonical Funding Intelligence project contract."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
PROJECT_SCHEMA_PATH = ROOT / "schemas" / "project.schema.yaml"


class ProjectValidationError(ValueError):
    """Raised when a project document does not satisfy the public contract."""


def normalize_yaml_scalars(value: Any) -> Any:
    """Convert YAML-native date objects to their schema representation."""

    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: normalize_yaml_scalars(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_yaml_scalars(item) for item in value]
    return value


def load_project_schema() -> dict[str, Any]:
    with PROJECT_SCHEMA_PATH.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream) or {}
    if not isinstance(value, dict):
        raise ProjectValidationError(f"Expected a schema mapping in {PROJECT_SCHEMA_PATH}")
    return value


def validate_project(project: dict[str, Any], source: str = "project") -> dict[str, Any]:
    """Validate and return a canonical project document."""

    if not isinstance(project, dict):
        raise ProjectValidationError(f"{source}: expected a project mapping")
    validator = Draft202012Validator(load_project_schema(), format_checker=FormatChecker())
    normalized = normalize_yaml_scalars(project)
    errors = sorted(validator.iter_errors(normalized), key=lambda error: [str(part) for part in error.absolute_path])
    if errors:
        details = []
        for error in errors[:10]:
            path = ".".join(str(part) for part in error.absolute_path) or "<root>"
            details.append(f"{path}: {error.message}")
        suffix = f"; plus {len(errors) - 10} more error(s)" if len(errors) > 10 else ""
        raise ProjectValidationError(f"{source}: invalid project contract: {'; '.join(details)}{suffix}")
    return project
