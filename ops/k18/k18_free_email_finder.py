#!/usr/bin/env python3
"""Refresh K-18 public contact evidence with the shared free email finder.

This stage only reads public pages and DNS MX records. It preserves the K-18
record contract, does not guess addresses, and never writes to Zoho/CRM or
opens SMTP. Role evidence is intentionally disabled for K-18: public generic
and domain-verified role routes are retained, while excluded privacy/legal or
automated mailboxes remain rejected by the shared classifier.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SHARED_SERVICE = Path("/srv/hermes/app/hermes/services")
if SHARED_SERVICE.is_dir():
    sys.path.insert(0, str(SHARED_SERVICE))
from free_email_finder_service import FreeEmailFinderService, normalize_website  # type: ignore  # noqa: E402


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def urls_for(record: dict[str, Any]) -> list[str]:
    values: list[Any] = [record.get("url"), record.get("contact_url"), record.get("source_url")]
    if isinstance(record.get("sources"), list):
        values.extend(record["sources"])
    result: list[str] = []
    for value in values:
        normalized = normalize_website(str(value or "").strip())
        if normalized and not normalized.lower().endswith((".pdf", ".doc", ".docx")) and normalized not in result:
            result.append(normalized)
    return result[:5]


def kind(item: dict[str, Any]) -> str:
    return "public_general_email" if item.get("contact_type") == "generic" else "public_role_email"


def merge_contacts(existing: Any, accepted: list[dict[str, Any]]) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    seen: set[str] = set()
    if isinstance(existing, list):
        for item in existing:
            if isinstance(item, dict):
                value = str(item.get("value") or "").strip().lower()
                if value and value not in seen:
                    seen.add(value)
                    merged.append({
                        "kind": str(item.get("kind") or "public_general_email"),
                        "value": value,
                        "source_url": str(item.get("source_url") or ""),
                    })
    for item in accepted:
        value = str(item.get("email") or "").strip().lower()
        if value and value not in seen:
            seen.add(value)
            merged.append({"kind": kind(item), "value": value, "source_url": str(item.get("source_url") or "")})
    return merged


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=int, default=15)
    parser.add_argument("--max-pages", type=int, default=8)
    args = parser.parse_args()
    source = load(args.input)
    raw_records = source.get("records", source.get("results", []))
    if not isinstance(raw_records, list):
        raise ValueError("input must contain records[] or results[]")
    service = FreeEmailFinderService(
        timeout_seconds=args.timeout_seconds,
        max_pages=args.max_pages,
        require_role_evidence=False,
        user_agent="HermesK18FreeEmailFinder/1.0",
    )
    records: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    accepted_contacts: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    seen_accounts: set[str] = set()
    for raw in raw_records:
        if not isinstance(raw, dict):
            continue
        account_key = str(raw.get("candidate_id") or raw.get("organization") or raw.get("url") or "").strip().lower()
        if not account_key or account_key in seen_accounts:
            continue
        seen_accounts.add(account_key)
        if len(records) >= args.limit:
            break
        run_results = []
        try:
            run_results = [service.find(website=url, company=str(raw.get("organization") or "")).as_dict() for url in urls_for(raw)]
            candidates: dict[str, dict[str, Any]] = {}
            for result in run_results:
                for item in result.get("candidates", []):
                    candidates.setdefault(str(item.get("email") or "").lower(), item)
            accepted = [item for item in candidates.values() if item.get("status") == "accepted"]
            merged = merge_contacts(raw.get("public_emails"), accepted)
            enriched = {
                **raw,
                "public_emails": merged,
                "contact_candidates": merged,
                "contact_checked_urls": list(dict.fromkeys(url for result in run_results for url in result.get("source_urls", []))),
                "contact_finder_status": "accepted" if accepted else "no_new_accepted_contact",
                "contact_finder_role_gate": "disabled",
            }
            if accepted:
                enriched["contact_route"] = kind(accepted[0])
                enriched["contact_url"] = accepted[0].get("source_url") or enriched.get("contact_url", "")
            records.append(enriched)
            reports.append({"candidate_id": raw.get("candidate_id"), "organization": raw.get("organization"), "source_urls": enriched["contact_checked_urls"], "accepted": accepted, "all_candidates": list(candidates.values())})
            for item in accepted:
                accepted_contacts.append({"candidate_id": raw.get("candidate_id"), "organization": raw.get("organization"), "email": item.get("email"), "kind": kind(item), "source_url": item.get("source_url"), "domain_match": item.get("domain_match"), "mx_valid": item.get("mx_valid")})
        except Exception as exc:  # noqa: BLE001
            errors.append({"candidate_id": account_key, "error": f"{type(exc).__name__}: {exc}"})
            records.append({**raw, "contact_finder_status": "error", "contact_finder_role_gate": "disabled"})
    payload = {
        "schema_version": "k18-free-email-finder.v1",
        "department": "K-18 Funding Match Research",
        "run_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": "public_contact_research_only",
        "role_gate": "disabled",
        "send_allowed": False,
        "messages_sent": 0,
        "crm_written": False,
        "zoho_written": False,
        "counts": {"candidates": len(records), "accepted_contacts": len(accepted_contacts), "accounts_with_new_contact": sum(1 for item in records if item.get("contact_finder_status") == "accepted"), "errors": len(errors)},
        "source_report": str(args.input),
        "accepted_contacts": accepted_contacts,
        "reports": reports,
        "errors": errors,
        "records": records,
        "next_gate": "K-18 relevance qualification, suppression check, then Zoho review-only draft",
    }
    args.output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "candidates": len(records), "accepted_contacts": len(accepted_contacts), "role_gate": "disabled", "send_allowed": False, "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
