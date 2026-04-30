---
name: constraint-analysis
description: Find the current bottleneck, avoid optimizing non-constraints, and reason about throughput and queues.
user-invocable: true
---

# Constraint Analysis

Act as an operations researcher applying Goldratt's Theory of Constraints. In any system that produces a flow — requests served, PRs merged, builds completed, features shipped — there is at one moment exactly one binding constraint that determines throughput. Effort spent improving anything else does not improve system output; it only increases inventory or operating expense. The discipline of this skill is to find that constraint *first*, and to refuse to optimize anything else until you have.

Success looks like correctly identifying the active constraint, refusing seductive non-constraint optimizations, applying the Five Focusing Steps, and reassessing once the constraint has moved. Failure looks like optimizing utilization on a non-constraint, treating symptoms (queue length somewhere) as the constraint itself, or assuming the bottleneck has not moved after a change.

## When to Use This

- Performance work, throughput problems, slow CI, slow UX, overloaded service, growing backlog
- Multiple optimizations are being proposed and you need to prioritize
- A team is "fully utilized" but throughput hasn't improved
- A change improves a local metric (CPU, latency at one hop) but not end-to-end output
- Capacity planning, scaling decisions, queue and pool sizing
- Reviewing a release/deploy/PR pipeline that takes too long
- Suspect that "everyone is busy" is being mistaken for "the system is working"

**Escape hatch**: For correctness, security, or design-quality problems that don't have a throughput dimension, this is the wrong lens. Use `popperian-debug` or `formal-invariants`. Use constraint analysis only when the question is *flow*.

## Core Mindset

A system's throughput is governed by its constraint. Improvements anywhere else are noise — or worse, they increase inventory and starve or flood the constraint. Ask:

- What is the goal of this system, expressed as a measurable flow?
- Where does work pile up? Where do workers wait?
- Where is utilization already at ~100%?
- If I doubled the speed of this proposed optimization target, would system output double? If not, why am I doing it?
- Has the constraint moved since we last measured?
- Are we confusing local efficiency (utilization) with system throughput?

## Theory-of-Constraints Vocabulary

| Concept | Meaning |
| --- | --- |
| **Throughput (T)** | Rate at which the system generates value (units/time) |
| **Inventory (I)** | Money/work tied up in things not yet delivered (WIP, queues, backlog) |
| **Operating Expense (OE)** | Money spent turning Inventory into Throughput |
| **Constraint** | The single resource currently limiting Throughput |
| **Non-constraint** | Any resource with idle capacity at the constraint's pace |
| **Drum** | The constraint, which sets the pace for the whole system |
| **Buffer** | Protective inventory just before the constraint to keep it fed |
| **Rope** | Mechanism that releases new work into the system at the constraint's rate |
| **Drum-Buffer-Rope (DBR)** | Scheduling pattern: pace work to the drum, buffer the drum, gate inputs by the rope |
| **Subordination** | Non-constraints work at the constraint's pace, not their own max |
| **Elevation** | Adding more capacity to the constraint |

### The Five Focusing Steps

1. **Identify** the constraint
2. **Exploit** the constraint — get the most from it without spending more
3. **Subordinate** everything else to the constraint
4. **Elevate** the constraint — only if exploitation is not enough
5. **Repeat**: when the constraint moves, return to step 1; do not let inertia become the new constraint

### Two laws you must internalize

- **Little's Law**: `L = λ × W`. Average inventory in a stable queue equals arrival rate times average wait time. Reducing wait time *or* arrival rate reduces inventory; adding capacity to a non-constraint does not.
- **Utilization vs throughput**: as utilization on the constraint approaches 100%, queue length (and hence latency) grows nonlinearly. Beyond ~85% utilization, small load increases produce large latency increases (M/M/1 intuition). High utilization on a *non*-constraint is just waste.

### Useful failure-mode names

- **Starvation**: the constraint is idle waiting for upstream work
- **Blocking**: the constraint cannot release output because downstream is full
- **Local optima**: each station optimized; system makes less
- **Wandering bottleneck**: constraint moves with workload mix; static optimization fails
- **Policy constraint**: the bottleneck is a rule (e.g., "all PRs need 2 reviews"), not a resource

## The Process

### Step 1: Define the Goal and the Throughput Metric

State the system goal as a flow with units.

```
GOAL:
- System: ...
- Flow being measured: (requests/sec, PRs merged/week, deploys/day, tickets closed/week)
- Current rate:
- Target rate:
- Definition of "done" for one unit:
```

If the goal is not a flow ("be reliable", "be fast"), translate it into one before continuing, or use a different skill.

### Step 2: Map the Flow

List every stage from input arrival to delivered output. Include human steps, queues, waits, retries, approvals.

```
FLOW:
1. [stage] — capacity: ___ units/time, queue at entry: ___, current rate through: ___
2. ...
```

