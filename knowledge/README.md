# Funding Intelligence knowledge base

The first version was assembled from a dated funding and BD handbook snapshot. Status checks in the initial source were recorded on 2026-07-20.

This directory contains only the operational data required for routing:

- `programs/*.yaml` — one card per program, mechanism, or BD route;
- `packs/<vertical>/programs/*.yaml` — vertical opportunity packs loaded only when structured facts match;
- `packs/<vertical>/rules/` — vertical fit and stage rules;
- `rules/` — shared classification, scoring, and stop rules;
- `templates/` — working-document templates.

## Card schema

Required fields include:

- `id`, `name`, `ecosystem`;
- `mechanism` — one or more of: `proposal_grant`, `retro`, `incentive`, `accelerator`, `investment`, `subsidy`, `bd`;
- `status.state` — `OPEN`, `ROLLING`, `ACTIVE`, `CLOSED`, `UPCOMING`, `VERIFY`, `WATCH`, `HOLD`, `BD-ONLY`;
- `status.last_checked`, `status.needs_verification`, `status.official_source`;
- `best_fit`, `bad_fit`, `required_evidence`;
- `failure_modes`, `next_action`, `stop_condition`.

Dates and statuses are not permanent. Before a real application, the agent must open the official source and the actual intake endpoint.
