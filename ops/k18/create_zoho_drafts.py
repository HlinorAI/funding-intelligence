#!/usr/bin/env python3
"""Append confirmed K-18 review drafts to Zoho Drafts; never send or delete."""

from __future__ import annotations

import email
import html
import imaplib
import json
import os
import re
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mail_dedup import normalized_addresses, recipient_index, special_folder as dedup_special_folder


ROOT = Path("/root/hlinor/k18")
ENV_FILE = Path("/etc/hermes/hermes.env")
SENDER = "funding@hlinor.com"
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def mailbox_arg(folder: str) -> str:
    if any(ch.isspace() for ch in folder) or '"' in folder:
        return '"' + folder.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return folder


def special_folder(client: imaplib.IMAP4_SSL) -> str:
    status, data = client.list()
    if status != "OK":
        raise RuntimeError("IMAP LIST failed")
    for raw in data or []:
        decoded = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
        match = re.search(r'\(([^)]*)\).*?"([^"]+)"$', decoded)
        if match and "\\drafts" in match.group(1).lower():
            return match.group(2)
    for raw in data or []:
        decoded = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
        if decoded.lower().endswith('"drafts"') or decoded.lower().endswith('"drafts"'):
            return decoded.rsplit('"', 2)[-2]
    raise RuntimeError("Zoho Drafts folder not found")


def existing_keys(client: imaplib.IMAP4_SSL, folder: str) -> set[str]:
    status, _ = client.select(mailbox_arg(folder), readonly=True)
    if status != "OK":
        raise RuntimeError("cannot select Zoho Drafts")
    status, found = client.uid("search", None, "ALL")
    if status != "OK":
        raise RuntimeError("cannot search Zoho Drafts")
    keys: set[str] = set()
    for uid in (found[0].split() if found and found[0] else []):
        status, fetched = client.uid("fetch", uid, b"(BODY.PEEK[HEADER.FIELDS (X-Hlinor-K18-Idempotency-Key)])")
        if status != "OK":
            continue
        raw = b"".join(part[1] for part in fetched or [] if isinstance(part, tuple) and isinstance(part[1], bytes))
        message = email.message_from_bytes(raw)
        value = str(message.get("X-Hlinor-K18-Idempotency-Key") or "").strip()
        if value:
            keys.add(value)
    return keys


def public_email(record: dict) -> str:
    for item in record.get("public_emails", []) if isinstance(record.get("public_emails"), list) else []:
        if isinstance(item, dict) and item.get("kind") not in {"public_role_email", "public_general_email"}:
            continue
        value = item.get("value") if isinstance(item, dict) else item
        if isinstance(value, str) and EMAIL_RE.fullmatch(value.strip()):
            return value.strip().lower()
    return ""


