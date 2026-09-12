"""Shared freshness policy for dated program-source snapshots."""

from __future__ import annotations

from datetime import date
from typing import Any


SOURCE_FRESHNESS_DAYS = 7


def source_freshness(
    last_checked: Any,
    *,
    today: date | None = None,
    max_age_days: int = SOURCE_FRESHNESS_DAYS,
) -> dict[str, Any]:
    """Classify a source snapshot without treating an invalid date as fresh."""

    if isinstance(last_checked, date):
        checked = last_checked
    else:
        try:
            checked = date.fromisoformat(str(last_checked))
        except (TypeError, ValueError):
            checked = None

    if checked is None:
        return {"state": "unknown", "age_days": None, "max_age_days": max_age_days}

    reference_date = today or date.today()
    age_days = (reference_date - checked).days
    if age_days < 0:
        state = "future"
    elif age_days <= max_age_days:
        state = "fresh"
    else:
        state = "stale"
    return {"state": state, "age_days": age_days, "max_age_days": max_age_days}


def pathway_window_state(pathway: Any, *, today: date | None = None) -> dict[str, Any]:
    """Classify a declared pathway application window.

    A card without a declared window is ``unknown`` and stays subject to the
    normal status gates; a declared window is a hard temporal boundary.
    """

    window = pathway.get("window") if isinstance(pathway, dict) else None
    if not isinstance(window, dict):
        return {"state": "unknown", "opens": None, "closes": None}

    reference = today or date.today()

    def parse(value: Any) -> date | None:
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value))
        except (TypeError, ValueError):
            return None

    opens = parse(window.get("opens"))
    closes = parse(window.get("closes"))
    if closes is not None and reference > closes:
        state = "closed"
    elif opens is not None and reference < opens:
        state = "not_open"
    elif closes is not None or opens is not None:
        state = "open"
    else:
        state = "unknown"
    return {
        "state": state,
        "opens": opens.isoformat() if opens else None,
        "closes": closes.isoformat() if closes else None,
    }
