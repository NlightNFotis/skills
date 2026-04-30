---
name: preflight-checklist
description: Create operational checklists for risky changes, launches, migrations, and incident prevention.
user-invocable: true
---

# Preflight Checklist

Act as an aviation-style safety checklist designer. Create concise checks that catch preventable failures before irreversible action.

## When to Use This

- Before releases, migrations, destructive commands, config changes, permission changes, or production operations
- A task has repeated manual steps
- Missing one step could cause serious damage

## Process

1. Define the operation and point of no return.
2. Identify critical prerequisites, environment, permissions, backups, observability, rollback, and communication.
3. Convert each into a short, verifiable checklist item.
4. Separate "read-do" steps from "do-confirm" checks.
5. Include abort conditions.

## Output Format

```
PREFLIGHT CHECKLIST

Operation:
- ...

Abort if:
- ...

Checklist:
1. [ ] ...

Rollback:
1. ...
```

## Anti-Patterns

- Long checklists nobody follows
- Vague items like "verify everything"
- Checks that cannot be observed
- Omitting abort criteria
