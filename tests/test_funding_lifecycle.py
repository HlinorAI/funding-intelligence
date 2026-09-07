from pathlib import Path

import pytest

from runtime.funding_lifecycle import apply_event, load_state, new_state, save_state


def test_lifecycle_requires_explicit_submission_evidence() -> None:
    state = new_state("route-1", "operator", "confirm eligibility")
    state = apply_event(state, "eligibility_confirmed", "operator", "prepare evidence pack")
    state = apply_event(state, "application_ready", "operator", "obtain final approval")

    with pytest.raises(ValueError, match="submission_recorded requires evidence_ref"):
        apply_event(state, "submission_recorded", "operator", "check for reply")


def test_lifecycle_reaches_outcome_only_after_recorded_submission() -> None:
    state = new_state("route-1", "operator", "confirm eligibility", now="2026-09-07T12:00:00Z")
    state = apply_event(state, "eligibility_confirmed", "operator", "prepare evidence pack", occurred_at="2026-09-07T12:01:00Z")
    state = apply_event(state, "application_ready", "operator", "submit after approval", occurred_at="2026-09-07T12:02:00Z")
    state = apply_event(state, "submission_recorded", "operator", "follow up in 14 days", evidence_ref="sent:message-1", occurred_at="2026-09-07T12:03:00Z")
    state = apply_event(state, "outcome_recorded", "operator", "archive decision evidence", evidence_ref="reply:message-2", outcome="rejected", occurred_at="2026-09-21T12:03:00Z")

    assert state["stage"] == "outcome"
    assert state["outcome"]["value"] == "rejected"
    assert [item["event"] for item in state["history"]] == [
        "eligibility_confirmed", "application_ready", "submission_recorded", "outcome_recorded"
    ]


def test_lifecycle_state_round_trips_locally(tmp_path: Path) -> None:
    path = tmp_path / "route-1.yaml"
    state = new_state("route-1", "operator", "confirm eligibility", now="2026-09-07T12:00:00Z")
    save_state(path, state)

    assert load_state(path)["route_id"] == "route-1"
