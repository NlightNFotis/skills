---
name: ooda-adaptive-execution
description: Use observe-orient-decide-act loops for fast adaptive work under uncertainty.
user-invocable: true
---

# OODA Adaptive Execution

Act as an adaptive operator using the Observe-Orient-Decide-Act loop. Use short cycles to make progress under uncertainty without overcommitting to a stale plan.

## When to Use This

- Incidents, exploratory debugging, ambiguous tasks, changing requirements, or unfamiliar code
- Speed matters but blind action is risky
- New information should change the plan

## Process

1. Observe: gather the smallest useful facts.
2. Orient: interpret facts in context; identify constraints, risks, and options.
3. Decide: choose the next reversible, information-rich action.
4. Act: perform it.
5. Loop: update orientation based on results.

Prefer actions that both move the task forward and reveal new information.

## Output Format

```
OODA LOOP

Observe:
- ...

Orient:
- ...

Decide:
- ...

Act:
- ...

Next loop trigger:
- ...
```

## Anti-Patterns

- Waiting for perfect information
- Continuing a plan after facts change
- Taking irreversible action too early
- Confusing activity with adaptation
