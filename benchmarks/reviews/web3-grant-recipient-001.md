# Benchmark Review: rotki

## Scope

This is a public-only Web3 benchmark. It uses the official [Optimism Retro Funding record](https://gov.optimism.io/t/rpgf3-deep-dive/7577), the [rotki Optimism integration page](https://rotki.com/integrations/optimism), and the public [rotki repository](https://github.com/rotki/rotki). It is not founder feedback and does not establish current funding needs or funding outcomes beyond the recorded prior award.

## Confirmed public facts

- rotki is a public open-source product with an Optimism integration.
- The official Optimism Retro Funding record lists rotki as a RetroPGF 3 recipient.
- The product supports Optimism balances, transaction decoding, and DeFi activity tracking.

## Facts retained as unknown

- Funding stage, legal entity details, revenue, users, pilots, partnerships, and current funding need.
- Current deployment, usage, and impact metrics for the Optimism integration.
- Whether a future Optimism funding route permits a new application for a materially different scope.

## Expected decision boundaries

| Route | Expected boundary | Review rationale |
| --- | --- | --- |
| Optimism / Superchain Funding | `DO_NOT_APPLY` | The recorded previous successful affiliation overrides ecosystem fit and prevents a duplicate recommendation. |

## Quality signal under test

The engine must not convert a real Optimism integration and a previous Retro Funding award into a fresh application recommendation. Affiliation precedence must be visible in the decision trace rather than hidden behind the card's closed status.
