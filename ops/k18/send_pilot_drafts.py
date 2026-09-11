#!/usr/bin/env python3
"""Send one explicitly approved K-18 pilot batch and reconcile it in Zoho."""

from __future__ import annotations

import email
import fcntl
import hashlib
import imaplib
import json
import os
import smtplib
import ssl
import tempfile
import time
from datetime import datetime, timezone
from email.message import Message
from email.utils import getaddresses
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mail_dedup import recipient_index


ROOT = Path("/root/hlinor/k18")
ENV_FILE = Path("/etc/hermes/hermes.env")
DEFAULT_MANIFEST = ROOT / "reports/pilot-send-manifest-2026-08-29.json"
DEFAULT_OUTPUT = ROOT / "reports/pilot-send-2026-08-29.json"
LOCK_PATH = ROOT / "reports/.k18-pilot-send.lock"
SENDER = "funding@hlinor.com"


def env_value(key: str) -> str:
    for line in ENV_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip(chr(34)).strip(chr(39))
    raise KeyError(key)


def private_write(path: Path, payload: str) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        os.chmod(handle.name, 0o600)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)
    os.chmod(path, 0o600)


def mailbox_arg(folder: str) -> str:
    if any(character.isspace() for character in folder) or '"' in folder:
        return '"' + folder.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return folder


def parse_folder(raw: bytes | str) -> tuple[str, str]:
    value = raw.decode(errors="replace") if isinstance(raw, bytes) else str(raw)
    import re

    match = re.match(r'^\((?P<flags>.*?)\)\s+"(?P<delimiter>.*?)"\s+"(?P<name>.*)"$', value)
    return (match.group("flags"), match.group("name")) if match else ("", value)


def special_folder(client: imaplib.IMAP4_SSL, flag: str, fallback: str) -> str:
    status, data = client.list()
    if status != "OK":
        raise RuntimeError("IMAP LIST failed")
    folders = [parse_folder(item) for item in data or []]
    for flags, name in folders:
        if flag.lower() in flags.lower():
            return name
    for _, name in folders:
        if name.lower() == fallback.lower():
            return name
    raise RuntimeError(f"IMAP folder not found: {fallback}")


def fetch_all(client: imaplib.IMAP4_SSL, folder: str) -> list[tuple[bytes, bytes, Message]]:
    status, _ = client.select(mailbox_arg(folder), readonly=True)
    if status != "OK":
        raise RuntimeError(f"cannot select {folder}")
    status, data = client.uid("search", None, "ALL")
    if status != "OK":
        raise RuntimeError(f"cannot search {folder}")
    result: list[tuple[bytes, bytes, Message]] = []
    for uid in data[0].split() if data and data[0] else []:
        status, fetched = client.uid("fetch", uid, b"(BODY.PEEK[] INTERNALDATE)")
        if status != "OK":
            raise RuntimeError(f"cannot fetch message {uid.decode(errors='replace')}")
        raw = b"".join(part[1] for part in fetched or [] if isinstance(part, tuple) and isinstance(part[1], bytes))
        result.append((uid, raw, email.message_from_bytes(raw)))
    return result


def sent_copy_for_key(client: imaplib.IMAP4_SSL, folder: str, key: str) -> tuple[bytes, bytes, Message] | None:
    status, _ = client.select(mailbox_arg(folder), readonly=True)
    if status != "OK":
        raise RuntimeError(f"cannot select {folder}")
    status, data = client.uid("search", None, "HEADER", "X-Hlinor-K18-Idempotency-Key", key)
    if status != "OK":
        raise RuntimeError(f"cannot search Sent for {key}")
    uids = data[0].split() if data and data[0] else []
    if not uids:
        return None
    if len(uids) > 1:
        raise RuntimeError(f"duplicate K-18 message key in mailbox: {key}")
    uid = uids[0]
    status, fetched = client.uid("fetch", uid, b"(BODY.PEEK[] INTERNALDATE)")
    if status != "OK":
        raise RuntimeError(f"cannot fetch Sent message {uid.decode(errors='replace')}")
    raw = b"".join(part[1] for part in fetched or [] if isinstance(part, tuple) and isinstance(part[1], bytes))
    return uid, raw, email.message_from_bytes(raw)


