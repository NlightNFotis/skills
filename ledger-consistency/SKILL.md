---
name: ledger-consistency
description: Reconcile state transitions so every acquire/release, enqueue/dequeue, event/source, and resource/owner pair balances.
user-invocable: true
---

# Ledger Consistency

Act as an accountant and auditor for software state. Your job is to treat every important state mutation the way an accountant treats a transaction: every entry has a counterpart, every account has an owner, every running balance has an authoritative source, and the sum of derived views must reconcile with the authoritative ledger or you have a bug.

A successful ledger review finds at least one missing counterpart (acquire without release, enqueue without dequeue, write without ack), one drift (derived view disagrees with source), or one orphan (resource with no owner) — and proposes a reconciliation rule that catches the next instance automatically. A failing review trusts a counter without ever looking at the underlying collection.

## When to Use This

- Bugs involve leaks (handles, connections, goroutines, listeners), duplicates, orphans, or "can't happen" stale state
- Designing or reviewing queues, locks, sessions, file handles, permissions, balances, caches, retries, or lifecycle state
- Designing or reviewing event-driven flows where every event must have a corresponding source / handler / acknowledgement
- Reconciling internal state with an external authoritative system (payments, inventory, user records)
- After incidents where counts disagreed, items appeared twice, or cleanup didn't run
- When introducing retries, replays, idempotency keys, or sagas
- When migrating between two stores and you need to prove they agree

**Escape hatch**: Do not apply this skill to read-only or fully derived data with no mutations and no observable counts. Use it where state mutates over time, especially across boundaries (process, network, persistence, retry).

## Core Mindset: Double-Entry Bookkeeping for Software State

The accounting metaphor is precise: in double-entry bookkeeping, every transaction is recorded twice — once as a debit on one account, once as a credit on another. If the books don't balance, something is wrong, and the *discrepancy itself* tells you where to look.

In software:

- Every **acquire** has a matching **release** (locks, handles, connections, semaphores)
- Every **enqueue** has a matching **dequeue or cancellation**
- Every **emit** has a matching **handle or drop**
- Every **start** has a matching **complete or fail**
- Every **debit** has a matching **credit** (any conserved quantity)
- Every **derived count** matches the underlying **collection's cardinality**

When the books don't balance, do not "just clean up the orphans" — find why the counterpart was never recorded, because that is the bug.

Ask:

- What entities here have a lifecycle (created → … → destroyed)?
- For each, what is the *authoritative* record vs the derived views/indexes?
- For each transition, what is the counterpart that must also be recorded?
- What conserved quantities exist (sum of balances, count of in-flight, total emitted)?
- What does "balance" look like — and how do we detect when it doesn't?
- Where can the chain break: process crash, network partition, partial write, retry, cancellation?

## Vocabulary

| Term | Meaning |
| --- | --- |
| **Authoritative state** | The single source of truth — if everything else were lost, this is what we'd rebuild from |
| **Derived state** | Indexes, counters, caches, materialized views computed from authoritative state |
| **Drift** | When derived state disagrees with authoritative state |
| **Orphan** | Entity with no valid owner (file with no handle, child with no parent, balance with no account) |
| **Leak** | Resource acquired but never released (memory, connection, lock, listener, goroutine) |
| **Duplicate** | Single logical event recorded as multiple entries (often from at-least-once retries) |
| **Idempotency key** | Caller-supplied unique key that lets the receiver detect and collapse duplicate requests |
| **At-least-once delivery** | Receiver may see the same message multiple times — must dedupe or be idempotent |
| **At-most-once delivery** | Receiver may miss messages — must reconcile to detect loss |
| **Exactly-once processing** | The combined effect, even with at-least-once delivery + idempotency on the receiver |
| **Saga** | Multi-step distributed operation with explicit compensating actions per step |
| **Compensating transaction** | The action that semantically undoes a previous step (refund undoes charge) |
| **Reconciliation job** | Periodic sweep that compares authoritative and derived state and repairs drift |
| **Outbox pattern** | Write business state and outbound event to the same DB transaction; a relay publishes the event later, guaranteeing every state change has an event |
| **Two-phase / saga commit** | Mechanisms to coordinate distributed state changes |
| **Eventual consistency** | Replicas / views converge after some time, not synchronously |
| **Strong consistency** | All readers always see the same up-to-date value |
| **Conserved quantity** | A total that should remain constant across allowed transitions (e.g., total balance across accounts in a transfer) |

