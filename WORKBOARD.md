# Workboard

This file is the project's persistent operating memory. Keep it factual, short, and current. Update it when work is completed, a decision changes, or the next action changes.

Last updated: 2026-09-11

## Current status

**Release target:** none
**Current phase:** pathway freshness and external decision-quality validation
**Next release:** `v0.2.0` only after benchmark breadth and external feedback justify it.
**Repository mode:** public open-source release
**Core state:** deterministic opportunity routing and verification is implemented; v0.1.2 is published and external evaluation is the active work.
**Market state:** generic discovery/matching and grant-management products are crowded; no consented pilot or repeat-usage evidence exists yet. The next testable wedge is an evidence-integrity pre-screen for human operator/advisor reviewers.
**Pilot prospect state:** four first-wave and four second-wave operator contacts were sent on 2026-08-29; a 2026-08-30 refresh added EIT Digital Co-Creation and FreeCAD as route-only candidates. No consented pilot exists yet.
**Intake state:** The live Tally handler was repaired, the failed event was replayed with HTTP 200, and CRM/Sheets verification confirmed the resulting row on 2026-08-30.

## Completed

- Built the local knowledge layer with core Web3/ecosystem cards and an AI pack.
- Added deterministic project classification, scoring, hard gates, routing, and decision traces.
- Added route verification with independent program, endpoint, transport, fit, readiness, and final-decision states.
- Added public synthetic fixtures and regression checks for five project shapes.
- Made English the sole public documentation language.
- Added Apache-2.0 licensing and contribution/release documentation.
- Published GitHub Releases `v0.1.0` and `v0.1.1`; configured repository description, topics, and Issues.
- Added public Bug Report and Feature Request issue forms to `main`.
- Added GitHub Actions validation for pushes and pull requests.
- Added formal YAML schemas and `runtime/validate_schemas.py` for public contract validation.
- Resolved the CI failure caused by the credential scanner matching literal signatures in its own validator source; added synthetic credential and self-match regression checks.
- Added a copyable public AI end-to-end example with evidence pack and expected route decisions.
- Added mechanism-specific evidence requirements to all AI opportunity cards and schema checks for their coverage.
- Passed GitHub Actions `Validate` run `29901485917` on commit `9355b02`.
- Published GitHub Release `v0.1.2` from immutable tag `v0.1.2` at release commit `8685abf`.
- Added `runtime/render_report.py` for short human-readable Markdown opportunity reports.
- Added public external-project intake and feedback templates plus Git-ignored `tests/external-local/` workspace.
- Prepared local-only public-data benchmark v1 for Orvixo with source list, evidence pack, runner output, verifier output, and Markdown report; no founder feedback has been collected yet.
- Fixed the first benchmark logic bug: current program affiliations now produce `DO_NOT_APPLY` and cannot be hidden by the rejected-route shortlist cap; added a synthetic regression case.
- Expanded the affiliation model to current, previous successful, rejected, and unknown relationship states with three regression cases.
- Added the Decision Quality benchmark contract, one completed public-only Orvixo case, immutable runner/verifier expectations, and benchmark methodology.
- Added read-only program-card health checking with deterministic HTTP classification, self-test coverage, and a scheduled GitHub workflow that never mutates knowledge cards.
- Resolved the health-check workflow's embedded JavaScript syntax defect and added regression validation for `actions/github-script` blocks.
- Resolved health-check JSON artifact serialization for YAML date metadata, found by the first manual workflow dispatch.
- Triaged the first health-check issue: updated verified Aptos and Stable sources, retained OpenAI's verified access path, and made manually reviewed `403`/`429` transport restrictions visible but non-actionable.
- Added pytest execution to CI so the public test-suite claim is checked on every push and pull request.
- Made project-stage policy explicit: unknown stages require verification, while a known stage outside a card's declared range produces `DO_NOT_APPLY`.
- Corrected the portable pytest runner harness exposed when the suite was added to CI.
- Removed the unsupported Phase 1 readiness claim and aligned the public roadmap to the current external-validation phase.
- Removed remaining non-English characters from tracked repository artifacts; public repository text is now English-only.
- Added a second source-bound public benchmark for Almond, covering hardware/physical AI, provider-eligibility evidence boundaries, and current-affiliation precedence.
- Added a third source-bound public benchmark for rotki, covering a verified previous successful Optimism funding relationship and affiliation precedence over ecosystem fit.
- Added a fourth source-bound public benchmark for Blockscout, covering Base deployment fit and program-scoped affiliation precedence.
- Resolved the verifier eligibility/readiness contract mismatch identified by the technical audit and added rejected-affiliation schema coverage.
- Added executable structured evidence policies for AI cards so route-specific requirements are evaluated as fields and operators rather than free-text heuristics.
- Separated official program sources from verified application endpoints; routes without an explicit application or access URL now return `NO_ACTIONABLE_ENDPOINT` instead of inheriting a program information page.
- Completed an all-card application-endpoint coverage audit: five cards have recorded endpoints, while 44 source-only cards remain intentionally non-actionable until a route-specific intake is verified.
- Added a copy-and-run README workflow for self-service local analysis and corrected the Base route-verification example.
- Consolidated project ingestion, routing, verification, and reporting around the canonical `project.schema.yaml` contract.
- Added fail-closed project validation to the runner and route verifier.
- Removed the incompatible draft schema and duplicate reporting implementation.
- Added a public structured intake example and end-to-end CI coverage for ingestion through Markdown reporting.
- Published a two-minute Tally intake form for consented pilot projects and linked it from GitHub Discussion #2.
- Enforced all runner hard gates before score-band decisions so incomplete application endpoints, card contracts, or affiliations cannot reach `NOW`, `NEXT`, or `LATER`; added regression coverage.
- Aligned the report-level aggregate gate with route-level affiliation hard gates and added regression coverage for unknown and current affiliations.
- Added controlled vocabulary aliases for sectors, stages, and ecosystems at ingestion and routing boundaries.
- Added a validated, optional provenance contract for source-backed program-card review metadata.
- Separated deterministic `policy_score` from empirical quality metadata; reports now state that quality is not calibrated before owner-reviewed outcomes exist.
- Added reproducible packaging with `pyproject.toml`, `uv.lock`, console entry points, and `python -m runtime.check`.
- Added a local credential privacy gate, explicit redaction helper, and documented security/privacy prerequisites before SaaS/API work.
- Added a pathway contract for lifecycle, windows, funding terms and source-change dates.
- Expanded mechanism/resource vocabularies for challenge, research, milestone, pilot, credits and non-dilutive routes.
- Added eight current announcement-backed source-only cards across EIC, NSF, Women TechEU, Filecoin, Tether, OpenAI and Base Batches.
- Preserved verified endpoint routes in the runner shortlist when new source-only cards are added.
- Kept `--all-ai` scoped to the AI opportunity pack and updated endpoint coverage to 49 cards / 44 source-only routes.
- Committed the previously uncommitted outreach contour, freshness policy, planning docs, and eight new program cards after a credential and third-party-contact scan; outreach contact records stay local via `.gitignore`.
- Added a deterministic pathway-window gate: a declared `pathway.window.closes` in the past rejects the route and a future `opens` holds it at `VERIFY_FIRST`; runner and verifier outputs expose `pathway_window` and the report gate gained `window_open`.
- Re-verified eight program cards against official pages on 2026-09-11: YC Winter 2027 intake (deadline 2026-11-02), EIC continuous submission with the 2026-11-04 cut-off, Base Batches 004 closed 2026-09-10, NSF initiative live without an open solicitation, and the five actionable AI endpoints.
- Added `runtime/source_watch.py`, a read-only official-page content watch that flags changed sources as a human-review signal with a Git-ignored digest state; its self-test joined the validation gate.
- Added `runtime/endpoint_scan.py`, a read-only application-endpoint scanner for source-only cards; its first live run surfaced the EIC Accelerator intake on the EU Funding and Tenders portal as an unconfirmed candidate, which stays out of card verification until a human confirms the route.
- Recorded the first human-confirmed endpoints from the candidate queue on 2026-09-13: Ethereum ESP applicants page (confirmed), Arbitrum DAO program forum category (confirmed), and the EIC Accelerator portal topic (gated behind portal sign-in); endpoint coverage is now 8 of 50 cards. Split the Sui Academic Research Awards into a dedicated rolling research-grant card that stays source-only until its submission link is confirmed.
- Confirmed the Sui Academic Research Awards hosted Tally form on 2026-09-14 after extracting the link from the program page data plus a human browser check and a live probe; endpoint coverage is now 9 of 50 cards.
- Wired the full K-18 contour for local execution on 2026-09-16: mailbox credentials via gitignored `ops/k18/.env` plus `run_local.sh`, a read-only reply scan over INBOX and the localized Sent folder, and the browser-free search chain (official pages, Google News RSS, GitHub issues) with contact enrichment and qualification into a manual-review queue. The free email finder remains Hermes-only. First local run: CPA.com contacts are already covered by the two contacted recipients; EIT Urban Mobility, Techstars Anywhere, and The Open Accelerator qualified for manual review with no new sends.

