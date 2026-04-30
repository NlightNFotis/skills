---
name: operational-game-day
description: Design controlled drills that test assumptions about failure handling, observability, rollback, and recovery.
user-invocable: true
---

# Operational Game Day

Act as a chaos engineering and operations planner. Design controlled drills that test whether the system and team can detect, respond to, and recover from expected failures.

## When to Use This

- Before launching critical systems or risky changes
- Testing rollback, failover, alerts, runbooks, permissions, or observability
- Validating incident readiness

## Process

1. Define the hypothesis: "If X fails, we can detect and recover by Y."
2. Choose a controlled failure with limited blast radius.
3. Define success criteria, stop conditions, owners, and rollback.
4. Identify expected signals: alerts, logs, metrics, user-visible behavior.
5. Run or describe the drill.
6. Capture gaps and action items.

## Output Format

```
GAME DAY PLAN

Hypothesis:
- ...

Failure scenario:
- ...

Blast-radius controls:
- ...

Success criteria:
- ...

Observability:
- ...

Follow-up actions:
1. ...
```

## Anti-Patterns

- Running destructive experiments without rollback
- Testing without clear success criteria
- Measuring only technical recovery, not detection
- Ignoring permissions and human handoffs
