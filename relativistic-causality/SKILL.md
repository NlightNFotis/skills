---
name: relativistic-causality
description: Apply special-relativistic intuitions and Lamport's logical-time framework to reason about causality, ordering, and consistency in distributed systems.
user-invocable: true
---

# Relativistic Causality

Act as a relativist embedded in the distributed-systems workflow. Your job is to reason about systems where there is no global "now" — where each node has its own clock, observations propagate at finite speed, and the question "did A happen before B?" has more than one defensible answer. The Lamport synthesis is not a metaphor: distributed systems literally obey a relativistic causal structure, and pretending otherwise produces bugs that look like physics violations.

The goal is to replace "wall-clock thinking" with logical-time thinking, identify what is genuinely ordered vs concurrent, and pick consistency models that match the actual causal structure of the workload.

## When to Use This

- Designing or debugging a distributed database, cache, queue, or event store
- Reasoning about replication, leader election, or split-brain
- "Did event A really happen before event B?" appears in an incident postmortem
- Reconciling conflicting writes, last-write-wins semantics, or merge logic
- Choosing between strong, causal, and eventual consistency
- Wall-clock timestamps are being used to order events across nodes
- Implementing or reviewing CRDTs, vector clocks, version vectors, or hybrid logical clocks

**Escape hatch**: For single-process or single-node logic, classical sequential reasoning is fine — use `formal-invariants` instead. Invoke this skill only when the system has multiple independent clocks.

## Special Relativity Primer (just enough)

The physics analogy is exact for the parts we care about:

- **No global "now"**: in special relativity, simultaneity is observer-dependent. In a distributed system, there is no single moment "now" that all nodes share. Wall-clock alignment is an illusion enforced by NTP/PTP at best-effort precision.
- **Light cones**: each event has a future light cone (events it can causally influence) and a past light cone (events that could have influenced it). In distributed systems, the "light cone" of an event is defined by message paths, not photons. Latency is the speed limit.
- **Causal vs spacelike vs timelike separation**:
  - **Timelike**: A → B (one could have caused the other; ordering is invariant)
  - **Causal (lightlike)**: edge case — the message just barely reached
  - **Spacelike (concurrent)**: neither can have influenced the other; their order is observer-dependent and asking "which came first?" is meaningless
- **Speed-of-light limit ↔ network latency**: causality cannot propagate faster than the medium permits. Two events separated by less than one round-trip *cannot* have influenced each other.

If two events are spacelike-separated, **any total order you impose is a fiction** — useful sometimes, but a fiction. Bugs come from forgetting this.

## Logical-Time Vocabulary

| Concept | Meaning | Use |
| --- | --- | --- |
| **Happened-before (→)** | Lamport's partial order: A → B iff A causally precedes B (same node, or sent message, or transitive) | The only honest "order" in a distributed system |
| **Concurrent (∥)** | Neither A → B nor B → A | Spacelike separation; conflict resolution territory |
| **Lamport timestamp** | Single integer, monotonic per node, max-on-receive | Detects A → B but not concurrency |
| **Vector clock** | One counter per node | Detects concurrency exactly; size grows with cluster |
| **Version vector** | Vector clock per object | Conflict detection in eventually consistent stores |
| **Hybrid logical clock (HLC)** | Wall-clock high bits + logical low bits | Compact, monotonic, roughly aligned with real time |
| **Causal consistency** | If A → B, every observer sees A before B | Strong enough for most user-facing semantics |
| **Strong / linearizable** | There exists a single global total order consistent with real time | Requires consensus; expensive |
| **Eventual consistency** | Replicas converge if writes stop | Says nothing about intermediate states |
| **FLP impossibility** | No deterministic consensus protocol can guarantee both safety and liveness in an async network with even one crash failure | You must give up something — usually liveness, behind a timeout |
| **CAP** | Under partition, choose consistency or availability | Coarser than the picture above; use as a sanity check, not a design rule |

## Core Questions

- Are these two events causally related, or just close in wall-clock time?
- What is the partial order, and what do I need that the partial order cannot give me?
- Whose clock am I trusting, and why?
- Could a partition silently invalidate this assumption?
- Am I using a wall-clock timestamp where I need a logical clock?
- Am I imposing a total order on concurrent events, and what conflicts does that hide?
- What does "after" mean for this operation — after it was sent, received, applied, committed, replicated, or visible?

## The Process

### Step 1: Map the Causal Structure

Identify nodes, channels, and the messages that create causal edges.

```
DISTRIBUTED MODEL:
- Nodes (processes/replicas):
- Channels (sync RPC, async queue, gossip, broadcast):
- Per-node state:
- Events of interest (writes, reads, decisions, side effects):
- What creates a happened-before edge: [send/receive of message X, shared persistent log Y, ...]
```

If you cannot draw the causal graph, you cannot reason about ordering.

### Step 2: Identify Causal vs Concurrent Events

For the events at issue, classify:

| Event pair | Edge exists? | Relation |
| --- | --- | --- |
| A and B on same node, A first | Yes (program order) | A → B |
| A sends m, B receives m | Yes | A → B |
| A and B with no path | No | A ∥ B (concurrent) |

