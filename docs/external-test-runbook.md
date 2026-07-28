# External Test Runbook

Use this runbook for one consented external project at a time. The purpose is to evaluate decision usefulness, not to demonstrate feature breadth.

## Privacy boundary

Create the case only under:

```text
tests/external-local/<case-id>/
```

This directory is ignored by Git. Do not commit:

- private decks or customer lists;
- credentials, tokens, or account identifiers;
- non-public revenue, usage, or application history;
- generated project, evidence, route, or report files;
- identifiable feedback without explicit publication consent.

## Case contents

```text
tests/external-local/<case-id>/
├── intake.json
├── project.yaml
├── evidence/
├── runner.yaml
├── routes.yaml
├── opportunity-report.md
└── feedback.md
```

Use `docs/external-test-intake.md` to collect the minimum factual input. Record unsupported fields as `unknown`.

## Canonical workflow

```bash
python3 runtime/ingest.py \
  tests/external-local/<case-id>/intake.json \
  --type json \
  --output tests/external-local/<case-id>/project.yaml

python3 runtime/runner.py \
  tests/external-local/<case-id>/project.yaml \
  --output tests/external-local/<case-id>/runner.yaml

python3 runtime/verify_route.py \
  tests/external-local/<case-id>/project.yaml \
  --all-ai \
  --evidence-dir tests/external-local/<case-id>/evidence \
  --output tests/external-local/<case-id>/routes.yaml

python3 runtime/render_report.py \
  tests/external-local/<case-id>/runner.yaml \
  tests/external-local/<case-id>/routes.yaml \
  --output tests/external-local/<case-id>/opportunity-report.md
```

Select explicit `--route` values instead of `--all-ai` when the project is not in the AI pack.

## Review before delivery

Confirm that:

1. project classification matches the supplied facts;
2. every recommended route has a source, next action, and stop condition;
3. no unknown fact is presented as evidence;
4. current or previous program affiliations are handled before fit;
5. resource types are not presented as equivalent forms of cash;
6. transport failures are not interpreted as program closure;
7. private facts do not appear in a public path.

Do not change scoring or expected behavior while reviewing the case. Record a suspected defect first and reproduce it with a public-safe fixture.

## Feedback and success criteria

Use `docs/external-test-feedback.md`. The first test is useful only if:

- at least one route is new or confirms a defensible direction;
- at least one unsuitable route is rejected with a useful reason;
- the owner understands the next action;
- the report saves at least two hours of manual research;
- factual corrections are recorded separately from decision-quality feedback.

One case does not justify market, acceptance-rate, or funding-outcome claims. It only identifies the next evidence-backed product decision.
