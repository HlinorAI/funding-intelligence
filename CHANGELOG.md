# Changelog

## 2026-09-07

### Added

- Added a local funding-route lifecycle state machine covering discovery, eligibility, application readiness, follow-up and outcome.
- Added explicit evidence references for recorded submission and outcome events.

### Security

- The lifecycle tool only updates a local YAML state file; it does not submit applications or contact external programmes.

All notable changes to Funding Intelligence are documented in this file.

The project uses semantic version tags for public releases. Program status changes, knowledge-pack updates, decision-rule changes, and verification behavior changes should be recorded when they affect public behavior or recommendations.

## [Unreleased]

### 2026-09-06

#### Fixed

- Added a fail-closed normalized-recipient deduplication gate across Zoho
  Drafts and Sent before draft creation and again before SMTP send, closing the
  gap where a different subject could be drafted to a previously contacted
  address.
- Kept continuous discovery and HTML draft preparation in the recurring
  contour while retaining explicit approval for future outbound batches.

### 2026-09-09

#### Fixed

- Disabled the legacy K-18 Zoho draft writer by default so old allowlisted
  programme records cannot be reintroduced by the source runner. Preserved
  official-source collection, public-email evidence and fail-closed recipient
  checks for the current controlled outreach workflow.

### 2026-09-05

#### Added

- Enabled an active six-hour Codex heartbeat for continuous public-source
  operator/advisor lead discovery, deduplication and qualification. The monitor
  does not send messages, submit forms or mutate CRM records.

### Product validation boundary

#### Changed

- Narrowed the next product test from generic funding matching or grant
  management to an evidence-integrity pre-screen for human operator/advisor
  reviewers.
- Added a consented operator-pilot protocol with redaction, frozen decision
  rules, evidence fields, metrics, pass conditions, and stop conditions.
- Marked the July strategic status document as historical and aligned the
  current roadmap and K-18 safety documentation with the actual repository
  state.

### Market and verification boundary

#### Added

- Added the 2026-08-29 market-landscape review. It records the crowded
  discovery/matching market, the stronger operator/advisor wedge, and the
  absence of public pilot or demand evidence.
- Added a research-only shortlist of six concrete operator/advisor pilot
  prospects, with official evidence, fit, entry points, risks, and a single-
  prospect approach order. No contact or outbound action is enabled.
- Added a public-contact map, one WIT-specific draft, and tailored discovery
  questions for the first pilot conversation; all outreach remains unsent.
- Added multipart HTML/text Zoho review drafts with individualized copy for
  each pilot contact; the four pilot drafts were physically verified in Zoho
  Drafts with sending disabled.
- Added the public repository link organically to each individualized draft
  body and verified it in both HTML and plain-text parts.
- Added an explicit four-message K-18 pilot send runner with manifest
  allowlisting, SMTP/IMAP reconciliation, backup, locking, and no implicit
  send permission.
- Sent the four explicitly approved pilot messages and reconciled one
  server-saved Zoho `Sent` copy per idempotency key; removed only four verified
  duplicate manual archive copies after private backup.
- Fixed the K-18 send runner to wait for Zoho's server-side `Sent` auto-save
  instead of appending a second copy, and to fail closed when that evidence is
  absent.
- Added a second research wave from GitHub-native programmes, Google News/IT
  coverage, and current official accelerator calls, with freshness, contact
  routes, caveats, and tailored questions; no second-wave outreach was sent.
- Added four individualized, styled Zoho review drafts for the second-wave
  candidates with public email routes; physically verified their recipients,
  HTML/plain alternatives, repository links, and send-disabled headers.
- Sent exactly the four explicitly approved second-wave messages and verified
  one server-saved Zoho `Sent` copy per recipient with zero target Drafts
  remaining; recipient inbox delivery remains unverified.
- Added subset-manifest recovery support to the K-18 send runner so an
  ambiguous SMTP/Zoho auto-save result stops safely and only unattempted
  recipients can continue.
- Repaired the live Tally Webhooks handler's nested `data.fields` parsing after
  the 2026-08-30 HTTP 400 incident, replayed the failed event, and verified the
  resulting CRM/Sheets row.