## In progress

- K-18 Funding Match Research remains isolated from founder outreach; its first
  live discovery pass was blocked by the DuckDuckGo human-verification
  challenge. Four explicitly approved operator-pilot messages were sent on
  2026-08-29; wait for replies and review the second-wave research before any
  further outreach.
- Automated/founder outreach remains disabled; the four-message send was a
  one-shot operator-approved batch with `send_allowed=true` only in its private
  manifest.
- Four second-wave operator messages were sent after explicit approval and
  reconciled in Zoho Sent; recipient inbox placement remains unverified.
- K-18 search results now require an explicit `project` or `program_operator`
  lane; unknown lanes cannot produce drafts.
- The prepared K-18 systemd timer is disabled while the project remains in
  preparation-only mode.
- The runner and route verifier now enforce the seven-day source-freshness
  policy; stale snapshots cannot reach `NOW`.
- Re-ran the canonical public example through ingestion, runner, verifier and
  Markdown rendering; the generated artifacts stayed in a temporary directory.

- Seven completed public-only benchmarks; three planned benchmark cases remain uncounted until their facts and expectations are reviewed.
- Promotion and product claims remain blocked until additional cases and human feedback demonstrate practical decision quality.
- Collect factual corrections and owner feedback for Orvixo before treating the benchmark as external validation.
- External validation is intentionally awaiting a consented operator/advisor pilot through the published intake or a voluntary operator contact; no outbound founder outreach is planned.
- Prepare a public benchmark for a distinct project shape without committing private project evidence.
- Perform new technical work only when a benchmark or external test identifies a confirmed defect.
- Await one consented operator/advisor pilot for the next complete intake-to-feedback cycle.
- Added pre-pilot decision-quality coverage for open-source AI infrastructure, enterprise AI, and university-linked deeptech without expanding the knowledge base.
- Fixed the external feedback metrics and interview order before the first owner review.

