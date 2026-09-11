"""Fail-closed mailbox recipient deduplication helpers for K-18."""

from __future__ import annotations

import email
import imaplib
import re
from email.utils import getaddresses


def mailbox_arg(folder: str) -> str:
    if any(character.isspace() for character in folder) or '"' in folder:
        return '"' + folder.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return folder


def parse_folder(raw: bytes | str) -> tuple[str, str]:
    value = raw.decode(errors="replace") if isinstance(raw, bytes) else str(raw)
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


def normalized_addresses(value: str | None) -> set[str]:
    return {
        address.strip().lower()
        for _, address in getaddresses([value or ""])
        if address and "@" in address
    }


def recipient_index(client: imaplib.IMAP4_SSL, folder: str) -> dict[str, dict[str, str]]:
    """Return normalized recipients from To/Cc/Bcc; raise on any read failure."""
    status, _ = client.select(mailbox_arg(folder), readonly=True)
    if status != "OK":
        raise RuntimeError(f"cannot select {folder}")
    status, data = client.uid("search", None, "ALL")
    if status != "OK":
        raise RuntimeError(f"cannot search {folder}")
    result: dict[str, dict[str, str]] = {}
    fields = b"(BODY.PEEK[HEADER.FIELDS (TO CC BCC SUBJECT MESSAGE-ID)])"
    for uid in data[0].split() if data and data[0] else []:
        status, fetched = client.uid("fetch", uid, fields)
        if status != "OK":
            raise RuntimeError(f"cannot fetch recipient headers in {folder}")
        raw = b"".join(
            part[1] for part in fetched or [] if isinstance(part, tuple) and isinstance(part[1], bytes)
        )
        message = email.message_from_bytes(raw)
        addresses: set[str] = set()
        for header in ("To", "Cc", "Bcc"):
            addresses.update(normalized_addresses(message.get(header)))
        evidence = {
            "folder": folder,
            "uid": uid.decode(errors="replace"),
            "subject": str(message.get("Subject", "")),
            "message_id": str(message.get("Message-ID", "")),
        }
        for address in addresses:
            result.setdefault(address, evidence)
    return result
