#!/usr/bin/env python3
"""Validate embedded JavaScript used by actions/github-script workflow steps."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return value


def github_script_blocks(workflow: dict[str, Any], source: str) -> list[tuple[str, str]]:
    """Return labels and scripts for actions/github-script steps in one workflow."""
    jobs = workflow.get("jobs") or {}
    if not isinstance(jobs, dict):
        raise ValueError(f"{source}: jobs must be a mapping")

    blocks: list[tuple[str, str]] = []
    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            raise ValueError(f"{source}: job {job_id!r} must be a mapping")
        steps = job.get("steps") or []
        if not isinstance(steps, list):
            raise ValueError(f"{source}: job {job_id!r} steps must be a list")
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                raise ValueError(f"{source}: job {job_id!r} step {index} must be a mapping")
            uses = step.get("uses")
            if not isinstance(uses, str) or not uses.startswith("actions/github-script@"):
                continue
            config = step.get("with") or {}
            script = config.get("script") if isinstance(config, dict) else None
            label = f"{source}:{job_id}:step-{index}"
            if not isinstance(script, str) or not script.strip():
                raise ValueError(f"{label}: actions/github-script requires a non-empty with.script")
            blocks.append((label, script))
    return blocks


def check_javascript(script: str, label: str) -> str | None:
    """Return a syntax error message, or None when Node accepts the script.

    actions/github-script allows top-level await, so the extracted block is checked
    inside the async function boundary supplied by that action's runtime.
    """
    node = shutil.which("node")
    if node is None:
        return "node is required to validate actions/github-script syntax"

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", encoding="utf-8", delete=False
        ) as temporary:
            temporary.write("(async () => {\n")
            temporary.write(script)
            temporary.write("\n})();\n")
            temporary_path = Path(temporary.name)
        result = subprocess.run(
            [node, "--check", str(temporary_path)],
            check=False,
            capture_output=True,
            text=True,
        )
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    if result.returncode == 0:
        return None
    details = (result.stderr or result.stdout).strip()
    return f"{label}: node --check failed\n{details}"


def self_test() -> int:
    valid_script = "const code = '`';\nconst body = `Checked at: ${code}2026-07-23${code}`;\n"
    invalid_script = "const body = `Checked at: `${value}`;\n"
    fixture = {
        "jobs": {
            "fixture": {
                "steps": [
                    {"uses": "actions/checkout@v4"},
                    {"uses": "actions/github-script@v7", "with": {"script": valid_script}},
                ]
            }
        }
    }
    blocks = github_script_blocks(fixture, "self-test")
    if blocks != [("self-test:fixture:step-2", valid_script)]:
        print("ERROR: workflow self-test did not extract the expected script", file=sys.stderr)
        return 1
    valid_error = check_javascript(valid_script, "self-test valid")
    if valid_error is not None:
        print(f"ERROR: valid workflow script was rejected\n{valid_error}", file=sys.stderr)
        return 1
    invalid_error = check_javascript(invalid_script, "self-test invalid")
    if invalid_error is None:
        print("ERROR: invalid nested-backtick script was accepted", file=sys.stderr)
        return 1
    print("OK: workflow validator self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run embedded-script extraction and syntax fixtures")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    errors: list[str] = []
    workflow_paths = sorted([*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml")])
    block_count = 0
    for path in workflow_paths:
        try:
            blocks = github_script_blocks(load_yaml(path), str(path.relative_to(ROOT)))
        except (OSError, ValueError, yaml.YAMLError) as error:
            errors.append(str(error))
            continue
        for label, script in blocks:
            block_count += 1
            error = check_javascript(script, label)
            if error is not None:
                errors.append(error)

    if errors:
        print("ERROR: embedded workflow JavaScript validation failed", file=sys.stderr)
        print("\n\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: validated {block_count} embedded github-script block(s) in {len(workflow_paths)} workflow(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