def fetch_expected_sent(client: imaplib.IMAP4_SSL, folder: str, expected: list[tuple[str, str]]) -> list[tuple[bytes, bytes, Message]]:
    result = []
    for key, _ in expected:
        found = sent_copy_for_key(client, folder, key)
        if found is not None:
            result.append(found)
    return result


def wait_for_sent_copy(client: imaplib.IMAP4_SSL, folder: str, key: str, *, timeout_seconds: int = 30) -> tuple[bytes, bytes, Message] | None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        found = sent_copy_for_key(client, folder, key)
        if found is not None or time.monotonic() >= deadline:
            return found
        time.sleep(1)


def load_manifest(path: Path) -> tuple[list[tuple[str, str]], str]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "k18-pilot-send-manifest.v1":
        raise RuntimeError("unsupported K-18 send manifest schema")
    if manifest.get("send_allowed") is not True:
        raise RuntimeError("send manifest is not explicitly unlocked")
    entries = manifest.get("messages")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 4:
        raise RuntimeError("K-18 pilot manifest must contain between one and four messages")
    result = []
    seen = set()
    for entry in entries:
        key = str(entry.get("idempotency_key", "")).strip()
        recipient = str(entry.get("recipient", "")).strip().lower()
        if not key or not recipient or "@" not in recipient or key in seen:
            raise RuntimeError("invalid or duplicate K-18 pilot manifest entry")
        seen.add(key)
        result.append((key, recipient))
    return result, hashlib.sha256(path.read_bytes()).hexdigest()


