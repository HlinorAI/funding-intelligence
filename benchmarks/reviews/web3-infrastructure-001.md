# Benchmark Review: Blockscout

## Scope

This is a public-only Web3 infrastructure benchmark. It uses the public [Base Mainnet explorer](https://base.blockscout.com/), the [Blockscout repository](https://github.com/blockscout/blockscout), and the official [Optimism Retro Funding record](https://gov.optimism.io/t/rpgf3-deep-dive/7577). It is not founder feedback and does not establish a current Base funding need or a current affiliation with Base.

## Confirmed public facts

- Blockscout has a public Base Mainnet explorer.
- Blockscout is an open-source EVM blockchain explorer project.
- The official Optimism Retro Funding record lists Blockscout as a previous recipient.

## Facts retained as unknown

- Funding stage, legal entity details, revenue, users, pilots, partnerships, and current funding need.
- Base-specific usage, transaction, repeat-use, and impact metrics.
- Whether Blockscout has any past or current Base-specific funding relationship. No such relationship is asserted by this case.

## Expected decision boundaries

| Route | Expected boundary | Review rationale |
| --- | --- | --- |
| Base Funding Ladder | `VERIFY_FIRST` | Native Base fit and public deployment are present, but the local card needs fresh status verification and the public sources do not establish route-specific impact evidence. |
| Optimism / Superchain Funding | `DO_NOT_APPLY` | The recorded previous successful Optimism affiliation blocks a duplicate recommendation for that program only. |

## Quality signal under test

The engine must keep program affiliations scoped to the matching program. A past Optimism funding relationship must not suppress the Base route, while a genuine Base deployment must not become an immediate application recommendation without status and impact proof.
