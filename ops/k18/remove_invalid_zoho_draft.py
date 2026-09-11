#!/usr/bin/env python3
"""Remove one known invalid K-18 review draft after backing up its RFC822 bytes."""

from __future__ import annotations

import email
import imaplib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/root/hlinor/k18")
ENV_FILE = Path("/etc/hermes/hermes.env")


def parse_env(path: Path) -> dict[str, str]:
    values = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def mailbox_arg(folder: str) -> str:
    return '"' + folder.replace("\\", "\\\\").replace('"', '\\"') + '"' if any(ch.isspace() for ch in folder) or '"' in folder else folder


def special_folder(client: imaplib.IMAP4_SSL) -> str:
    status, data = client.list()
    if status != "OK":
        raise RuntimeError("IMAP LIST failed")
    for raw in data or []:
        decoded = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
        match = re.search(r'\(([^)]*)\).*?"([^"]+)"$', decoded)
        if match and "\\drafts" in match.group(1).lower():
            return match.group(2)
    raise RuntimeError("Zoho Drafts folder not found")


def main() -> int:
    key = os.environ.get("K18_INVALID_DRAFT_KEY", "").strip()
    if not key:
        raise SystemExit("K18_INVALID_DRAFT_KEY is required")
    values = parse_env(ENV_FILE)
    client = imaplib.IMAP4_SSL(values["MAILBOX_1_HOST"], int(values["MAILBOX_1_PORT"]))
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    backup_dir = ROOT / "reports" / f"invalid-draft-backup-{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
    removed = []
    try:
        client.login(values["MAILBOX_1_EMAIL"], values["MAILBOX_1_PASSWORD"])
        folder = special_folder(client)
        status, _ = client.select(mailbox_arg(folder))
        if status != "OK":
            raise RuntimeError("cannot select Zoho Drafts")
        status, found = client.uid("search", None, "ALL")
        if status != "OK":
            raise RuntimeError("cannot search Zoho Drafts")
        for uid in (found[0].split() if found and found[0] else []):
            status, fetched = client.uid("fetch", uid, b"(BODY.PEEK[])")
            if status != "OK":
                continue
            raw = b"".join(part[1] for part in fetched or [] if isinstance(part, tuple) and isinstance(part[1], bytes))
            message = email.message_from_bytes(raw)
            if str(message.get("X-Hlinor-K18-Idempotency-Key") or "").strip() != key:
                continue
            backup_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
            backup_path = backup_dir / f"{uid.decode()}.eml"
            backup_path.write_bytes(raw)
            os.chmod(backup_path, 0o600)
            client.uid("store", uid, "+FLAGS", "(\\Deleted)")
            removed.append({"uid": uid.decode(), "backup": str(backup_path)})
        if removed:
            client.expunge()
        report = {"schema_version": "k18-invalid-draft-cleanup.v1", "run_at": timestamp.isoformat().replace("+00:00", "Z"), "folder": folder, "idempotency_key": key, "removed": removed, "send_allowed": False, "messages_sent": 0}
        report_path = ROOT / "reports" / "invalid-draft-cleanup.latest.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.chmod(report_path, 0o600)
        print(json.dumps({"removed": len(removed), "send_allowed": False, "messages_sent": 0}))
        return 0
    finally:
        try:
            client.logout()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
