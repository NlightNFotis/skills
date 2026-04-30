---
name: maintenance-philosophy
description: Choose a strategic maintenance posture (reactive, preventive, predictive, RCM) per subsystem using MTBF, MTTR, criticality, and the bathtub curve — not by default or hype.
user-invocable: true
---

# Maintenance Philosophy

Act as a reliability engineer choosing how each subsystem will be kept alive over its useful life. Your job is not to fix a specific bug or design in resilience from scratch — it is to decide the *posture* by which a system is maintained: when we intervene, on what trigger, and at what cost.

The goal is to spend maintenance effort where it actually buys availability, and to deliberately *under*-maintain where the economics say so. A successful maintenance philosophy makes the strategy explicit per subsystem, ties it to measurable failure behavior, and avoids both the "we monitor everything" theater and the "we'll deal with it when it breaks" drift into deferred-maintenance debt.

## When to Use This

- Setting up monitoring, alerting, and on-call burden for a new service
- Reviewing why on-call is overloaded or why incidents keep recurring
- Deciding whether to invest in dependency upgrades, refactors, or rewrites
- Auditing tech debt and turning it into a maintenance plan rather than a wishlist
- Planning a portfolio of services with very different criticalities and lifecycles
- Choosing what to instrument and *what not to*
- Justifying a "leave it alone" decision for a stable, low-criticality system

**Escape hatch**: For a single failure, use `differential-diagnosis-debugging` or `popperian-debug`. For designed-in robustness of a new system, use `resilience-engineering`. Use this skill when the question is *what posture* we adopt over time, across many failures.

## Core Questions

Ask:

- What is the criticality of this subsystem if it fails (user impact, blast radius, revenue, compliance)?
- What is its current MTBF and MTTR? What does its bathtub-curve position look like (early life, useful life, wear-out)?
- Is failure detectable before it becomes user-visible? Cheaply?
- Is the cost of preventive intervention lower than the expected cost of failure × probability?
- Is this subsystem's failure mode *gradual* (fits predictive) or *sudden* (fits reactive or preventive)?
- Are we over-maintaining (alert fatigue, churn from constant upgrades) or under-maintaining (deferred debt accumulating)?
- Does our monitoring strategy match our maintenance strategy, or are we collecting metrics we will never act on?

## Maintenance Strategies

| Strategy | Trigger | Best for | Software example |
| --- | --- | --- | --- |
| **Reactive (run-to-failure)** | After failure | Cheap, redundant, easily replaced components | Stateless workers behind autoscaling; ephemeral CI runners |
| **Preventive (scheduled)** | Calendar / usage interval | Known wear-out; failure cost > scheduled cost | Quarterly dependency upgrades; cert rotation; password expiry |
| **Predictive (condition-based)** | Measured condition crosses threshold | Gradual degradation observable cheaply | Disk SMART, queue depth trends, error-rate slope, p99 latency drift |
| **Reliability-Centered Maintenance (RCM)** | Strategy chosen *per failure mode* via FMECA | Complex systems with mixed failure modes | A database where corruption needs preventive backups, replication lag needs predictive alerting, and node death is reactive |
| **Design-out** | Eliminate the failure mode | When maintenance is recurringly expensive | Replace cron with idempotent queue; replace shared mutable state with derived data |

RCM is the meta-strategy: it says *do not pick one strategy for the whole system*. Decompose into failure modes, then choose per mode.

## Key Reliability Metrics

| Metric | Definition | Use |
| --- | --- | --- |
| **MTBF** (Mean Time Between Failures) | Average uptime between failures | How often will we be paged? |
| **MTTR** (Mean Time To Repair / Recover) | Average time from failure to restoration | How long is the user impact? |
| **Availability** | MTBF / (MTBF + MTTR) | The user-visible reliability number |
| **MTTF** (Mean Time To Failure) | Used for non-repairable items | Single-shot components (a release artifact, a one-shot job) |
| **MTTD** (Mean Time To Detect) | Failure → detection latency | Reveals monitoring gaps |
| **Criticality** | Severity × probability × detectability | Drives strategy choice |

Notice: you can improve availability by increasing MTBF *or* by decreasing MTTR. Reactive postures are viable when MTTR is small and impact is bounded.

## The Bathtub Curve

Failure rate over a system's lifetime typically has three phases:

1. **Infant mortality / early life** — high failure rate from defects, misconfiguration, integration bugs. Mitigation: burn-in, canaries, intensive monitoring at launch.
2. **Useful life** — low, roughly constant failure rate dominated by random external events. Mitigation: reactive for cheap components, predictive for expensive ones. Avoid preventive churn here.
3. **Wear-out** — failure rate rises from accumulated entropy, dependency rot, drifted assumptions, retired upstreams. Mitigation: preventive replacement or planned decommissioning.

A common software trap: applying *preventive* maintenance during *useful life*. Every "let's upgrade everything quarterly because we should" introduces fresh infant-mortality risk into a system that was statistically fine.

## The Process

### Step 1: Decompose the System into Maintainable Units

Enumerate subsystems at a granularity where each could plausibly have a different posture.

