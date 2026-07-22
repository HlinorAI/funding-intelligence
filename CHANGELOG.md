# Changelog

All notable changes to Funding Intelligence are documented in this file.

The project uses semantic version tags for public releases. Program status changes, knowledge-pack updates, decision-rule changes, and verification behavior changes should be recorded when they affect public behavior or recommendations.

## [Unreleased]

### Added

- Markdown report renderer combining runner and route-verification outputs for human review.
- Public external-project intake and feedback templates, with a Git-ignored local workspace for real pilot cases.
- Public affiliation metadata in the project schema, with regression fixtures for current, previous successful, and rejected program relationships.

### Fixed

- Current program affiliations now hard-gate duplicate accelerator/program applications and remain visible in the rejected-route shortlist.
- Affiliation precedence now distinguishes current/previous successful, rejected, and unknown program relationships before opportunity fit becomes an application recommendation.

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

## [0.1.0] - 2026-07-22

### Added

- Deterministic project classification, scoring, hard gates, routing, and decision traces.
- Local knowledge cards for Web3/ecosystem routes and an AI opportunity pack.
- Independent route verification states for program status, endpoint status, transport, project fit, and project readiness.
- Public synthetic fixtures and regression checks for AI, hardware, SME, and Web3 project shapes.
- English-first public documentation with a maintained Russian README mirror.
- Apache License 2.0, contribution guidance, and release-facing project memory.

### Changed

- Public documentation now uses English as the primary language.
- Unknown facts remain unknown and are never promoted to evidence.
- Transport failures are recorded independently and are not interpreted as a closed program.

### Security and privacy

- Private project evidence, live fixtures, application history, feedback records, and generated reports remain excluded from the public repository.

[Unreleased]: https://github.com/HlinorAI/funding-intelligence/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/HlinorAI/funding-intelligence/releases/tag/v0.1.2
[0.1.0]: https://github.com/HlinorAI/funding-intelligence/releases/tag/v0.1.0
