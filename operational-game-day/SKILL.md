---
name: operational-game-day
description: Design controlled drills that test assumptions about failure handling, observability, rollback, and recovery.
user-invocable: true
---

# Operational Game Day

Act as a chaos engineering and operations planner. Your job is to design controlled drills that deliberately exercise the parts of the system — and the team — that are normally only tested by real incidents: failover, alerts, runbooks, on-call ergonomics, permissions, observability, and human handoffs.

A successful game day produces evidence: it either *confirms* the team can detect and recover from a class of failure within a stated objective, or it *exposes* a specific gap (alert that did not fire, runbook that did not exist, permission that was missing, dashboard that lied) that becomes a tracked action item. A failed game day is one with no hypothesis, no stop conditions, no measurement, and no recorded learning — chaos for its own sake.

## When to Use This

- Before launching a new critical system, region, or major feature
- After significant architecture changes affecting failover, scaling, or recovery
- When runbooks have not been exercised in months
- When an incident review surfaced a response gap that needs validation
- When onboarding new on-call engineers
- Periodically (quarterly is common) to fight skill atrophy and test alert decay
- Before high-risk windows (peak season, regulatory deadline) where surprises are unaffordable

**Escape hatch**: Do not run a game day to discover obvious problems already caught by tests, monitoring, or recent incidents. Use this skill when the unknown is *not the failure itself* but *whether the team and system together can handle it*.

## Core Mindset

A game day is an **experiment with a falsifiable hypothesis**, not a stunt. The hypothesis is always of the form *"under failure X, the system continues to satisfy property Y, and the team detects and recovers within time Z."* You learn the most when the hypothesis is **plausibly false** — there is no point chaos-testing something you are certain works.

Ask:

- What is the steady state we are claiming to preserve?
- What failure are we injecting, and how does it model a real-world event?
- What is the smallest blast radius that still tests the hypothesis?
- How will we know to stop?
- Are we measuring detection (people + alerts), or just technical recovery?
- Who is naive (no advance knowledge) and who is informed?
- What evidence are we capturing for the postmortem?

## Vocabulary and Models

| Term | Meaning |
| --- | --- |
| **Game Day** | A planned, scheduled exercise testing a system + team against a defined failure. Often white-box; participants may know the scenario in advance. |
| **Fire Drill** | A short, narrow drill — typically a single alert or runbook step. Often unannounced. |
| **DiRT (Disaster Recovery Testing)** | Google-style large-scale, multi-team drill, sometimes spanning days, testing organizational response. |
| **Chaos Engineering** | Continuous, often automated, fault injection in production or production-like systems to build confidence in steady state. |
| **Steady-state hypothesis** | A measurable property the system normally maintains (latency, error rate, throughput, business metric) that the experiment claims will hold. |
| **Blast radius** | The maximum scope of users, requests, data, or systems the experiment can affect before being aborted. |
| **Kill switch / abort** | The pre-defined mechanism that immediately ends the experiment. Must be tested before the drill begins. |
| **Stop condition** | Pre-committed observable that triggers immediate abort (e.g., real-customer error rate > 0.5%). |
| **Naive responder** | An on-call engineer who is not told the scenario; their response is the data being collected. |
| **Game master / coordinator** | The person running the drill, monitoring real impact, and authorized to abort. |
| **Tabletop** | A discussion-only exercise (no real injection) where the team walks through a scenario verbally — useful when injection is too risky. |

## Chaos Engineering Principles (Netflix-derived)

A game day is not the same as load testing or QA. The principles:

1. **Build a hypothesis around steady-state behavior** — measurable system properties, not internal correctness.
2. **Vary real-world events** — inject failures that actually happen (instance loss, latency, dependency 5xx, region outage), not synthetic ones the system was designed for.
3. **Run experiments in production** — eventually; staging confidence does not transfer fully to production. Start in staging, graduate when blast-radius controls are mature.
4. **Automate experiments to run continuously** — for mature programs; one-off game days are the on-ramp.
5. **Minimize blast radius** — experiments are scientific instruments, not weapons.

