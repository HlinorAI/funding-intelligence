# Decision flow

```text
project.yaml
    ↓
normalize facts (unknown stays unknown)
    ↓
classify stage / sector / goals / mechanism fit
    ↓
load knowledge/programs/*.yaml + matching knowledge/packs/<vertical>/programs/*.yaml
    ↓
calculate score and penalties
    ↓
anti-hallucination gate
    ├── failed status/endpoint → VERIFY_FIRST
    ├── missing proof/readiness → BUILD_FIRST
    ├── closed/hold route → DO_NOT_APPLY
    └── all passed → NOW / NEXT / LATER
    ↓
shortlist max 7 + DO_NOT_APPLY reasons
    ↓
report YAML/JSON
```

The first version is local-only. Web verification is a later adapter; the current runner refuses to treat a snapshot card as verified.
