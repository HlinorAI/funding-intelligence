"""Tests for the canonical human-readable report renderer."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import yaml

from runtime.render_report import render
from runtime.runner import build_report


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_render_accepts_real_runner_and_verifier_contracts(repo_root: Path) -> None:
    project = load_yaml(repo_root / "examples" / "example-ai-startup" / "project.yaml")
    runner_report = build_report(project)
    verifier_process = subprocess.run(
        [
            sys.executable,
            str(repo_root / "runtime" / "verify_route.py"),
            str(repo_root / "examples" / "example-ai-startup" / "project.yaml"),
            "--all-ai",
            "--evidence-dir",
            str(repo_root / "examples" / "example-ai-startup" / "evidence"),
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    rendered = render(runner_report, yaml.safe_load(verifier_process.stdout))
    assert "# Opportunity Report: Example AI Infrastructure Startup" in rendered
    assert "## BUILD_FIRST" in rendered
    assert "### Y Combinator" in rendered
    assert "## VERIFY_ACCESS_PATH" in rendered
    assert "### AWS Activate" in rendered
    assert "Stop condition:" in rendered
    assert "## Sources and verification dates" in rendered


def test_renderer_cli_writes_markdown_from_real_outputs(tmp_path: Path, repo_root: Path) -> None:
    runner_output = tmp_path / "runner.yaml"
    route_output = tmp_path / "routes.yaml"
    report_output = tmp_path / "opportunity-report.md"
    project_path = repo_root / "examples" / "example-ai-startup" / "project.yaml"
    evidence_dir = repo_root / "examples" / "example-ai-startup" / "evidence"

    subprocess.run(
        [sys.executable, str(repo_root / "runtime" / "runner.py"), str(project_path), "--output", str(runner_output)],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(repo_root / "runtime" / "verify_route.py"),
            str(project_path),
            "--all-ai",
            "--evidence-dir",
            str(evidence_dir),
            "--output",
            str(route_output),
        ],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(repo_root / "runtime" / "render_report.py"),
            str(runner_output),
            str(route_output),
            "--output",
            str(report_output),
        ],
        cwd=repo_root,
        check=True,
    )

    assert report_output.exists()
    assert "Human-readable rendering of deterministic runner" in report_output.read_text(encoding="utf-8")
