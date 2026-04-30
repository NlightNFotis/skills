---
name: user-context-fieldwork
description: Investigate user workflows, hidden norms, workarounds, friction, and real operating context.
user-invocable: true
---

# User Context Fieldwork

Act as an anthropologist doing lightweight fieldwork. Understand users in their real context before assuming what they need or why they behave as they do.

## When to Use This

- Designing UX, CLI flows, docs, onboarding, settings, or workflows
- Users behave in unexpected ways
- Support reports lack context
- A product decision depends on real work practices

## Process

1. Identify the user group and real task.
2. Reconstruct the context: environment, constraints, tools, time pressure, incentives, collaboration.
3. Look for workarounds, rituals, local norms, copy-pasted commands, and hidden dependencies.
4. Separate stated preference from observed behavior.
5. Identify friction points and what users are actually optimizing for.
6. Recommend changes that fit the workflow rather than idealized usage.

## Output Format

```
USER CONTEXT FIELDWORK

User/task:
- ...

Context:
- ...

Observed/likely workarounds:
1. ...

Friction:
1. ...

Design implications:
1. ...
```

## Anti-Patterns

- Assuming users read docs before acting
- Treating workarounds as user error
- Designing for ideal conditions only
- Confusing stated needs with actual constraints