- Added a fresh public-source pilot-prospect refresh covering EIT Digital
  Co-Creation, FreeCAD's GitHub-native grant process, and a revalidation of AI
  Launchpad; no new outreach was sent.
- Added a dated, source-backed shortlist of five new B2B operator/advisor
  leads and draft-only pilot proposals; no outreach or CRM changes were made
  at that preparation stage.
- Created and verified three new Zoho review drafts for public email routes;
  two form-only proposals remain local.
- Reworked the three Zoho drafts into compact, readable outreach emails with
  short paragraphs, value bullets, and one clear call to action.
- Sent the three explicitly approved compact emails to Nexus Grant Solutions,
  Sploro, and INTERALTER; verified one matching Zoho Sent copy per recipient.
  Recipient inbox delivery remains unverified, and the two form-only leads
  were not contacted.
- Added explicit source-freshness metadata to runner and route-verifier
  outputs.

#### Fixed

- Enforced the documented seven-day source snapshot rule after a card claims
  its status is verified. A stale dated card can no longer reach `NOW` solely
  because its legacy `needs_verification` flag is false; source-snapshot routes
  still expose their age for review.
- Rendered source freshness in the human-readable report so stale snapshot
  state is visible at the review boundary.

### Knowledge and routing freshness

#### Added

- A `pathway` contract for route type, lifecycle, source-change date, windows,
  and funding terms so cohorts, RFPs, retroactive routes and credits are not
  collapsed into one programme status.
- Controlled mechanism and resource types for challenge, research,
  milestone, pilot, credits, non-dilutive, compute and research-support routes.
- Eight source-only cards covering EIC Accelerator, EIC Transition, NSF Tech
  Accelerators, Women TechEU, Filecoin ProPGF, Tether Developer Grants, OpenAI
  Economic Opportunity Funding and Base Batches 004.
- Ecosystem and sector aliases for research, payments, local-first AI, EIC,
  NSF, Filecoin and Tether.

#### Changed

- Base, Optimism, Ethereum ESP and Solana cards now record pathway lifecycle
  and current source-change dates; Optimism Retro Funding is represented as
  paused rather than implicitly active.
- The runner preserves verified application-endpoint routes when adding new
  source-only candidates and expands the shortlist ceiling to twelve routes.
- `--all-ai` verifies the AI opportunity pack only, preserving its five-route
  contract when core knowledge gains AI/deep-tech cards.
- Endpoint coverage audit now records 49 cards and 44 intentionally source-only
  routes.

#### Fixed

- Report and route schemas now accept the expanded mechanism vocabulary and
  pathway metadata without weakening the existing fail-closed gates.

### Added

- Added the K-18 adapter for the shared free public-email finder. It traverses
  official record/contact/source URLs, decodes public Cloudflare-obfuscated
  addresses, verifies domain syntax and MX, deduplicates by account, and keeps
  Zoho and outbound sending disabled.
- Prepared the isolated `K-18 Funding Match Research` workflow for a
  controlled, public-signal-only outreach experiment.
- Added a separate target-audience contract, funding-need search queries,
  fail-closed qualification gates, and draft-only output with sending disabled.
- K-18 now records search-provider anti-bot challenges as `blocked` instead of
  misreporting them as an empty successful run.
- Added a separate `program_operator` buyer lane for accelerator, grant,
  residency, and venture-program teams, with an evidence-gated applicant
  triage offer and no outbound send capability.
- Added an allowlisted `official_pages` collector so K-18 can continue when
  public search engines present human-verification challenges. Each source is
  fetched independently and failures are reported rather than collapsing the
  whole run into a false empty success.
- Added a six-hour Hermes timer for search and qualification only; Zoho drafts
  and outbound sending remain disabled.
- Added separate Google News RSS and GitHub issue discovery queues. News links
  require official-page enrichment; GitHub results exclude known aggregators,
  pull requests, generic issue noise, and private contact harvesting.
- Fixed the K-18 timer schedule to use explicit six-hour UTC calendar slots so
  it cannot become an elapsed one-shot after a manual service run.
- Added contact enrichment and an idempotent Zoho Drafts append step. It only
  creates review-only drafts after current relevance and public-email gates pass;
  it never sends or deletes mail.
