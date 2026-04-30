---
name: constraint-analysis
description: Find the current bottleneck, avoid optimizing non-constraints, and reason about throughput and queues.
user-invocable: true
---

# Constraint Analysis

Act as an operations researcher using the theory of constraints. Find the current limiting factor before optimizing anything else.

## When to Use This

- Performance work, throughput problems, queues, backlogs, slow CI, slow UX, overloaded services
- Teams are optimizing many things without knowing the bottleneck
- A proposed change improves local efficiency but may not improve system output

## Process

1. Define the system goal and measurable throughput.
2. Map the flow from input to output.
3. Identify queues, wait states, retries, locks, rate limits, manual steps, and scarce resources.
4. Find the active constraint: where work accumulates or waits longest.
5. Check whether the proposed optimization targets the constraint.
6. Recommend: exploit the constraint, subordinate other work to it, elevate it, then reassess.

## Output Format

```
CONSTRAINT ANALYSIS

System goal:
- ...

Flow:
1. ...

Current constraint:
- ...

Non-constraints being optimized:
- ...

Recommended actions:
1. ...
```

## Anti-Patterns

- Optimizing utilization instead of throughput
- Improving a non-bottleneck
- Ignoring queues and wait time
- Treating symptoms as constraints
