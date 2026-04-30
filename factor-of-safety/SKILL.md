---
name: factor-of-safety
description: Designed margin against expected load, applied to capacity, retries, rate limits, and headroom decisions. Use when deciding "how much buffer is enough" for a system that must not fail under realistic peaks.
user-invocable: true
---

# Factor of Safety

Act as a structural engineer reviewing a load-bearing design. Bridges, aircraft, and elevators do not survive because their designers got the load right; they survive because their designers multiplied the worst credible load by a deliberate, documented number — the factor of safety — and built to that. Software systems usually fail not because the load was unforeseeable but because the margin against it was implicit, untested, or vibes-based.

Success looks like an explicit, defensible number per subsystem, traceable to enumerated load cases. Failure looks like "we have plenty of headroom" with no one able to say plenty of what against which load.

## When to Use This

- Sizing capacity, queues, connection pools, thread pools, or rate limits
- Choosing retry budgets, timeout values, or circuit-breaker thresholds
- Reviewing autoscaling minimums and ceilings
- Post-incident analysis where the system "ran out of" something
- Capacity planning before a launch, marketing event, or migration
- Trade-off conversations where someone proposes shrinking a buffer to save cost
- Designing redundancy (N+1, N+2, multi-AZ, multi-region)

**Escape hatch**: If the system has soft, low-cost failure modes (graceful 503, automatic retry from idempotent client, no SLA) and the cost of margin is high, vibes-based sizing may be acceptable. Use this skill where the cost of running out is meaningfully larger than the cost of the margin.

## Core Questions

Ask:

- What is the working load? What is the ultimate (failure) load?
- What is FoS = ultimate / working *right now*?
- Which load cases did we enumerate? Which did we forget?
- Is the FoS appropriate for the consequence of failure?
- Is the margin against the load *type* or against the *measured* load?
- Where is redundancy doing the work, and where is overdesign doing the work?
- What is the cost of the current margin? What would we save by shrinking it?
- How will we know when the margin is being eaten?

## Domain Vocabulary

| Term | Definition | Notes |
| --- | --- | --- |
| **Working stress** (σ_w) | The stress under expected normal load | "Steady-state utilisation" in software |
| **Ultimate strength** (σ_u) | Stress at which the structure fails | "Tip-over point" — saturation, OOM, deadlock |
| **Yield strength** (σ_y) | Stress at which permanent deformation begins | "Degradation point" — latency cliff before outage |
| **Factor of Safety** | FoS = σ_u / σ_w | A ratio ≥ 1; convention varies whether vs ultimate or yield |
| **Margin of Safety** | MoS = FoS − 1 | Expressed as a fraction; MoS = 0.5 means 50% extra |
| **Characteristic load** | A statistically defined load (e.g., 95th percentile expected) | "p95 traffic" |
| **Design load** | Characteristic load × load factor | "p95 × 1.5" |
| **Load factor** (γ_f) | Multiplier applied to load (LRFD / Eurocode style) | Different per load type |
| **Resistance factor** (φ) | Multiplier applied to capacity (LRFD) | φ < 1 reduces nominal capacity |
| **Partial safety factors** | Separate γ_f and φ instead of one global FoS | Modern practice; allows asymmetric treatment |
| **Reliability** | Probabilistic statement: P(load > capacity) < ε | FoS is deterministic; reliability is probabilistic |
| **Redundancy** | Independent backup capacity (N+1) | Distinct from increasing FoS on one path |
| **Overdesign** | FoS above what the rule requires | Cost without explicit benefit |

### Typical FoS values (engineering reference)

| Domain | Typical FoS | Reason |
| --- | --- | --- |
| Aircraft structures | 1.5 | Mass cost is huge; loads are well-characterised; inspected often |
| Pressure vessels | 3.5 – 4 | Catastrophic failure; load well-known |
| Buildings (steel) | 1.67 – 2 | Long life, varied loads, code-mandated |
| Lifting equipment | 4 – 6 | Human consequence, dynamic loads |
| Elevator cables | 8 – 12 | Severe consequence, fatigue, abuse |
| Cheap consumer parts | 1.5 – 2 | Cost-driven; failure tolerated |

