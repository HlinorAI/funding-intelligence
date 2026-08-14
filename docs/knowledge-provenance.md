# Knowledge-card provenance

Program cards are operational snapshots, not permanent truth. A card may carry
an optional `provenance` block with:

- `source_snapshot_hash` — SHA-256 of the reviewed source snapshot;
- `semantic_reviewed_at` and `reviewer` — who reviewed the meaning and when (ISO 8601 UTC timestamp);
- `change_type` — what changed (`status`, `endpoint`, `eligibility`, or policy);
- `deadline` and `eligibility_version` — time-bounded eligibility context;
- `confidence` and optional `diff_review` — review confidence and source-diff state.

The schema validates this block when present. Existing cards remain compatible
as legacy snapshots until their provenance is backfilled from an actual source
snapshot; no reviewer, hash, or confidence value is invented during migration.

The runner's `policy_score` is also intentionally separate from empirical
quality. Reports currently emit `quality.status: not_calibrated` until
owner-reviewed outcomes provide a defensible calibration sample.
