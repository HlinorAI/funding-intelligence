"""P2 tests for reproducible packaging and local privacy controls."""

from pathlib import Path
import subprocess
import sys

import tomllib

from runtime.privacy import redact_text, scan_text


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_declares_runtime_and_test_contract() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["requires-python"] == ">=3.11"
    assert "PyYAML>=6.0,<7.0" in project["project"]["dependencies"]
    assert "jsonschema>=4.20,<5.0" in project["project"]["dependencies"]
    assert "pytest>=7.0,<10.0" in project["project"]["optional-dependencies"]["test"]
    assert project["project"]["scripts"]["funding-check"] == "runtime.check:main"


def test_privacy_scan_reports_findings_without_leaking_values() -> None:
    sensitive_value = "".join(("api", "_key: synthetic-secret"))
    findings = scan_text(f"safe: true\n{sensitive_value}\n", "fixture")
    assert findings == [{"source": "fixture", "line": 2, "pattern": 2}]
    assert "synthetic-secret" not in "\n".join(str(item) for item in findings)
    assert "[REDACTED]" in redact_text(sensitive_value)


def test_privacy_cli_fails_closed_without_printing_secret(tmp_path: Path) -> None:
    sensitive_value = "".join(("api", "_key: synthetic-secret"))
    path = tmp_path / "input.yaml"
    path.write_text(sensitive_value, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "runtime.privacy", str(path)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "synthetic-secret" not in result.stderr
