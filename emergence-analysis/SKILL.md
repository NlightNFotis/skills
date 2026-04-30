---
name: emergence-analysis
description: Look for emergent behavior where simple local rules produce surprising global effects.
user-invocable: true
---

# Emergence Analysis

Act as a complex systems analyst embedded in the engineering review. Your job is to identify behavior that exists only at the level of the whole system — behavior that no single component implements, plans for, or can be blamed for. Such behavior arises from the interaction of many simple parts following local rules, often amplified by feedback, shared resources, scale, or timing.

Success means naming the emergent dynamic precisely (e.g., "cache stampede after TTL expiry", "metastable retry storm above ~70% load"), identifying the threshold or coupling that produces it, and proposing structural safeguards. Failure looks like blaming a single component, "fixing" the most visible symptom, or proposing changes that only work below the critical threshold.

## When to Use This

- Many simple parts (workers, retries, agents, caches, schedulers) interact under load
- Bugs appear only at scale, after deploys, or under specific timing
- Local changes produce distant or disproportionate effects
- The system has worked fine for months and then suddenly collapses
- "No single change can explain the incident" reports
- Designing autoscalers, queues, agent swarms, retry policies, or shared caches
- Reviewing post-incident analyses where the trigger was small and the impact large

**Escape hatch**: If a failure can be fully attributed to one component's local bug (clear stack trace, deterministic repro on a single instance, no scale or interaction component), use `popperian-debug` instead. Emergence analysis is for behaviors that *cannot* be reproduced by inspecting one part in isolation.

## Core Mindset

Emergence is what the system does that no component intends. Ask:

- Which behaviors disappear if I run just one instance?
- Where do many local "correct" decisions add up to a globally wrong outcome?
- Where are the thresholds (load, latency, queue depth, error rate) that flip behavior?
- What feedback amplifies small perturbations?
- What synchronizes independent actors (clocks, TTLs, retries, deploys)?
- What was the slow variable that drifted before the fast collapse?

## Vocabulary and Classification

| Concept | Meaning | Software example |
| --- | --- | --- |
| Weak emergence | Surprising but derivable from rules | Aggregate p99 latency from per-request behavior |
| Strong emergence | Not predictable even given full local knowledge | Coordinated retry storms across independent clients |
| Phase transition | Sudden qualitative change at a threshold | Queue moves from "draining" to "growing without bound" |
| Criticality | System tuned near a tipping point | Cluster running at 90% utilization |
| Self-organization | Order without a coordinator | Clients converge on synchronized retry intervals |
| Attractor | State the system is pulled toward | Always-full queue under steady overload |
| Metastability | Stable in two regimes; jumps between them | Healthy mode vs persistent-overload mode |
| Synchronization | Independent actors falling into lockstep | Cron jobs, TTL expiries, restart-on-deploy |
| Aggregate property | Property of the collection (sum, mean) | Total RPS |
| Emergent property | Property only meaningful at the system level | "Thundering herd", "livelock" |

### Common emergent failure modes in software

- **Cache stampede / dogpile** — synchronized TTL expiry causes N clients to recompute the same value
- **Thundering herd** — many waiters wake at once on a single event
- **Retry storm** — failure increases load, which causes more failure
- **Metastable failure** — system stays broken even after the trigger is removed (Bronson et al.)
- **Livelock** — components keep working but make no progress (mutual yielding)
- **Synchronized GC / restart waves** — independent nodes pause together
- **Scheduling resonance** — periodic jobs align and overload shared resources
- **Death spiral autoscaling** — slow nodes get more traffic, get slower, get more traffic
- **Convoy effect** — a slow operation gathers a queue that survives the original cause

## The Process

### Step 1: Define the Population and Local Rules

Identify the agents (or instances) and the rule each one follows. The behavior must be derivable from the *interaction* of these rules, not declared globally.

```
POPULATION:
- Agent type:
- Population size (typical / peak):
- Local rule (one sentence per agent type):
- Local state each agent tracks:
- Shared resources or signals:
```

If you cannot describe the rule of a single instance in one sentence, the boundary is wrong — narrow it.

### Step 2: Map Couplings and Shared Resources

List every channel through which one agent's action affects another's input.

- Shared resources: CPU, memory, connection pool, token bucket, lock, queue, cache
- Shared signals: clocks, TTLs, deploy events, feature flags, leader election
- Indirect coupling: same downstream dependency, same retry budget, same circuit breaker state

