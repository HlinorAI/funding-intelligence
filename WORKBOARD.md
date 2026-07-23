# Workboard

This file is the project's persistent operating memory. Keep it factual, short, and current. Update it when work is completed, a decision changes, or the next action changes.

Last updated: 2026-07-23

## Current status

**Release target:** none
**Current phase:** external decision-quality validation
**Next release:** `v0.2.0` only after benchmark breadth and external feedback justify it.
**Repository mode:** public open-source release
**Core state:** deterministic opportunity routing and verification is implemented; v0.1.2 is published and external evaluation is the active work.

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
- Removed remaining non-English characters from tracked repository artifacts; public repository text is now English-only.

## In progress

- One completed public-only benchmark; nine planned benchmark cases remain uncounted until their facts and expectations are reviewed.
- Promotion and product claims remain blocked until additional cases and human feedback demonstrate practical decision quality.
- Collect factual corrections and owner feedback for Orvixo before treating the benchmark as external validation.
- Prepare the next benchmark in a different sector or affiliation state without committing private project evidence.
- Perform new technical work only when a benchmark or external test identifies a confirmed defect.

The remote already contains tag `v0.1.0` at commit `d0103e8`. It was not moved to the release-packaging commit because rewriting or force-pushing history is out of scope.

## Next actions

1. Review the tracked Orvixo benchmark expectations against the existing public-data review.
2. Record factual corrections and feedback using `docs/external-test-feedback.md`.
3. Select and source the second benchmark with a different affiliation state or sector.
4. Complete the remaining nine cases only after public sources and expected decisions are reviewed.
5. Recruit external projects only after the first owner-reviewed case is assessed.

## Decisions already made

- Funding Intelligence is an internal capability and open-source engine, not a SaaS product in v0.1.
- Local knowledge and deterministic policy come before web search and automatic updates.
- `unknown` is not evidence.
- Cloud credits, incentives, BD, accelerator access, and investment must not be presented as the same resource type or as cash grants.
- A transport failure must not be interpreted as a closed program.
- Public regression fixtures remain synthetic; public-only benchmark cases may be tracked with source URLs, while private project evidence stays outside Git.
- Changes to `runtime/runner.py` and `runtime/verify_route.py` require explicit contract tests and changelog entries.
- Existing program affiliation precedence is a core policy: current/previous successful relationships override fit; rejected relationships require a material change before reapplication; unknown relationships require verification.
- Public benchmark expectations are source-bound and must fail closed when the engine changes; benchmark cases are not evidence of funding outcomes.
- Health checks may create or update a `stale-data` issue, but only a human may change a card's program status or verification date.
- Benchmark and external-test findings are the only authorized triggers for new technical work during the current phase.

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
