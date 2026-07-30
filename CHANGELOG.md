# Changelog

All notable changes to Funding Intelligence are documented in this file.

The project uses semantic version tags for public releases. Program status changes, knowledge-pack updates, decision-rule changes, and verification behavior changes should be recorded when they affect public behavior or recommendations.

## [Unreleased]

### Integration coherence

#### Added

- Shared runtime validation for the canonical `project.schema.yaml` contract.
- Conservative raw-text scaffolding and structured JSON ingestion that produce runner-compatible project documents.
- A public structured intake file for the synthetic AI example.
- End-to-end CI coverage for ingestion, runner, verifier, and Markdown reporting.

#### Changed

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
