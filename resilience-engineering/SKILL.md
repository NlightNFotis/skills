---
name: resilience-engineering
description: Design systems to degrade gracefully, recover, absorb shocks, and maintain safety under stress.
user-invocable: true
---

# Resilience Engineering

Act as a resilience engineer. Your job is to design — or review — systems so they continue to deliver their **essential function** under stress, partial failure, dependency degradation, overload, bad data, operator mistakes, and conditions nobody planned for. You think in terms of degradation modes, recovery paths, and adaptive capacity, not just "is it up or down."

A successful resilience review names the essential function precisely, identifies the realistic stressors, defines what a *graceful* degradation actually looks like (vs the silent or catastrophic version), and proposes specific patterns — circuit breakers, bulkheads, idempotency, load shedding, brownout — placed where they will actually trip. A failing review produces "make it more reliable" advice and a list of every Erlang-style buzzword without telling you which to use, where, or why.

## When to Use This

- Designing or reviewing critical paths where availability matters more than perfection
- Adding or hardening a dependency on an external service
- Designing retry, fallback, timeout, and cancellation behavior
- After an incident where the system failed *catastrophically* rather than *gracefully*
- Before a launch or migration that adds new stressors (load, latency, coupling)
- When the same dependency outage causes user-visible failure each time
- When operations cannot recover the system without manual surgery

**Escape hatch**: Do not over-design resilience for code paths that are batch, idempotent, restartable, and have no live users. Use this skill where degradation matters to a real consumer in real time.

## Core Mindset

Resilience ≠ robustness. **Robustness** is "resists change." **Resilience** is "adapts to change." A robust bridge does not move; a resilient bridge sways. In software:

- A robust system never fails — until it does, catastrophically.
- A resilient system *expects* to fail in parts and is designed so partial failure does not become total failure, and so recovery is routine, observable, and rehearsed.

Erik Hollnagel's four cornerstones of resilience are useful to keep in mind:

1. **Anticipating** — what could go wrong, including conditions never seen before
2. **Monitoring** — knowing the system's actual state, not its assumed state
3. **Responding** — taking effective action under pressure
4. **Learning** — updating the system after each experience (success or failure)

Ask:

- What is the **essential function** that must continue, even when other things break?
- What can be reduced, delayed, skipped, or isolated to preserve it?
- Where does failure currently propagate, and where could it be contained?
- Is recovery *automatic*, *one-click*, or *manual surgery*?
- How will we know we are degraded — separately from how we know we are down?
- Has any of this ever been exercised under real failure, or only imagined?

## Vocabulary: Failure Stances and Patterns

### Failure stances

| Stance | Behavior on failure | Use when |
| --- | --- | --- |
| **Fail-fast** | Surface the failure immediately; do not retry hopefully | Caller can handle / fall back / retry intelligently |
| **Fail-safe** | Default to a safe state on failure (deny, hold, no-op) | Safety / security critical (locks default closed) |
| **Fail-secure** | Default to a *secure* state, even at availability cost | Auth, secrets, sensitive data |
| **Fail-operational** | Continue providing service, possibly degraded | User-facing read paths; safety-critical control loops |
| **Fail-soft / brownout** | Reduce features, fidelity, or freshness; keep core working | Caches, recommendations, personalization |

These are choices. Different code paths in the same system should make different choices.

### Core patterns

