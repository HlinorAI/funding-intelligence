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