def render_html(record: dict, recipient: str) -> str:
    draft = record["draft"]
    organization = html.escape(str(record.get("organization") or "Funding Intelligence"))
    subject = html.escape(str(draft.get("subject") or "Funding Intelligence"))
    preheader = html.escape(str(draft.get("preheader") or "A small, review-only pilot for evidence-gated funding triage."))
    intro = html.escape(str(draft.get("intro") or ""))
    ask = html.escape(str(draft.get("ask") or "Would a short review-only pilot be useful for your team?"))
    source_url = html.escape(str(record.get("url") or ""), quote=True)
    repository_url = html.escape(str(draft.get("repository_url") or ""), quote=True)
    repository_sentence = html.escape(str(draft.get("repository_sentence") or "The workflow is publicly inspectable before any data is shared; you can review the"))
    source_link = ""
    if source_url:
        source_link = f'<p style="margin:22px 0 0;color:#607089;font-size:12px;line-height:18px;">Source context: <a href="{source_url}" style="color:#246bfe;text-decoration:none;">{source_url}</a></p>'
    repository_block = ""
    if repository_url:
        repository_block = f'<p style="margin:16px 0 0;color:#263653;font-size:15px;line-height:24px;">{repository_sentence} <a href="{repository_url}" style="color:#246bfe;text-decoration:none;font-weight:600;">Funding Intelligence repository</a>.</p>'
    questions = draft.get("questions") if isinstance(draft.get("questions"), list) else []
    question_items = "".join(
        f'<li style="margin:0 0 9px;padding-left:3px;">{html.escape(str(question))}</li>'
        for question in questions
        if str(question).strip()
    )
    questions_block = ""
    if question_items:
        questions_block = f'''<div style="margin:22px 0;padding:18px 20px;background:#f5f8fc;border:1px solid #e5ebf3;border-radius:12px;">
  <p style="margin:0 0 10px;color:#14213d;font-size:14px;font-weight:700;">A few questions before we suggest a format</p>
  <ol style="margin:0;padding-left:20px;color:#40506a;font-size:14px;line-height:21px;">{question_items}</ol>
</div>'''
    return f'''<!doctype html>
<html lang="en">
  <body style="margin:0;padding:0;background:#eef2f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:#17233b;">
    <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">{preheader}</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef2f7;padding:28px 12px;">
      <tr><td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:640px;background:#ffffff;border:1px solid #dce4ef;border-radius:18px;overflow:hidden;">
          <tr><td style="padding:24px 30px;background:#14213d;">
            <p style="margin:0;color:#9fb8ff;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">Hlinor · Funding Intelligence</p>
            <h1 style="margin:14px 0 0;color:#ffffff;font-size:25px;line-height:32px;font-weight:700;">{subject}</h1>
          </td></tr>
          <tr><td style="padding:30px;">
            <p style="margin:0 0 18px;color:#607089;font-size:13px;line-height:20px;">Prepared for <strong style="color:#14213d;">{organization}</strong></p>
            <p style="margin:0;color:#263653;font-size:16px;line-height:26px;">Hello,</p>
            <p style="margin:16px 0 0;color:#263653;font-size:16px;line-height:26px;">{intro}</p>
            <p style="margin:16px 0 0;color:#263653;font-size:16px;line-height:26px;">{ask}</p>
            {repository_block}
            {questions_block}
            <div style="margin:24px 0 0;padding:16px 18px;border-left:4px solid #3ecf8e;background:#f1fbf6;border-radius:8px;">
              <p style="margin:0;color:#245541;font-size:14px;line-height:22px;"><strong>Review-only pilot:</strong> no applications submitted, no CRM connection, and no applicant contacted.</p>
            </div>
            {source_link}
            <p style="margin:28px 0 0;color:#263653;font-size:16px;line-height:26px;">Best regards,<br><strong>Hlinor</strong><br><span style="color:#607089;font-size:13px;">Funding Intelligence</span></p>
          </td></tr>
          <tr><td style="padding:18px 30px;background:#f8fafc;border-top:1px solid #e8edf4;">
            <p style="margin:0;color:#7b899f;font-size:11px;line-height:17px;">This is a manually reviewed research invitation. It does not promise funding, acceptance, or application outcomes.</p>
          </td></tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>'''


def build_message(record: dict, recipient: str, key: str) -> EmailMessage:
    draft = record["draft"]
    message = EmailMessage()
    message["From"] = SENDER
    message["Reply-To"] = SENDER
    message["To"] = recipient
    message["Subject"] = draft["subject"]
    message["Date"] = formatdate(localtime=False)
    message["Message-ID"] = make_msgid(domain="hlinor.com")
    message["X-Hlinor-K18-Review-Only"] = "true"
    message["X-Hlinor-Send-Allowed"] = "false"
    message["X-Hlinor-K18-Idempotency-Key"] = key
    message["X-Hlinor-K18-Candidate-ID"] = str(record.get("candidate_id") or "")
    message["X-Hlinor-K18-Source-URL"] = str(record.get("url") or "")
    message.set_content(draft["body"])
    message.add_alternative(render_html(record, recipient), subtype="html")
    return message


