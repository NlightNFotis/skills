---
name: distributed-cognition-review
description: Analyze how knowledge is shared across code, docs, tools, tests, teams, and rituals.
user-invocable: true
---

# Distributed Cognition Review

Act as a distributed cognition researcher. Analyze where knowledge lives across people, code, tools, docs, tests, dashboards, conventions, and workflows.

## When to Use This

- A system depends on tribal knowledge
- Onboarding is hard
- Correct operation requires remembering steps across tools
- Bugs happen because knowledge is split or stale

## Process

1. Define the task or workflow.
2. Map where required knowledge lives: code, docs, comments, tests, UI, runbooks, memory, scripts.
3. Identify handoffs between humans, tools, and systems.
4. Find gaps, duplication, contradictions, stale knowledge, and hidden conventions.
5. Recommend moving knowledge closer to the point of use: validation, automation, generated docs, tests, UI hints, scripts.

## Output Format

```
DISTRIBUTED COGNITION REVIEW

Workflow:
- ...

Knowledge map:
- ...

Gaps/risks:
1. ...

Recommended relocations:
1. ...
```

## Anti-Patterns

- Storing critical process only in memory
- Depending on docs that code can violate
- Duplicating rules in many places
- Making humans reconcile tool disagreements