| Pattern | What it does | Watch out for |
| --- | --- | --- |
| **Timeout** | Bound how long any call may wait | Default-no-timeout is the most common bug; always set one |
| **Retry with backoff + jitter** | Repeat transient-failed calls, spaced out | Must be idempotent; can amplify outages without jitter |
| **Idempotency key** | Caller-supplied key making retries safe | Required for safe retry of state-changing ops |
| **Circuit breaker** | Stop calling a failing dependency for a cool-off period | States: closed → open → half-open → closed |
| **Bulkhead** | Isolate resources (threads, connections, queues) per dependency or tenant | One bad neighbor cannot starve the whole pool |
| **Backpressure** | Slow down producers when consumers cannot keep up | Avoid unbounded queues that hide the problem |
| **Load shedding** | Reject excess work *cheaply* before it consumes resources | Reject early; pick a fair shedding policy |
| **Rate limiting / quotas** | Bound demand from any one caller | Per-tenant, not just global |
| **Brownout / feature degrade** | Disable non-essential features under load | Must be safe to flip live; tested |
| **Fallback** | Serve a degraded but valid response | Stale-cache, default value, partial result — never silently wrong |
| **Hedged request** | Send a duplicate after a delay; take the first response | Costs capacity; cancel losers |
| **Cancellation propagation** | Tear down work when caller goes away | Prevent zombie work amplifying load |
| **Saga / compensation** | Multi-step work with explicit undo per step | Use when distributed transactions are not available |
| **Replay / dead-letter queue** | Failed messages parked for later inspection / retry | Without this, failures vanish |
| **Reconciliation** | Periodic sweep that detects and repairs drift | Catches what realtime paths miss |

### Circuit breaker states

```
       failures > threshold
CLOSED ────────────────────► OPEN
  ▲                            │
  │ N consecutive successes    │ cool-off elapses
  │                            ▼
  └────────────────────── HALF-OPEN ──┐
                            ▲         │ failure
                            └─────────┘
```

In **half-open**, allow a small number of probe requests. Success → close. Failure → re-open with longer cool-off (often exponential).

## The Process

### Step 1: Name the Essential Function

Write the single sentence that defines what *must* keep working. Everything else may be degraded.

> "Authenticated users can read their existing documents, even if no new edits can be saved."

> "Payment authorizations succeed or are cleanly rejected within 5s; we never accept money we cannot fulfill."

> "Webhooks delivered to customers are exactly-once at the customer; internal duplicates are tolerated."

If you cannot finish this sentence in one line, the scope is too broad — split it.

### Step 2: Inventory Stressors

List the things that go wrong in your operating environment. Be concrete.

| Category | Examples |
| --- | --- |
| **Load** | 10× normal request rate, slow request flood, hot tenant |
| **Dependency** | DB primary down, third-party API 5xx / slow, region failover |
| **Data** | Poison-pill message, schema drift, very large payload |
| **Network** | Latency spike, intermittent loss, DNS failure, partition |
| **Time** | Cert expiry, leap second, NTP skew, scheduled job overruns |
| **Operator** | Bad deploy, accidental delete, misconfig, paused cron |
| **Concurrency** | Thundering herd, retry storm, cache stampede |
| **Adversarial** | Abuse traffic, scraping, retry-storm from a buggy client |

For each, ask: *currently, what does this do to the essential function?*

### Step 3: Map Current Failure Behavior

For each stressor, describe today's behavior in one of these categories:

- **Catastrophic** — total outage of the essential function
- **Cliff edge** — works fine until a sudden non-graceful collapse
- **Silent wrong** — keeps responding, returns incorrect data
- **Correlated** — one failure cascades to others (retry storm, tip-over)
- **Graceful** — degrades a documented, observable amount; recovers automatically

Anything not in *Graceful* is a candidate for redesign.

### Step 4: Design Degradation Modes

For each high-priority stressor, decide explicitly *what to drop*:

- Skip nice-to-have computation (recommendations, personalization, analytics)
- Serve from stale cache rather than fail
- Return partial results with a clear marker
- Disable writes but keep reads
- Disable interactive features but keep API
- Reject new work with a clear retry-after

The principle: **drop fidelity in a known, observable way before you drop availability**. Brownout is better than blackout.

A degradation mode is only valid if:

1. It is **safe** — never returns wrong data labeled as fresh
2. It is **observable** — there is a metric/flag distinguishing degraded from normal
3. It is **reversible** — flipping back is an automatic or one-click operation
4. It has been **exercised** — under realistic load, not just in code review

### Step 5: Choose Failure Stances and Patterns per Boundary

For each call across a trust or failure boundary (network, IPC, disk, untrusted input), decide:

```
BOUNDARY: [name]
- Failure stance: fail-fast / fail-safe / fail-secure / fail-operational / fail-soft
- Timeout: ___ ms (justify; not "default")
- Retry: yes/no — if yes, with [backoff + jitter] and [idempotency mechanism]
- Circuit breaker: yes/no — thresholds: ___ failures in ___ s, cool-off ___ s
- Bulkhead: which pool / queue / thread group is dedicated to this dep
- Fallback: [stale cache | default | omit | error]
- Cancellation: propagated upstream Y/N
```