## The Pairing Catalogue

Every important state mutation belongs to one of these pairs. Walk through this list during review:

| Acquire / Start side | Counterpart | Common bugs when missing |
| --- | --- | --- |
| Lock acquire | Lock release | Deadlock, hung worker |
| Connection / handle open | Close | FD exhaustion, pool starvation |
| `addEventListener` / subscribe | `removeEventListener` / unsubscribe | Memory leak, ghost callbacks after disposal |
| Enqueue | Dequeue or cancel | Unbounded queue, stuck items |
| Emit event | Handle or explicit drop | Lost work, dropped notification |
| Reserve / hold inventory | Release or convert to fulfillment | Phantom out-of-stock |
| Allocate id | Free / mark complete | Id space exhaustion, replay collision |
| Start span / timer | End span | Open spans, broken traces |
| Begin transaction | Commit or rollback | Held row locks, replication lag |
| Charge | Capture or refund | Stranded auth holds |
| Grant permission | Revoke | Stale access |
| Create child | Reparent or destroy | Orphan in tree |
| Schedule callback | Run or cancel | Zombie work after disposal |

For each pair, the question is not just "does the release happen on the happy path?" but: **does it happen on every error, cancellation, panic, restart, and partial-failure path?**

## The Process

### Step 1: Define the Ledger

Pick one entity / lifecycle / conserved quantity. Avoid auditing the whole system at once.

```
LEDGER:
- Entities: (e.g., "in-flight HTTP requests", "pending payments", "open file handles")
- Transitions: (created, mutated, transferred, completed, cancelled, deleted)
- Conserved quantity (if any): (e.g., total balance, count of inflight)
- Authoritative store:
- Derived views (indexes, counters, caches, dashboards):
- Boundary in: (where new entries originate)
- Boundary out: (where entries leave the system)
```

### Step 2: Identify Authoritative vs Derived State

Authoritative state is what you would rebuild from. Derived state is what you would *recompute*. The most common bug class in this skill: **mutating derived state without mutating authoritative state**, or doing them in the wrong order or in non-atomic steps.

Rules:

1. Authoritative state is updated **first**, in a single atomic operation.
2. Derived state is updated **from** authoritative state — ideally by re-deriving, not by parallel mutation.
3. If derived state must be mutated separately (cache, index, search store), there must be a **reconciliation** mechanism that detects drift.
4. Counters that are not derived from a collection are themselves authoritative — and must be transactional with whatever they count.

### Step 3: Walk Every Transition and Name the Counterpart

For each transition in the lifecycle, write the counterpart and the failure paths.

```
TRANSITION: openConnection(host)
- Counterpart: closeConnection(conn)
- Where called: ConnectionPool.borrow / ConnectionPool.return
- Failure paths:
  - request throws after open, before return → defer/finally release? ✓/✗
  - request cancelled → cancellation tears down? ✓/✗
  - process killed mid-request → server-side timeout reclaims? ✓/✗
  - return called twice → double-release detected? ✓/✗
```

A transition with any unanswered failure path is a candidate bug.

### Step 4: Check for the Five Defects

Walk the ledger looking for each defect class:

| Defect | Detection question |
| --- | --- |
| **Orphans** | Are there entities with no valid owner / parent / pair? |
| **Leaks** | Are there acquire-side records with no release-side record (after expected lifetime)? |
| **Duplicates** | Could the same logical event create multiple records? Are idempotency keys applied? |
| **Drift** | Does the derived count match the underlying collection? Do the cache values match the source? |
| **Negative / impossible** | Could a counter go negative, a balance underflow, a state machine reach an undefined state? |

For each, write the SQL / code / log query that *would detect* the defect today. If you can't write it, the system is unobservable on this dimension and that itself is finding #1.

### Step 5: Idempotency and Retry Discipline

If anything in the system can retry — clients, queues, schedulers — every state-mutating operation must be **idempotent at the boundary**, typically via:

- An **idempotency key** carried by the request, persisted at the receiver
- A **deduplication window** at the consumer (kafka group offsets + transactional sink, dedup table with TTL)
- An **outbox** to bind state mutation and event emission in one transaction
- A **state-machine guard** that rejects re-application from the same source state

Anti-pattern to flag: "we use at-least-once delivery and the handler is idempotent" — but the handler is idempotent because it does an UPSERT, while also incrementing a counter on every call.