The remote already contains tag `v0.1.0` at commit `d0103e8`. It was not moved to the release-packaging commit because rewriting or force-pushing history is out of scope.

## Next actions

0. Monitor the repaired Tally intake for the next consented case and run the
   canonical ingestion-to-report workflow without changing expectations.
1. Review replies from the eight approved operator-pilot contacts; do not send
   another batch before assessing response quality.
2. Run one consented operator/advisor pilot through intake, triage, route
   verification and feedback.
3. Configure an approved search API/provider for K-18 only if the pilot needs
   a live discovery pass; do not infer demand from search volume or drafts.
4. Monitor the published Tally intake and GitHub Discussion #2 for one consented case.
5. Store its intake, evidence, generated YAML, report, and feedback only under ignored local paths.
6. Run the canonical ingestion-to-report workflow without modifying expectations during the case.
7. Record factual corrections and feedback using `docs/external-test-feedback.md`.
8. Open technical work only for a reproducible defect or a demonstrated coverage gap.
9. If no consented case arrives within 21 days of an intake refresh, review the invitation and distribution channel instead of adding engine features.

## Decisions already made

- Funding Intelligence is an internal capability and open-source engine, not a SaaS product in v0.1.
- Local knowledge and deterministic policy come before web search and automatic updates.
- `unknown` is not evidence.
- Cloud credits, incentives, BD, accelerator access, and investment must not be presented as the same resource type or as cash grants.
- A transport failure must not be interpreted as a closed program.
- Public regression fixtures remain synthetic; public-only benchmark cases may be tracked with source URLs, while private project evidence stays outside Git.
- Changes to `runtime/runner.py` and `runtime/verify_route.py` require explicit contract tests and changelog entries.
- Legacy program cards without provenance remain valid until source-backed metadata can be backfilled; migration must not invent hashes or reviewers.
- `score` remains a compatibility field equal to `policy_score`; neither field is a probability of acceptance.
- SaaS/API work is blocked until tenant isolation, consent, retention/deletion, auditability, redaction, secret scanning, and external-provider controls are designed and tested.
- Existing program affiliation precedence is a core policy: current/previous successful relationships override fit; rejected relationships require a material change before reapplication; unknown relationships require verification.
- Public benchmark expectations are source-bound and must fail closed when the engine changes; benchmark cases are not evidence of funding outcomes.
- Health checks may create or update a `stale-data` issue, but only a human may change a card's program status or verification date.
- Benchmark and external-test findings are the only authorized triggers for new technical work during the current phase.
- A card's `routing.stages` is a hard boundary only when the project stage is known; `unknown` is not positive stage-fit evidence.
- An official program source is evidence for program status only. `current affiliation > opportunity fit`, and a verified application endpoint is required before a route can be considered actionable.
- The market has mature discovery, matching, application-support, and grant-management products; the current wedge is an evidence-integrity pre-screen with explicit source freshness and route-specific intake verification.