## Game Day vs Adjacent Activities

| Activity | Tests | When to use |
| --- | --- | --- |
| **Unit / integration test** | Code correctness | Always |
| **Load test** | Capacity at known load profile | Before launch / capacity changes |
| **Game day** | System + team + tools + runbook under failure | Periodically; before risky windows |
| **Tabletop** | Plan & decision-making only | When injection is too risky or expensive |
| **Continuous chaos** | Steady-state confidence over time | Mature programs with strong blast-radius controls |

## The Process

### Step 1: State the Hypothesis

Write a single, falsifiable sentence.

```
HYPOTHESIS:
  Under [failure scenario],
  the system maintains [steady-state property: metric, threshold, duration],
  and the on-call team detects within [T_detect]
  and recovers within [T_recover].
```

Concrete examples:

- *"Under loss of one of three Kafka brokers, end-to-end event lag stays < 30s, and on-call detects via existing alert within 5min."*
- *"Under 30% increased latency from PaymentSvc, checkout success rate stays > 99.0%, and the dependent-circuit-breaker opens within 60s."*
- *"Under accidental deletion of the primary read-replica, on-call can complete failover using only the runbook in #db-runbooks within 20min."*

### Step 2: Choose the Failure Injection

Match the failure to a real-world event. Common categories:

- **Instance / pod loss**: kill node, drain instance, terminate pod
- **Network**: latency injection, packet loss, partition, DNS failure
- **Dependency degradation**: upstream returns 5xx, slow responses, wrong shape
- **Resource exhaustion**: CPU pinned, disk full, file descriptors exhausted, queue backed up
- **Data**: corrupt message, poison-pill input, replay of historic event
- **Operational**: revoked credential, expired cert, rotated secret, paused cron
- **Human**: on-call paged at 3am with no advance notice; primary on-call unreachable

Prefer the **smallest injection that exercises the hypothesis**. Killing an entire region tests almost nothing if the system already failed at the first node.

### Step 3: Define Blast-Radius Controls and Stop Conditions

Before scheduling, write the abort plan.

```
BLAST RADIUS:
- Environment: staging / staging-with-prod-mirror / one prod cell / full prod
- Scope: requests matching [filter] / single tenant / canary cohort
- Duration: max ___ minutes
- Maximum affected users: N (estimated)

STOP CONDITIONS (any one triggers immediate abort):
- Real-customer error rate > X% for Y minutes
- Any SEV1/SEV2 alert fires unrelated to the experiment
- Game master loses access to the kill switch
- Any participant calls "abort"

KILL SWITCH:
- Mechanism: (feature flag, terraform revert, kubectl patch, etc.)
- Tested at: T-24h dry run
- Time-to-stop: ___ seconds (verified)
```

If the kill switch has never been tested, that is the first game day — test the kill switch.

### Step 4: Define Roles

| Role | Responsibility |
| --- | --- |
| **Game master** | Runs the experiment, holds the kill switch, monitors real impact |
| **Naive responders** | The on-call engineers being tested; do not know the scenario in advance (or know only that *a* drill will happen) |
| **Observers / scribes** | Record the timeline, what was tried, what worked, what was confusing |
| **Safety officer** | Independent of game master; can call abort; watches real-customer signals |
| **Stakeholder comms** | Informs internal channels that a drill is in progress (and again when it ends) |

For high-blast-radius drills, the safety officer must not also be the game master.

### Step 5: Pre-Flight

Run a checklist before the experiment starts:

- [ ] Hypothesis, stop conditions, kill switch, and abort owners written down and shared
- [ ] Kill switch dry-run executed in last 24h
- [ ] Real customer-facing alerts not silenced (silencing them defeats the experiment)
- [ ] Status page / internal comms posted: "drill in progress, real customer impact possible but not expected"
- [ ] All participants have access to the systems and channels they will need
- [ ] Recording / scribing in place
- [ ] Naive responders are actually on duty (not pre-warned by chance)

### Step 6: Run the Experiment

