---
name: pacing-and-energy-budget
description: Apply endurance pacing — lactate threshold, glycogen budget, negative split, fueling — to sustainable engineering rate, sprint cadence, and avoiding mid-quarter exhaustion.
user-invocable: true
---

# Pacing and Energy Budget

Act as an endurance coach embedded in the engineering workflow. Your job is to model effort over hours, days, and weeks the way a marathon coach models effort over a race: with a finite energy budget, a sustainable threshold above which damage accumulates faster than recovery, and an asymmetric cost between maintaining pace and recovering from over-pacing.

The goal is a team or individual that finishes the cycle stronger than the middle, not one that explodes at mile 20. Success looks like a negative-split project — slow start, accelerating finish — and a team that still has capacity in the final week. Failure looks like the classic pace-bomb: hot start, mid-quarter exhaustion, missed deadline, recovery that costs more than the gains.

## When to Use This

- Setting the rate for a multi-week project (not the destination — the rate)
- Diagnosing a team that started fast and is now stalling mid-cycle
- Estimating sustainable on-call burden
- Designing a sprint cadence where every sprint is described as "a sprint" but they're really a marathon
- Deciding whether to accept a heroic short-term ask (and what its energy cost will be over the next month)
- Auditing whether you are above or below your lactate threshold right now
- Coaching a new lead who is pace-bombing their first quarter

**Escape hatch**: For a single discrete event with a hard deadline (a launch week, an incident response), use sprint pace and accept the cost. This skill is for the *sustained rate over weeks*, not the moment of peak effort. Distinguish from `capital-allocation`, which is about *where* to spend; this skill is about *how fast*.

## Core Mindset

- You have a finite energy budget. You spend it whether you notice or not.
- There is a threshold above which lactate (fatigue, technical debt, cognitive load) accumulates faster than you clear it. Below it, you can sustain almost indefinitely. Above it, you have minutes to hours, not weeks.
- The cost of recovering from over-pacing is greater than the gain from over-pacing. The asymmetry is the whole point.
- Pace by feel only after you know your numbers. Beginners pace by enthusiasm and blow up.
- Negative split — start slower than you can, accelerate as confidence grows — beats positive split in almost every domain.

Ask:

