# Funding Intelligence

[Русский](README.ru.md)

An evidence-gated, deterministic engine for routing startups and technical projects to funding, accelerator, cloud-credit, investment, incentive, and business-development opportunities.

## Why this exists

Generic LLM workflows tend to produce long lists of plausible-looking programs. Funding Intelligence is designed to make fewer, more defensible decisions:

- irrelevant routes are rejected before recommendation;
- `unknown` is not treated as evidence;
- a transport failure is not treated as `CLOSED`;
- a failed hard gate cannot become `NOW` through prose or a high raw score;
- every recommendation includes a reason, next action, and stop condition.

The project is an internal capability and open-source engine prototype, not a funding marketplace or an application service.

## What it does

- classifies project stage, sector, goals, and mechanism fit;
- matches projects to local opportunity cards and vertical packs;
- calculates a deterministic score and penalties;
- gates recommendations on structured evidence;
- keeps program status, endpoint status, endpoint transport, project fit, and project readiness independent;
- emits route-specific decisions;
- preserves an explainable `decision_trace` in the machine report.

## What it does not do

- guarantee funding, acceptance, or investment;
- submit applications automatically;
- treat credits, incentives, accelerator access, or BD value as cash grants;
- invent missing facts or convert claims into evidence;
- treat a dated snapshot as permanent truth;
- replace legal, financial, compliance, or investment advice.

## Resource types

- `proposal_grant` — review-based funding against scope, milestones, and reporting;
- `retro` — ship first, then seek a reward for demonstrated impact;
- `incentive` — rewards tied to activity, liquidity, or network outcomes;
- `accelerator` / `investment` — selection, capital, mentorship, or investor access;
- `bd` — strategic partnerships, pilots, integrations, and distribution;
- `cloud_credits` / `startup_support` — infrastructure credits, technical support, or founder resources.

## Decision examples

- `COMPLETE_ELIGIBILITY_DATA` — the route may be relevant, but required company or account facts are missing;
- `VERIFY_ACCESS_PATH` — the opportunity exists as a category, but the actual path into the benefit is not established;
- `BUILD_FIRST` — product, traction, or application proof must be built before applying;
- `BUILD_NVIDIA_USE_CASE` — the project lacks a credible native NVIDIA/GPU use case;
- `DO_NOT_APPLY` — the mechanism, stage, ecosystem, or project fit is wrong;
- `NO_ACTIONABLE_ENDPOINT` — no usable intake endpoint is known.

## Repository structure

```text
agent/       operator policy for the Funding Intelligence Agent
knowledge/   program cards, vertical packs, rules, and templates
runtime/     deterministic runner, route verifier, and schema validator
schemas/     formal project, program-card, route, and report schemas
tests/       public synthetic cases and expected decisions
examples/    public sample report artifacts
history/     documentation for human-maintained application history
```

Private evidence, live project fixtures, operational history, and generated reports are excluded by `.gitignore`.

## Installation

Python 3 with PyYAML is required:

```bash
python3 -m pip install -r requirements.txt
```

No web service or database is required for the local runner.

## Usage

Run the deterministic evaluator on a public synthetic AI fixture:

```bash
python3 runtime/runner.py tests/cases/ai_startup.yaml --output /tmp/example-ai-report.yaml
```

Run route verification on a public synthetic Web3 fixture. This deliberately uses a card without a verified source snapshot, so it demonstrates the `VERIFY_FIRST` path:

```bash
python3 runtime/verify_route.py \
  tests/cases/web3.yaml \
  --route base-funding-ladder \
  --output /tmp/base-route-verification.yaml
```

Add `--live` only when you explicitly want an HTTP transport probe. A failed probe does not automatically mean that a program is closed.

## Example output

The public fixture `tests/cases/ai_startup.yaml` represents an `Example AI Infrastructure Startup`. Its current expected contract is:

```yaml
project: Example AI Infrastructure Startup
decision: VERIFY_FIRST
gate_passed: false
must_include: microsoft-for-startups
```

The compact sample artifact is available at [examples/sample_report.yaml](examples/sample_report.yaml).

## Knowledge coverage

The repository currently contains:

- an AI opportunity pack covering startup programs, cloud/API credits, technical support, enterprise access, and accelerator/investment routes;
- Web3 and ecosystem cards for selected chains, infrastructure, incentives, retro routes, and BD paths;
- shared mechanism, scoring, rejection, status-verification, and stop-condition rules.

This is a deliberately bounded knowledge snapshot. It is not a comprehensive global database, and a route outside the cards is not evidence that the project has no other options.

## Status verification model

Route verification keeps these states separate:

- `program_status` — the status recorded for the program, with source and verification date;
- `endpoint_status` — whether an actionable endpoint is known;
- endpoint transport — whether the runtime could reach that URL in a live probe;
- `project_fit` — how the structured project facts match the route;
- `project_readiness` — whether the evidence and eligibility gates are complete;
- final `decision` — the route-specific action produced by the policy.

If an official source was checked but a later HTTP probe cannot reach it, the verifier preserves the source-backed status and records transport as `UNREACHABLE`. It does not silently convert a network problem into `CLOSED`.

## Tests

Run the public regression suite:

```bash
python3 runtime/runner.py --check-all
python3 -m py_compile runtime/runner.py runtime/verify_route.py
```

Run the full public contract validator locally:

```bash
python3 runtime/validate_schemas.py
```

The validator checks every public YAML file, project fixtures, program-card structure, generated runner reports, a public route-verification record, issue forms, private-path exclusions, and credential-like patterns. GitHub Actions runs the same checks on every push and pull request.

Validate all public YAML files:

```bash
python3 - <<'PY'
from pathlib import Path
import yaml

files = sorted(Path(".").rglob("*.yaml"))
for path in files:
    if any(part in {".git", ".venv"} for part in path.parts):
        continue
    with path.open("r", encoding="utf-8") as f:
        yaml.safe_load(f)
print(f"yaml_ok {len(files)}")
PY
```

## Contributing

When adding a program card:

1. identify the mechanism and resource type;
2. link an official source and record a snapshot date;
3. document fit, bad fit, required evidence, next action, and stop condition;
4. do not rely on an aggregator as the only verification source;
5. add or update a public synthetic fixture and expected decision;
6. run the regression and YAML checks.

Do not add real project evidence, credentials, contacts, internal metrics, or generated private reports.

See [CONTRIBUTING.md](CONTRIBUTING.md), [CHANGELOG.md](CHANGELOG.md), and [WORKBOARD.md](WORKBOARD.md) for contribution and project-state guidance.

## Limitations

- program cards are snapshots and require re-verification before a real application;
- scoring is deterministic but only as good as the structured facts and card quality;
- the current knowledge coverage is selective;
- human review is still required for claims, eligibility, and execution decisions;
- licensed under the [Apache License 2.0](LICENSE).

## Official source examples

The AI pack currently points to official pages such as [AWS Activate](https://aws.amazon.com/startups/credits/), [Microsoft for Startups](https://learn.microsoft.com/en-us/startups/microsoft-for-startups/overview), [NVIDIA Inception](https://www.nvidia.com/en-us/startups/), [OpenAI for Startups](https://openai.com/business/why-openai/startups/), and [Y Combinator Apply](https://www.ycombinator.com/apply). These links document source locations; they do not guarantee eligibility or acceptance.