The pattern: **higher consequence and worse load knowledge → higher FoS**. The same logic transfers to software subsystems.

## The Process

### Step 1: Enumerate Load Cases

You cannot design a margin against an unenumerated load. Most software capacity incidents are not "we underestimated the load" but "we never wrote that load down at all."

Borrow the structural engineer's checklist and translate:

| Structural | Software analogue |
| --- | --- |
| Dead load (permanent) | Baseline traffic, background jobs |
| Live load (variable, expected) | Diurnal peak, weekly peak |
| Wind load (intermittent, environmental) | Marketing event, viral spike, partner integration burst |
| Seismic load (rare, severe) | Retry storm, thundering herd, dependency outage causing fail-over |
| Impact / dynamic load | Single oversized request, batch import, replay queue drain |
| Snow / accumulation load | Slow leaks: queue backlog, log buildup, growing dataset |

```
LOAD CASES:
1. [Name] — magnitude / units / source of estimate
2. ...
Combined cases (which can occur together):
- ...
Cases excluded by design (and why):
- ...
```

### Step 2: Identify Working and Ultimate Capacity

For each subsystem, name two numbers, not one.

- **Working capacity**: the load at which the system runs sustainably (latency in SLO, error rate < threshold, no resource exhaustion)
- **Ultimate capacity**: the load at which something breaks (OOM, queue saturation, downstream timeout, deadlock)

The gap between them is where the FoS lives. If you only know one, the FoS is undefined.

Weak:

> The DB pool is sized at 100 connections.

Strong:

> The DB pool is sized at 100. Working load is 35 connections at p95 (measured). Ultimate is 100 (hard limit). FoS = 100/35 ≈ 2.85. At 80 connections we begin to see queue wait > 50ms, so yield ≈ 80, FoS_yield ≈ 2.3.

### Step 3: Choose FoS Per Subsystem

Resist the temptation to apply one FoS everywhere. Different subsystems deserve different margins because the consequence and load uncertainty differ.

Decision matrix:

| Consequence of saturation | Load predictability | Recommended FoS (vs working) |
| --- | --- | --- |
| Soft (queue, retry resolves) | High | 1.3 – 1.5 |
| Soft | Low | 2 – 3 |
| Hard (user-visible error) | High | 2 – 3 |
| Hard | Low | 3 – 5 |
| Catastrophic (data loss, cascading outage) | Any | 5+ and add redundancy |

Document the choice. "We chose FoS 3 because retry storms are credible and we have weak data on tail load" is a defensible decision; "it felt right" is not.

### Step 4: Prefer Partial Safety Factors When Loads Are Heterogeneous

A single global FoS treats all load sources symmetrically. Real systems have a small number of well-characterised load sources and a long tail of poorly-characterised ones. The LRFD / Eurocode pattern handles this:

```
Design load = Σ (γ_i × L_i)   where γ_i is the load factor for source i
Design capacity = φ × C_nominal   where φ ≤ 1
Design check: Design load ≤ Design capacity
```

Translation: apply a *larger* multiplier to the load you trust *less*. A burst from an unknown partner integration deserves γ = 2.0; baseline diurnal traffic deserves γ = 1.2.

This avoids the failure mode of "we sized for 3× peak baseline, but the partner doubled their call rate overnight and we had no margin against *that* class."

### Step 5: Distinguish FoS, Redundancy, and Reliability

These are not interchangeable.

| Concept | What it does | Failure mode it does not cover |
| --- | --- | --- |
| **FoS** | Margin between working and ultimate on a single path | Independent failure of the path itself |
| **Redundancy** (N+1, multi-AZ) | Survives loss of one component | Correlated failures across "independent" components |
| **Reliability** | Probabilistic: P(load < capacity) | The tail you did not characterise |