- What is my (or my team's) lactate threshold pace — the pace I can hold all day without accumulating fatigue?
- Am I currently above or below it?
- How much glycogen is left — how many hard pushes do I have before depletion?
- What is the fueling strategy — when and how do I replenish?
- Am I pace-bombing, or am I running a planned negative split?

## Domain Vocabulary

| Term | Meaning | Engineering analogue |
| --- | --- | --- |
| **Aerobic system** | Sustainable, oxygen-fueled, fat-burning | Steady focused work; can sustain for hours/days |
| **Anaerobic system** | High-power, glycogen-burning, time-limited | Heroic pushes, all-nighters; minutes to hours of capacity |
| **Lactate threshold (LT)** | Pace above which lactate accumulates faster than clearance | Effort level above which fatigue compounds — debt, errors, missed signals |
| **VO2max** | Maximum aerobic capacity | Theoretical ceiling of sustainable throughput |
| **Glycogen depletion** | Running out of stored carbohydrate fuel | "Hitting the wall" — sudden cognitive collapse, decision fatigue |
| **Fueling strategy** | When and what to consume during effort | Breaks, sleep, food, social recovery during a long push |
| **Sprint pace vs marathon pace** | Anaerobic vs aerobic effort | Launch week pace vs Tuesday in week 6 pace |
| **Negative split** | Second half faster than first | Project that accelerates as it matures |
| **Positive split / pace-bombing** | Hot start, slower finish | Started strong, fizzled — most common failure mode |
| **Conservation of energy** | Fuel spent here is not available there | Heroics on Project A reduce capacity on Projects B–E |
| **Cost of accelerations** | Surges burn disproportionately more fuel than steady pace | Context switches, scope changes burn more energy than the work itself |
| **Galloway run-walk** | Planned walk breaks extend total distance | Planned breaks (Pomodoro, no-meeting Fridays) extend sustainable output |
| **Fartlek** | "Speed play" — variable pace by feel | Mixed-intensity weeks; alternating deep work and recovery |
| **Bonk / wall** | Sudden depletion event | Mid-quarter morale collapse, attrition spike |

## The Process

### Step 1: Identify the Distance

Pacing is meaningless without knowing the distance. Name the time horizon explicitly.

```
EFFORT:
  Distance: [days / weeks / quarters]
  Hard deadline: [date / none]
  Acceptable arrival state: [fresh enough for next cycle? cooked is OK? somewhere between?]
```

A 5K and a marathon both look like "running." The pacing strategies are opposite. Most engineering "sprints" are actually multi-week efforts being paced like 5Ks — which is the source of mid-cycle collapse.

### Step 2: Estimate Lactate Threshold Pace

LT is the pace you can hold all day. Above it, you have a clock. Find it for yourself or your team:

- What sustained workload have you held for *6+ weeks* without rising incident rate, attrition signals, or quality drop?
- That is at-or-below threshold.
- What workload did you hold for 1–2 weeks before things started slipping? That is above threshold.
- The threshold is between them.

Weak: "We're working hard."
Strong: "Sustainable pace = 1 major and 1 minor feature per sprint, with on-call ≤ 8 pages/week. Above that we accumulate debt faster than we pay it down — observed last in Q2."

### Step 3: Identify Current Pace Relative to Threshold

Ask honestly: are we currently above or below LT?

Above-threshold signals (in engineers, the "lactate" is decision fatigue, error rate, debt accumulation):

- Bug rate climbing
- PRs taking longer to review
- Meeting attendance dropping
- Small decisions feeling hard
- Code review comments getting terser or absent
- "We'll fix it later" frequency rising
- Tests being skipped to ship

Below-threshold signals:

- Capacity to take an unplanned ask without dropping committed work
- Retros producing new ideas, not the same complaints
- People leaving on time, sick days low

If you are above LT, you have a finite clock. Estimate it (days? weeks?) and plan the recovery before depletion forces it.

### Step 4: Plan the Pacing Strategy

Choose one consciously. The default of "go as hard as we can" is pace-bombing.

| Strategy | When | How |
| --- | --- | --- |
| **Even split** | Predictable, well-scoped work | Hold steady at ~95% of LT throughout |
| **Negative split** | High uncertainty early, clarity later | Start at 80% of LT, accelerate as scope solidifies |
| **Positive split** | Front-loaded deadline, fixed end | Start at 105% of LT, accept the fade — only if total distance is short |
| **Fartlek** | Mixed work, varying readiness | Vary by week: deep weeks alternating with recovery weeks |
| **Galloway run-walk** | Long distance, want to extend reach | Build planned walk breaks (no-meeting days, Friday recovery) into the cadence |

For most multi-week engineering work, the right answer is **negative split**: start deliberately slower than you feel you can. The first week's "extra" capacity goes into clarifying scope, building shared understanding, and removing risks — which makes the later weeks faster. Pace-bombers skip this and pay 2–3x in mid-cycle scope churn.

### Step 5: Design the Fueling Strategy

You cannot run on empty. Plan when and how energy gets replenished during the effort, not after.

| Fuel type | Source | Cadence |
| --- | --- | --- |
| Cognitive recovery | Deep work blocks, no-meeting days | Daily or weekly |
| Social recovery | 1:1s, team rituals, collaboration | Weekly |
| Physical recovery | Sleep, weekends actually off | Daily / weekly |
| Morale fuel | Visible progress, shipped wins, recognition | Weekly to monthly |
| Strategic fuel | Re-grounding in purpose, retro, replanning | Per sprint |

Fueling is not a reward for finishing; it is what enables finishing. Skipping it to "save time" is the runner skipping the aid station — saves 30 seconds, costs the race.

### Step 6: Watch for the Wall (Glycogen Depletion)

The wall is sudden, not gradual. Symptoms appear hours or days before the collapse but are easy to miss because the effort feels possible up to the moment it isn't.

Pre-wall signals at team scale:

- Difficulty making small decisions (decision fatigue)
- Quality of code review degrading sharply
- Sick days clustering
- Retro topics narrowing to grievances
- A senior person quietly disengaging
- Increased "this is fine" responses to things that are not fine

Once the wall hits, recovery costs 2–4x what it would have cost to throttle back earlier. The asymmetry is the rule, not the exception.

### Step 7: Manage the Cost of Accelerations

Surges cost disproportionate fuel. Two surges of effort cost more than the same total effort spread evenly. In engineering terms:

- Context switches between projects burn more than the work itself
- Mid-sprint scope changes cost more than equivalent work scoped at the start
- "Quick" interrupts have a long tail of recovery
- Re-orgs and re-prioritizations are accelerations; price them in

Strategy: **defend against unplanned accelerations**. Each interrupt accepted is fuel taken from the planned distance. Sometimes it's worth it — but always price it.

### Step 8: Plan the Negative Split

If you have any choice in pacing, choose negative split:

1. Week 1: 70–80% of LT. Use slack for scope clarification, risk reduction, foundations.
2. Mid-cycle: 90–95% of LT. Confidence has grown; momentum is real.
3. Final third: at LT. The work is well-understood, the team is grooved, the acceleration is *sustainable* because it was built on a slower base.

The pace-bomb pattern is the inverse: 110% week 1 (hero phase), 90% mid-cycle (drag), 60% final week (collapse). Same total effort, much worse outcome.

## Output Format

```
PACING PLAN

Distance:
  - Time horizon:
  - Hard deadline:
  - Target arrival state:

Lactate threshold (estimated):
  - Sustainable pace:
  - Evidence:

Current pace vs LT:
  - Above / below / at threshold:
  - Signals:
  - Estimated time-to-wall (if above):

Pacing strategy chosen:
  - Even / negative / positive / fartlek / run-walk — rationale:

Fueling strategy:
  - Cognitive:
  - Social:
  - Morale:
  - Cadence:

Acceleration defense:
  - Interrupts to refuse / price:
  - Scope change policy:

Wall watch (signals + threshold for intervention):
  - ...

Risks / non-goals:
  - ...
```

## Anti-Patterns to Avoid

- **Pace-bombing**: hero start, mid-cycle drag, final-week collapse — the most common failure mode
- **Treating every week as a sprint**: anaerobic pace applied to an aerobic distance — guaranteed wall
- **Skipping the aid station**: cutting recovery rituals "to save time" — costs the race
- **Ignoring lactate-threshold signals**: bug rate climbing, decisions getting hard — treating these as "push through" rather than "throttle back"
- **Unpriced accelerations**: every interrupt, every scope change, every re-org costs fuel; pretending otherwise empties the tank invisibly
- **Pace by enthusiasm**: gauging effort by how motivated you feel, not by sustainable load
- **Catching up on a deficit by going faster**: doubles the lactate accumulation; almost always makes things worse
- **Confusing busy with productive**: high heart rate, low forward motion — common in over-meetinged orgs

## Relationship to Other Skills

- Use `periodization-and-recovery` for the macro arc that contains the pacing decisions.
- Use `progressive-overload` to *build* the threshold higher over months — pacing is about staying within it today.
- Use `constraint-analysis` to find which work is actually rate-limiting, so the pace is set by reality not anxiety.
- Use `incentive-analysis` when stakeholders are pushing for above-threshold pace and you need to negotiate.
- Use `incident-review` to detect post-wall signals after a pace-bomb cycle.
