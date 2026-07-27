# Changelog

All notable changes to Funding Intelligence are documented in this file.

The project uses semantic version tags for public releases. Program status changes, knowledge-pack updates, decision-rule changes, and verification behavior changes should be recorded when they affect public behavior or recommendations.

## [Unreleased]
## Unreleased

### Added (Phase 2: Product Features Preparation)
- **Ingestion Layer Foundation:** Planned `runtime/ingest.py` to accept raw text/JSON and output strictly validated `project_draft.yaml`, reducing user friction and eliminating manual YAML authoring.
- **Reporting UX Enhancements:** Planned integration of `rich` library into `runtime/render_report.py` for structured, color-coded CLI output, plus Markdown/PDF export capabilities for investor-ready artifacts.
- **Integration Layer Skeleton:** Planned lightweight FastAPI / MCP server wrapper to expose deterministic runner and verifier functions to external tools (Cursor, Claude Desktop, CRM).
- **Automated Live-Verification:** Planned `--auto-verify` flag in `runtime/runner.py` to seamlessly trigger `health_check` on routes flagged with `needs_verification: true`, auto-clearing the flag upon `HEALTHY` HTTP response.
- **External Pilot Framework:** Prepared structure for running evaluations on 3 external real-world projects and collecting structured human feedback (stored in git-ignored `tests/external-local/`).

### Changed
- **Strategic Focus Shift:** Transitioned from Phase 1 (Engine Stabilization & Hermes Agent Fixes, readiness 6/10) to Phase 2 (User-facing Product Features & Bootstrap SaaS Preparation).
- **Documentation:** Clarified self-service analysis workflow in `README.md`, emphasizing the copy-edit-run pattern from `examples/` rather than manual schema authoring.

### Planned
- Execute external pilot evaluations and iterate on ingestion error messages based on human feedback.
- Implement mechanism-specific evidence policies for remaining non-AI knowledge packs (e.g., deeper Web3, Hardware, SME routes).
- Finalize B2B SaaS API authentication stubs for future monetization tiers.

### Added

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

- Run evaluations on three external projects and collect human feedback.
- Add live web verification as a separate adapter after the decision logic is validated.
- Improve knowledge coverage selectively, based on observed project needs.

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

## [0.1.3] - 2026-07-28

### Added
- **Ingestion Layer (Phase 2.1):** Created `runtime/ingest.py` to accept raw text/JSON and output strictly validated `project_draft.yaml`.
  - Supports graceful degradation: missing fields are marked in `needs_user_input` array.
  - Optional LLM extraction stub (`--use-llm` flag) prepared for Phase 2.2 (requires API key).
  - Strict schema validation via `schemas/project_draft.schema.yaml`.
- **Schema:** Added `schemas/project_draft.schema.yaml` with support for `unknown` values and `needs_user_input` tracking.
- **Tests:** Added `tests/test_ingest.py` with 10 test cases covering raw text, JSON, validation, and edge cases.

### Changed
- **Test Coverage:** Increased from 11 to 21 passing tests (pytest).
- **CI/CD:** All GitHub Actions checks remain green.

### Planned
- Phase 2.2: Implement real LLM extraction in `extract_with_llm()` (OpenAI/Anthropic integration).
- Phase 2.3: Human-readable reporting with `rich` library and Markdown/PDF export.
