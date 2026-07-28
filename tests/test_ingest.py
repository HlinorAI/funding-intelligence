"""Tests for canonical project ingestion."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from runtime import ingest
from runtime.ingest import ingest_json, ingest_raw_text, validate_and_save
from runtime.project_contract import ProjectValidationError, validate_project
from runtime.runner import build_report


SAMPLE_RAW_TEXT = "We are building an AI-powered drone for pizza delivery in Estonia, seeking seed funding."
SAMPLE_JSON = {
    "project_name": "PizzaDrone AI",
    "description": "AI-powered drone for pizza delivery",
    "stage": "seed",
    "geography": {"country": "Estonia", "region": "Tallinn"},
    "domain": "AI",
    "funding_amount_usd": 100000,
    "team_background": "Former mobility engineers",
    "official_source": "https://example.invalid",
}


def test_raw_text_creates_valid_conservative_project() -> None:
    project = ingest_raw_text(SAMPLE_RAW_TEXT)
    validate_project(project)
    assert project["schema_version"] == 1
    assert project["name"] == "Unknown Project"
    assert project["description"] == SAMPLE_RAW_TEXT
    assert project["sector"] == ["unknown"]
    assert project["stage"] == "unknown"
    assert project["geography"] == ["unknown"]
    assert project["ingestion_metadata"]["confidence_score"] == 0.0
    assert project["needs_user_input"]


def test_empty_text_is_valid_and_does_not_infer_facts() -> None:
    project = ingest_raw_text("")
    validate_project(project)
    assert project["description"] == "No description provided."
    assert project["evidence"]["users"] == "unknown"
    assert project["needs"]["goals"] == []


def test_structured_json_maps_to_canonical_contract() -> None:
    project = ingest_json(SAMPLE_JSON)
    validate_project(project)
    assert project["name"] == "PizzaDrone AI"
    assert project["sector"] == ["artificial_intelligence"]
    assert project["stage"] == "seed"
    assert project["geography"] == ["Estonia", "Tallinn"]
    assert project["needs"]["funding"] == 100000
    assert project["needs"]["goals"] == ["funding"]
    assert project["evidence"]["site"] is True


def test_canonical_json_is_preserved_and_annotated(repo_root: Path) -> None:
    project = yaml.safe_load((repo_root / "examples" / "example-ai-startup" / "project.yaml").read_text())
    normalized = ingest_json(project)
    validate_project(normalized)
    assert normalized["name"] == project["name"]
    assert normalized["product"] == project["product"]
    assert normalized["ingestion_metadata"]["source_type"] == "structured_json"


def test_ingestion_output_runs_through_engine() -> None:
    report = build_report(ingest_json(SAMPLE_JSON))
    assert report["project"] == "PizzaDrone AI"
    assert report["classification"]["sectors"] == ["artificial_intelligence"]


def test_invalid_canonical_project_fails_closed() -> None:
    with pytest.raises(ProjectValidationError):
        validate_project({"name": "Incomplete"}, "test input")


def test_validate_and_save_uses_requested_absolute_path(tmp_path: Path) -> None:
    destination = tmp_path / "project.yaml"
    assert validate_and_save(ingest_json(SAMPLE_JSON), str(destination))
    saved = yaml.safe_load(destination.read_text())
    validate_project(saved)
    assert saved["name"] == "PizzaDrone AI"


def test_validate_and_save_rejects_invalid_project(tmp_path: Path) -> None:
    destination = tmp_path / "invalid.yaml"
    assert not validate_and_save({"name": "Incomplete"}, str(destination))
    assert not destination.exists()


def test_cli_json_ingestion_produces_runner_compatible_file(tmp_path: Path, repo_root: Path) -> None:
    source = tmp_path / "intake.json"
    destination = tmp_path / "project.yaml"
    source.write_text(json.dumps(SAMPLE_JSON), encoding="utf-8")
    ingest_process = subprocess.run(
        [
            sys.executable,
            str(repo_root / "runtime" / "ingest.py"),
            str(source),
            "--type",
            "json",
            "--output",
            str(destination),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert ingest_process.returncode == 0, ingest_process.stderr
    runner_process = subprocess.run(
        [sys.executable, str(repo_root / "runtime" / "runner.py"), str(destination)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert runner_process.returncode == 0, runner_process.stderr
    assert yaml.safe_load(runner_process.stdout)["project"] == "PizzaDrone AI"


def test_relative_output_remains_private(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ingest, "DRAFTS_DIR", tmp_path)
    assert validate_and_save(ingest_raw_text(SAMPLE_RAW_TEXT), "private-project.yaml")
    assert (tmp_path / "private-project.yaml").exists()


def test_runner_cli_rejects_invalid_project_without_traceback(tmp_path: Path, repo_root: Path) -> None:
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("name: Incomplete\n", encoding="utf-8")
    process = subprocess.run(
        [sys.executable, str(repo_root / "runtime" / "runner.py"), str(invalid)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert process.returncode == 2
    assert "invalid project contract" in process.stderr
    assert "Traceback" not in process.stderr