def validate_folder(messages: list[tuple[bytes, bytes, Message]], expected: list[tuple[str, str]], *, sent: bool) -> dict[str, tuple[bytes, bytes, Message]]:
    expected_map = dict(expected)
    found: dict[str, tuple[bytes, bytes, Message]] = {}
    for uid, raw, message in messages:
        key = str(message.get("X-Hlinor-K18-Idempotency-Key", "")).strip()
        if key not in expected_map:
            continue
        recipients = {address.lower() for _, address in getaddresses([message.get("To", "")])}
        if recipients != {expected_map[key]}:
            raise RuntimeError(f"recipient mismatch for {key}: {sorted(recipients)}")
        if key in found:
            raise RuntimeError(f"duplicate K-18 message key in mailbox: {key}")
        if sent:
            found[key] = (uid, raw, message)
            continue
        if SENDER not in str(message.get("From", "")).lower():
            raise RuntimeError(f"sender mismatch for {key}")
        if str(message.get("X-Hlinor-K18-Review-Only", "")).lower() != "true":
            raise RuntimeError(f"review-only marker missing for {key}")
        found[key] = (uid, raw, message)
    return found


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm-send", action="store_true")
    args = parser.parse_args()
    if not args.dry_run and not args.confirm_send:
        raise SystemExit("refusing to send without --confirm-send")

    LOCK_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with LOCK_PATH.open("a+") as lock_handle:
        os.chmod(lock_handle.name, 0o600)
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("K-18 pilot send is already running")

        expected, manifest_sha256 = load_manifest(args.manifest)
        expected_count = len(expected)
        imap = imaplib.IMAP4_SSL(env_value("MAILBOX_1_HOST"), int(env_value("MAILBOX_1_PORT")))
        imap.login(env_value("MAILBOX_1_EMAIL"), env_value("MAILBOX_1_PASSWORD"))
        drafts_folder = special_folder(imap, "\\Drafts", "Drafts")
        sent_folder = special_folder(imap, "\\Sent", "Sent")
        try:
            drafts = validate_folder(fetch_all(imap, drafts_folder), expected, sent=False)
            sent_recipients = recipient_index(imap, sent_folder)
            prior_recipients = {
                recipient: sent_recipients[recipient]
                for _, recipient in expected
                if recipient in sent_recipients
            }
            if prior_recipients:
                raise RuntimeError(
                    "recipient already present in Zoho Sent; refusing to send: "
                    + json.dumps(prior_recipients, ensure_ascii=False, sort_keys=True)
                )
            sent = validate_folder(fetch_expected_sent(imap, sent_folder, expected), expected, sent=True)
            if set(drafts) != {key for key, _ in expected}:
                raise RuntimeError("K-18 pilot Drafts do not exactly match the send manifest")
            if sent:
                raise RuntimeError(f"pilot messages already present in Sent: {sorted(sent)}")

            timestamp = datetime.now(timezone.utc).replace(microsecond=0)
            backup_dir = ROOT / "backups" / ("zoho-k18-pilot-send-" + timestamp.strftime("%Y%m%dT%H%M%SZ"))
            backup_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
            for key, _ in expected:
                (backup_dir / f"{key.replace(':', '_')}.eml").write_bytes(drafts[key][1])

            if args.dry_run:
                result = {"schema_version": "k18-pilot-send.v1", "status": "preflight_ok", "manifest_sha256": manifest_sha256, "backup_dir": str(backup_dir), "messages_expected": expected_count, "messages_sent": 0, "send_allowed": False, "outbound_send_performed": False}
                private_write(args.output, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
                print(json.dumps(result, ensure_ascii=False))
                return 0

            smtp = smtplib.SMTP(env_value("EMAIL_SMTP_HOST"), int(env_value("EMAIL_SMTP_PORT")), timeout=30)
            smtp_accepted: list[dict[str, str]] = []
            sent_rows: list[dict[str, str]] = []
            failures: list[dict[str, str]] = []
            try:
                smtp.ehlo()
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
                smtp.login(env_value("MAILBOX_1_EMAIL"), env_value("MAILBOX_1_PASSWORD"))
                for key, recipient in expected:
                    uid, raw, message = drafts[key]
                    try:
                        refused = smtp.sendmail(SENDER, [recipient], raw)
                    except Exception as exc:
                        failures.append({"idempotency_key": key, "recipient": recipient, "error": f"SMTP outcome ambiguous: {type(exc).__name__}"})
                        break
                    if refused:
                        failures.append({"idempotency_key": key, "recipient": recipient, "error": repr(refused)})
                        break
                    smtp_accepted.append({"idempotency_key": key, "recipient": recipient})
                    server_sent = wait_for_sent_copy(imap, sent_folder, key)
                    if server_sent is None:
                        failures.append({"idempotency_key": key, "recipient": recipient, "error": "SMTP accepted but Zoho Sent auto-save was not observed; reconcile before retry"})
                        break
                    imap.select(mailbox_arg(drafts_folder))
                    status, _ = imap.uid("store", uid, "+FLAGS", "(\\Deleted)")
                    if status != "OK":
                        failures.append({"idempotency_key": key, "recipient": recipient, "error": "Sent archived but Draft deletion failed; reconcile before retry"})
                        break
                    sent_rows.append({"idempotency_key": key, "recipient": recipient, "message_id": str(server_sent[2].get("Message-ID", ""))})
            finally:
                smtp.quit()

            imap.select(mailbox_arg(drafts_folder))
            imap.expunge()
            sent_after = validate_folder(fetch_expected_sent(imap, sent_folder, expected), expected, sent=True)
            expected_keys = {key for key, _ in expected}
            reconciled = set(sent_after) == expected_keys and len(sent_rows) == expected_count and not failures
            status = "sent" if reconciled else "reconcile_required"
            result = {
                "schema_version": "k18-pilot-send.v1",
                "run_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "status": status,
                "approval_basis": "explicit user approval in current task",
                "manifest_sha256": manifest_sha256,
                "backup_dir": str(backup_dir),
                "messages_expected": expected_count,
                "smtp_accepted": smtp_accepted,
                "messages_sent": len(sent_rows),
                "sent": sent_rows,
                "failures": failures,
                "sent_reconciled_keys": sorted(sent_after),
                "send_allowed": True,
                "outbound_send_performed": bool(smtp_accepted),
            }
            private_write(args.output, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            print(json.dumps(result, ensure_ascii=False))
            return 0 if reconciled else 2
        finally:
            imap.logout()


if __name__ == "__main__":
    raise SystemExit(main())
