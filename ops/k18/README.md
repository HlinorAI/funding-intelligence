# K-18 Funding Match Research

K-18 is a separate search department for a controlled Funding Intelligence
outreach experiment. Its job is to find public, evidence-backed signals that a
technical project may currently need funding, credits, an accelerator, or a
strategic route, then prepare a small manual-review queue.

It is deliberately separate from K16/K17. It does not use their search
categories, lead records, suppression files, copy, mailboxes, timers, or
services.

## Target audience

Primary audience:

- technical startup founders and CEOs;
- CTOs or technical co-founders;
- heads of fundraising, grants, or startup programs;
- maintainers of technically credible open-source projects.

There are two explicitly separated audience lanes:

- `project`: technical startup founders, CTOs, grant owners, and maintainers
  with a current public funding or support need;
- `program_operator`: accelerator, grant-program, residency, and venture-studio
  teams that manage an applicant or portfolio pipeline.

The second lane is the current B2B buyer hypothesis. It offers an
evidence-integrity pre-screen: applicant triage, source/freshness checks, and
route matching for human review. It is not a founder-facing funding promise or
a replacement for grant-management software. VC/PE funds, angel syndicates,
agencies, directories, and generic startup lists remain excluded until a
separate evidence-backed lane is approved.

The `project` lane is a research signal only at this stage. It is not evidence
of founder demand and is not an approved outbound audience. K-18's next
validation target is an operator, grant advisor, accelerator, or similar team
that can compare manual applicant triage with a source-backed pilot.

## What counts as a lead

Search discovers candidates only. A candidate becomes a reviewable lead only if
the operator can verify all of the following from public sources:

1. an explicit or strongly evidenced current need (`grant`, `credits`,
   `accelerator`, `funding`, `pilot`, or similar);
2. a real technical project with a public site, repository, demo, or launch
   evidence;
3. a plausible route in the local Funding Intelligence knowledge base;
4. a role-level route to a founder, CTO, or funding/program owner;
5. a fresh first-party source, normally no older than 90 days;
6. no suppression or prior-contact conflict.

Search snippets alone never satisfy qualification.

## Offer prepared by K-18

The first-touch draft offers a short, source-backed funding route map: a small
set of relevant routes, the official source and current verification state,
missing eligibility evidence, and the next concrete action. It does not promise
funding, acceptance, a grant amount, or automatic application submission.

The draft asks whether this would be useful and offers a low-friction review of
public project facts. It contains an opt-out and is held for human review.

## Safety state

Research, qualification, and draft creation remain review-only and emit
`send_allowed: false` and `messages_sent: 0`. A separate
`send_pilot_drafts.py` runner exists for a narrowly allowlisted batch only; it
requires an explicit `--confirm-send`, exact-recipient preflight, backup, and
sender-side Sent reconciliation. It is not an automatic workflow and does not
authorize future sends. The two historical four-message batches were approved
separately; recipient inbox placement remains unverified.

Every search result must carry exactly one `audience_lane`: `project` or
`program_operator`. Missing or unknown lanes are held without a draft. Queries
without an explicit lane default to `project`; provider-specific lanes are
validated before a search can run.

The prepared Zoho identity is recorded in `sender.yaml`: `funding@hlinor.com`
as the From/Reply-To alias on the `hello@hlinor.com` mailbox. This identity is
not marked verified for sending until a separate owner-approved mail test and
review gate are completed.

## Commands

Run the local self-test:

```bash
python3 ops/k18/k18_workflow.py self-test
```

Collect a low-volume public research queue only after approval:

```bash
python3 ops/k18/k18_workflow.py search \
  --provider playwright_google \
  --output /path/to/private/k18-search.json
```

`playwright_google` uses the installed host-native Chromium on Hermes and
reads public result links only. If Google presents a human-verification
challenge, the run is marked `blocked`; K-18 does not bypass the challenge.
`playwright_bing` is an equivalent browser path used when Google is blocked.

Two additional discovery paths are available:

- `google_news_rss` reads fresh public announcements without the search-page
  CAPTCHA path. Its links are discovery signals only and must be enriched to an
  official program page before qualification.
- `github_issues` reads public issue metadata for explicit funding signals. It
  excludes known aggregator repositories and pull requests and never harvests
  private contact data. The query layer also rejects generic issue discussions
  that merely mention funding without a current need signal.

For the program-operator lane, `official_pages` reads only the allowlisted
official pages in `sources.yaml`. This is the server-side fallback when public
search engines return human-verification challenges. It extracts page evidence
and publicly displayed contact routes but does not submit forms or send mail.

Example operator run:

```bash
python3 ops/k18/k18_workflow.py search \
  --provider official_pages \
  --lane program_operator \
  --output /path/to/private/k18-operator-search.json
```

Qualify manually enriched candidates into a draft-only queue:

```bash
python3 ops/k18/k18_workflow.py qualify \
  --input /path/to/private/k18-candidates.json \
  --output /path/to/private/k18-qualification.json
```

Operational input and output must stay in a private directory with restrictive
permissions. Do not put private contacts, candidate files, or reports in the
public repository.

Confirmed operator records with a public email are appended as review-only
Zoho drafts by `create_zoho_drafts.py`. Before append, the contour resolves
Drafts and Sent, normalizes To/Cc/Bcc addresses, and refuses a recipient found
in either folder. This recipient-level gate is in addition to the
idempotency-key gate, uses the `funding@hlinor.com` alias, and fails closed if
Sent cannot be read. Records without a current relevance confirmation or
public email are skipped.

The legacy K-18 Zoho writer is now disabled by default. `run_operator.sh` keeps
the allowlisted official-page collection, public-email evidence, qualification,
and fail-closed deduplication logic for research, but does not append anything
to Zoho. Direct execution of `create_zoho_drafts.py` also stops unless the
caller explicitly sets `K18_DRAFTS_MODE=enabled`; the current controlled
outreach workflow is the only normal draft-creation path.

The operator run now adds `k18_free_email_finder.py` after the legacy
contact-enrichment step. It checks the official record URL, contact URL, and
source URLs, decodes public Cloudflare-obfuscated addresses, verifies syntax and
MX, and writes `enriched.operator.free-finder.latest.json`. Its role gate is
disabled for K-18, but privacy/legal/automated addresses and unverified domains
remain excluded by the shared classifier. This stage is evidence-only and
keeps `send_allowed: false`. The explicitly approved send runner repeats the
same normalized-recipient Sent preflight before SMTP, then waits for Zoho's
server-side Sent copy before archiving a Draft. New lead discovery and draft
preparation may run continuously; sending new recipients remains a separate
approval gate.
