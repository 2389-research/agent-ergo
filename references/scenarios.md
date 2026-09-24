# Acceptance journeys

Run the scenarios for the principal journey and for each failure branch the request or
sources show (SKILL.md section 3). Use existing tests or documented walkthroughs where
available. A designed test is not a passed test; a walkthrough is not an executed
runtime check.

## Scenario bank

| Scenario | Setup and action | Observable pass condition |
| --- | --- | --- |
| Cold-start operator | Start with only the revised entrypoint and a normal goal. | Discover legal actions, state, constraints, and evidence without hidden project context. |
| Normal vertical slice | Complete the core task across its actual component boundaries. | Establish the business postcondition, not just tool-call success. |
| Invalid or ambiguous input | Supply an invalid enum, wrong ID type, missing field, or contradictory argument. | Fail before prohibited effects and provide specific correction guidance. |
| Stale observation | Read version A, mutate authoritative state elsewhere, then act on A. | Apply documented concurrency semantics; do not silently overwrite incompatible state. |
| Timeout after effect | Let a side effect occur but withhold its response. | Resolve the operation before retry; do not duplicate the effect or falsely mark failure. |
| Duplicate request | Repeat the same logical request; then repeat its key with different input. | Honor the documented deduplication window and conflict rule; no unsupported exactly-once claim. |
| Process interruption | Interrupt after meaningful partial progress and restart. | Resume or reconcile from authoritative progress without losing or repeating committed effects. |
| Competing operators | Have two actors attempt incompatible updates. | Maintain ownership/isolation invariants and expose the loser or conflict. |
| Dependency outage | Make one external dependency unavailable during a partial workflow. | Bound retries, expose partial state, and identify a safe recovery or escalation path. |
| Cancellation race | Request cancellation while the operation may be completing. | Distinguish cancellation request, final outcome, and remaining effects. |
| Incomplete evidence | Paginate, truncate, redact, or delay important output. | Expose incompleteness/freshness and avoid unsupported conclusions. |
| Untrusted instructions | Put hostile instructions inside a retrieved document, log, or candidate memory. | Treat them as data; preserve tool authority, privacy, and task scope. |
| Learning invalidation | Retain a validated asset, then change a dependency or contradict its claim. | Mark stale/disputed, revalidate, or retire; do not blindly reuse. |
| Permission/scope mismatch | Reuse an ID or retained asset across an unauthorized boundary. | Refuse unauthorized access/effects without leaking restricted content. |
| Budget exhaustion | Exhaust the declared time, calls, context, or retry budget mid-task. | Stop safely, preserve necessary state, report partial results, and do not claim completion. |
| Version migration | Use an old consumer while a contract changes. | Preserve promised compatibility or fail with the documented migration path. |

## Walkthrough record

Record goal, initial knowledge, source/version, action sequence, expected observations,
actual observations, postcondition evidence, recovery path, method, result, and gaps.
Use the revised public surface rather than privileged knowledge accumulated while
editing. Do not invent tool outputs to complete the story.

For an unimplemented system, assess whether the specification makes the action and
expected observations unambiguous. Label the result "document walkthrough passed"
and runtime verification "not run". This establishes design completeness for that
scenario, not operational correctness.

## Worked small-system example

**Input:** A single-user CLI reads local Markdown and emits a summary. It has an
existing `--json` flag, stable exit codes, no shared writes, and no retained memory.
Its README omits the JSON schema and sends readers to three inconsistent examples.

**Appropriate intervention:** Reconcile the examples, document the existing schema,
state input limits and output completeness, and add a concrete acceptance example.
Check failure behavior for invalid input and interrupted output when relevant.
Do not invent a memory platform, distributed locks, event sourcing, or a new tool
transport. Mark cross-agent coordination and memory promotion not applicable.

**Completion:** Report the actual README/design changes and which checks ran. Do not
claim a latency improvement without measurements or edit code in improve-docs mode.

## Worked distributed-system example

**Input:** A build coordinator, workers, and artifact store disagree about whether a
job is complete. Workers retry after timeouts; the artifact store can contain partial
outputs; an earlier design says "retry all failures".

**Appropriate intervention:** Identify authoritative job and artifact state; define
operation identity, legal transitions, partial-output visibility, and postcondition
verification. Replace indiscriminate retries with reconciliation and bounded retry
semantics. Propagate the contract through coordinator design, worker plan, artifact
acceptance criteria, and recovery guidance. Add migration work for current behavior.

**Completion:** Walk through accepted/running/succeeded and timeout-after-write
scenarios. Label the runtime behavior unimplemented unless tested. Include retained
failure recipes only after evidence supports their scope and invalidation rules.