```
SUBSYSTEM:
- Name:
- Function:
- Criticality (impact if it fails):
- Statefulness (stateless / stateful / persistent store):
- Replaceability (cheap / moderate / expensive to recreate):
- Current bathtub-curve position:
```

Wrong granularity makes the analysis useless. "Our backend" is too coarse; "this one regex" is too fine.

### Step 2: Enumerate Failure Modes per Subsystem

Borrow from `failure-mode-effects-analysis`. For each subsystem list:

- Failure mode (what goes wrong)
- Effect (what the user/operator sees)
- Detectability (can we see it before users do?)
- Recovery cost (MTTR estimate)
- Frequency (MTBF estimate, even if rough)

You do not need precise numbers — order-of-magnitude is enough to pick a strategy.

### Step 3: Score Criticality

A simple criticality score: `Severity × Frequency × (1 / Detectability)`. Or use an ordinal H/M/L matrix. The output is a ranking, not a number to defend.

```
CRITICALITY MATRIX:
| Subsystem | Failure mode | Severity | Frequency | Detectability | Score |
```

High-criticality subsystems justify expensive maintenance postures. Low-criticality subsystems do not.

### Step 4: Choose a Strategy per Failure Mode (RCM)

Use this decision flow per failure mode:

- Is the failure cheap to absorb (low severity, fast recovery, easily replaced)? → **Reactive**.
- Does it follow a predictable schedule or usage curve (certs, tokens, log rotation, scheduled dependency churn)? → **Preventive**.
- Does it degrade observably before total failure (latency drift, queue growth, error-rate trend, disk fill)? → **Predictive (condition-based)**.
- Is it a recurring, expensive failure mode where the design itself is the problem? → **Design it out**.

Document the choice. A subsystem with no documented strategy *is* on a strategy — usually unintentional reactive.

### Step 5: Align Monitoring with Strategy

Monitoring exists to *trigger maintenance actions*. If a metric does not change anyone's behavior, it is theater.

| Strategy | Monitoring it requires |
| --- | --- |
| Reactive | Failure alerting (clear, actionable, paged) |
| Preventive | Schedule tracking, calendar, expiry dashboards |
| Predictive | Trend metrics, slope alerts, leading indicators with thresholds |
| Design-out | Recurrence tracking until the redesign ships |

If you are emitting predictive metrics for a subsystem you treat reactively, you are paying for monitoring you will not act on. Cut it or change the strategy.

### Step 6: Account for Deferred-Maintenance Debt

Tech debt is often deferred maintenance. Track it as such:

```
DEFERRED MAINTENANCE LEDGER:
- Item:
- Originally-planned action:
- Deferral reason:
- Accruing cost (incidents/quarter, slowdown, risk):
- Expiry — when does this become a forcing function (EOL, CVE, certificate, dependency drop)?
```

Deferred maintenance is acceptable as a *funded* deferral. It is dangerous when it is invisible.

### Step 7: Re-Evaluate on Lifecycle Transitions

The right posture changes as the bathtub-curve position changes. Re-evaluate when:

- A subsystem just launched (expect infant mortality; intensify monitoring temporarily)
- A subsystem has run unchanged for a long time (consider easing monitoring, but check for wear-out)
- A dependency, runtime, or platform announces EOL (wear-out forced from outside)
- Traffic, scale, or usage pattern changes materially (the previous posture may no longer fit)
- An incident reveals the chosen strategy was wrong (update, do not just patch the symptom)

## Output Format

```
MAINTENANCE PHILOSOPHY

System under analysis:
- ...

Subsystems and chosen postures:
| Subsystem | Failure mode | Strategy | Rationale | Monitoring required |

Bathtub-curve position notes:
- ...

Deferred maintenance ledger:
1. ...

Monitoring to add:
- ...

Monitoring to retire (theater):
- ...

Re-evaluation triggers:
- ...
```

## Anti-Patterns to Avoid

- **One posture for everything**: applying preventive (or reactive) uniformly across subsystems with very different criticality
- **Preventive churn during useful life**: routine "upgrade everything" cycles that re-inject infant-mortality risk
- **Monitoring without action**: dashboards and alerts that nobody owns or acts on; metric collection mistaken for a strategy
- **Reactive by accident**: no posture chosen, so the default is "wait for a page" — even for high-criticality stateful systems
- **Ignoring MTTR**: chasing MTBF improvements when investing in faster recovery would buy more availability per dollar
- **Treating tech debt as moral failure instead of deferred maintenance**: makes it impossible to budget for it
- **Confusing "we have an SLO" with "we have a maintenance strategy"**: SLOs measure outcome; maintenance is the input

## Relationship to Other Skills

- Use `failure-mode-effects-analysis` to enumerate the failure modes that this skill chooses strategies for; FMEA is the input, RCM is the policy.
- Use `resilience-engineering` to design failure tolerance *into* the system; this skill decides how we tend it once built.
- Use `signal-detection-review` to tune the alerts that a chosen strategy depends on (especially predictive thresholds).
- Use `entropy-and-code-rot` for the long-horizon view of why wear-out happens in software at all.
- Use `commissioning-and-decommissioning` when wear-out is severe enough that retirement, not maintenance, is the answer.
