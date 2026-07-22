# Analyze a project

Use the deterministic runner first:

```bash
python3 runtime/runner.py tests/cases/ai_startup.yaml
```

For a real project:

```bash
python3 runtime/runner.py project.yaml --output report.yaml
```

Then use `agent/FUNDING_ANALYST.md` to turn the machine report into a concise operator report. The LLM may explain a score, but may not override a failed gate or invent missing evidence.

Required sequence:

1. Extract facts and preserve `UNKNOWN`.
2. Classify stage, sector, goals and likely mechanism.
3. Run score and penalties.
4. Run the anti-hallucination gate.
5. Shortlist at most seven routes.
6. Write NOW/NEXT/LATER/DO NOT APPLY.
7. Add 7/30/90-day execution plan and missing proof.
