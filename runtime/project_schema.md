# Project input schema

`project.yaml` — единый вход для evaluator.

```yaml
schema_version: 1
name: Example project
description: Short factual description
sector: [artificial_intelligence]
stage: seed # idea | prototype | testnet | mainnet | revenue; a list is normalized to its first value
geography: [EU]

product:
  description: What the product does
  customers: [developers]
  technology: [machine_learning]
  ecosystems: []

evidence:
  site: true
  github: true
  live_demo: true
  live_deployment: false
  users: 5000
  transactions: 0
  volume: 0
  tvl: 0
  revenue: false
  pilots: 2
  partners: 0
  metrics: true
  audit: false

# Use `unknown` when the field was not checked; do not use it as a positive claim.

needs:
  goals: [funding] # funding | partnerships | accelerator | distribution | technical_support
  funding: 500000
  runway_months: 12

constraints:
  no_token: true
  no_dilution: false
  native_ecosystems: []
  target_ecosystems: []
  generic_multichain: false

access:
  champions: 0
  warm_intros: 0
```

Missing facts stay `UNKNOWN` in the report. `false` means the user checked and the evidence is absent; omit a field when it is unknown.
