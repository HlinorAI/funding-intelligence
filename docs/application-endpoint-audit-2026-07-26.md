# Application endpoint coverage audit

**Review date:** 2026-07-26  
**Scope:** all 41 tracked program cards  
**Method:** read card metadata first, then manually inspect selected official sources. This audit does not change program status, eligibility, or application-endpoint metadata.

## Result

| Endpoint state | Cards | Meaning |
| --- | ---: | --- |
| `confirmed` | 4 | A card records a separately verified public application or access URL. |
| `gated` | 1 | A card records a verified access path, but the requested benefit still needs a referral, partner path, or other gate. |
| `missing` | 36 | The card has an official program source but no separately verified action URL. The source is not promoted to an application endpoint. |

The five cards with a recorded application endpoint are `aws-activate`, `microsoft-for-startups`, `nvidia-inception`, `openai-for-startups`, and `y-combinator`.

## Important boundary

`status.official_source` establishes where program information was reviewed. It does not establish that a founder can submit an application at that URL.

Some cards deliberately group multiple mechanisms or pathways. A single card-level application URL would be misleading when each route has a different intake surface. Such cards remain `missing` until the knowledge model is split into route-level cards or can record endpoint data by mechanism.

## Priority review findings

| Card | Official evidence reviewed | Endpoint conclusion | Required follow-up |
| --- | --- | --- | --- |
| `base-funding-ladder` | [Base Get Funded](https://docs.base.org/get-started/get-funded) lists separate Builder Rewards, Builder Grants, OP Retro Funding through Atlas, and Base Batches pathways. | Do not set one endpoint for the combined card. The official page links to multiple distinct action surfaces. | Split the card by pathway or add per-mechanism endpoint data before promoting any route. |
| `optimism-superchain` | [Optimism Grants](https://gov.optimism.io/c/grants/87) lists cycle- and mission-specific grant opportunities. | No stable card-level endpoint confirmed. | Review the active mission or Retro Funding round when a project matches; record its own current application URL. |
| `ethereum-esp` | [ESP Applicants](https://esp.ethereum.foundation/applicants) instructs applicants to select an active Wishlist or RFP item and submit against that item. | No universal grant submission URL confirmed. | Treat the applicants page as a route-selection surface, not a universal application form; verify a selected item before recommendation. |
| `stellar-scf` | [Stellar Community Fund](https://communityfund.stellar.org/) presents multiple award tracks and verification/community steps. | A generic card-level submission URL was not established by this review. | Verify the active round and required account or verification flow before recording an endpoint. |
| `web3-foundation-polkadot` | The recorded Grants documentation route currently redirects to [Web3 Foundation](https://web3.foundation/). | The former documentation source needs human review; no endpoint can be confirmed. | Find the current official grants intake or mark the card status for review. |
| `arbitrum-dao-grants` | The recorded [Arbitrum Foundation forum](https://forum.arbitrum.foundation/) is informational and program calls are mission-specific. | No stable application endpoint confirmed. | Verify a current named grant, RFP, or mission before an application recommendation. |
| `solana-foundation` | The card is a funding umbrella rather than one verified intake. | No card-level endpoint confirmed in this pass. | Review the specific grant, accelerator, or ecosystem route selected by project fit. |
| `polygon-funding-bd` | The card combines funding and strategic BD. | No single application endpoint can represent both mechanisms. | Split funding and BD into separate cards before recording an endpoint. |
| `celo-funding-ladder` | The card groups funding and MiniPay distribution pathways. | No single endpoint can represent the combined route. | Split the route by mechanism or verify a current mechanism-specific intake. |
| `sui-programs` | The card combines multiple program types. | No single endpoint confirmed. | Verify the specific current program before updating endpoint metadata. |

## Remaining source-only cards

The following cards remain intentionally source-only after this audit. Their `missing` state is an explicit safety boundary, not a claim that the underlying programs are closed.

```text
aleo-developer-grants
algorand-xgov
aptos-ecosystem
arbitrum-dao-grants
avalanche-retro9000
base-funding-ladder
bnb-chain
canton-development-fund
celestia-delegation
celo-funding-ladder
circle-arc
codex-forward-deployed
solana-colosseum
interchain-builders
ethereum-esp
fuse-ember-business
hedera-tha
miden-pioneer
mina-current-route
minipay-distribution
near-funding-ladder
oasis-sapphire
optimism-superchain
web3-foundation-polkadot
polygon-funding-bd
scroll-security-subsidy
solana-foundation
stablechain-bd
stellar-scf
sui-programs
superchain-strategic-bd
tempo-bd
tezos-foundation
uniswap-hook-ladder
usual-usd0
xrpl-routes
```

## Decision

Do not bulk-fill endpoint fields from official sources. Prioritize a route-level review only when a benchmark or external project selects the card. The next safe knowledge change is to split a multi-path card where a real case needs one of its mechanisms.
