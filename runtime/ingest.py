#!/usr/bin/env python3
"""Create a canonical project document from raw text or structured JSON."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any

import yaml

try:
    from runtime.project_contract import ProjectValidationError, validate_project
except ImportError:
    from project_contract import ProjectValidationError, validate_project


ROOT = Path(__file__).resolve().parents[1]
DRAFTS_DIR = ROOT / "drafts"
UNKNOWN = "unknown"
STAGE_ALIASES = {
    "pre-seed": "pre_seed",
    "preseed": "pre_seed",
    "early product": "early_product",
    "growth": "revenue",
}
SECTOR_ALIASES = {
    "ai": "artificial_intelligence",
    "artificial intelligence": "artificial_intelligence",
    "saas": "software",
}


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def as_text(value: Any, fallback: str = UNKNOWN) -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def normalize_stage(value: Any) -> str:
    stage = as_text(value).lower().replace(" ", "_")
    return STAGE_ALIASES.get(stage.replace("_", "-"), stage)


def normalize_sector(value: Any) -> list[str]:
    values = value if isinstance(value, list) else [value]
    sectors = []
    for item in values:
        token = re.sub(r"[^a-z0-9]+", "_", as_text(item).lower()).strip("_")
        token = SECTOR_ALIASES.get(token.replace("_", " "), token)
        if token and token not in sectors:
            sectors.append(token)
    return sectors or [UNKNOWN]


def normalize_geography(value: Any) -> list[str]:
    if isinstance(value, dict):
        values = [value.get("country"), value.get("region")]
    elif isinstance(value, list):
        values = value
    else:
        values = [value]
    result = [as_text(item) for item in values if item is not None and item != ""]
    return list(dict.fromkeys(result)) or [UNKNOWN]


def empty_project(description: str) -> dict[str, Any]:
    project_description = as_text(description, "No description provided.")
    return {
        "schema_version": 1,
        "name": "Unknown Project",
        "description": project_description,
        "sector": [UNKNOWN],
        "stage": UNKNOWN,
        "geography": [UNKNOWN],
        "product": {"description": project_description},
        "evidence": {
            "site": UNKNOWN,
            "github": UNKNOWN,
            "live_demo": UNKNOWN,
            "live_deployment": UNKNOWN,
            "users": UNKNOWN,
            "revenue": UNKNOWN,
            "pilots": UNKNOWN,
            "partners": UNKNOWN,
            "metrics": UNKNOWN,
        },
        "needs": {"goals": []},
        "constraints": {
            "no_token": UNKNOWN,
            "no_dilution": UNKNOWN,
            "generic_multichain": UNKNOWN,
            "native_ecosystems": [],
            "target_ecosystems": [],
        },
        "readiness": {"budget": UNKNOWN, "milestones": UNKNOWN},
        "access": {"champions": UNKNOWN, "warm_intros": UNKNOWN},
        "needs_user_input": ["name", "sector", "stage", "geography", "needs.goals"],
        "ingestion_metadata": {
            "source_type": "raw_text",
            "confidence_score": 0.0,
            "timestamp": timestamp(),
        },
    }


def ingest_raw_text(raw_text: str) -> dict[str, Any]:
    """Return a safe canonical scaffold without inferring facts from prose."""

    return validate_project(empty_project(raw_text), "raw-text ingestion")


def is_canonical_project(value: dict[str, Any]) -> bool:
    return value.get("schema_version") == 1 and all(
        field in value for field in ("name", "sector", "product", "evidence", "needs", "constraints")
    )


def ingest_json(json_data: dict[str, Any]) -> dict[str, Any]:
    """Normalize structured JSON into the canonical project contract."""

    source = deepcopy(json_data)
    if is_canonical_project(source):
        project = source
        project.setdefault("needs_user_input", [])
        project["ingestion_metadata"] = {
            "source_type": "structured_json",
            "confidence_score": 1.0,
            "timestamp": timestamp(),
        }
        return validate_project(project, "structured JSON ingestion")

    description = as_text(source.get("description"), "No description provided.")
    official_source = source.get("official_source")
    funding = source.get("funding_amount_usd")
    project = empty_project(description)
    project.update(
        {
            "name": as_text(source.get("project_name")),
            "sector": normalize_sector(source.get("domain")),
            "stage": normalize_stage(source.get("stage")),
            "geography": normalize_geography(source.get("geography")),
            "product": {"description": description},
            "team_background": as_text(source.get("team_background")),
            "needs_user_input": list(source.get("needs_user_input") or []),
            "ingestion_metadata": {
                "source_type": "structured_json",
                "confidence_score": 1.0,
                "timestamp": timestamp(),
            },
        }
    )
    if official_source:
        project["official_sources"] = [as_text(official_source)]
        project["evidence"]["site"] = True
    if isinstance(funding, (int, float)) and not isinstance(funding, bool) and funding >= 0:
        project["needs"]["funding"] = funding
        project["needs"]["goals"] = ["funding"]
    elif funding not in {None, "", UNKNOWN}:
        project["needs"]["funding"] = funding
        project["needs"]["goals"] = ["funding"]
    return validate_project(project, "structured JSON ingestion")


def output_path(filename: str) -> Path:
    path = Path(filename)
    return path if path.is_absolute() else DRAFTS_DIR / path


def validate_and_save(data: dict[str, Any], output_filename: str = "project.yaml") -> bool:
    try:
        validate_project(data, "ingestion output")
        destination = output_path(output_filename)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"Success: validated canonical project saved to {destination}")
        if data.get("needs_user_input"):
            print(f"Needs user input: {', '.join(data['needs_user_input'])}")
        return True
    except (ProjectValidationError, OSError) as error:
        print(f"Validation error: {error}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Raw text string or path to a JSON file")
    parser.add_argument("--type", choices=["text", "json", "auto"], default="auto", help="Input type")
    parser.add_argument("--output", default="project.yaml", help="Output path; relative paths are stored in drafts/")
    args = parser.parse_args()

    input_type = args.type
    input_path = Path(args.input)
    if input_type == "auto":
        input_type = "json" if input_path.suffix.lower() == ".json" and input_path.exists() else "text"

    try:
        if input_type == "json":
            data = json.loads(input_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("JSON input must be an object")
            project = ingest_json(data)
        else:
            project = ingest_raw_text(args.input)
    except (OSError, ValueError, ProjectValidationError, json.JSONDecodeError) as error:
        print(f"Ingestion failed: {error}", file=sys.stderr)
        return 1

    return 0 if validate_and_save(project, args.output) else 1


if __name__ == "__main__":
    raise SystemExit(main())
