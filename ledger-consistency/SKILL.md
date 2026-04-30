---
name: ledger-consistency
description: Reconcile state transitions so every acquire/release, enqueue/dequeue, event/source, and resource/owner pair balances.
user-invocable: true
---

# Ledger Consistency

Act as an accountant and auditor for software state. Every important state mutation should have a corresponding entry, owner, transition, reversal, or reconciliation rule.

## When to Use This

- Queues, resources, sessions, events, locks, files, handles, permissions, balances, counters, caches, or lifecycle state
- Bugs involve leaks, duplicates, orphaned state, missing cleanup, or mismatched counts
- You need to reconcile expected and actual state

## Process

1. Define the ledger: what entities, balances, or transitions must reconcile?
2. Identify authoritative records vs derived views.
3. List creation, mutation, transfer, cancellation, completion, and deletion events.
4. Check pairings: acquire/release, enqueue/dequeue, create/delete, start/stop, grant/revoke, emit/handle.
5. Find orphaned, duplicated, negative, stale, or unowned entries.
6. Recommend reconciliation checks, invariant assertions, tests, or cleanup paths.

## Output Format

```
LEDGER CONSISTENCY REVIEW

Ledger:
- ...

Authoritative source:
- ...

Expected pairings:
1. ...

Mismatches:
1. ...

Recommended checks:
1. ...
```

## Anti-Patterns

- Trusting counters without reconciling collections
- Updating derived state without authoritative state
- Missing cleanup on failure/cancellation
- Allowing unowned resources
