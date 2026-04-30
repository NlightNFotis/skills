---
name: emergence-analysis
description: Look for emergent behavior where simple local rules produce surprising global effects.
user-invocable: true
---

# Emergence Analysis

Act as a complex systems analyst. Look for global behavior that arises from local rules, interactions, feedback, and scale rather than from any single component.

## When to Use This

- Many simple parts interact unpredictably
- Bugs appear only at scale or under load
- Local changes cause distant effects
- Queues, retries, agents, schedulers, caches, or policies interact

## Process

1. Define the agents/components and their local rules.
2. Identify interactions, feedback loops, thresholds, and shared resources.
3. Ask what behavior appears only when many instances run together.
4. Look for phase changes: behavior that flips after a threshold.
5. Simulate mentally or with small experiments: what happens over repeated cycles?
6. Recommend safeguards: caps, damping, backpressure, isolation, observability, randomized jitter, circuit breakers.

## Output Format

```
EMERGENCE ANALYSIS

Local rules:
- ...

Interactions:
- ...

Emergent risks:
1. ...

Thresholds:
- ...

Safeguards:
1. ...
```

## Anti-Patterns

- Explaining global behavior from one component only
- Ignoring scale and repetition
- Missing feedback loops
- Assuming local optimization improves the whole system
