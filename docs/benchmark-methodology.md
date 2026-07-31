# Benchmark methodology

Funding Intelligence benchmarks measure decision quality, not funding outcomes.

## Case requirements

Each completed case must use either public sources or explicitly synthetic facts. Public-only cases must include source URLs and must leave unproven legal, traction, revenue, deployment, and access facts as `unknown`.

Each case records expected behavior at two boundaries:

1. the deterministic runner, which classifies and routes against the local knowledge snapshot;
2. the route verifier, which adds source status, endpoint, readiness, evidence requirements, and route-specific action.

## Review dimensions

For every case, reviewers should score:

- classification accuracy;
- correct rejection of irrelevant or already-affiliated routes;
- usefulness of at least one discovered route;
- clarity of the next action;
- false positives and false negatives;
- whether any unknown fact was incorrectly promoted to evidence.

The suite also reports coverage breadth separately from decision correctness:

- completed case shapes versus the ten-case target;
- represented sectors and mechanism boundaries;
- routes with confirmed application endpoints;
- public-only cases versus consented owner-reviewed cases.

Passing public-only benchmarks is regression evidence, not external validation.

## Anti-hallucination rules

- Public marketing copy is not automatically customer traction.
- A public company profile does not establish revenue, users, pilots, legal entity, or deployment unless it says so.
- A previous application is not a successful affiliation.
- A route status is not current unless the local card records an official source and verification date.
- Expected decisions must be justified by facts in the case or by an explicit benchmark review note.

## Running the suite

```bash
python3 runtime/run_benchmarks.py
```

The suite must fail when a declared expected decision changes. It does not silently rewrite expectations from the current engine output.
