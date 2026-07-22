# Workboard

This file is the project's persistent operating memory. Keep it factual, short, and current. Update it when work is completed, a decision changes, or the next action changes.

Last updated: 2026-07-22

## Current status

**Release target:** `v0.1.0`
**Repository mode:** public open-source release
**Core state:** deterministic opportunity routing and verification is implemented; public release packaging is ready except for GitHub metadata/release settings.

## Completed

- Built the local knowledge layer with core Web3/ecosystem cards and an AI pack.
- Added deterministic project classification, scoring, hard gates, routing, and decision traces.
- Added route verification with independent program, endpoint, transport, fit, readiness, and final-decision states.
- Added public synthetic fixtures and regression checks for five project shapes.
- Made English the primary public documentation language and preserved a complete Russian README.
- Added Apache-2.0 licensing and contribution/release documentation.

## In progress

- Finish GitHub release metadata for `v0.1.0`: description, topics, Issues, tag, and Release notes.
- Keep the first public release limited to the current deterministic capability; do not expand the database or add a UI in this release.

The remote already contains tag `v0.1.0` at commit `d0103e8`. It was not moved to the release-packaging commit because rewriting or force-pushing history is out of scope.

## Next actions

1. Run three external project evaluations.
2. Ask reviewers whether the classification, rejection logic, next action, and report saved time.
3. Record feedback and rule changes without weakening hard gates.
4. Add live web verification only after the decision logic has been validated externally.
5. Expand knowledge packs selectively from observed route gaps.

## Decisions already made

- Funding Intelligence is an internal capability and open-source engine, not a SaaS product in v0.1.
- Local knowledge and deterministic policy come before web search and automatic updates.
- `unknown` is not evidence.
- Cloud credits, incentives, BD, accelerator access, and investment must not be presented as the same resource type or as cash grants.
- A transport failure must not be interpreted as a closed program.
- Public fixtures must be synthetic; private project evidence stays outside Git.
- Changes to `runtime/runner.py` and `runtime/verify_route.py` require explicit contract tests and changelog entries.

## Intentionally deferred

- Web UI, SaaS packaging, payments, and marketing.
- Automatic application submission.
- Broad expansion to hundreds of additional programs.
- Automatic web-driven knowledge updates.
- Public release of real project evidence, application history, feedback records, or generated private reports.

## Release checklist

- [x] Apache-2.0 license file added.
- [x] `CONTRIBUTING.md` added.
- [x] `CHANGELOG.md` and `WORKBOARD.md` added.
- [x] Existing Git tag `v0.1.0` confirmed pushed (points to `d0103e8`).
- [ ] GitHub Release `v0.1.0` published.
- [ ] GitHub About description and topics configured.
- [ ] GitHub Issues confirmed enabled.
