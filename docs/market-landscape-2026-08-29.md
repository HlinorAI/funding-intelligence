# Funding-intelligence market check

**Review date:** 2026-08-29  
**Scope:** public funding discovery, matching, application support, and
programme-operator tooling relevant to Funding Intelligence.

This is a positioning check, not a total-addressable-market estimate. Product
claims below are taken from the vendors' current public pages and should be
rechecked before external use.

## Verified market signals

| Segment | Public signal | Implication for this repository |
| --- | --- | --- |
| Broad startup discovery | [F6S](https://www.f6s.com/) advertises 15k accelerators/grants/funding opportunities and 6.5m members. [Gust](https://gust.com/) advertises 300+ accelerator matches and 750+ angel investment groups. | A generic founder-facing directory or ranked list is a crowded wedge. |
| Grant search and matching | [OpenGrants](https://opengrants.io/product/) advertises 78k+ open grants/contracts, daily refresh, four funding sources, an API, and an MCP server. [Instrumentl](https://www.instrumentl.com/product-overview) advertises 36k+ active RFPs, 450k+ funder profiles, matching, application support, and post-award management. | Database size, AI matching, and reminders are not sufficient differentiation. |
| Managed application support | [Grantify](https://www.grantify.io/) combines ranked matches, eligibility checks, guided applications, and human funding experts for UK SMEs. | Do not compete on generic grant-writing or a promise of faster applications. |
| B2B/operator tooling | [Fundica](https://www.fundica.com/en-us/) sells funding search infrastructure to financial institutions, accounting firms, governments, and accelerators. [Gust for Accelerators](https://gust.com/accelerators) focuses on application intake, screening, evaluation, and feedback. | The strongest adjacent buyer hypothesis is programme operators or advisors who need defensible triage, not another founder directory. |
| Source and eligibility complexity | [Grants.gov](https://www.grants.gov/applicants/applicant-eligibility.html) says legal eligibility is defined in each opportunity's attached application instructions. The [EU Funding & Tenders Portal](https://ec.europa.eu/info/funding-tenders/opportunities/portal/) aggregates many programmes and calls. | Route-specific eligibility, source provenance, and a verified intake path remain real problems even when discovery is easy. |

## Repository reality

- Local `main` is at `4cd5eb4`, the same commit as `origin/main`; the working
  tree also contains an uncommitted knowledge/runtime expansion.
- The local validation gate passes: 45 tests, 7 public decision-quality
  benchmarks, schema/privacy checks, workflow validation, and compilation.
- The current local snapshot contains 49 cards, but only five have a recorded
  application/access endpoint; the remaining cards are intentionally
  source-only. This is a safety property, not market coverage.
- The public repository currently shows 3 stars, 0 forks, and 0 open issues on
  [GitHub](https://github.com/HlinorAI/funding-intelligence). There is no
  public evidence yet of a consented pilot, repeat usage, or funding outcome.

## Decision

1. Keep the deterministic local engine and its fail-closed boundaries.
2. Stop treating card count or a larger discovery catalogue as the next
   product milestone.
3. Position the next pilot around an operator/advisor workflow: applicant
   intake, evidence normalization, route-specific eligibility, verified
   endpoint, and an explainable next action.
4. Keep founder/project discovery as research input only until a consented
   pilot proves that it creates value; do not use it as an outbound-growth
   claim.
5. Treat source freshness and endpoint verification as product outputs, not
   internal implementation details.

## Next evidence gate

The next meaningful signal is one consented operator or advisor pilot with a
before/after comparison of manual triage time, false positives, false
negatives, and unsupported facts. Until that exists, the project remains a
validated prototype rather than a market-proven funding platform.

## 2026-09-11 delta check

A two-week follow-up review confirmed the positioning decision and found no
reason to widen the wedge.

**Competitive signals.**

- [Optimy](https://www.optimy.com/blog-optimy/grant-application-screening) now
  publishes a 2026 guide selling automated grant-application screening to
  funders: eligibility rules, pre-qualification, weighted scoring, and
  AI-assisted review workflows. Funder-side triage is no longer an empty niche.
- [Granted AI](https://grantedai.com/) combines AI grant discovery across
  133K+ foundations with proposal drafting;
  [GrantWatch](https://www.prnewswire.com/news-releases/grantwatchs-2026-ai-tools-redefine-grant-discovery-and-writing-302742442.html)
  shipped 2026 AI discovery and writing tools; [MZN
  International](https://ai.mzninternational.com/grant-opportunities) runs an
  AI grant-opportunity scanner for NGOs.
- None of the reviewed vendors advertises evidence gating, a source-freshness
  policy, or route-specific application-endpoint verification. The
  differentiator holds, but the window for a consented pilot is narrowing.

**Program facts refreshed in the knowledge base the same day.**

- EIC Accelerator 2026: EUR 634M budget, continuous short-proposal submission,
  six full-proposal cut-offs (next: 2026-11-04).
- Y Combinator: Winter 2027 intake with a 2026-11-02 on-time deadline.
- Base Batches 004: applications closed 2026-09-10.
- NSF Tech Accelerators: initiative live, no open solicitation window yet.

**Conclusion.** Keep the operator/advisor evidence-pre-screen wedge. Competitor
momentum in AI screening increases the cost of waiting for pilot evidence;
distribution review (not engine features) remains the constraint.
