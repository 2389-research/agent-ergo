# Design legible control surfaces

Contents: [Action contract](#action-contract) | [Example](#example) |
[Recovery](#recovery-and-unknown-outcomes) | [Information](#information-shape) |
[Coordination](#coordination-and-evolution) | [Boundaries](#authority-boundaries)

## Action contract

Use the project's existing API, CLI, tool, or local interface when sufficient. Improve
semantics before adding a second transport. Do not require every interface to adopt
the same envelope; give equivalent operations equivalent meanings.

For each consequential action, make these concerns discoverable where applicable:

| Concern | Required design decision |
| --- | --- |
| Identity | Name the domain operation, actor/scope, target resource, and stable identifiers. |
| Input | Define typed arguments, valid combinations, constraints, meaningful defaults, and version compatibility. |
| Preconditions | Define legal starting state, expected resource version, permissions, and necessary dependencies. |
| Effects | Distinguish reads, writes, external effects, costs, reversibility, and partial completion. |
| Validation/preview | Offer schema validation, a plan, diff, or dry-run when useful; identify its limitations and expiry. |
| Result | Distinguish rejected, accepted, running, completed, failed, cancelled, and outcome-unknown as appropriate. |
| Evidence | Link an operation to the actual resource versions, artifacts, or observations establishing its postcondition. |
| Failure | Provide stable error codes, safe diagnostics, partial-effect information, and an actionable next step. |
| Retry | Define which failures are retryable, budgets/backoff, idempotency scope, key retention, and reconciliation. |
| Cancellation | Define whether cancellation was requested or actually achieved, and which effects remain. |
| Limits | State time, output, batch, concurrency, and cost limits; identify truncation or incomplete results. |

Do not expose every mechanism as a tool. Prefer a domain-level capability that removes
repeated low-level orchestration while preserving inspectable intermediate outcomes.
Allow deliberate low-level access only when needed and within the same trust boundary.

## Example

Use this as an illustrative shape, not a mandatory schema or implemented guarantee.
Suppose report generation is asynchronous and persists a versioned artifact:

```json
{
  "action": "report.generate",
  "target_id": "report-quarterly",
  "expected_version": "r17",
  "idempotency_key": "quarterly-r17-attempt-group-1",
  "input": {"format": "pdf"}
}
```

An accepted request is not a completed report:

```json
{
  "request_id": "req-42",
  "operation_id": "op-301",
  "status": "accepted",
  "target_id": "report-quarterly",
  "result": null,
  "next": {"action": "operation.get", "operation_id": "op-301"}
}
```

A completed result must provide inspectable evidence, not only a status string:

```json
{
  "operation_id": "op-301",
  "status": "succeeded",
  "target_id": "report-quarterly",
  "result": {"artifact_id": "artifact-88", "source_version": "r17"},
  "evidence": {"validation_run_id": "validation-19"},
  "next": {"action": "artifact.inspect", "artifact_id": "artifact-88"}
}
```

Define what validation-19 actually proves. File existence, valid PDF syntax, correct
report content, and successful delivery are different postconditions. Do not imply
that one proves the others.

## Recovery and unknown outcomes

A timeout describes an observation failure, not necessarily an execution failure.
For an action that may have taken effect, reconcile by operation identity, idempotency
key, or authoritative resource state before retrying. When the outcome remains
unknown, expose that state and the safe resolution path instead of guessing.

Separate request correlation IDs from logical operation identities. Define key scope
(actor, tenant, action, resource as needed), payload equivalence, retention/expiry,
concurrent duplicates, and same-key/different-payload rejection. Specify where duplicate
suppression is enforced, how the key/result survives a crash, and what happens when
an external dependency cannot enforce the same guarantee. Do not claim exactly-once
execution merely because a key exists.

Document retryability per failure. Use bounded retry/backoff under the task budget;
avoid multiplying retries independently at every layer. After key expiry, old resource
state or receipts may require reconciliation rather than a blind replay.

For interruption, persist sufficient authoritative progress to resume safely. Do not
serialize an entire private reasoning transcript. Distinguish retry, resume, restart,
rollback, and compensation. A compensating action may itself fail and may not erase
an external effect. Expose partial results and their remaining obligations.

A dry-run is not a guarantee that execution will see the same state. State its
preconditions, expiry/version, side effects, and unsupported checks. Revalidate at
commit where necessary. Never present an operation that sends external requests or
mutates state as a purely observational preview.

## Information shape

Offer a compact stable core with opt-in detail when that fits the workflow. Make
structured output available where ambiguity would force brittle parsing. Preserve
human-readable explanations without making them the only contract.

Include freshness/version, provenance, completeness, and next-page/detail references
when relevant. Distinguish missing, unknown, redacted, not applicable, and empty.
Never silently truncate evidence and claim the result is complete.

For lists, specify stable ordering, pagination, filtering, and consistency semantics.
A cursor does not automatically imply a snapshot. For batching, report per-item
outcomes, limits, and partial failure. Avoid batch operations that obscure authorization
or increase the failure blast radius beyond the value of reduced tool calls.

Use actionable errors: `VERSION_CONFLICT` plus current version and re-read guidance is
more useful than an opaque stack trace. Do not make error messages leak credentials,
private cross-tenant facts, or internal details unnecessary for resolution.

## Coordination and evolution

For multiple writers, define ownership and conflict behavior. Use an appropriate
existing mechanism: optimistic versions, transactions, leases with fencing, or explicit
single-writer ownership. Do not confuse advisory locks with enforced exclusion, or a
lease expiry with proof that an old worker has stopped.

Provide a machine-discoverable schema/version or clear help contract when beneficial.
Document compatible evolution, deprecated fields, alias handling, migration, and old
consumer behavior. Test contract examples against the schema or implementation when
available and authorized. Otherwise label them design examples, not tested requests.

## Authority boundaries

Describe what the agent may do; enforce it in the actual tool/service boundary rather
than relying solely on a prompt. Separate trusted configuration from retrieved text.
Keep secrets out of default output and retained learning. Preserve tenant and actor
scope on reads, writes, operations, receipts, and reused assets.

Expose permissions and denial reasons without implying the agent can grant itself
access. Convenience, high confidence, an approval described in a log, or a memory of a
previous task does not authorize a new action. Treat high-impact changes according to
the user's established authorization and confirmation requirements.