A common error: "we have 3× headroom" (FoS) used as if it answered "what if a region goes down" (redundancy) or "what is our P99 of saturation" (reliability). Each load case needs the right tool.

### Step 6: Cost the Margin

FoS is not free. Mass, money, complexity, and energy all scale with margin. The right FoS is the one where the marginal cost of more margin equals the marginal benefit of avoided failure.

```
MARGIN COST:
- Direct cost (instances, licenses, storage):
- Operational cost (more to monitor, more to deploy, more to upgrade):
- Latency cost (oversized pools can hurt cache locality):
- Cognitive cost (more parts to reason about):
```

Then compare to:

```
FAILURE COST:
- Probability of saturation per year at current FoS:
- Cost of a saturation event (revenue, trust, on-call):
- Expected annual loss = P × cost
```

If margin cost > expected loss, the FoS is too high. If << expected loss, it is too low. This is the same calculation an aircraft designer does between mass and inspection interval.

### Step 7: Instrument the Margin

A margin you cannot observe is a margin you do not have. For each subsystem, expose:

- Current working load (gauge)
- Ultimate capacity (constant or slowly-changing gauge)
- Current FoS (= ultimate / working) (gauge)
- Alert at MoS < threshold (e.g., FoS < 2 → warn, FoS < 1.3 → page)

This converts FoS from a design-time number into an operational signal, and lets you catch margin erosion (load growth, capacity reduction, degraded dependency) before saturation.

### Step 8: Re-derive FoS After Every Significant Change

Margin erodes silently:

- Traffic grows
- A dependency gets slower (working load on connections rises)
- A retry policy changes
- A larger payload becomes common
- A new caller appears

Trigger a re-check on: launch of new dependent system, observed working-load increase > 25%, post-incident, quarterly capacity review.

## Output Format

When using this skill, produce:

```
FACTOR-OF-SAFETY REPORT

Subsystem:
- ...

Load cases enumerated:
1. [Case] — characteristic load — load factor γ — source
2. ...

Capacities:
- Working capacity:
- Yield capacity (degradation onset):
- Ultimate capacity (failure):

Current FoS:
- vs working / ultimate:
- vs working / yield:
- MoS:

Required FoS (with justification):
- Consequence class:
- Load predictability:
- Required FoS:

Gap analysis:
- ...

Recommended action:
- Capacity change / load shed / redundancy added / instrumentation added
- Cost of action:
- Expected reduction in failure probability:

Monitoring:
- Gauges added / alerts set
```

## Anti-Patterns to Avoid

- **Vibes-based headroom**: "we have plenty" without a number against an enumerated load
- **One global FoS**: applying the same multiplier to a well-known and a poorly-known load source
- **Confusing FoS with redundancy**: 3× capacity on one node does not survive that node failing
- **Confusing FoS with reliability**: a 2× FoS may still have a 5% saturation probability if the load distribution has a long tail
- **Margin without instrumentation**: the FoS at design time is not the FoS today
- **Infinite FoS**: oversizing to "be safe" without counting the cost — you would build nothing if cost were zero
- **Margin erosion blindness**: not re-deriving FoS when load or capacity changes
- **Hidden load cases**: the case you did not enumerate is the one that takes you down

## Relationship to Other Skills

- Use `hedging-and-insurance` when the question is about *risk transfer* (paying someone else to absorb the failure) rather than *designed margin* in your own system.
- Use `resilience-engineering` for the broader design philosophy of graceful degradation and recovery; FoS is one specific tool within it.
- Use `feedback-loop-analysis` when the load itself is endogenous (retries, backpressure) — FoS without loop analysis can be overwhelmed by self-amplifying load.
- Use `failure-mode-effects-analysis` to enumerate *what fails when the margin runs out*, which then informs the required FoS.
- Use `tolerance-stack-up` when end-to-end margin must be allocated across many subsystems with their own FoS.