## Intentionally deferred

- Web UI, SaaS packaging, payments, and marketing.
- Automatic application submission.
- Broad expansion to hundreds of additional programs.
- Automatic web-driven knowledge updates.
- Public release of real project evidence, application history, feedback records, or generated private reports.
- Additional public benchmarks remain intentionally uncommitted until their facts, source coverage, and expected decisions are reviewed.
- Automatic mutation of knowledge cards from HTTP results remains intentionally deferred.

## Recently completed

- [x] GitHub Release `v0.1.0` published from the existing technical snapshot.
- [x] GitHub Release `v0.1.1` published from the release-packaging tag.
- [x] GitHub About description and topics configured.
- [x] GitHub Issues confirmed enabled.

## Release checklist

- [x] Apache-2.0 license file added.
- [x] `CONTRIBUTING.md` added.
- [x] `CHANGELOG.md` and `WORKBOARD.md` added.
- [x] Existing Git tag `v0.1.0` confirmed pushed (points to `d0103e8`).
- [x] GitHub Releases `v0.1.0` and `v0.1.1` published.
- [x] GitHub About description and topics configured.
- [x] GitHub Issues confirmed enabled.
- [x] Public issue forms added to `main`.
- [x] CI workflow added for push and pull request validation.
- [x] Formal schemas and schema validator added.
- [x] Public end-to-end AI example added.
- [x] Route-specific evidence requirements completed.
- [x] GitHub Actions `Validate` run `29901485917` passed.
- [x] Tag and GitHub Release `v0.1.2` published.
