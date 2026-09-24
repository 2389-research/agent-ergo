# Build a working system model

Treat this as a diagnostic instrument, not a demand for a new architecture document.
Reuse existing diagrams, contracts, and vocabulary. Mark absent evidence as unknown.

## Model the operating environment

Capture the minimum needed to make safe design decisions:

| Concern | Questions to resolve |
| --- | --- |
| Purpose | Which observable outcome makes the system valuable? Who judges it? What is explicitly out of scope? |
| Operator | Which agent acts, with what context, tools, identity, permissions, and runtime constraints? Which human decisions remain reserved? |
| Reality | Which system owns each fact? How is freshness known? Which views are derived or cached? |
| Control | Which actions are available, legal now, reversible, costly, external, or irreversible? |
| Proof | How is the desired outcome distinguished from a successful request, an accepted job, or a confident narrative? |
| Recovery | What persists across interruption? How is partial progress or an unknown outcome reconciled? |
| Learning | What survives a run, who may trust it, and how can it be corrected or invalidated? |
| Constraints | Which compatibility, privacy, latency, cost, tenancy, accessibility, and human-authority requirements bind the design? |

For an agentic system, distinguish the domain's business state, the agent's execution
state, and the evidence of what occurred. They may share storage, but they are not
interchangeable facts. A task marked complete is not evidence that its business
postcondition holds.

## Trace the abstraction tower

| Layer | Contract with the layer above | Question for the layer below |
| --- | --- | --- |
| Outcome | Define success, constraints, and unacceptable results. | Which journeys establish this outcome? |
| Journey | Define user intent, entry conditions, branches, and completion. | Which capabilities cover every meaningful branch? |
| Capability | Express one domain-level action or query and its authority. | Which inputs, outputs, failures, and state changes implement it? |
| Contract | Define schema, semantics, preconditions, postconditions, and failure behavior. | Which authoritative resources and transitions make it true? |
| State/resource | Define identity, lifecycle, ownership, version, and retention. | Which mechanisms store, enforce, observe, and recover it? |
| Mechanism | Satisfy the above contracts within operational constraints. | Which evidence demonstrates the behavior? |

Do not turn this logical tower into six mandatory services. A small command can
satisfy every layer in a few functions and one help page.

For each important link, trace both directions. Flag:

- An outcome with no observable acceptance criterion.
- A journey that depends on an undocumented capability or human intervention.
- A capability that requires knowledge of internal filenames or database tables
  without making that coupling intentional and stable.
- A contract with undefined failure, version, identity, or authorization semantics.
- Multiple authoritative writers without a conflict rule.
- A mechanism whose complexity has no corresponding outcome or invariant.

Keep cross-cutting constraints visible across layers. Security, ownership, and cost
are not features to bolt onto the bottom of the tower.

## Inspect the seven operator questions

A capable operator should be able to answer, using discoverable evidence:

1. **Orient:** Where am I, what am I trying to accomplish, and what rules bind me?
2. **Observe:** What is true now, how fresh is it, and what remains uncertain?
3. **Decide:** What actions are available and appropriate in this state?
4. **Act:** What precisely will happen, under whose authority, with what limits?
5. **Verify:** What happened, and what establishes the intended postcondition?
6. **Recover:** How do I stop, reconcile, retry, resume, compensate, or escalate?
7. **Learn:** What should a later run reuse, and when should it stop trusting it?

Prefer one navigable entrypoint with compact state and links to detail over one
monolithic prompt containing everything. Do not add a dashboard when a clear status
response or project index suffices. Treat the shape of this entrypoint as a hypothesis
to test with the cold-start journey.

## Record epistemic and authority boundaries

For each material assertion, distinguish source, version/time, interpretation, and
intended applicability. Different sources can be authoritative for different facts:
code may describe current behavior, a signed-off specification desired behavior,
and a deployment manifest what is running. Do not collapse these into a universal
ranking or pick the newest file automatically.

For unresolved contradictions, record the conflicting claims, their locations,
affected decisions, and the decision needed. Proceed with reversible independent
work. Do not silently settle a product, security, or ownership decision by changing
whichever document is easiest to edit.

## Completion test

Explain the main journey with authoritative identities, state transitions, verification,
and failure recovery. Trace its key outcome down to mechanisms and back. Identify
what the system should retain and what it must not retain. Stop expanding the model
when further inventory is unlikely to change a material decision within scope.
