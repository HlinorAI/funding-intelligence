# Workboard

This file is the project's persistent operating memory. Keep it factual, short, and current. Update it when work is completed, a decision changes, or the next action changes.

Last updated: 2026-07-22

## Current status

**Release target:** `v0.1.2`
**Repository mode:** public open-source release
**Core state:** deterministic opportunity routing and verification is implemented; v0.1.2 is published and the next step is external evaluation.

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
- Published GitHub Release `v0.1.2` from immutable tag `v0.1.2` at release commit `8685abf`.
- Added `runtime/render_report.py` for short human-readable Markdown opportunity reports.
- Added public external-project intake and feedback templates plus Git-ignored `tests/external-local/` workspace.

## In progress

- Keep the first public release limited to the current deterministic capability; do not expand the database or add a UI in this release.
- Run three external project evaluations and collect human feedback.
- Use the renderer for the three external reports; do not create another release before feedback identifies a real need.
- Start with one external project end-to-end before recruiting the second and third.

The remote already contains tag `v0.1.0` at commit `d0103e8`. It was not moved to the release-packaging commit because rewriting or force-pushing history is out of scope.

## Next actions

1. Recruit the first external project using `docs/external-test-intake.md`.
2. Convert the intake into a local `project.yaml` and evidence pack.
3. Run runner, verifier, renderer, and collect `docs/external-test-feedback.md`.
4. Record systematic errors before repeating the test with projects two and three.
5. Add live web verification only after the decision logic has been validated externally.

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
- [x] Tag and GitHub Release `v0.1.2` published.