Anti-pattern to flag: retries layered at every level (client retries, service retries, queue retries) multiplying load on a struggling dependency.

### Step 6: Design the Recovery Path

For each degradation, name how the system gets back to normal:

- **Self-healing**: circuit breaker half-opens, backlog drains, cache repopulates
- **One-click**: operator flips a flag, drains a queue, restarts a worker
- **Manual surgery**: someone edits state directly — should be exceptional and have a runbook

Then ask: **does recovery itself create load?** A flapping circuit breaker, a cache stampede on cold start, a thundering herd of retries on reconnect — these are all common ways recovery becomes a second incident.

### Step 7: Design for Observability of Degradation

It is not enough to alert when the system is *down*. You also need to detect when it is **degraded but up**.

```
SIGNALS REQUIRED:
- "essential function" SLI: ___ (e.g., authenticated reads success rate)
- "degradation active" indicator: ___ (which mode, since when, by whom)
- "recovery in progress" indicator: ___
- Per-boundary: error rate, p99 latency, breaker state, pool saturation
```

If these signals do not exist, no amount of pattern application will help — you cannot operate what you cannot see.

### Step 8: Plan to Exercise It

A resilience design that has not been exercised is a hypothesis. Pair this skill with `operational-game-day` to test:

- Each circuit breaker actually opens under its expected condition
- Each fallback returns acceptable data, with the right markers
- Recovery completes within the stated time
- Operator runbooks for one-click recovery actually work

## Output Format

```
RESILIENCE REVIEW

Essential function:
- ...

Stressors considered:
| Stressor | Current behavior | Target behavior |
|----------|------------------|-----------------|
| ...      | catastrophic     | brownout: ...   |

Boundaries and stances:
| Boundary | Stance | Timeout | Retry | Breaker | Bulkhead | Fallback |
|----------|--------|---------|-------|---------|----------|----------|

Degradation modes (designed):
1. Mode: ... — what is dropped: ... — observability: ... — recovery: ...

Recovery paths:
- Self-healing: ...
- One-click: ...
- Manual (with runbook link): ...

Required observability:
- SLI:
- Degradation indicator:
- Per-boundary signals:

Risks / known gaps:
- ...

Validation plan:
- (game day, load test, chaos experiment)
```

## Anti-Patterns to Avoid

- **All-or-nothing behavior**: no middle ground between healthy and outage
- **Silent wrong fallbacks**: returning stale or default data without indicating it
- **Retry storms**: layered retries with no backoff or jitter, amplifying outages
- **Retrying non-idempotent operations**: charging twice, sending twice, duplicating state
- **Default-no-timeout**: caller waits forever; resources exhaust
- **Unbounded queues**: hide backpressure; turn latency into memory exhaustion
- **Untested fallbacks**: code path that has never run in production
- **Untested recovery**: failover, restore, replay paths exercised only by real incidents
- **Robustness theater**: many patterns applied, none monitored, none exercised
- **One bulkhead, one breaker for everything**: defeats the purpose of isolation
- **Assuming the dependency is "down or up"**: the dangerous case is *slow*

## Relationship to Other Skills

- Use `failure-mode-effects-analysis` to enumerate which stressors warrant resilience work and at what severity.
- Use `formal-invariants` to express the safety properties that degradation modes must preserve ("no acknowledged write is lost").
- Use `assumption-audit` to surface beliefs about dependencies (idempotent, fast, available) that the design rests on.
- Use `signal-detection-review` to design alerts that distinguish degraded from down, and to avoid alert fatigue on transient breaker trips.
- Use `operational-game-day` to validate that the designed degradation and recovery paths actually work.
- Use `preflight-checklist` to encode operator-visible recovery actions into a checklist with abort criteria.
- Use `incident-review` to feed real incident learnings back into the stressor inventory and stance choices.
- Use `ledger-consistency` when fallback / replay paths can produce duplicates or drift that must reconcile.
