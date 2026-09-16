# Changelog

## 2026-09-14

### Added

- Confirmed the Sui Ecosystem Academic Research Awards intake at its hosted
  Tally application form (`tally.so/r/3X85rz`). A human visually confirmed the
  form, the link was extracted from the program page's own data, and the form
  answered a live probe. Endpoint coverage is now 9 of 50 cards.

## 2026-09-13

### Added

- Recorded the first human-confirmed application endpoints from the
  endpoint-candidate review: the Ethereum Foundation ESP applicants page and
  the Arbitrum DAO program forum category as `confirmed`, and the EIC
  Accelerator portal topic as `gated` behind EU portal sign-in. Eight of 50
  cards now carry a recorded endpoint.
- Split the Sui Ecosystem Academic Research Awards into a dedicated rolling
  research-grant card after the endpoint scan surfaced the program. The card
  stays source-only until the submission link in the program-page callout is
  opened and confirmed by a human.

## 2026-09-12

### Added

- Added a read-only application-endpoint scanner (`runtime/endpoint_scan.py`)
  that fetches the official page of every source-only card, extracts links
  plausibly leading to an application or intake, and writes a human-review
  queue to `reports/endpoint-candidates.yaml`. Candidates are unverified
  leads; a card's `verification.application_url` may still be recorded only
  by a human who confirmed the route. Transport failures and pages without
  candidate links are not evidence about endpoints. Its self-test joined the
  local validation gate.

## 2026-09-11

### Added

- Added a deterministic pathway-window gate: a declared `pathway.window.closes`
  date in the past rejects the route with `DO_NOT_APPLY`, and a future
  `pathway.window.opens` date holds the route at `VERIFY_FIRST` until a human
  re-verifies the card. Runner and route-verifier outputs expose
  `pathway_window`, the aggregate report gate gained a `window_open` key, and a
  closed window overrides reapplication advice for previously rejected
  applicants.
- Added a read-only official-source content watch (`runtime/source_watch.py`)
  that hashes official page bodies and reports changed pages as a
  human-review signal. Digest state is stored outside Git; the tool never
  mutates knowledge cards, and transport failures are never evidence that a
  program changed or closed. Its self-test joined the local validation gate.

## 2026-09-07

### Added

- Added a local funding-route lifecycle state machine covering discovery, eligibility, application readiness, follow-up and outcome.
- Added explicit evidence references for recorded submission and outcome events.

### Security

- The lifecycle tool only updates a local YAML state file; it does not submit applications or contact external programmes.

All notable changes to Funding Intelligence are documented in this file.

The project uses semantic version tags for public releases. Program status changes, knowledge-pack updates, decision-rule changes, and verification behavior changes should be recorded when they affect public behavior or recommendations.

## [Unreleased]

### Product validation boundary

#### Changed

- Narrowed the next product test from generic funding matching or grant
  management to an evidence-integrity pre-screen for human operator/advisor
  reviewers.
- Added a consented operator-pilot protocol with redaction, frozen decision
  rules, evidence fields, metrics, pass conditions, and stop conditions.
- Marked the July strategic status document as historical and aligned the
  current roadmap with the actual repository state.

### Market and verification boundary

#### Added

- Added the 2026-08-29 market-landscape review. It records the crowded
  discovery/matching market, the stronger operator/advisor wedge, and the
  absence of public pilot or demand evidence.
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

- Apache-2.0 licensing, contribution guidance, and maintained changelog files.
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
