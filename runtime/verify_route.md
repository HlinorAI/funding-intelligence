# Route verification

Offline verification using a public synthetic fixture:

```bash
python3 runtime/verify_route.py \
  tests/cases/web3.yaml \
  --route base-funding-ladder \
  --output /tmp/base-route-verification.yaml
```

Live endpoint checks:

```bash
python3 runtime/verify_route.py \
  tests/cases/web3.yaml \
  --route base-funding-ladder \
  --live \
  --output /tmp/base-route-verification-live.yaml
```

The command does not mutate knowledge cards. It emits one route record with independent states:

- `program_status`: `OPEN`, `ACTIVE`, `CLOSED`, or `UNKNOWN`, with source and verification date;
- `endpoint_status`: `AVAILABLE`, `MISSING`, `UNREACHABLE`, or `UNKNOWN`;
- endpoint transport: `NOT_RUN`, `PASS`, or `UNREACHABLE` for a live probe;
- `project_fit`: `STRONG`, `POSSIBLE`, `WEAK`, or `NONE`;
- `project_readiness`: `READY`, `BUILD_FIRST`, `INCOMPLETE`, `UNKNOWN`, or `INELIGIBLE`.

Program affiliation is a separate precedence gate. A current or previously successful relationship produces `INELIGIBLE` and `DO_NOT_APPLY`; a previous rejection produces `REAPPLY_AFTER_CHANGE` and `APPLY_AGAIN_AFTER_CHANGE`; an unverified relationship produces `UNKNOWN` and `VERIFY_FIRST`.

It also emits:

- snapshot status and actual endpoint;
- endpoint check result;
- eligibility state and missing proof;
- resource type;
- project fit and score;
- next action and stop condition;
- verification timestamp;
- `NOW`, `BUILD_FIRST`, `VERIFY_FIRST`, `APPLY_AGAIN_AFTER_CHANGE`, or `DO_NOT_APPLY`.

If the runtime cannot reach an endpoint but the official source was already checked, the result keeps `program_status: ACTIVE` and `endpoint_status: AVAILABLE`, while recording `transport: UNREACHABLE`. A failed HTTP check is never treated as evidence that a program is closed.
