# Diagnostic lenses and prioritization

Apply only relevant lenses. For each material finding, attach a concrete situation,
source location, operator burden, consequence, proposed invariant, and acceptance
check. Do not infer defects merely because a favored technology is absent.

## Review lenses

| Lens | Inspect | Characteristic failure | Prefer the smallest sufficient remedy |
| --- | --- | --- | --- |
| Orientation and discovery | Entry point, capabilities, examples, current scope | Agent guesses command names or repeatedly scans the whole project | A maintained index, help surface, or capability description |
| Vocabulary and identity | Domain nouns, typed IDs, aliases, reference stability | One object has incompatible names; display labels act as IDs | Shared terms and canonical identities with explicit aliases |
| State and lifecycle | Owners, legal transitions, terminal states, freshness | Agent acts on stale state or treats accepted as completed | State/version visibility and explicit transition semantics |
| Action fit | Domain granularity, defaults, composability, dependencies | One task needs many ambiguous low-level steps | Reuse or add a domain-level operation without hiding its effects |
| Information shape | Schemas, bounded output, query/projection, errors | Prose parsing, truncated evidence, context floods | Stable structured core with optional detail and honest completeness |
| Outcome evidence | Receipts, postconditions, read-back, provenance | A success message substitutes for business verification | Inspectable evidence tied to the operation and affected resource |
| Recovery and interruption | Retry rules, reconciliation, checkpoints, cancellation | Timeout causes a duplicate side effect or total restart | Explicit unknown-outcome resolution and scoped durable progress |
| Multi-actor coordination | Ownership, versions, leases, contention, isolation | Parallel agents overwrite each other or share unsafe workspace state | Existing concurrency controls plus visible conflict semantics |
| Trust and authority | Identity, permissions, untrusted text, secrets, isolation | Retrieved text becomes an instruction or memory becomes authorization | Enforced capability boundaries and provenance-aware evidence handling |
| Accretion and invalidation | Reuse unit, retrieval scope, freshness, deletion | Wrong conclusions become permanent or irrelevant traces dominate | Small verified assets with dependencies and an invalidation path |
| Evolution and interoperability | Versions, compatibility, migration, adapter behavior | Updated docs break old consumers or drift from actual interfaces | Explicit version policy, staged migration, and conformance checks |
| Resource economy | Calls, latency, tokens, retries, attention, storage, maintenance | Local token savings increase failure or total system cost | Measure the complete task; remove repeated work at its source |

## Describe severity without false precision

Use these labels as contextual judgments, with a reason:

- **Blocker:** The central task cannot complete correctly or a non-negotiable safety,
  data integrity, or authority boundary cannot be maintained.
- **High:** A plausible ordinary or failure path produces a materially wrong result,
  unrecoverable ambiguity, repeated intervention, or major waste.
- **Medium:** A recurring, bounded burden or inconsistency materially hinders operation
  but has a reliable workaround.
- **Low:** A localized improvement with limited impact or unconfirmed prevalence.

Record evidence confidence separately from severity. An uncertain but severe hazard
may deserve targeted verification; uncertainty does not make its consequences small.
Do not invent probabilities, quantitative scores, savings, or incident frequency.

Distinguish a missing capability from an undocumented existing capability. Search
for existing implementations or conventions before proposing a new one. Separate
new defects from issues outside the authorized review boundary.

## Prioritize system effects

Apply hard constraints first. Next prioritize central task completion and safe
recovery. Then consider task frequency, downstream leverage, implementation risk,
migration cost, maintenance burden, and reversibility. Use qualitative comparisons
unless measured inputs justify numerical analysis.

An improvement with many consumers may have high leverage, but may also have a wide
compatibility blast radius. Prefer a small vertical slice that tests the central
contract before a broad migration. Defer a speculative platform with an explicit
reason rather than disguising it as required groundwork.

## Measure comparable work

Choose measures appropriate to the task, such as verified completions, manual
interventions, calls per completed task, evidence inspected, latency, input/output
volume, retries, recovery effort, duplicate effects, storage growth, and maintenance.
State task mix, sample size, model/tool environment, method, and uncertainty when
reporting numbers. Label expected benefits as hypotheses until measured.

Count the whole loop, including discovery, setup, verification, retries, and retained
assets. Avoid optimizing an intermediate proxy at the expense of the outcome. A
schema that reduces tokens but removes essential uncertainty is a regression.

## Anti-bloat test

Before adding a service, registry, memory tier, abstraction, or agent, ask:

1. Which observed problem or required invariant does it address?
2. Could deletion, renaming, a small contract change, an existing utility, or a local
   file solve the same problem?
3. What new concepts, failure modes, operational duties, or sources of truth appear?
4. How will an unfamiliar agent verify the benefit and discover its limits?
5. Is the simpler design sufficient for the real scope and expected scale?

Use the answers to accept, shrink, or reject the mechanism. Do not require a new
mechanism to make a review look productive. No change is better than negative value.