### Step 6: Cross-Boundary Reconciliation

When state lives in two places (your DB and Stripe; your DB and the search index; primary and replica), define the reconciliation explicitly:

```
RECONCILIATION:
- Source A (authoritative):
- Source B (replica/derived):
- Pairing key:
- Cadence: (continuous CDC / hourly / daily / on-demand)
- Drift action: (auto-repair / alert / human review)
- Drift floor / alert threshold:
- Last known agreement:
```

Without this, "they agree most of the time" decays silently.

### Step 7: Design Cleanup for Failure Paths

Every state machine must remain consistent under:

- Process crash mid-transition
- Network partition between pair sides
- Partial write (some derived views updated, others not)
- Operator intervention (force-kill, manual edit)
- Replay of a historic event
- Out-of-order arrival

For each, name the recovery: timeout-based reclaim, server-side TTL, replay-safe handler, compensating transaction, manual runbook.

A good test: *"if the process crashes between any two lines of this handler, is the system still in a consistent state, even if not the intended state?"* If no, refactor until yes — typically by collapsing the work to a single atomic write plus an outbox event.

### Step 8: Express the Ledger Rules as Invariants

The most valuable output of this review is a small set of **runtime-checkable invariants** that catch future bugs:

- *"For every row in `pending_charges`, either a `captures` row exists with the same idempotency key, or `pending_charges.expires_at > now() − 24h`."*
- *"`pool.in_use_count == len(pool.in_use_set)`."*
- *"For every `subscribe(listener)` call there is exactly one `unsubscribe(listener)` call before the parent component is disposed."*
- *"Sum of all `account.balance` across accounts is constant during a transfer (no money created or destroyed mid-flight)."*

Place each as either an assertion at the right boundary or a periodic reconciliation job.

## Output Format

```
LEDGER CONSISTENCY REVIEW — [Entity / lifecycle]

Ledger definition:
- Entities:
- Authoritative store:
- Derived views:
- Conserved quantity:

Transitions and counterparts:
| Transition | Counterpart | Failure paths covered? |
|------------|-------------|------------------------|

Defects found:
- Orphans: ...
- Leaks: ...
- Duplicates: ...
- Drift: ...
- Negative/impossible: ...

Idempotency assessment:
- Boundary: ...
- Mechanism: ...
- Gaps: ...

Cross-boundary reconciliation:
- Source A vs B:
- Cadence:
- Drift action:

Invariants to enforce:
1. [Precise statement] — where checked: [assertion / job / test]

Recommended actions:
1. ...

Open questions:
- ...
```

## Anti-Patterns to Avoid

- **Trusting counters without reconciling collections**: an authoritative counter that drifts is worse than no counter
- **Updating derived state directly**: bypasses the source of truth and guarantees drift
- **Cleanup only on the happy path**: most ledger bugs hide in error / cancellation / restart paths
- **At-least-once delivery + non-idempotent handler**: silently doubles state on retry
- **Dual writes without outbox**: writing to DB and emitting an event as separate steps; one will eventually fail
- **Allowing unowned resources**: anything created should have a clear destroy / GC / TTL path
- **"Eventually consistent" as a synonym for "we never check"**: eventual consistency requires *reconciliation*
- **Compensating transactions that aren't actually compensating**: refund is not always the inverse of charge (timing, fees, partial)
- **Not distinguishing logical vs physical operations**: one logical "transfer" is two physical mutations; both must be in one atomic unit or there must be a saga
- **Reconciliation jobs without alerts**: a job that finds drift and prints to a log nobody reads

## Relationship to Other Skills

- Use `formal-invariants` to express the ledger rules precisely and choose where to assert them.
- Use `assumption-audit` to surface beliefs about delivery semantics, atomicity, ordering, and idempotency.
- Use `code-forensics` when a current discrepancy needs to be reconstructed from logs, audit trails, and event history.
- Use `popperian-debug` when "the books don't balance" is the symptom and the cause is unknown — the discrepancy itself is the falsifiable evidence.
- Use `resilience-engineering` for the cleanup-on-failure paths (timeouts, dead-letter queues, compensating transactions).
- Use `failure-mode-effects-analysis` to score the severity of each detected drift class.
- Use `signal-detection-review` to tune drift-detection alerts so they fire on real divergence and not on transient lag.
- Use `incident-review` to feed historical "duplicate / lost / orphan" incidents back into the pairing catalogue for the affected system.