The game master injects the failure and then **stops touching things**. The point is to observe what the team and system do without further intervention.

Capture for each interesting moment:

- Time-of-injection
- Time first alert fires (and which alert)
- Time first responder acknowledges
- Time hypothesis is verified or violated
- Each action a responder takes (what they tried, what they saw)
- Each tool/runbook they consulted (and whether it helped)
- Time of recovery / abort

### Step 7: Capture Findings — Including the Negative Ones

A game day where everything worked is still a finding (and a rare one). More commonly:

- Alert fired late, fired wrong, did not fire
- Runbook was missing, wrong, or out of date
- Responder lacked permission to take the obvious action
- Dashboard showed the wrong picture (sampling, lag, broken query)
- Feature flag did not propagate / cache stayed warm
- Recovery worked technically but communication broke down
- Recovery took longer than the SLO commitment

```
FINDINGS:
1. [Observed behavior] → [Gap identified] → [Severity]
2. ...
```

### Step 8: Convert Findings into Tracked Actions

Each finding becomes an action item with an owner, a date, and a verification — the verification is often *"re-run this game day in N weeks and confirm the gap is closed."*

### Step 9: Decide Cadence and Graduation

If the system + team passed cleanly:

- Increase blast radius or move toward production
- Increase variation (different failure type, different time of day)
- Move toward continuous / automated injection

If gaps were exposed:

- Fix and re-run the same scenario before broadening

## Output Format

```
GAME DAY PLAN — [Scenario]

Hypothesis:
  Under [failure], system maintains [property], detection ≤ [T_d], recovery ≤ [T_r].

Failure injection:
- What:
- Mechanism:
- Smallest viable scope:

Blast radius:
- Environment / scope / duration / max affected users:

Stop conditions:
- ...

Kill switch:
- Mechanism / tested at / time-to-stop:

Roles:
- Game master / safety officer / naive responders / scribe / comms:

Pre-flight checklist:
- [ ] ...

Expected signals:
- Alerts:
- Logs / traces:
- Metrics:
- User-visible behavior:

Schedule:
- T-24h: dry run
- T0:    inject
- T+?:   debrief

Comms plan:
- Pre / during / post:

POST-DRILL FINDINGS

Timeline:
- ...

Hypothesis result: CONFIRMED / FALSIFIED / INCONCLUSIVE

Findings:
1. ...

Action items:
| # | Action | Owner | Due | Verification |
|---|--------|-------|-----|--------------|

Re-run scheduled: yes/no, when
```

## Anti-Patterns to Avoid

- **No hypothesis**: "let's break stuff and see" — produces stories, not learning
- **No stop condition**: an experiment that cannot be aborted is an outage
- **Silencing alerts during the drill**: defeats the test of the detection layer
- **Pre-warning the naive responders**: optimizes for a feel-good drill, not a real one
- **Measuring only technical recovery**: skips the slowest layer (humans, comms, permissions)
- **Game master is also the safety officer**: nobody is watching real impact independently
- **Untested kill switch**: the most dangerous habit — confidence without evidence
- **No follow-up**: drill exposes gap, gap is filed, never closed, next drill exposes the same gap
- **Running in production before staging**: skip the on-ramp at your peril
- **Theater**: drill that everyone knows will succeed because the scenario was chosen for that reason

## Relationship to Other Skills

- Use `failure-mode-effects-analysis` to choose which failure modes deserve a game day (high RPN with untested controls).
- Use `resilience-engineering` to design the degradation and recovery paths the drill exercises.
- Use `preflight-checklist` for the dry-run and execution checklists; use it also to test whether the operational checklist itself is correct.
- Use `signal-detection-review` to evaluate alerts that fired late, fired wrong, or didn't fire.
- Use `incident-review` for the post-drill debrief — a game day finding is essentially a near-miss.
- Use `assumption-audit` before the drill to surface what the team *believes* will happen vs what is enforced.
- Use `code-forensics` if the drill produces unexpected behavior that needs evidence-based reconstruction.
