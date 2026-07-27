"""
Tests for runtime/report.py - Human-Readable Reporting Layer
"""
import pytest
import yaml
from pathlib import Path
from runtime.report import render_cli_report, render_markdown_report, get_decision_icon

@pytest.fixture
def sample_project_draft(tmp_path):
    draft = {
        "project_name": "TestAI",
        "description": "AI for testing",
        "stage": "seed",
        "geography": {"country": "US"},
        "domain": "AI",
        "needs_user_input": ["funding_amount_usd"]
    }
    path = tmp_path / "draft.yaml"
    with open(path, "w") as f:
        yaml.dump(draft, f)
    return draft

@pytest.fixture
def sample_runner_output(tmp_path):
    output = {
        "decision": "NOW",
        "match_score": 90,
        "routes": [
            {"program_name": "Y Combinator", "decision": "NOW", "official_source": "https://ycombinator.com"}
        ]
    }
    path = tmp_path / "output.yaml"
    with open(path, "w") as f:
        yaml.dump(output, f)
    return output

class TestReportIcons:
    def test_decision_icons(self):
        assert get_decision_icon("NOW") == "✅"
        assert get_decision_icon("VERIFY_FIRST") == "⚠️"
        assert get_decision_icon("DO_NOT_APPLY") == "❌"
        assert get_decision_icon("UNKNOWN_DECISION") == "❓"

class TestMarkdownExport:
    def test_markdown_generation(self, tmp_path, sample_project_draft, sample_runner_output):
        output_path = tmp_path / "test_report.md"
        render_markdown_report(sample_project_draft, sample_runner_output, output_path)
        
        assert output_path.exists()
        content = output_path.read_text()
        
        assert "# Match Report: TestAI" in content
        assert "**Decision:** NOW" in content
        assert "**Match Score:** 90" in content
        assert "Y Combinator" in content
        assert "funding_amount_usd" in content

class TestCLIReport:
    def test_cli_render_no_crash(self, capsys, sample_project_draft, sample_runner_output):
        # Просто проверяем, что функция выполняется без ошибок и выводит в консоль
        render_cli_report(sample_project_draft, sample_runner_output)
        captured = capsys.readouterr()
        assert "MATCH REPORT: TestAI" in captured.out
        assert "Y Combinator" in captured.out
