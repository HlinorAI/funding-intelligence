# TODO

## Product validation

- [x] Narrow the wedge to an evidence-integrity pre-screen for human
  operator/advisor reviewers.
- [x] Reconcile the current roadmap links and K-18 send-state documentation.
- [ ] Review the eight approved operator contacts before any further outreach.
- [ ] Run one consented operator pilot using
  `docs/operator-pilot-protocol.md`.
- [ ] Build only the batch evidence-pack or reviewer-queue slice demonstrated
  necessary by pilot feedback.
- [ ] Decide whether repeat use justifies a v0.2.0 release and one integration.

## New lead research

- [x] Research five new operator/advisor leads from official public sources.
- [x] Prepare individualized pilot proposals for the five leads.
- [x] Create and verify three Zoho drafts for the leads with appropriate public
  email routes; keep two form-only proposals local.
- [x] Send and verify the three approved Zoho outreach emails; keep two
  form-only proposals local.
- [x] Enable an active six-hour, read-only new-lead monitor with public-source
  qualification and deduplication; keep outreach and CRM changes approval-gated.
- [ ] Record replies separately from delivery, drafts, or public interest.

## Pathway freshness

- [x] Add a pathway contract for lifecycle, window and funding model.
- [x] Add current announcement-backed cards for EIC, NSF, Women TechEU,
  Filecoin, Tether, OpenAI and Base Batches.
- [ ] Verify application/intake endpoints for selected pathways before marking
  them actionable.
- [ ] Split additional multi-route ecosystem cards when a real case selects a
  specific mechanism.

## Decision quality

- [x] Re-run the canonical public example through ingestion, runner, verifier
  and Markdown rendering before accepting a private pilot.
- [x] Identify a prioritised, evidence-backed shortlist of external
  operator/advisor pilot prospects; keep it research-only until outreach is
  explicitly approved.
- [x] Verify public role contacts and prepare a first-pilot question set;
  keep messages unsent.
- [ ] Run one consented operator/advisor pilot through intake, routing,
  verification and feedback.
- [ ] Record false positives, false negatives, corrections and time saved.
- [ ] Recalibrate quality metadata only after owner-reviewed outcomes exist.

## Product boundary

- [x] Confirm that generic funding discovery/matching is a crowded market
  wedge; keep the next pilot focused on evidence-gated operator triage.
- [ ] Reassess API/SaaS packaging after endpoint coverage and pilot evidence
  improve; do not infer readiness from card count alone.

## Local process lifecycle

- [x] Add an explicit local route state: discovery, eligibility,
  application-ready, follow-up and outcome.
- [x] Require an evidence reference before recording submission or outcome.
- [x] Keep application submission and provider communication outside the tool.

## Freshness and route safety

- [x] Enforce the seven-day source snapshot freshness rule in runner and route
  verifier decisions.
- [ ] Re-verify the five recorded application/access endpoints before a real
  pilot report is delivered.

## K-18 Funding Match Research

- [x] Prepare the isolated search and qualification contour on Hermes.
- [x] Configure the `funding@hlinor.com` sender identity without enabling send.
- [!] First low-volume live discovery pass was blocked by the DuckDuckGo
  human-verification challenge; no candidates were accepted.
- [x] Repair the live Tally Webhooks handler: it now extracts `data.fields`
  from Tally's envelope; the deployed route passes an in-process FORM_RESPONSE
  test with the configured header token and returns HTTP 200 without writing to
  the production sheet.
- [x] Replay the failed Tally submission through the repaired endpoint and
  verify the resulting CRM/Sheets row (`Leads!A8:N8`, 14 columns).
- [x] Refresh the public-source operator prospect scan and prepare questions
  for EIT Digital Co-Creation and the FreeCAD Project Association; keep both
  route-only until a current owner contact is verified.
- [x] Verify Google and Bing browser fallbacks; Google is challenged and Bing
  is not reliable enough for qualification.
- [x] Add the separate `program_operator` lane and official-page fallback.
- [x] Run a five-source local operator pilot: five candidates, all held only by
  the final review gate; one source also lacks an approved contact route.
- [x] Deploy and run the official-page operator collector on Hermes.
- [x] Add Google News RSS and GitHub public-issue discovery as separate queues.
- [x] Enable a six-hour multi-source timer with relevance-gated Zoho drafts;
  outbound sending remains off.
- [x] Make search records fail closed when `audience_lane` is missing and keep
  unlabelled queries in the `project` lane only.
- [x] Add relevance-gated, idempotent Zoho review-draft creation for confirmed
  operator records with public email evidence.
- [x] Add the shared free public-email finder to K-18 operator enrichment with
  official-page traversal, Cloudflare-obfuscated email decoding, MX evidence,
  account deduplication, and role-gate-disabled review output.
- [x] Create and physically verify four individualized multipart HTML/text
  Zoho review drafts for the pilot prospects; keep sending disabled.
- [x] Add and physically verify the public repository link in each draft body;
  keep the link out of detached promotional blocks.
- [x] Add a four-message, explicitly approved send runner with exact-recipient
  preflight and Sent-folder reconciliation.
- [x] Send exactly the four explicitly approved pilot messages and reconcile
  one Zoho Sent copy per idempotency key; recipient-side delivery remains
  unverified.
- [x] Fix the runner's Zoho auto-save handling so it cannot create a second
  manual Sent archive copy.
- [ ] Review recipient replies and run one consented operator/advisor pilot.
- [x] Prepare four second-wave Zoho review drafts for verified public-email
  routes and physically verify their HTML/plain content.
- [x] Send the four explicitly approved second-wave messages; reconcile one
  Zoho Sent copy per recipient and remove only their verified Draft copies.
  Recipient-side delivery remains unverified.
- [x] Add a permanent normalized-recipient gate across Zoho Drafts and Sent
  before draft creation and again before sending; fail closed on unreadable
  mailbox state.
- [ ] Keep the six-hour lead search and HTML draft preparation running; require
  explicit approval for each future outbound batch.
- [x] Select and contact the first-wave operator-pilot prospects through the
  explicitly approved four-message batch; no consented pilot is implied.
- [ ] Review first- and second-wave replies and select at most one candidate
  for a consented pilot; do not infer consent from message delivery.