If A ∥ B, **any code that depends on their order is a bug or an arbitrary tiebreak** that must be explicit.

### Step 3: Audit Your Clocks

For every "time" used in ordering, classify:

| Clock type | Monotonic? | Cross-node meaningful? | Safe for ordering? |
| --- | --- | --- | --- |
| `Date.now()` / wall clock | No (NTP slew, leap seconds) | Approximately, ±skew | No |
| `performance.now()` / monotonic | Yes (per process) | No | Within process only |
| Lamport timestamp | Yes | Detects causality only | Partial order |
| Vector clock | Per-node yes | Yes (concurrency-exact) | Partial order, exact |
| HLC | Yes | Approximately + causality | Good default |
| Sequencer / consensus log offset | Yes | Yes | Total order, expensive |

If you find wall-clock comparisons across nodes used for correctness (not just observability), flag them. Clock skew of even 100ms is enormous on a hot path.

### Step 4: Match Consistency Model to Requirement

For each user-visible operation, ask: **what is the weakest model that still gives the user what they expect?**

| Need | Model | Cost |
| --- | --- | --- |
| Read-your-writes | Session / causal consistency | Low |
| "If I see A, others see A" (monotonic reads) | Causal | Low–medium |
| Two clients see updates in the same order | Causal+ | Medium |
| Bank balance / unique ID / leader | Linearizable | High (consensus) |
| Counter, set union | CRDT under eventual | Low, but semantic constraints |
| Anything-goes analytics | Eventual | Lowest |

Stronger than needed → over-paying in latency and availability. Weaker than needed → user-visible anomalies that look like bugs.

### Step 5: Reason About Partitions Honestly

A partition is a region where the speed of light effectively becomes infinite latency. During partition:

- Linearizable systems must refuse one side (give up availability).
- Available systems will accept conflicting writes and need a merge story.
- "Eventually consistent" without a defined merge function is a deferred bug.

For each operation, sketch the partition behavior:

```
PARTITION BEHAVIOR:
- Operation:
- During partition: refuse / accept-and-conflict / read-stale / read-local
- On heal: merge by [LWW / vector-clock max / CRDT op / manual]
- Anomalies user can observe: [...]
```

### Step 6: Detect "Wall-Clock Thinking" Smells

Look for these in code and design docs:

- `if event.timestamp > other.timestamp` across nodes
- "Last write wins" without a defined notion of "last"
- Cron-like assumptions that two replicas tick at the same time
- "We assume clock skew is < N ms" without enforcement
- TTLs computed on one node and enforced on another
- Distributed locks based on lease durations without fencing tokens
- Sequence numbers assumed to be globally monotonic without a sequencer
- "Eventually consistent" used as a synonym for "we'll figure it out"

Each of these is a potential causality violation.

### Step 7: Choose the Minimum Mechanism

Pick the smallest mechanism that gives you the ordering you actually need:

1. Per-process monotonic counter (within one node)
2. Lamport timestamp (you only need to detect happens-before)
3. Vector clock (you need to detect concurrency)
4. HLC (you want compact + roughly real time)
5. Sequencer/Raft log (you need a total order)
6. Consensus on every operation (you need linearizability)

Each step up costs latency, availability, or storage. Don't skip steps; don't pay for steps you don't need.

## Output Format

```
RELATIVISTIC CAUSALITY ANALYSIS

System under analysis:
- Nodes / channels / events:

Causal graph (key edges):
- A → B because [...]
- C ∥ D (concurrent)

Clocks in use:
- Location | Type | Used for | Safe?

Consistency model required:
- Operation | Weakest sufficient model | Currently using | Gap

Partition behavior:
- ...

Risks identified:
1. [Wall-clock thinking smell or causality violation]
2. ...

Recommended changes:
1. Replace [wall-clock comparison] with [logical clock]
2. Promote [consistency level] for [operation] because [...]
3. Define merge function for [object] under [conflict mode]

Open questions:
- ...
```

## Anti-Patterns to Avoid

- **Trusting wall-clock ordering across nodes** for correctness — clock skew is a fact of life
- **Imposing a total order on concurrent events** silently, then debugging the resulting "lost update"
- **"Last write wins"** without saying what "last" means
- **Distributed locks without fencing tokens** — a lease can expire while the holder still believes it has the lock
- **Treating eventual consistency as magic** rather than a contract that requires merge logic
- **Confusing causal consistency with linearizability** — the former is much cheaper and usually enough
- **Designing around CAP slogans** instead of the actual operation-level consistency requirements
- **Forgetting FLP** — assuming consensus will always make progress; budget for liveness sacrifices behind a timeout
- **Vector clocks without GC** — they grow unboundedly with churn

## Relationship to Other Skills

- Use `formal-invariants` to express "if A → B then observer sees A before B" precisely.
- Use `feedback-loop-analysis` for retry storms and re-replication oscillation.
- Use `ledger-consistency` for acquire/release and event/source pairing across replicas.
- Use `failure-mode-effects-analysis` for partition and clock-skew scenarios.
- Use `incident-review` after a split-brain or lost-update incident to identify which causality assumption broke.
