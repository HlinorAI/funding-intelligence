# Funding route scoring

## Hard gates

1. `CLOSED` cannot reach `NOW` or receive an `APPLY` recommendation.
2. `VERIFY` and `WATCH` require an official-source and actual-intake-endpoint check.
3. The mechanism must match the ask: retro does not fund an idea before shipping, incentive is not runway, and investment is not a grant.
4. A chain/ecosystem route requires concrete native value: deployment, architecture, users, integrations, or a public-good artifact.
5. If required evidence is missing, the recommendation is `BUILD_FIRST`, not a speculative application.
6. If a project does not specify a target/native ecosystem, a chain-specific card receives `DO_NOT_APPLY`, not “weak fit.”

## Base score — 100

- `strategic_fit`: 25
- `technical_fit`: 20
- `evidence`: 20
- `mechanism_fit`: 15
- `execution_readiness`: 10
- `access`: 10

## Penalties

- `-25`: a closed program is presented as an application route;
- `-20`: generic multichain port without a native thesis;
- `-15`: pre-funding ask in a retro/incentive route;
- `-15`: no shipped product where it is required;
- `-10`: budget is only payroll without an ecosystem outcome;
- `-10`: no measurable milestones;
- `-10`: users/TVL are promised without a distribution plan.

## Interpretation

- `80–100`: `NOW`;
- `65–79`: `NOW` or `NEXT` after closing gaps;
- `50–64`: `LATER` / relationship building;
- `<50`: `DO_NOT_APPLY`.

The anti-hallucination gate can still block any score band.

## Output contract

For every selected route, the agent states:

- fit and score;
- exact mechanism and status;
- why it fits;
- missing proof;
- next step;
- stop condition.