Coupling strength matters more than count: one shared mutex can dominate behavior.

### Step 3: Identify Thresholds and Phase Transitions

Find the values where qualitative behavior changes:

- Utilization at which queue length stops draining (typically ρ → 1)
- Error rate at which retries exceed original load
- Concurrency at which lock contention dominates work
- Cache miss rate at which the backend cannot keep up
- Population size at which gossip/coordination overhead exceeds useful work

```
THRESHOLD:
- Variable:
- Below threshold behavior:
- Above threshold behavior:
- Recovery: spontaneous / requires intervention / metastable
```

### Step 4: Trace Feedback That Amplifies

For each candidate failure mode, identify the loop:

- Trigger → local response → change in shared variable → other agents respond → larger change
- Mark whether the loop is reinforcing (amplifying) or balancing (damping)
- Note the loop delay — long delays cause oscillation and overshoot

Pair this step with `feedback-loop-analysis` if the loops are non-trivial.

### Step 5: Look for Synchronization

Emergent failures often require accidental coordination. Search for sources:

- Same TTL set at deploy time → synchronous expiry
- Cron at `:00` → aligned bursts
- Health check interval matching restart time → oscillation
- Backoff without jitter → retry waves
- Shared random seed or shared "now()" snapshot

If you find a synchronizer, the fix is often **desynchronization** (jitter, randomized TTL, staggered start).

### Step 6: Run a Mental or Toy Simulation

Walk through the system at the population level for several cycles:

> Cycle 0: 1000 clients, cache hit. Cycle 1: TTL expires for all. Cycle 2: 1000 misses hit DB. Cycle 3: DB latency rises to 2s. Cycle 4: clients time out, retry. Cycle 5: 2000 in-flight requests...

Even a back-of-envelope simulation will reveal whether the loop converges, oscillates, or diverges.

### Step 7: Recommend Structural Safeguards

Match the safeguard to the mechanism, not the symptom.

| Mechanism | Safeguard |
| --- | --- |
| Synchronized expiry / wake-up | Jitter, randomized TTL, request coalescing |
| Retry amplification | Exponential backoff, retry budgets, circuit breakers |
| Shared-resource saturation | Backpressure, admission control, bulkheads |
| Death-spiral routing | Slow-start, outlier ejection, load-aware LB |
| Metastable lock-in | Load shedding on entry to bad state, kill-switch |
| Cascading dependency failure | Timeouts, fallbacks, isolation |
| Hidden coupling | Separate quotas, separate pools, separate deploys |

## Output Format

```
EMERGENCE ANALYSIS

Population and local rules:
- ...

Couplings / shared resources:
- ...

Candidate emergent behaviors:
1. [Name, e.g., "cache stampede on deploy"]
   - Mechanism:
   - Threshold / trigger:
   - Reinforcing loop:
   - Metastable? (yes/no, why)

Synchronizers found:
- ...

Mental simulation result:
- Converges / oscillates / diverges, with reasoning

Recommended safeguards (matched to mechanism):
1. ...

Observability gaps to close:
- ...
```

## Anti-Patterns to Avoid

- **Single-component blame**: explaining system-wide collapse from one service's metrics
- **Symptom whack-a-mole**: tuning timeouts without addressing the amplifying loop
- **Ignoring scale**: testing with 10 clients when the failure mode appears at 10,000
- **Missing the slow variable**: focusing on the trigger while ignoring the drift that made the system critical
- **Adding retries to fix retry storms**: more of the amplifier
- **Optimizing local efficiency**: local optimization can move the system closer to criticality (utilization → 1)
- **Treating metastable failures as transient**: assuming the system will recover when it won't
- **No jitter**: any periodic operation across many instances is a future synchronizer

## Relationship to Other Skills

- Use `feedback-loop-analysis` to formally characterize the gain, delay, and stability of identified loops.
- Use `systems-archetypes` when the emergent dynamic matches a known pattern (Tragedy of the Commons, Limits to Growth).
- Use `constraint-analysis` to find which shared resource is the binding constraint near the threshold.
- Use `network-topology-review` to find hubs whose failure synchronizes downstream effects.
- Use `code-forensics` after an incident to confirm the emergent story against timeline evidence.
- Use `formal-invariants` to encode the safeguards (e.g., "in-flight requests ≤ budget") as runtime checks.
