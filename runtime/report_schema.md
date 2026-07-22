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
  application_endpoint_exists: true
  mechanism_identified: true
  evidence_requirements_known: true
  next_action_exists: true
  passed: false
opportunities:
  - program_id: base-funding-ladder
    score: 62
    decision: VERIFY_FIRST
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
```

`opportunities` contains at most seven routes. Closed or structurally invalid routes are listed in `do_not_apply`, not silently omitted.
