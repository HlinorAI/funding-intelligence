# Decision Quality Benchmarks

This directory contains public, reproducible benchmark cases for Funding Intelligence.

The benchmark is intentionally separate from the synthetic regression suite in `tests/cases/`. A benchmark case must record:

- the public sources used;
- the project facts extracted from those sources;
- the expected classification;
- expected runner decisions;
- expected route-verifier decisions;
- decisions that would be considered wrong for the case.

Run the completed benchmark cases from the repository root:

```bash
python3 runtime/run_benchmarks.py
```

Current status: seven completed public-only cases (`orvixo-001`, `hardware-public-product-001`, `web3-grant-recipient-001`, `web3-infrastructure-001`, `ai-open-source-001`, `ai-enterprise-001`, and `deeptech-university-001`). Three planned target cases remain in [`plan.yaml`](plan.yaml) and are not represented as facts until their public sources are reviewed.

Public benchmark results are decision-quality evidence, not evidence of funding acceptance, revenue, traction, or founder satisfaction. Unknown facts remain `unknown`.
