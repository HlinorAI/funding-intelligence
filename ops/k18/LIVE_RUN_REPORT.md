# K-18 first live run

## Result

- Host: Hermes
- Mode: public discovery only
- Provider attempted: DuckDuckGo HTML
- Queries attempted: 6
- Candidates: 0
- Provider blocks: 6
- `discovery_status`: `blocked`
- `send_allowed`: `false`
- `messages_sent`: 0

## Evidence

The provider returned HTTP 202 with an interactive human-verification
challenge. K-18 now records this as a provider block rather than treating it
as an empty search result. CAPTCHA or other human challenges are not bypassed.

## Actions

- K-18 search code was updated to fail closed on the challenge response.
- No Zoho login, draft append, SMTP call, mailbox change, or outbound message
  was performed.
- No systemd service or timer was added or restarted.

## Next gate

Configure an approved search API/provider for Hermes, then rerun the same
low-volume K-18 discovery command. No new lead or message will be produced
until a provider returns verifiable results.

## Addendum — 2026-08-25 signal-to-draft run

- Official-page, Google News RSS, and GitHub issue sources returned verifiable
  records on Hermes.
- Relevance and public-contact enrichment ran before qualification.
- Two confirmed public-email operator records have review-only Zoho drafts;
  sending remains disabled and the drafts are idempotent.
- A privacy-only address was detected and excluded after correcting the
  contact classifier; the mistaken draft was backed up privately and removed.

## Addendum — 2026-08-29 individualized pilot preview drafts

- Four review-only drafts were created for WIT Funding & Consulting,
  Uniresearch BV, and two separate CPA.com Startup Accelerator contacts.
- Each draft has unique subject/body/questions and a `multipart/alternative`
  MIME body with both styled HTML and plain-text fallback.
- The four earlier plain-text versions were backed up privately and replaced;
  no other Drafts were changed.
- A direct IMAP read-back found all four target idempotency keys in the Zoho
  Drafts folder, with HTML and text parts present on every message.
- `send_allowed=false`, `messages_sent=0`, and no outbound send was performed.

## Addendum — 2026-08-29 repository-link revision

- The four individualized drafts were replaced once more with the public
  repository link woven into each recipient-specific body paragraph.
- The link is present once in each HTML body and once in each plain-text
  fallback; it is not a detached promotional block.
- A direct IMAP read-back confirmed all four target keys, unique subjects,
  repository link presence in both body formats, and `send_allowed=false`.

## Addendum — 2026-08-29 explicit four-message send

- A one-shot send runner and exact four-message manifest were prepared after
  explicit user approval.
- The runner requires `--confirm-send`, refuses unexpected or duplicate keys,
  backs up the raw drafts, sends only the allowlisted recipients, archives
  Sent evidence, and reconciles the Sent folder before reporting success.

## Addendum — 2026-08-29 send outcome

- Exactly the four explicitly approved pilot messages were accepted by Zoho
  SMTP; no additional recipient was attempted and no retry was performed.
- Zoho's own SMTP integration auto-saved one copy of each accepted message in
  `Sent`; the first runner version also appended a manual copy, so the final
  reconciliation stopped on four duplicate archive entries.
- A read-only comparison showed identical recipients, Message-IDs and decoded
  text/HTML bodies. Only the four manual archive copies were removed after
  private backup; the four server-saved `Sent` copies were retained.
- The four corresponding Drafts are no longer present. Sender-side evidence
  therefore confirms `messages_sent=4`, one `Sent` copy per idempotency key,
  and zero Drafts. Recipient-side inbox placement is not independently
  verified.
- The runner was corrected to rely on Zoho's server-side `Sent` auto-save and
  to fail closed if it is not observed, avoiding a second manual archive.

## Addendum — 2026-08-29 second-wave review drafts

- Four additional individualized review-only drafts were created in Zoho for
  imec.istart, Open Source for Science Fund, a16z speedrun, and 28DIGITAL.
- A direct IMAP read-back found all four expected idempotency keys, matching
  recipients and unique subjects. Every message is `multipart/alternative`
  with the repository link present in both the HTML and plain-text parts.
- Each message carries `X-Hlinor-K18-Review-Only: true` and
  `X-Hlinor-Send-Allowed: false`; the report records `messages_sent=0` and
  `outbound_send_performed=false`.
- No draft was created for the GitHub/LFX, AI Launchpad, STATION F, or Plug
  and Play route-only candidates because a current direct email was not
  verified. Their contact routes and questions remain in the research map.

## Addendum — 2026-08-29 second-wave send outcome

- Exactly the four explicitly approved second-wave messages were accepted by
  Zoho SMTP: imec.istart, Open Source for Science Fund, a16z speedrun, and
  28DIGITAL. No other recipient was attempted.
- A delayed/unstable Sent search caused each recovery run to stop after its
  first SMTP acceptance. No SMTP-accepted recipient was retried; the three
  recovery manifests narrowed the remaining work to recipients not yet
  attempted.
- A final read-only IMAP check found one Sent copy for each recipient (UIDs
  183, 189, 190, 191), with matching recipient, subject, Message-ID,
  `Review-Only: true`, and the repository link. The three remaining Drafts
  were removed only after exact Message-ID and recipient matching; no target
  Drafts remain.
- Sender-side evidence is complete. Delivery into each recipient's inbox is
  not independently verified.

## Addendum — 2026-08-30 intake integration incident

- The mailbox received a Tally alert for one submission to `Submit a case —
  Hlinor`: the Webhooks integration returned HTTP 400 and the submission was
  not delivered to the configured webhook.
- The event was replayed after the fix. The live endpoint returned HTTP 200 and
  created `Leads!A8:N8`; a read-only Google Sheets verification confirmed the
  new 14-column row with source `Tally Form`.
- Inspection of the live service found that the handler received Tally's
  `FORM_RESPONSE` envelope but did not extract its nested `data.fields` array.
  The deployed handler now supports that envelope, and a safe in-process test
  with a substituted Sheets client returned HTTP 200 before the replay. The
  Tally URL and header configuration were left intact.
