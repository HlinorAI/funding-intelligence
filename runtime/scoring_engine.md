# Deterministic scoring engine

The runner calculates a comparable score before the LLM writes prose.

## Components

`score = strategic_fit + technical_fit + evidence + mechanism_fit + readiness + access - penalties`

Maximum positive score is 100:

- `strategic_fit`: 25 — target/native ecosystem or explicit product match;
- `technical_fit`: 20 — native deployment/technology and architecture evidence;
- `evidence`: 20 — live demo, repo, deployment, users, metrics, pilots and revenue;
- `mechanism_fit`: 15 — goal and stage match the card's mechanism;
- `readiness`: 10 — milestones, budget, team, legal and security readiness;
- `access`: 10 — champion, warm intro, partner or named integration owner.

## Penalties

- `closed_program`: -25;
- `wrong_stage`: -20;
- `no_proof`: -15;
- `mechanism_mismatch`: -15;
- `generic_multichain`: -20;
- `no_milestones`: -10;
- `no_distribution_plan`: -10.

## Deterministic limits

The engine does not infer that a project has traction from prose. It only reads structured fields from `project.yaml`. A route may score highly and still be excluded from `NOW` by the anti-hallucination gate.

## Decision bands

- `80–100`: `NOW` if all gates pass;
- `65–79`: `NEXT` if all gates pass;
- `50–64`: `LATER` if all gates pass;
- `<50`: `DO_NOT_APPLY`;
- any failed gate: `VERIFY_FIRST` or `BUILD_FIRST`, never `NOW`.
