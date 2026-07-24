"""Shared fixtures for Funding Intelligence tests."""

from pathlib import Path
import sys
import yaml
import pytest

# Ensure runtime/ is on the path for runner imports
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

CASES_DIR = REPO_ROOT / "tests" / "cases"
EXPECTED_DIR = REPO_ROOT / "tests" / "expected"


def load_yaml(path: Path) -> dict:
    """Load a YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a mapping")
    return data


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


def pytest_generate_tests(metafunc):
    """Parametrize tests with (case_name, case_path, expected_path) tuples."""
    if "test_case" in metafunc.fixturenames:
        case_files = sorted(CASES_DIR.glob("*.yaml"))
        params = []
        for cf in case_files:
            case_name = cf.stem
            expected = EXPECTED_DIR / f"{case_name}.yaml"
            params.append(pytest.param(
                case_name,
                cf,
                expected,
                id=case_name,
            ))
        metafunc.parametrize("test_case", params)