def main() -> int:
    input_path = Path(os.environ.get("K18_QUALIFICATION_INPUT", str(ROOT / "reports/qualification.operator.latest.json")))
    output_path = Path(os.environ.get("K18_ZOHO_REPORT", str(ROOT / "reports/zoho-drafts.latest.json")))
    if os.environ.get("K18_DRAFTS_MODE", "disabled").strip().lower() != "enabled":
        report = {
            "schema_version": "k18-zoho-drafts.v3",
            "run_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "mode": "legacy_writer_disabled",
            "created": [],
            "skipped_existing": [],
            "skipped": [],
            "send_allowed": False,
            "messages_sent": 0,
            "outbound_send_performed": False,
        }
        output_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False))
        return 0
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    records = payload.get("records", []) if isinstance(payload, dict) else []
    eligible = []
    skipped = []
    for record in records:
        recipient = public_email(record)
        non_review_holds = [value for value in record.get("holds", []) if value != "manual_review_required"]
        if record.get("relevance_status") != "confirmed" or record.get("status") != "manual_review" or not isinstance(record.get("draft"), dict) or non_review_holds:
            skipped.append({"candidate_id": record.get("candidate_id"), "reason": "not_confirmed_relevant"})
            continue
        if not recipient:
            skipped.append({"candidate_id": record.get("candidate_id"), "reason": "no_public_email"})
            continue
        eligible.append((record, recipient))
    values = parse_env(ENV_FILE)
    required = ["MAILBOX_1_HOST", "MAILBOX_1_PORT", "MAILBOX_1_EMAIL", "MAILBOX_1_PASSWORD"]
    missing = [key for key in required if not values.get(key)]
    if missing:
        raise SystemExit("missing mailbox configuration: " + ",".join(missing))
    client = imaplib.IMAP4_SSL(values["MAILBOX_1_HOST"], int(values["MAILBOX_1_PORT"]))
    created = []
    skipped_existing = []
    try:
        client.login(values["MAILBOX_1_EMAIL"], values["MAILBOX_1_PASSWORD"])
        folder = dedup_special_folder(client, "\\Drafts", "Drafts")
        sent_folder = dedup_special_folder(client, "\\Sent", "Sent")
        keys = existing_keys(client, folder)
        draft_recipients = recipient_index(client, folder)
        sent_recipients = recipient_index(client, sent_folder)
        timestamp = datetime.now(timezone.utc).replace(microsecond=0)
        for record, recipient in eligible:
            key = f"k18:{record.get('candidate_id')}:{recipient}"
            if recipient in sent_recipients:
                skipped_existing.append({
                    "candidate_id": record.get("candidate_id"),
                    "recipient": recipient,
                    "reason": "prior_recipient_in_sent",
                    "evidence": sent_recipients[recipient],
                })
                continue
            if recipient in draft_recipients:
                skipped_existing.append({
                    "candidate_id": record.get("candidate_id"),
                    "recipient": recipient,
                    "reason": "recipient_already_in_drafts",
                    "evidence": draft_recipients[recipient],
                })
                continue
            if key in keys:
                skipped_existing.append({"candidate_id": record.get("candidate_id"), "recipient": recipient, "idempotency_key": key})
                continue
            message = build_message(record, recipient, key)
            status, _ = client.append(mailbox_arg(folder), "(\\Draft)", imaplib.Time2Internaldate(timestamp.timestamp()), message.as_bytes())
            if status != "OK":
                raise RuntimeError(f"IMAP Draft append failed: {record.get('candidate_id')}")
            created.append({"candidate_id": record.get("candidate_id"), "recipient": recipient, "idempotency_key": key})
            draft_recipients[recipient] = {"folder": folder, "uid": "new", "subject": str(record["draft"].get("subject", "")), "message_id": str(message.get("Message-ID", ""))}
        report = {"schema_version": "k18-zoho-drafts.v2", "run_at": timestamp.isoformat().replace("+00:00", "Z"), "mode": "zoho_drafts_review_only", "draft_folder": folder, "sent_folder": sent_folder, "deduplication": "normalized_recipient_across_drafts_and_sent", "eligible": len(eligible), "created": created, "skipped_existing": skipped_existing, "skipped": skipped, "send_allowed": False, "messages_sent": 0, "outbound_send_performed": False}
        output_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False))
        return 0
    finally:
        try:
            client.logout()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
