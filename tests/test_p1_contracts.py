"""Focused P1 contract tests for vocabulary and program provenance."""

from pathlib import Path

import jsonschema
import yaml

from runtime.ingest import normalize_sector, normalize_stage
from runtime.taxonomy import canonicalize


ROOT = Path(__file__).resolve().parents[1]


def load_schema(name: str) -> dict:
    return yaml.safe_load((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def test_controlled_vocabulary_resolves_aliases() -> None:
    assert normalize_sector(["GenAI", "SaaS", "physical ai"]) == [
        "artificial_intelligence",
        "software",
        "hardware",
    ]
    assert normalize_stage("series-a") == "series_a"
    assert canonicalize("ETH", "ecosystems") == "ethereum"


def test_program_provenance_contract_accepts_review_metadata() -> None:
    card = {
        "id": "provenance-example",
        "name": "Provenance Example",
        "ecosystem": "Ethereum",
        "mechanism": ["proposal_grant"],
        "status": {
            "state": "OPEN",
            "last_checked": "2026-08-14",
            "needs_verification": True,
            "official_source": "https://example.com/program",
        },
        "provenance": {
            "source_snapshot_hash": "a" * 64,
            "semantic_reviewed_at": "2026-08-14T12:00:00Z",
            "reviewer": "reviewer@example.com",
            "change_type": "eligibility",
            "deadline": None,
            "eligibility_version": "2026-08-14.1",
            "confidence": "medium",
            "diff_review": {"status": "reviewed", "reviewed_at": "2026-08-14T12:05:00Z", "reviewer": "reviewer@example.com"},
        },
        "best_fit": ["example project"],
        "bad_fit": ["unrelated project"],
        "required_evidence": ["project overview"],
        "score": {"strategic_fit": 1, "evidence": 1, "mechanism_fit": 1},
        "failure_modes": ["stale source"],
        "next_action": {"action": "VERIFY", "deliverable": "Confirm intake", "horizon_days": 1},
        "stop_condition": "No current source",
    }
    jsonschema.Draft202012Validator(load_schema("program-card.schema.yaml")).validate(card)
