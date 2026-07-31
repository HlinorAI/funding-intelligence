# Project roadmap

**Last updated:** July 31, 2026
**Current phase:** External decision-quality validation

## Current position

- The latest public release is `v0.1.2`.
- The repository contains a deterministic, evidence-gated runner and an independent route verifier.
- Seven completed public-only benchmarks are tracked: AI/manufacturing, hardware/physical AI, open-source AI infrastructure, enterprise AI, university deeptech, Web3 with a verified previous funding relationship, and Web3 infrastructure with a Base deployment. Planned cases are not evidence until their sources and expected decisions are reviewed.
- GitHub Actions validates runner fixtures, benchmarks, pytest regression tests, schemas, embedded workflow JavaScript, report rendering, and public-safety rules.
- Application endpoints are intentionally sparse: an official information source is not promoted to an actionable route until a specific intake path is verified.

## Operating principles

- The deterministic core does not use an LLM to make routing decisions.
- Unknown facts remain unknown and cannot become positive evidence.
- Health checks are read-only. They can create a review issue but cannot change knowledge cards.
- A current or previous successful program affiliation overrides opportunity fit.
- A known stage mismatch rejects a route. An unknown stage requires verification and is not positive stage-fit evidence.

## Current priorities

1. Accept one consented external project and keep its private evidence outside Git.
2. Run the documented canonical intake-to-report workflow without changing decision rules mid-case.
3. Record false positives, false negatives, useful routes, owner feedback, and time saved.
4. Make additional technical changes only when the external case identifies a reproducible defect.

## Pre-pilot backlog

1. Keep the seven completed public-only benchmarks green and complete the remaining three only when their source boundaries are reviewable.
2. Re-run the canonical workflow as a new user before the first private case.
3. Check the five recorded actionable endpoints before delivering a pilot report.
4. Use the fixed feedback metrics and interview order in `docs/external-test-feedback.md`.
5. If no consented inbound case arrives within 21 days of an intake refresh, review distribution and invitation clarity rather than adding engine features.

## Release boundary

`v0.2.0` is not justified until benchmark breadth and external human feedback demonstrate that the recommendations are useful and safe. No `v0.1.3` release is planned.

## Intentionally deferred

- User interface, SaaS packaging, payments, and marketing.
- Automatic application submission.
- LLM extraction from raw pitch text, an MCP/API layer, and automatic web-driven knowledge updates.
- Broad knowledge-pack expansion before external cases identify a coverage gap.
