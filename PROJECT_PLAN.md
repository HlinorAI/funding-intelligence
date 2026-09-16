# Funding Intelligence project plan

## Objective

Maintain a local-first, deterministic engine that routes startups and technical
projects to evidence-gated funding, credits, accelerator, investment, pilot,
and business-development pathways.

## Current architecture

- Python runtime with YAML program cards and JSON Schema contracts.
- Deterministic runner and independent route verifier; no LLM or web call in
  the decision core.
- Public Web3/ecosystem cards plus an AI opportunity pack.
- Source provenance, explicit policy scores, privacy scanning, locked `uv`
  packaging, benchmarks, and CI validation.

## Current status

The engine is in external decision-quality validation. The knowledge base now
contains 49 cards, including eight refreshed pathway cards for current AI,
deep-tech and ecosystem funding signals. New announcement-backed cards remain
non-actionable until a route-specific intake endpoint is verified.

Outreach and lead research run as a separate, local-only operational contour
outside this repository. No private operational state, contacts, or mailbox
integration belongs in the public tree.

## Product boundary

The product is an evidence-integrity and pre-screening layer for small
accelerators, grant advisers, and programme teams reviewing heterogeneous
applicant or project pipelines. It is not a grant marketplace, application
writer, CRM, award-management system, funding predictor, or automatic decision
maker.

The narrow job to validate is: make a case review-ready by checking hard
criteria, binding material claims to sources, exposing source freshness and
route endpoint state, listing missing evidence, and producing an explainable
hold/reject/advance recommendation for a human reviewer.

## Priorities

1. Reconcile project documentation around the operator/advisor evidence-
   pre-screening wedge.
2. Keep the six-hour public-signal lead search running and review only newly
   qualified prospects; do not infer demand from delivery, drafts, or search
   volume.
3. Review the existing approved outreach and obtain one consented operator
   pilot.
4. Run a measured batch comparison with redacted cases before adding product
   layers.
5. Add only the smallest batch evidence-pack or reviewer-queue capability that
   the pilot demonstrates is necessary.
6. Calibrate policy quality before considering SaaS, API, or MCP packaging.

## Constraints

- `unknown` is never evidence.
- An official programme page is not an application endpoint.
- A single ecosystem brand must not imply that all cohorts, RFPs, credits or
  retroactive routes share one intake.
- The market has mature discovery, matching, and application-support products;
  the current wedge is narrower: an evidence-integrity pre-screen for
  operator/advisor reviewers with explicit source freshness and route-specific
  intake verification.
- Knowledge cards are updated by reviewed changes, not HTTP health checks.
