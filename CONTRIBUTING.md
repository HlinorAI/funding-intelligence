# Contributing to Funding Intelligence

Thank you for helping improve Funding Intelligence. Contributions should make routing decisions more evidence-gated, explainable, and useful in execution.

## Before opening a change

1. Read [README.md](README.md) and the relevant files in `agent/`, `knowledge/`, and `runtime/`.
2. Keep the repository public-safe: do not add real project evidence, credentials, contact details, internal metrics, application records, or generated private reports.
3. Preserve the existing YAML schema, route IDs, enum values, CLI commands, and machine-readable contracts unless the change explicitly updates the contract and its tests.

## Local setup

```bash
python3 -m pip install -r requirements.txt
```

Run the public checks before submitting a change:

```bash
python3 runtime/runner.py --check-all
python3 -m py_compile runtime/runner.py runtime/verify_route.py
```

Validate public YAML files with the command in [README.md](README.md).

## Program cards and knowledge changes

Every new or materially changed program card should include:

- the exact mechanism and resource type;
- an official source and snapshot date;
- best fit and bad fit;
- required evidence;
- next action and stop condition;
- a public synthetic fixture or expected-decision update when behavior changes.

Do not use an aggregator as the only verification source. Do not present cloud credits, investment, incentives, accelerator access, or BD value as cash grants.

## Code and decision behavior

The runner and verifier are intentionally deterministic. If code changes affect scores, gates, decisions, output fields, or transport semantics:

- explain the contract change in the pull request;
- update the relevant tests and schemas;
- add an entry to `CHANGELOG.md`;
- update `WORKBOARD.md` if the project state or next action changes.

Keep unknown facts as `unknown`/`UNKNOWN`; never fill a gap from assumption or prose.

## Documentation and operational memory

Documentation changes should keep English as the primary public language. Update `README.ru.md` when the public README contract changes materially.

Maintain both operational files:

- `CHANGELOG.md` records public behavior and release history;
- `WORKBOARD.md` records completed work, current work, decisions, deferred items, and next actions.

Every release-related change must update both files before the release commit.

## Pull requests

Use a focused title and describe:

- what changed;
- why it changed;
- which public behavior or documentation contract is affected;
- tests and scans run;
- any known limitation or follow-up.

Do not include secrets, local absolute paths, private fixtures, or unrelated generated files.

## License

By contributing to this repository, you agree that your contribution is provided under the [Apache License 2.0](LICENSE), unless a separate written agreement states otherwise.
