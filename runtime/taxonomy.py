"""Canonical vocabulary and alias resolution for ingestion and routing."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = ROOT / "knowledge" / "taxonomy.yaml"


def normalize_label(value: Any) -> str:
    """Normalize a label without assigning it a semantic category."""

    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


@lru_cache(maxsize=1)
def load_taxonomy() -> dict[str, dict[str, list[str]]]:
    with TAXONOMY_PATH.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream) or {}
    return value.get("categories", value) if isinstance(value, dict) else {}


def canonicalize(value: Any, category: str) -> str:
    """Return the category's canonical label, or a normalized unknown label."""

    normalized = normalize_label(value)
    if not normalized:
        return "unknown"
    for canonical, aliases in (load_taxonomy().get(category) or {}).items():
        labels = {normalize_label(canonical), *(normalize_label(alias) for alias in aliases or [])}
        if normalized in labels:
            return normalize_label(canonical)
    return normalized
