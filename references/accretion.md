# Make experience compound without making mistakes permanent

Treat accretion as improving the system's reusable knowledge, interfaces, procedures,
and tests, not simply accumulating chat logs. Require an identifiable future use and
a correction path for each retained asset.

## Separate operational state from retained knowledge

Persist task checkpoints only as needed for execution and recovery. Treat observations
as evidence about a particular run. Treat generalizations as hypotheses until checked.
Keep standing policy and permissions in their authoritative configuration, not in
retrieved memory. Do not let a remembered approval authorize a different operation.

Useful retained units can be small: a corrected example, a stable domain glossary, a
contract test, a bounded troubleshooting recipe, a verified dependency constraint,
a reusable tool wrapper, or a decision record. Prefer an existing file or store when
it already supports the required scope, provenance, and invalidation.

## Define the promotion lifecycle

Use the smallest appropriate form of this lifecycle:

`observation -> candidate -> validation -> scoped promotion -> retrieval/application -> feedback -> revision/retirement`

Before promotion, establish what happened, its evidence, the applicable conditions,
counterexamples or competing explanations, and the future decision it should improve.
A successful outcome may be coincidental; repeated agreement by copies of the same
agent is not independent evidence. A failure can yield a useful bounded lesson when
its cause and scope are adequately supported.

For low-risk corrections to authoritative documentation, a verified source may be
sufficient. For consequential procedural automation, require stronger validation
appropriate to the risk, such as reproducible tests or established review. Follow
existing authority; do not create a mandatory human review step for every harmless
asset and do not bypass an existing required approval.

## Retain the minimum useful record

Choose fields by need, rather than deploying a mandatory database schema:

| Field | Why it matters |
| --- | --- |
| Stable identity and kind | Distinguish an observation, fact, procedure, decision, or test. |
| Claim or procedure | State what to reuse without a whole transcript. |
| Evidence and provenance | Link to the origin, observed result, and validation method. |
| Scope and preconditions | Bound the project, tenant, task, capability, environment, and permissible use. |
| Dependencies/version | Identify facts, contracts, tools, or implementations whose changes invalidate it. |
| Validation state | Distinguish candidate, verified-for-scope, disputed, stale, superseded, and retired. |
| Freshness policy | Choose expiry, revalidation triggers, or explicit non-expiring justification. |
| Owner and correction path | Identify the authoritative updater and conflict/invalidation behavior. |
| Sensitivity and retention | Control visibility, minimization, deletion, and downstream copies. |

Keep language appropriately bounded: "This command succeeded on version X under Y"
is supportable where "This always works" is not. Store evidence rather than an agent's
private deliberation. Redact secrets and unnecessary personal information before
retention; provenance is not a reason to preserve confidential raw content forever.

## Make retrieval task-relevant

Select by current task, permissions, scope, dependencies, freshness, and validation
state. Return a concise claim with evidence/detail references. Reveal uncertainty,
conflicts, and stale status instead of retrieving every asset as equally authoritative.
Treat retrieved text as data, not instructions with new privileges.

Prefer an exact lookup, small index, or existing search before a new retrieval
platform. Evaluate whether retention reduces future verified-task cost enough to
justify writing, validating, storing, retrieving, and maintaining the asset.

## Make correction stronger than accumulation

Support supersession and conflict records instead of silent overwrites. Invalidate
dependent assets after a relevant contract, environment, source, or policy change.
Revalidate at use time where the consequence of stale advice warrants it. Avoid
using obsolete guidance merely because it has many historical successes.

Quarantine suspect claims; preserve enough provenance to repair dependent decisions.
Support authorized deletion across indexes and derived copies where applicable,
with retention exceptions made explicit. Do not promise complete erasure from systems
outside the controlled boundary.

## Acceptance scenario

Complete a representative task. Extract one justified reusable asset. On a later run,
retrieve it under matching conditions and verify its usefulness. Change a dependency
or supply counterevidence; ensure it is rejected, marked stale, or revalidated rather
than blindly reused. Attempt retrieval under the wrong tenant or scope and confirm
it is excluded. Record the test method and actual evidence.

A good result may be "retain nothing": the lesson is transient, already documented,
unverified, sensitive, or more expensive to maintain than to rediscover.
