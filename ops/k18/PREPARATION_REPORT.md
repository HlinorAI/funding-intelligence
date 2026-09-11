# K-18 preparation report

## Scope

Prepared a separate `K-18 Funding Match Research` department for a controlled
funding-intelligence outreach experiment. The department is isolated from
K16/K17 search, lead, copy, mailbox, timer, and service files.

## Prepared artifacts

- `README.md` — target audience, qualification contract, and offer boundary.
- `queries.yaml` — six focused public-signal search queries and exclusions.
- `k18_workflow.py` — public research, manual enrichment qualification, and
  draft-only output.
- `sender.yaml` — prepared Zoho From/Reply-To identity for `funding@hlinor.com`.
- `tests/test_k18_workflow.py` — explicit-signal and exclusion regression tests.

## Verification

- Local K-18 self-test: passed.
- Local K-18 pytest tests: 2 passed.
- Repository contract gate: passed.
- Hermes self-test: passed after installation under `/root/hlinor/k18`.
- Systemd/timer changes: none.
- Mailbox changes: none.
- External searches: none.
- Messages sent: 0.
- Zoho mailbox changes: sender identity recorded only; no login, draft append,
  test message, or send performed.

## Addendum — live signal-to-draft pipeline

The preparation-only gate was superseded by the owner's explicit instruction to
run research and create review-only Zoho drafts for confirmed contacts.

- Signals now trigger relevance qualification and public-contact enrichment.
- Google News RSS and GitHub issue discovery remain separate from official-page
  operator discovery.
- A single live run created two idempotent review-only drafts in Zoho for
  confirmed public-email routes; one invalid privacy-address draft was removed
  with a private RFC822 backup, and the filter was fixed before rerun.
- No SMTP connection, send, form submission, or contact-page transmission was
  performed.
