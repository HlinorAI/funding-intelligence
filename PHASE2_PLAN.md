# Integration Coherence Plan

This file records the narrow integration work required before another external evaluation. It does not authorize a new product layer, API, SaaS packaging, or automatic application workflow.

## Objective

Preserve the deterministic decision engine while making the public self-service path internally consistent:

`structured intake → canonical project → runner → verifier → Markdown report`

## Completed integration work

- [x] Use `schemas/project.schema.yaml` as the only project contract.
- [x] Make structured JSON and conservative raw-text ingestion produce canonical project documents.
- [x] Validate project inputs in the runner and route verifier.
- [x] Consolidate human reporting in `runtime/render_report.py`.
- [x] Test reporting against real runner and verifier outputs.
- [x] Add a public synthetic intake artifact and an end-to-end CI workflow.
- [x] Keep unresolved facts explicit in `needs_user_input` and preserve `unknown` values.

## External-validation boundary

The next product-quality signal must come from one consented external project. Its private evidence, generated reports, and feedback stay in Git-ignored local paths.

Success requires:

1. correct project classification;
2. at least one defensible route or a useful justified rejection;
3. a clear next action;
4. no invented evidence;
5. owner feedback on usefulness and time saved.

## Intentionally deferred

- LLM-based fact extraction from unstructured pitch text.
- MCP or HTTP APIs.
- Web UI, accounts, billing, and SaaS packaging.
- Automatic status mutation or automatic application submission.
- Broad knowledge expansion without an observed external-case need.
- A new public release before external decision quality justifies one.
