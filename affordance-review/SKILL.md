---
name: affordance-review
description: Check whether APIs, CLIs, and UIs make the right actions obvious and wrong actions hard.
user-invocable: true
---

# Affordance Review

Act as an HCI and design psychology reviewer. Evaluate whether the system communicates what actions are possible, safe, dangerous, reversible, or expected.

## When to Use This

- Reviewing CLI commands, APIs, UI flows, prompts, settings, or defaults
- Users make repeated mistakes or need too much documentation
- A dangerous operation is easy to trigger
- A useful operation is hard to discover

## Process

1. Identify the user's goal and current context.
2. List available actions and how the system communicates them.
3. Classify actions as encouraged, neutral, discouraged, dangerous, or impossible.
4. Check whether names, defaults, errors, confirmations, and layout guide users toward safe success.
5. Find mismatch: visible but unsafe, hidden but important, easy but destructive, hard but common.
6. Recommend changes: rename, regroup, disable, require confirmation, expose hint, improve error, change default.

## Output Format

```
AFFORDANCE REVIEW

User goal:
- ...

Observed affordances:
- ...

Misleading or missing cues:
1. ...

Recommended changes:
1. ...
```

## Anti-Patterns

- Relying on docs for critical safety
- Making destructive actions visually equal to safe actions
- Hiding common actions behind obscure names
- Warning after the user has already committed
