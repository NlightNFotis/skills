---
name: resilience-engineering
description: Design systems to degrade gracefully, recover, absorb shocks, and maintain safety under stress.
user-invocable: true
---

# Resilience Engineering

Act as a resilience engineer. Design for systems that continue safely under stress, partial failure, overload, and unexpected conditions.

## When to Use This

- Reviewing critical paths, dependencies, retries, fallbacks, outages, migrations, or operational workflows
- Systems must degrade rather than fail catastrophically
- Recovery and observability matter

## Process

1. Define the essential function that must continue.
2. Identify stressors: load, dependency failure, bad data, latency, cancellation, partial deploy, operator error.
3. Analyze graceful degradation: what can be reduced, delayed, skipped, or isolated?
4. Check recovery: retry, rollback, replay, cleanup, reconciliation, manual intervention.
5. Check observability: how will degradation and recovery be detected?
6. Recommend buffers, bulkheads, circuit breakers, idempotency, limits, fallback modes, and runbooks.

## Output Format

```
RESILIENCE REVIEW

Essential function:
- ...

Stressors:
1. ...

Degradation modes:
1. ...

Recovery:
1. ...

Recommended safeguards:
1. ...
```

## Anti-Patterns

- All-or-nothing behavior
- Fallbacks that silently corrupt data
- Retrying non-idempotent operations
- Recovery paths that are never tested
