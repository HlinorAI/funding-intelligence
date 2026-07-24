# Changelog

All notable changes to Funding Intelligence are documented in this file.

The project uses semantic version tags for public releases. Program status changes, knowledge-pack updates, decision-rule changes, and verification behavior changes should be recorded when they affect public behavior or recommendations.

## [Unreleased] - 2026-07-25

### 🎉 Phase 1 Complete: Hermes Agent Review Critical Fixes (Readiness: 2/10 → 6/10)

#### Fixed
- **Runner Affiliation Logic**: Reverted `program_affiliation_state` in `runtime/runner.py` to correctly return `None` for missing affiliations, and strictly check `== "unknown"`. This resolves false `VERIFY_FIRST` decisions in hardware/empty cases while preserving correct behavior for known programs.
- **AI Program Card Stages**: Added `unknown` to `routing.stages` in `knowledge/packs/ai/programs/` (aws-activate, microsoft-for-startups, nvidia-inception, openai-startups, y-combinator). This allows the runner to properly evaluate projects with `stage: unknown` (e.g., `orvixo-001` benchmark).
- **Schema Validation**: Removed invalid/broken program card YAMLs from `knowledge/programs/` that were violating `program-card.schema.yaml`.

#### CI/CD Status
- ✅ **11/11 pytest tests passing** locally and in GitHub Actions.
- ✅ Runner regression suite (7 cases) passing.
- ✅ Decision-quality benchmark suite passing.
- ✅ Health-check self-test and Schema validation passing.

---

## [Unreleased]

### Added

- Markdown report renderer combining runner and route-verification outputs for human review.
- Public external-project intake and feedback templates, with a Git-ignored local workspace for real pilot cases.
- Public affiliation metadata in the project schema, with regression fixtures for current, previous successful, and rejected program relationships.
- Read-only program-card health check with weekly/manual GitHub Actions workflow, artifact output, and a human-reviewed `stale-data` issue lifecycle.
- Validation of embedded `actions/github-script` JavaScript in workflow YAML.
- Explicit per-card handling for manually verified GitHub transport restrictions (`403` and `429`) in the health check.
- Removed the legacy language mirror and translated the remaining tracked Hlinor report so public repository content is English-only.

### Fixed

- Current program affiliations now hard-gate duplicate accelerator/program applications and remain visible in the rejected-route shortlist.
- Affiliation precedence now distinguishes current/previous successful, rejected, and unknown program relationships before opportunity fit becomes an application recommendation.
- The project schema now accepts a single `unknown` value for fields that may be boolean or numeric without treating the value as ambiguous.
- Corrected invalid embedded JavaScript in the health-check workflow.
- Normalized YAML date metadata in health-check reports so JSON artifact output remains serializable.
- Updated verified Aptos and Stable official source routes after the first program-card health review.
- Prevented known, manually reviewed GitHub `403` and `429` access restrictions from reopening the stale-data issue while retaining their raw report state.
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