- Fixed K-18 lane leakage: generic search results now receive an explicit
  audience lane, unlabelled queries default only to `project`, incompatible
  provider/lane combinations fail before search, and unknown lanes cannot
  produce drafts.
- Disabled the prepared Hermes K-18 timer while the contour remains in
  preparation-only mode; re-enabling it is a separate approval step.

### Integration coherence

#### Added

- Reproducible Python packaging with `pyproject.toml`, committed `uv.lock`, console entry points, and a one-command validation gate.
- A local privacy scanner/redaction helper and a documented threat model and pre-SaaS/API security boundary.
- Shared runtime validation for the canonical `project.schema.yaml` contract.
- Conservative raw-text scaffolding and structured JSON ingestion that produce runner-compatible project documents.
- A public structured intake file for the synthetic AI example.
- End-to-end CI coverage for ingestion, runner, verifier, and Markdown reporting.

#### Changed

- CI now installs the project and test extra through the package contract instead of maintaining a separate dependency-install sequence.
- Runner and route verifier inputs now fail closed when they do not satisfy the canonical project schema.
- Human-readable reporting is consolidated in `runtime/render_report.py` and tested against real runner and verifier output.
- Project ingestion metadata and unresolved input fields are optional fields in the canonical project schema.

#### Removed

- The incompatible `project_draft.schema.yaml` contract.
- The duplicate `runtime/report.py` implementation and its unused Rich dependency.

#### Fixed

- Prevented ingestion output from reaching the runner with an incompatible project shape.
- Prevented malformed project documents from being interpreted as valid unknown projects.
- Replaced isolated reporting fixtures with integration tests against actual engine contracts.

### Added

- Three source-bound public benchmarks covering open-source AI infrastructure, enterprise AI with a public deployment signal, and university-linked deeptech.
- A pre-pilot readiness review of the canonical workflow, fixed feedback metrics, interview order, five recorded application endpoints, and the no-inbound decision point.
- Benchmark assertions for an expected knowledge-coverage gap when no local program card matches a project shape.
- A public two-minute Tally intake path and GitHub Discussion entry point for consented external pilot projects.
- A public application-endpoint coverage audit documenting why source-only cards remain non-actionable until a route-specific intake is verified.
- A distinct `application_endpoint` route contract, separating a program's official information source from a verified application or access path.
- A dedicated human-report section for routes blocked by a missing application endpoint.
- Executable mechanism-specific evidence policies for the AI opportunity pack, with structured field operators and a legacy fallback for cards not yet migrated.
- A source-bound public Web3 infrastructure benchmark for Blockscout, verifying that a prior Optimism funding relationship does not suppress a separate Base route.
- A source-bound public Web3 benchmark for rotki, verifying that a recorded previous successful Optimism funding relationship overrides active ecosystem fit.
- A source-bound public hardware and physical-AI benchmark for Almond, including a human review of unknown-fact boundaries and affiliation precedence.
- Markdown report renderer combining runner and route-verification outputs for human review.
- Public external-project intake and feedback templates, with a Git-ignored local workspace for real pilot cases.
- Public affiliation metadata in the project schema, with regression fixtures for current, previous successful, and rejected program relationships.
- Read-only program-card health check with weekly/manual GitHub Actions workflow, artifact output, and a human-reviewed `stale-data` issue lifecycle.
- Validation of embedded `actions/github-script` JavaScript in workflow YAML.
- Explicit per-card handling for manually verified GitHub transport restrictions (`403` and `429`) in the health check.
- Pytest execution in the GitHub Actions validation workflow.
- Explicit regression fixtures for an unknown project stage and a known stage mismatch.
- Removed the legacy language mirror and translated the remaining tracked Hlinor report so public repository content is English-only.

### Fixed

