# Operator pilot protocol

**Status:** ready for one consented, review-only pilot
**Owner:** project owner and participating operator/advisor
**Scope:** redacted applicant or project cases; no application submission,
award decision, CRM write, or outbound message

## Objective

Test whether Funding Intelligence makes an operator's first-pass review more
defensible and faster. The system assists with evidence collection and route
triage; the participating operator remains the decision maker.

## Required setup

1. Obtain explicit consent for the review-only pilot.
2. Agree which fields and documents may be used.
3. Redact names, personal contact details, credentials, confidential financial
   data, and any material not needed for the review.
4. Select 10–20 cases, or a smaller set if that is the operator's normal
   review unit.
5. Record the operator's expected route, hold/reject reason, and missing
   evidence before showing the generated report.
6. Freeze the engine version, card snapshot, source dates, and decision rules
   for the run.

## Workflow

1. Store intake, evidence, generated project files, reports, and feedback only
   in an ignored local directory with restrictive permissions.
2. Run the canonical path: intake → project contract → runner → route verifier
   → Markdown report.
3. For each case, capture hard gates, source links, source freshness, endpoint
   state, missing evidence, decision, and next action.
4. Let the operator review the report without an implementation explanation.
5. Record corrections and disagreement categories separately from usefulness
   opinions.
6. Delete private case material after the agreed retention period.

## Metrics

Record before the first case how each measure will be timed or labelled:

- operator minutes per case before and with the report;
- useful routes and missed routes;
- false positives and false negatives;
- unsupported or incorrectly promoted facts;
- manual intake corrections;
- cases blocked by missing or stale endpoints;
- clarity of the next action;
- willingness to repeat the workflow.

## Pass conditions

- No unsupported fact is promoted as evidence.
- At least one useful route or justified rejection is identified per agreed
  success definition.
- The operator can explain the next action without an operator-side defence of
  the engine.
- Corrections, false positives, and false negatives are recorded.
- Any time saving is measured against the agreed manual baseline.

These conditions are evidence gates for the next product decision, not a claim
that the pilot predicts funding outcomes.

## Stop conditions

Stop the pilot if the participant requests applicant PII, live CRM access,
automatic submission, an award decision, or external sending. Stop and record
the run as inconclusive if source or consent status cannot be verified.
