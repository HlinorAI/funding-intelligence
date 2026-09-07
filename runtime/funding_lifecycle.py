#!/usr/bin/env python3
"""Local, explicit lifecycle state for a funding route.

This module records workflow progress; it never submits an application or
contacts a programme. Every transition requires an explicit local event,
actor, next action, and (where relevant) an evidence reference.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


STAGES = ("discovery", "eligibility", "application-ready", "follow-up", "outcome")
EVENT_TARGETS = {
    "eligibility_confirmed": ("discovery", "eligibility"),
    "application_ready": ("eligibility", "application-ready"),
    "submission_recorded": ("application-ready", "follow-up"),
    "outcome_recorded": ("follow-up", "outcome"),
}
OUTCOMES = ("accepted", "rejected", "withdrawn", "unknown")


def new_state(route_id: str, owner: str, next_action: str, *, now: str | None = None) -> dict[str, Any]:
    """Create a discovery-stage state without implying route eligibility."""

    return {
        "schema_version": 1,
        "route_id": _required(route_id, "route_id"),
        "stage": "discovery",
        "owner": _required(owner, "owner"),
        "next_action": _required(next_action, "next_action"),
        "submission": None,
        "outcome": None,
        "history": [],
        "updated_at": now or _now(),
    }


def apply_event(
    state: dict[str, Any],
    event: str,
    actor: str,
    next_action: str,
    *,
    evidence_ref: str | None = None,
    outcome: str | None = None,
    occurred_at: str | None = None,
) -> dict[str, Any]:
    """Apply one explicit local transition and return a copied state."""

    validate_state(state)
    actor = _required(actor, "actor")
    next_action = _required(next_action, "next_action")
    if event not in EVENT_TARGETS:
        raise ValueError(f"unsupported lifecycle event: {event}")
    source, target = EVENT_TARGETS[event]
    if state["stage"] != source:
        raise ValueError(f"event {event} requires stage {source}, got {state['stage']}")
    timestamp = occurred_at or _now()
    _validate_timestamp(timestamp, "occurred_at")
    if event == "submission_recorded" and (not isinstance(evidence_ref, str) or not evidence_ref.strip()):
        raise ValueError("submission_recorded requires evidence_ref")
    if event == "outcome_recorded" and outcome not in OUTCOMES:
        raise ValueError(f"outcome_recorded requires one of: {', '.join(OUTCOMES)}")

    next_state = dict(state)
    next_state["stage"] = target
    next_state["owner"] = actor
    next_state["next_action"] = next_action
    next_state["updated_at"] = timestamp
    next_state["history"] = [*state["history"], {
        "event": event,
        "from_stage": source,
        "to_stage": target,
        "actor": actor,
        "occurred_at": timestamp,
        **({"evidence_ref": evidence_ref} if evidence_ref else {}),
        **({"outcome": outcome} if outcome else {}),
    }]
    if event == "submission_recorded":
        next_state["submission"] = {"recorded_at": timestamp, "evidence_ref": evidence_ref}
    if event == "outcome_recorded":
        next_state["outcome"] = {"value": outcome, "recorded_at": timestamp, "evidence_ref": evidence_ref}
    validate_state(next_state)
    return next_state


def validate_state(state: dict[str, Any]) -> None:
    if state.get("schema_version") != 1:
        raise ValueError("lifecycle state schema_version must be 1")
    if not isinstance(state.get("route_id"), str) or not state["route_id"].strip():
        raise ValueError("lifecycle state requires route_id")
    if state.get("stage") not in STAGES:
        raise ValueError(f"lifecycle state stage must be one of: {', '.join(STAGES)}")
    _required(state.get("owner"), "owner")
    _required(state.get("next_action"), "next_action")
    if not isinstance(state.get("history"), list):
        raise ValueError("lifecycle state history must be a list")
    _validate_timestamp(state.get("updated_at"), "updated_at")
    if state["stage"] == "follow-up" and not state.get("submission"):
        raise ValueError("follow-up state requires recorded submission evidence")
    if state["stage"] == "outcome":
        if not state.get("outcome") or state["outcome"].get("value") not in OUTCOMES:
            raise ValueError("outcome state requires a recorded outcome")


def load_state(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise ValueError("lifecycle state must be a YAML mapping")
    validate_state(value)
    return value


def save_state(path: Path, state: dict[str, Any]) -> None:
    validate_state(state)
    path.write_text(yaml.safe_dump(state, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _required(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value.strip()


def _validate_timestamp(value: Any, field: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an RFC3339 timestamp")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an RFC3339 timestamp") from exc


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("--init-route")
    parser.add_argument("--owner")
    parser.add_argument("--event", choices=sorted(EVENT_TARGETS))
    parser.add_argument("--actor")
    parser.add_argument("--next-action")
    parser.add_argument("--evidence-ref")
    parser.add_argument("--outcome", choices=OUTCOMES)
    args = parser.parse_args()

    if args.init_route:
        if args.state.exists():
            raise SystemExit(f"refusing to overwrite existing state: {args.state}")
        save_state(args.state, new_state(args.init_route, args.owner or "", args.next_action or ""))
    else:
        if not args.event:
            parser.error("--event is required when updating existing state")
        state = load_state(args.state)
        save_state(args.state, apply_event(
            state,
            args.event,
            args.actor or "",
            args.next_action or "",
            evidence_ref=args.evidence_ref,
            outcome=args.outcome,
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
