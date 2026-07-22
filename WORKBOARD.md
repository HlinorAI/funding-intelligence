# Workboard

This file is the project's persistent operating memory. Keep it factual, short, and current. Update it when work is completed, a decision changes, or the next action changes.

Last updated: 2026-07-22

## Current status

**Release target:** `v0.1.2`
**Repository mode:** public open-source release
**Core state:** deterministic opportunity routing and verification is implemented; v0.1.2 release candidate is CI-green and ready to publish.

## Completed

- Built the local knowledge layer with core Web3/ecosystem cards and an AI pack.
- Added deterministic project classification, scoring, hard gates, routing, and decision traces.
- Added route verification with independent program, endpoint, transport, fit, readiness, and final-decision states.
- Added public synthetic fixtures and regression checks for five project shapes.
- Made English the primary public documentation language and preserved a complete Russian README.
- Added Apache-2.0 licensing and contribution/release documentation.
- Published GitHub Releases `v0.1.0` and `v0.1.1`; configured repository description, topics, and Issues.
- Added public Bug Report and Feature Request issue forms to `main`.
- Added GitHub Actions validation for pushes and pull requests.
- Added formal YAML schemas and `runtime/validate_schemas.py` for public contract validation.
- Resolved the CI failure caused by the credential scanner matching literal signatures in its own validator source; added synthetic credential and self-match regression checks.
- Added a copyable public AI end-to-end example with evidence pack and expected route decisions.
- Added mechanism-specific evidence requirements to all AI opportunity cards and schema checks for their coverage.
- Passed GitHub Actions `Validate` run `29901485917` on commit `9355b02`.

## In progress

- Keep the first public release limited to the current deterministic capability; do not expand the database or add a UI in this release.
- After publishing `v0.1.2`, run three external project evaluations and collect human feedback.

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
- [ ] Tag and GitHub Release `v0.1.2` published.
