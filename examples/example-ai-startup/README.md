# Example AI Startup

This is a fully synthetic, copyable end-to-end example. It shows how a seed-stage AI infrastructure project moves from structured facts to deterministic opportunity routing and independent route verification.

From the repository root, install dependencies and run the runner:

```bash
python3 -m pip install -r requirements.txt
python3 runtime/runner.py \
  examples/example-ai-startup/project.yaml \
  --output /tmp/example-report.yaml
```

The generated report should contain AI routes such as Microsoft for Startups, AWS Activate, NVIDIA Inception, OpenAI for Startups, and Y Combinator. Unverified or incomplete routes must not become `NOW` automatically.

Run the independent verifier against the same evidence pack:

```bash
python3 runtime/verify_route.py \
  examples/example-ai-startup/project.yaml \
  --all-ai \
  --evidence-dir examples/example-ai-startup/evidence \
  --output /tmp/example-route-verification.yaml
```

The evidence files are synthetic and use `example.invalid` or placeholder GitHub URLs. They are included to demonstrate the input contract, not to claim real customers, eligibility, or program access.

The checked-in [expected-report.yaml](expected-report.yaml) is the public regression artifact for this example.
