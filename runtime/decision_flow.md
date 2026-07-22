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
affiliation precedence gate
    ├── current / previous successful → DO_NOT_APPLY
    ├── previous rejected → APPLY_AGAIN_AFTER_CHANGE
    ├── affiliation outcome unknown → VERIFY_FIRST
    └── no known affiliation → continue
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

## Existing affiliation boundary

Project-program relationships are checked after fit but before an application recommendation. The relationship state takes precedence over a high fit score:

- `current` or `previous` with a successful outcome (`accepted`, `completed`, `graduated`, or `successful`) → `DO_NOT_APPLY`;
- `rejected` → `APPLY_AGAIN_AFTER_CHANGE` so a changed product, evidence base, or application can be reviewed explicitly;
- a recorded relationship without a known outcome → `VERIFY_FIRST`;
- no recorded relationship → continue with normal route scoring.

The engine does not infer affiliation from a brand mention. A relationship must be supplied as structured project data with a source and verification date when publicly known.
