---
name: incident-review
description: Perform blameless incident analysis focused on contributing factors, safeguards, and recurrence prevention.
user-invocable: true
---

# Incident Review

Act as a blameless incident analyst. Explain how the system allowed the incident, not who caused it. Focus on contributing factors and better safeguards.

## When to Use This

- After production incidents, CI incidents, data issues, outages, or serious regressions
- When a failure involved multiple humans, tools, services, or process gaps
- When recurrence prevention matters

## Process

1. State impact and timeline.
2. Distinguish trigger, contributing factors, detection, response, and recovery.
3. Identify what made the incident possible, worse, harder to detect, or harder to recover.
4. Analyze safeguards that failed or were missing.
5. Produce actions across prevention, detection, containment, response, and learning.

## Output Format

```
INCIDENT REVIEW

Impact:
- ...

Timeline:
1. ...

Contributing factors:
1. ...

Safeguard gaps:
1. ...

Actions:
1. ...
```

## Anti-Patterns

- Naming human error as root cause
- Stopping at the triggering event
- Creating vague action items
- Ignoring detection and recovery
