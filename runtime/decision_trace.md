# Decision trace

Every evaluated card includes a `decision_trace` object in the report:

```yaml
decision_trace:
  program: Base Funding Ladder
  considered: true
  rejected: false
  score: 76
  positive:
    - shipped product
    - ecosystem fit
  negative:
    - no deployment
  decision: VERIFY_FIRST
  why:
    - current endpoint is not verified
```

Semantics:

- `considered: false` means the route was excluded before recommendation because project fit failed;
- `rejected: true` means the route is in `DO_NOT_APPLY`;
- `positive` and `negative` are derived from structured facts and penalties, not LLM prose;
- `decision` is the engine's final route decision;
- `why` is the short human-readable explanation.

The trace is part of the machine report, so it remains available when an LLM later rewrites the result into an operator-facing answer.