- Added controlled sector, stage, and ecosystem aliases at ingestion and routing boundaries so equivalent labels resolve to the same canonical values.
- Added an optional source-backed provenance contract for program cards, including snapshot hash, semantic review, eligibility version, confidence, and diff-review state.
- Made runner and route-verification outputs explicit about deterministic `policy_score` semantics and reported empirical quality as not calibrated until owner-reviewed outcomes exist.
- Aligned the report-level aggregate gate with route-level affiliation hard gates so unknown or already-affiliated routes cannot be hidden by a passing summary gate.
- Enforced all runner hard gates before score-band decisions so source-only routes cannot reach `NOW`, `NEXT`, or `LATER` when their application endpoint or card contract is incomplete.
- Added a complete self-service workflow to the README and corrected the Base verifier example to describe `NO_ACTIONABLE_ENDPOINT` accurately.
- Prevented official program pages from being treated as actionable application endpoints when no verified application or access route exists.
- Required a confirmed source verification before a card can mark an application endpoint as confirmed or gated.
- Prevented Microsoft for Startups from reaching `NOW` when route-specific eligibility data such as prior-credit history is absent.
- Separated verifier eligibility from project readiness so rejected applications can return `REAPPLY_AFTER_CHANGE` without producing a schema-invalid eligibility state.
- Current program affiliations now hard-gate duplicate accelerator/program applications and remain visible in the rejected-route shortlist.
- Affiliation precedence now distinguishes current/previous successful, rejected, and unknown program relationships before opportunity fit becomes an application recommendation.
- The project schema now accepts a single `unknown` value for fields that may be boolean or numeric without treating the value as ambiguous.
- Corrected invalid embedded JavaScript in the health-check workflow.
- Normalized YAML date metadata in health-check reports so JSON artifact output remains serializable.
- Updated verified Aptos and Stable official source routes after the first program-card health review.
- Prevented known, manually reviewed GitHub `403` and `429` access restrictions from reopening the stale-data issue while retaining their raw report state.
- Restored absent program affiliations to a distinct `None` state so only recorded unknown affiliations produce `VERIFY_FIRST`.
- Made `routing.stages` an enforced decision boundary: unknown stages require verification and known incompatible stages are rejected.
- Removed invalid program-card YAML files that violated the public schema.
- Made the pytest runner harness portable by reading the process stdout instead of writing to `/dev/stdout`.
- Aligned repository version metadata with the latest published release.
- Removed the obsolete README language self-link.

### Planned

- Run one consented external project through the complete intake-to-feedback cycle.
- Record human corrections, useful routes, false positives, false negatives, and time saved.
- Make further technical or knowledge changes only when the external case identifies a reproducible need.

## [0.1.2] - 2026-07-22

### Added

- Public GitHub issue forms for bug reports and feature requests.
- GitHub Actions validation on pushes and pull requests.
- Formal project, program-card, route-verification, and runner-report schemas with a public contract validator.
- A complete synthetic AI startup example with project facts, evidence pack, runner output contract, and verifier commands.
- Mechanism-specific evidence requirements for the AI opportunity pack.

### Fixed

- Prevented the credential scanner from matching its own source while preserving detection of provider-token signatures, private-key markers, credential assignments, and private paths.

## [0.1.1] - 2026-07-22

### Added

- Apache-2.0 licensing, contribution guidance, and maintained changelog/workboard files.
- GitHub repository metadata and public issue forms for open-source maintenance.

### Changed

- Established English as the primary language for public repository documentation.

## [0.1.0] - 2026-07-22

### Added

- Deterministic project classification, scoring, hard gates, routing, and decision traces.
- Local knowledge cards for Web3/ecosystem routes and an AI opportunity pack.
- Independent route verification states for program status, endpoint status, transport, project fit, and project readiness.
- Public synthetic fixtures and regression checks for AI, hardware, SME, and Web3 project shapes.
- English-first public documentation with a maintained documentation mirror.
- Apache License 2.0, contribution guidance, and release-facing project memory.

### Changed

- Public documentation now uses English as the primary language.
- Unknown facts remain unknown and are never promoted to evidence.
- Transport failures are recorded independently and are not interpreted as a closed program.

### Security and privacy

- Private project evidence, live fixtures, application history, feedback records, and generated reports remain excluded from the public repository.

[Unreleased]: https://github.com/HlinorAI/funding-intelligence/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/HlinorAI/funding-intelligence/releases/tag/v0.1.2
[0.1.1]: https://github.com/HlinorAI/funding-intelligence/releases/tag/v0.1.1
[0.1.0]: https://github.com/HlinorAI/funding-intelligence/releases/tag/v0.1.0
