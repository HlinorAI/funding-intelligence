# Report schema

The runner emits a YAML report with:

```yaml
report_version: 1
project: Example project
classification:
  stage: seed
  sectors: [artificial_intelligence]
  goals: [funding]
  confidence: medium
gate:
  status_verified: false
  source_fresh: false
  application_endpoint_exists: true
  mechanism_identified: true
  evidence_requirements_known: true
  next_action_exists: true
  passed: false
opportunities:
  - program_id: base-funding-ladder
    score: 62                 # legacy compatibility field
    policy_score: 62          # deterministic routing policy score
    score_semantics: deterministic_policy_score
    decision: VERIFY_FIRST
    source_freshness: {state: stale, age_days: 8, max_age_days: 7}
    mechanism: retro
    why: []
    missing: []
    next_action: {}
    stop_condition: "..."
do_not_apply: []
coverage_gaps: []
decision_trace:
  - program: Base Funding Ladder
    considered: true
    rejected: false
    score: 76
    positive: [shipped product, ecosystem fit]
    negative: [no deployment]
    decision: VERIFY_FIRST
    why: [Need current endpoint verification]
execution_plan:
  days_7: []
  days_30: []
  days_90: []

quality:
  status: not_calibrated
  sample_size: 0
```

`opportunities` contains at most twelve routes. Closed or structurally invalid routes are listed in `do_not_apply`, not silently omitted. `source_fresh` and `source_freshness` make the dated-snapshot boundary explicit; a stale source cannot pass the status gate.