Include **wait states** as explicit stages — they are usually where the constraint hides. Pay particular attention to handoffs between humans and automation.

### Step 3: Identify the Active Constraint

Use multiple signals — they should agree.

| Signal | Meaning |
| --- | --- |
| Queue grows in front of stage X | X is the constraint |
| Stage X is at ~100% utilization | X is the constraint |
| Stage X workers never wait | X is the constraint |
| Other stages periodically idle waiting for X | X is the constraint |
| Speeding up stage Y did not improve T | Y was not the constraint |

If signals disagree, the constraint may be wandering, may be a policy rather than a resource, or you may be measuring the wrong stage.

```
CONSTRAINT:
- Stage:
- Type: physical resource / human / policy / market / external dependency
- Evidence:
- Current capacity:
- Current demand at this stage:
```

### Step 4: Check the Optimization Being Proposed

For every proposed optimization, ask the constraint test:

> If this change made stage X infinitely fast, would system throughput increase?

- If **no** — X is not the constraint. Refuse the work or re-scope it.
- If **yes** — X is the constraint or directly feeds it. Proceed.

This is the single most valuable use of this skill: stopping work that cannot improve throughput.

### Step 5: Exploit the Constraint

Before adding capacity, get more from what you have.

- Eliminate waste at the constraint: rework, idle time, low-value work
- Don't run non-throughput work on the constraint resource (e.g., don't run lint on the test runner if tests are the bottleneck)
- Pre-stage work so the constraint never waits for setup
- Batch only when batching improves constraint output, not just convenience elsewhere
- Move quality checks *before* the constraint so it never spends capacity on doomed work

### Step 6: Subordinate Everything Else

Non-constraints must run at the constraint's pace, not their own max.

- Pace input release (the **rope**) so inventory doesn't pile up
- Cap WIP upstream of the constraint
- Don't optimize utilization of non-constraints — slack there is healthy
- Schedules, rate limits, and admission control downstream of the constraint should match its output rate

Common error: managers reward 100% utilization at every station. This *guarantees* exploding inventory between stations and disguises the real constraint.

### Step 7: Elevate Only if Necessary

Now consider adding capacity to the constraint:

- Add resource (more workers, bigger machine, more reviewers)
- Offload work from the constraint to a non-constraint
- Change the policy if it is a policy constraint
- Externalize (buy instead of build for that step)

Elevation is often the most expensive option. Do it only after exploitation and subordination.

### Step 8: Re-identify (the constraint has probably moved)

After any meaningful change, the constraint has likely moved.

- Re-measure: queue lengths, utilization, throughput
- The new constraint may be different in kind (was code, now reviews; was DB, now network)
- Beware **inertia**: refusing to change policies that "worked" because they fit the *previous* constraint

```
RE-IDENTIFY:
- Previous constraint: ...
- New constraint: ...
- Policies that need updating because the constraint moved:
```

## Output Format

```
CONSTRAINT ANALYSIS

Goal and throughput metric:
- ...

Flow map (with capacities and queues):
1. ...

Active constraint:
- Stage:
- Type:
- Evidence:

Constraint test on proposed optimizations:
- Optimization X: PASSES / FAILS — because ...

Exploitation actions (no new resources):
1. ...

Subordination actions (other stages adapt to the constraint's pace):
1. ...

Elevation actions (only if exploitation is insufficient):
1. ...

Predicted next constraint after these changes:
- ...

Policies to revisit when the constraint moves:
- ...
```

## Anti-Patterns to Avoid

- **Optimizing utilization instead of throughput**: a 100%-utilized non-constraint is waste
- **Improving a non-bottleneck**: feels productive, changes nothing
- **Ignoring queues and wait time**: the constraint usually announces itself with a queue
- **Treating symptoms as constraints**: high CPU on one node may be downstream of the real constraint
- **Forgetting that constraints move**: yesterday's bottleneck is today's slack
- **Local optima everywhere**: each team optimized, system worse
- **Confusing busy with productive**: humans and machines can be 100% busy on the wrong work
- **Skipping exploit/subordinate, jumping to elevate**: spending money instead of thinking
- **Over-batching to "improve efficiency"**: efficiency at one stage, latency and inventory everywhere

## Relationship to Other Skills

- Use `feedback-loop-analysis` when the constraint interacts with retry/backpressure loops; constraint behavior near 100% utilization is highly nonlinear.
- Use `systems-archetypes` (especially Limits to Growth and Shifting the Burden) when the constraint is structural rather than resource-based.
- Use `network-topology-review` to find betweenness hubs that are likely throughput constraints.
- Use `system-ecosystem-analysis` when the constraint is a shared resource at carrying capacity.
- Use `emergence-analysis` when the constraint only appears at high load due to interactions among components.
- Use `code-forensics` to validate that throughput claims and queue measurements are real, not artifacts of sampling.
