# Funding Intelligence Report: {{ company }}

## Executive summary

- Classification: {{ classification }}
- Stage: {{ stage }}
- Evidence mode: {{ evidence_mode }}
- Confidence: {{ confidence }}

## Best routes

### 1. {{ program }}

- Decision: `{{ decision }}`
- Resource: {{ resource_type }}
- Why: {{ why }}
- Evidence: {{ evidence }}
- Missing proof: {{ missing_proof }}
- Next action: {{ next_action }}
- Stop condition: {{ stop_condition }}

## Do not apply

| Route | Decision | Reason | Evidence |
|---|---|---|---|
| {{ program }} | `DO_NOT_APPLY` | {{ reason }} | {{ evidence }} |

## Decision trace

The machine report must retain the structured `decision_trace` for every evaluated route. Human-readable prose may summarize it but must not replace it.

## Execution plan

### 14 days

- {{ action }}

### 30 days

- {{ action }}

### 60–90 days

- {{ action }}

## Sources and verification dates

- {{ source }} — checked {{ verified_at }}
