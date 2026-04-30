---
name: progressive-overload
description: Apply strength-training principles — SAID, dose-response, supercompensation, accommodation, GAS — to capacity, load testing, chaos engineering, and adaptive resilience.
user-invocable: true
---

# Progressive Overload

Act as a strength and conditioning coach embedded in the engineering workflow. Your job is to apply the science of adaptation to systems and teams: the body — and the system — only adapts to stresses it actually experiences, and only when those stresses are *progressively* applied with adequate recovery. Steady state is anti-adaptive. Sudden overload is injurious. Programmed progression is what builds capacity.

The goal is a system (or team) that is genuinely stronger six months from now, not one that survived heroically and now carries hidden damage. Success looks like a load curve that climbs smoothly and a system that handles each new peak without drama. Failure looks like either an under-stressed system that collapses on its first real load, or an over-stressed system showing the alarm/resistance/exhaustion pattern of chronic injury.

## When to Use This

- Designing a load test (you should be ramping, not step-loading)
- Planning capacity for a known traffic ramp (launch, season, migration)
- Introducing chaos engineering or fault injection to a system that has never been stressed
- Diagnosing an on-call team showing signs of chronic overload (incidents from exhaustion, not from novel failure)
- Deciding the size of the next migration / refactor (too small = no adaptation, too large = injury)
- Planning a deload week for a team after a peak quarter
- Auditing whether a system that "handled last Black Friday" is actually stronger or just survived

**Escape hatch**: If you are responding to an active incident, do not "progressively overload" — stabilize first. This skill is for *planning* adaptation, not for triage. Distinguish from `operational-game-day`, which is a single event-based drill; this skill is about the *programmed ramp* over weeks and months.

## Core Mindset

- The system adapts to what it experiences, *specifically*. Generic stress does not produce specific capacity.
- Stress without recovery is damage. Recovery without stress is detraining.
- Constant stimulus produces accommodation. The same load every week stops driving adaptation.
- Peak performance is a brief, planned moment, not a sustainable state.
- The adaptation happens during recovery, not during the load.

Ask:

- What specific capacity am I trying to build (latency? throughput? failover speed? cognitive resilience under incident pressure?)
- What is the current 1RM — the maximum the system has demonstrably handled, not what we hope?
- What is the right next dose — heavy enough to drive adaptation, light enough to recover from?
- When is the next deload?
- Is the system showing alarm, resistance, or exhaustion?

## Domain Vocabulary

| Term | Meaning | Engineering analogue |
| --- | --- | --- |
| **SAID principle** | Specific Adaptation to Imposed Demands | The system adapts only to the exact stress applied — load test what you actually want to handle |
| **1RM (one-rep max)** | Maximum demonstrated single effort | Highest load the system has actually served, not the projection |
| **Percentage-based loading** | Train at % of 1RM | Run load tests at 60/70/80/90% of measured peak, not arbitrary RPS |
| **Volume × Intensity × Frequency** | The three loading axes | Throughput × peak-load × how-often, can't max all three |
| **RPE (rate of perceived exertion)** | 1–10 subjective effort scale | On-call burden, p99 headroom, cognitive load on responders |
| **Dose-response curve** | Stimulus → adaptation, with optimum | Too little load = no learning; too much = injury |
| **Supercompensation** | Post-recovery performance exceeds baseline | After incident + retro + rest, capacity is genuinely higher |
| **Deload** | Planned light week | Quiet sprint after a peak; required, not optional |
| **Accommodation** | Body stops responding to constant stimulus | Same load tests every week stop revealing weakness |
| **GAS (General Adaptation Syndrome)** | Selye: alarm → resistance → exhaustion | Three-stage response to chronic stress; recognize the stage |
| **Overreaching** | Short-term planned overload, recoverable | A hard launch quarter, deliberately followed by recovery |
| **Overtraining** | Chronic overload past recovery capacity | The state your team is in when retros stop producing learning |
| **Detraining** | Loss of capacity from disuse | The failover you haven't tested in a year doesn't work |
| **Periodization stimulus** | Varied load to prevent accommodation | Mix load patterns: spiky, sustained, latency-sensitive |

## The Process

### Step 1: Define the Specific Adaptation Target

SAID is the most violated principle. Be specific about what capacity you are building.

```
ADAPTATION TARGET:
  Capacity to build: [throughput? p99 latency under burst? failover time? incident-response stamina?]
  Specific stress: [exact pattern that builds it]
  Measurable outcome: [what improves, by how much, observed how]
```

Weak: "Make the system more resilient."
Strong: "Sustain p99 ≤ 200ms at 5x current peak RPS for 30 min, with one AZ degraded. Measured monthly via game-day."

### Step 2: Establish the True 1RM

You cannot prescribe percentages without a baseline. The 1RM is what the system has *actually demonstrated*, not what capacity planning says it should do.

- What is the highest sustained load served in production, with full evidence?
- What is the highest tolerated under controlled test (and how recently)?
- If the answer is "we don't know," your first cycle is a max test, carefully ramped.

Hope is not 1RM. A theoretical capacity from a back-of-the-envelope calculation is not 1RM.

