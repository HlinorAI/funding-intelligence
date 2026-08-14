# Security and privacy boundary

Funding Intelligence is currently a local CLI that reads project documents and
writes local YAML/Markdown artifacts. It is not yet a SaaS/API and must not be
treated as a secure multi-tenant service.

## Current threat model

| Threat | Current control | Remaining limitation |
|---|---|---|
| Credentials committed to the public repository | Tracked-file credential and private-path validation; ignored local evidence paths | The scanner is a safety gate, not a secrets manager |
| Sensitive values copied into a report or log | `runtime/privacy.py` can scan before sharing and redact detected credential-like spans | Redaction is explicit; ingestion does not silently mutate project facts |
| Private project evidence exposed by fixtures | `tests/external-local/`, `evidence/hlinor/`, private history, drafts, and reports are ignored | Local filesystem permissions remain the operator's responsibility |
| False privacy assurance from the deterministic engine | Public docs and CLI contracts prohibit credentials, customer lists, and confidential documents | No server-side storage, access control, encryption, or audit service exists |
| Dependency or workflow drift | `pyproject.toml`, `uv.lock`, CI validation, and the one-command check | Dependency review and release signing are still manual |

## Rules before a private pilot

- Obtain explicit consent for collection, processing, retention, and deletion.
- Keep private evidence outside Git and outside public issue forms, benchmarks,
  logs, generated reports, and pull requests.
- Run `python -m runtime.privacy <file>` before sharing or storing an artifact;
  use `redact_text` for a reviewed redacted copy, never as a silent data-loss
  step.
- Do not send private project data to an external model, search provider, or
  connector without an explicit, recorded consent decision.
- Delete local evidence and derived artifacts when the agreed retention window
  ends; do not rely on Git history deletion as a privacy control.

## Mandatory gates before SaaS/API

The following are prerequisites, not implied capabilities of this repository:

1. tenant-scoped authorization and isolation;
2. encrypted storage and transport with managed key rotation;
3. explicit retention, export, correction, and deletion workflows;
4. append-only audit events for access, processing, and deletion;
5. intake redaction and secret scanning before persistence;
6. consent records and a policy for external model/provider use;
7. incident response, backup/restore, dependency review, and abuse limits;
8. security testing of authentication, authorization, uploads, and report
   access before production exposure.

Until these gates exist, the supported privacy posture is local, operator-
controlled processing of consented or public data only.
