# Coordinated change protocol

Contents: [Authority](#establish-authority-and-preserve-work) |
[Propagation](#map-semantic-propagation) | [Ledger](#use-a-minimal-change-ledger) |
[Slices](#define-executable-implementation-slices) | [Verification](#verify-and-report-truthfully)

## Establish authority and preserve work

Inspect the actual source and its version before editing. Follow project instructions
and user-provided edit boundaries. In a repository, inspect status and existing diffs;
never reset, clean, overwrite, or reformat unrelated work. Read tool descriptions
before connector writes. A source's permission to be read is not permission to write
it, and a request to improve a design is not permission to deploy it.

For material claims, cite a stable location: repository path and section/symbol,
document ID and heading, or supplied text and paragraph. Use native source citations
where available. Distinguish an inaccessible source from a source that does not exist.
Do not use a broad external search to invent facts about a private system.

Respect explicit source authority. Where it is not given, determine which source
owns which fact; do not assume the newest document or the implementation is the
normative design. Preserve both current and target behavior when they differ.

For shared documents, re-read the relevant section or use a revision guard immediately
before writing when supported. For multi-file changes, preserve rollback ability and
verify the set as one logical change. When a write partially fails, identify exactly
what changed, what did not, and the coherent next repair or rollback step.

## Map semantic propagation

For each change, inspect these surfaces when they exist and are relevant:

| Surface | Reconcile |
| --- | --- |
| Requirements | Outcomes, invariants, constraints, non-goals, measurable acceptance |
| Architecture | Boundaries, responsibilities, dependencies, system-level tradeoffs |
| Contracts and schemas | Names, IDs, inputs/outputs, defaults, auth, errors, versions |
| State model | Owners, transitions, persistence, derived views, retention |
| Plans and tasks | Dependencies, sequencing, scope, verification, completion |
| Examples and onboarding | Runnable examples, legal states, entrypoint discoverability |
| Tests and acceptance design | Positive/negative scenarios and claimed guarantees |
| Operations | Status, diagnostics, recovery, limits, incident behavior |
| Migration | Compatibility, old/new coexistence, deprecation, fallback |

Maintain one authoritative home for each rule and link to it where possible. Do not
copy a full contract into every document. Do not create every surface when an existing
small specification can own the relevant facts.

Classify each affected surface as updated, deliberately unchanged with a reason,
or blocked. Search known obsolete terms and defaults after editing, and inspect
matches rather than blindly replacing them. A text search alone cannot establish
semantic consistency; also replay a journey spanning the documents.

## Use a minimal change ledger

Reuse an existing issue, table, or review record. Capture:

`finding + evidence -> chosen change -> affected surfaces -> dependent tasks -> check -> disposition`

Use stable IDs only when they improve traceability. Do not require a second project
management system. For large or automated handoffs, the optional JSON manifest gives
mechanical checks; for a small edit, a few rows in the final report suffice.

Separate these states:

- **Applied:** The declared artifact was actually changed.
- **Proposed:** A replacement, patch, or design is supplied but not applied there.
- **Verified:** A named check passed by a declared method, with evidence.
- **Unresolved/deferred:** Work or a decision remains, with consequence and reason.

A design edit may be applied and structurally verified while its desired runtime
behavior remains unimplemented and untested. State that distinction at the change
and final-summary level.

## Define executable implementation slices

For each slice, specify goal, prerequisites, input artifacts, owned edit scope,
required outputs, postconditions, verification commands or procedures, failure and
recovery behavior, and a completion rule. Add dependency IDs when ordering matters.
Avoid tasks like "add robust observability" without the concrete behavior to observe.

Keep the implementation choice open only when the contract and constraints allow it.
Make default decisions for reversible engineering details; record unresolved product,
policy, security, and ownership decisions instead of silently delegating them as
implementation guesses. Do not manufacture a requirement for human approval when
existing authority already permits the action; do not remove required approvals.

For parallel work, isolate ownership and integrate against an agreed contract. A
shared filesystem is not a concurrency policy. Use existing worktrees, branches,
locks, leases, or optimistic concurrency where appropriate instead of mandating a
new coordinator.

## Verify and report truthfully

Record checks by method: structural review, document-based scenario walkthrough,
or executed runtime test. Record pass/fail/not-run/blocked separately. Only call an
independent review independent if another reviewer actually performed it.

Require high-severity findings to be resolved or prominently disclosed. Report blocked
or incomplete remediation as partial; do not bury it beneath a global green score.
An audit can be complete even when remediation remains open.

When permissions or tool availability prevent an edit, deliver exact replacement
sections or a patch in the requested format. Do not claim an unapplied patch is a
changed source file. Stop unsafe branches, complete safe independent work, and ask
only for an indispensable missing decision or permission.