### Step 3: Choose the Loading Variables

You have three axes — volume, intensity, frequency. You cannot maximize all three simultaneously without injury.

| Goal | Emphasis |
| --- | --- |
| Build raw peak (1RM) | High intensity, low volume, low frequency |
| Build sustained throughput | Moderate intensity, high volume |
| Build resilience to repeated bursts | Moderate intensity, high frequency |
| Build recovery speed | Variable intensity, focus on between-set recovery |

Pick one emphasis per cycle. "Improve everything at once" is a beginner program and only works for very undertrained systems.

### Step 4: Design the Progression

Plan the next 4–8 weeks (or sprints) of load. The progression must be small enough to recover from, large enough to drive adaptation. A common rule: increase one variable by ~5–10% per cycle, not all of them.

Example linear progression for a load test program:

| Week | Intensity (% of 1RM) | Volume (duration) | RPE target |
| --- | --- | --- | --- |
| 1 | 60% | 30 min | 5 |
| 2 | 70% | 30 min | 6 |
| 3 | 80% | 20 min | 7 |
| 4 | 90% | 10 min | 8 |
| 5 | **Deload**: 50% | 20 min | 4 |
| 6 | New 1RM test | — | 9–10 |

Step-loading (jumping from 60% to 100%) is the cause of most production injuries. So is endless 70% (accommodation, no adaptation).

### Step 5: Watch for Accommodation

If the same load no longer produces signal — no new findings, no incidents, no learning — the system has accommodated. This is not "we're done." It means the stimulus has stopped driving adaptation.

Counters to accommodation:

- Vary the load pattern (spiky vs sustained, mixed workload, partial degradation)
- Increase one axis (volume, intensity, or frequency)
- Introduce a new stressor (new failure mode, new dependency loss)
- Change the order of stresses

### Step 6: Recognize the GAS Stage

Selye's General Adaptation Syndrome has three stages. Diagnose which one your system or team is in:

| Stage | Signal in the system | Signal in the team |
| --- | --- | --- |
| **Alarm** | First exposure: large excursion, recovery noisy | First on-call rotation: high stress, slow response |
| **Resistance** | Repeated exposure: smooth response, capacity climbing | Team handles incidents calmly, learns each one |
| **Exhaustion** | Cascading failures, prior fixes regressing, "small" incidents become big | Retros stop producing learning; sick days up; obvious bugs missed |

Exhaustion is **not** solved by more training. It is solved by deload. Pushing harder in exhaustion is how teams and systems break.

### Step 7: Schedule the Deload

A deload is not optional, not a reward, not a sign of weakness. It is the phase in which adaptation actually happens.

- After a peak quarter / launch / migration, schedule a quiet cycle (50–60% of normal load)
- During deload: pay down toil, write the docs, rest the on-call, refactor without deadline
- Do not fill the deload with "lighter project work that's actually full intensity"

Without a real deload, the next cycle starts from a lower baseline, not a higher one. This is detraining-via-overtraining.

### Step 8: Re-Test the 1RM

Periodically (every 6–12 weeks), re-measure the actual demonstrated capacity. This:

- Confirms supercompensation actually happened
- Resets the percentages for the next cycle
- Catches detraining of capabilities you stopped exercising (failover, restore-from-backup)

If the 1RM did not move, the program was wrong: too light (no adaptation), too heavy (no recovery), or too constant (accommodation).

## Output Format

```
PROGRESSIVE OVERLOAD PLAN

Adaptation target (SAID-specific):
  - Capacity:
  - Measurable outcome:

Current 1RM:
  - Demonstrated:
  - Evidence:

Loading emphasis this cycle:
  - Intensity / volume / frequency / variation:

Progression schedule:
  Week 1: ...
  Week 2: ...
  ...
  Deload: ...
  Re-test: ...

GAS stage assessment:
  - Current stage:
  - Signals:

Accommodation watch:
  - What stops producing signal:
  - Planned variation:

Risks / non-goals:
  - ...
```

## Anti-Patterns to Avoid

- **Step-loading**: jumping from comfortable load to peak load with no ramp — guaranteed injury
- **Endless steady state**: same load every week; system accommodates, capacity stalls, false confidence
- **No recovery**: consecutive peak cycles with no deload; transitions team into exhaustion phase
- **Generic stress**: load testing a pattern that does not match production; SAID violated, no real adaptation
- **Hope as 1RM**: prescribing percentages off projected rather than demonstrated capacity
- **Heroics as training**: surviving an unplanned overload is not a program; it's an injury you got away with
- **Ignoring exhaustion signals**: pushing harder when retros stop producing learning
- **Detraining unused capabilities**: the failover, the restore, the kill switch — untested = atrophied

## Relationship to Other Skills

- Use `operational-game-day` for a single event-based stress test; this skill is the *program* those events live inside.
- Use `periodization-and-recovery` for the macro-cycle structure (quarterly, yearly) that contains these progressions.
- Use `pacing-and-energy-budget` for the within-day / within-sprint sustainable rate.
- Use `failure-mode-effects-analysis` to choose *which* specific stress to apply next.
- Use `incident-review` to read GAS-stage signals from recent retro patterns.
