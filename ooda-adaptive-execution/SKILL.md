---
name: ooda-adaptive-execution
description: Use observe-orient-decide-act loops for fast adaptive work under uncertainty.
user-invocable: true
---

# OODA Adaptive Execution

Act as an adaptive operator running John Boyd's **Observe–Orient–Decide–Act** loop. The premise: in an uncertain, changing environment, the side that completes high-quality OODA loops faster — and forces the opponent (or the problem) to react to *its* moves — wins. Your job is to make small, information-rich moves that update your model of the situation while keeping forward progress.

Success looks like: each loop produces both *progress* and *new information*; orientation is updated when reality contradicts the plan; and irreversible actions are taken only after orientation is high-confidence. Failure looks like running an Act–Act–Act loop (motion without observation), or an Observe–Observe–Observe loop (analysis paralysis).

## When to Use This

- Active incident response or production debugging
- Exploratory work in unfamiliar code or systems
- Ambiguous tasks where requirements will shift as you learn
- Multi-step work where early steps reveal what later steps should be
- Time pressure makes a full upfront plan infeasible
- Previous plans went stale and a new orientation is needed

**Escape hatch**: Skip OODA when the path is fully known and the environment is stable — just execute the plan. Skip it for one-line fixes. Skip it when the right move is to *stop and design* before acting at all (use `formal-invariants` or `assumption-audit` instead).

## Core Mindset — Boyd's Insight

Boyd's loop is often drawn as four equal boxes. It isn't. **Orientation is the most important phase** — it is where mental models, prior experience, cultural traditions, and new observations are synthesized into the lens through which everything else is interpreted. A wrong orientation makes every subsequent observation meaningless and every decision wrong.

Two further Boyd ideas matter here:

- **Getting inside the opponent's loop**: act faster than the situation can stabilize, so the problem must respond to *you* rather than the other way around. In debugging: change one thing fast, observe the effect, before the system's noise floor obscures it.
- **Implicit vs explicit guidance**: experienced operators run OODA implicitly — patterns trigger action without articulation. Novices (and LLMs in unfamiliar terrain) must run it explicitly. Switch to implicit only after the situation is well-understood.

Ask:

- What do I actually observe (not infer)?
- What is my current orientation, and what would invalidate it?
- Of the available actions, which is most reversible *and* most information-rich?
- Am I about to take a one-way-door action with low orientation?
- Is my loop faster than the situation is changing? If not, what can I cut?

## The Four Phases

### Observe

Gather the smallest set of fresh facts needed to update orientation. Not "all the facts" — fresh facts.

- Direct signals: error text, logs, output, metrics, user reports
- The state of your own work: what changed since the last loop?
- The state of the environment: did anyone else change something?
- What is *missing* from observation (silences are signals too)

Bias: under-observing in a hurry. Counter: name two specific signals you will check this loop.

### Orient

The synthesis step. Combine new observations with prior knowledge, mental models, and cultural/codebase conventions into an updated picture.

Components of orientation (Boyd):

- **Genetic heritage / training**: your background experience and biases
- **Cultural traditions**: this codebase's conventions, this team's norms
- **Previous experience**: what you learned in earlier loops
- **New information**: what you just observed
- **Analysis & synthesis**: forming the model

Output: a one-line statement of what is going on and what matters now.

Bias: skipping orient and acting on raw observation. Counter: write the one-liner before deciding.

### Decide

Choose the next action. Apply two filters:

1. **Reversibility**: prefer reversible moves; reserve one-way doors for high-confidence orientation.
2. **Information value**: prefer moves whose result will sharpen orientation regardless of outcome.

Boyd: decisions are hypotheses about what will work. Treat them as such.

### Act

Do the thing. Make the change small enough that its effect can be attributed cleanly. Capture the result for the next Observe.

## Loop Cadence and Tempo

The right cadence depends on volatility and stakes:

| Situation | Loop length | Notes |
| --- | --- | --- |
| Live incident | seconds–minutes | Tiny reversible probes; explicit logging of each loop |
| Exploratory debugging | minutes | One hypothesis test per loop |
| Refactor of unfamiliar code | minutes–hour | Each loop = small change + verification |
| Multi-day feature build | hours–day | Loops bracketed by build/test/review |
| Architecture decision | days | Long orient phase; few but high-stakes decisions |

If your loop is slower than the system is changing, you are *behind* the situation. Shorten observation; cut nice-to-have analysis; act on smaller hypotheses.

## Orientation Health Checks

Before each Decide, sanity-check your orientation:

- Is any current belief older than 2 loops without re-validation?
- Did the last result *match* my prediction, or was it surprising?
- Have I been getting "close to working" for several loops in a row? (suspicion signal)
- Has the goal shifted under me?
- Am I solving the original problem, or one that drifted?

A surprising result is a signal to **re-orient**, not to push harder on the same plan.

## When to Break the Loop

OODA is not infinite. Stop and switch modes when:

- **Orientation is collapsing**: too many surprises in a row → step back, do `code-forensics` or `assumption-audit`
- **One-way door ahead**: stop looping; design carefully before acting
- **Loop is producing motion without progress**: cut to a different approach
- **Goal has fundamentally changed**: re-scope before continuing
- **The task is now mechanical**: drop OODA overhead and just execute

## The Process (Per-Loop Template)

```
LOOP n:

Observe:
- Fresh signal 1:
- Fresh signal 2:
- Notable absences:

Orient (one-liner):
- What is going on:
- What changed from previous orientation:
- Confidence: low / medium / high

Decide:
- Candidate actions: [list 1–3]
- Chosen action: [...]
- Why (reversibility, information value):
- Predicted result:

Act:
- What was done:
- Actual result:
- Match / mismatch with prediction:

Loop trigger:
- Continue (next observation due when ...)
- Re-orient (because ...)
- Break loop (because ...)
```

After several loops, also produce a **session orientation summary**: the current model, what's been ruled out, what remains uncertain. This is what an oncoming collaborator (or your future self) needs.

## Worked Mini-Example

Loop 1 — Observe: test fails with `ECONNREFUSED` on CI, passes locally. Orient: probably env-specific, not code. Decide: run the same test on a clean container locally (reversible, high info). Act: test passes locally in container.
Loop 2 — Observe: same env locally → green; CI → red. Orient: difference is *network policy*, not container. Decide: print resolved DNS in CI (reversible, high info). Act: DNS resolves to wrong IP in CI.
Loop 3 — Orient confidence high; root cause is CI DNS. Decide: this is now a one-way door (config change). Stop OODA; write the proper fix and review it.

Each loop produced both progress and information. The decision to *break the loop* came when orientation was high enough that reversibility no longer mattered.

## Tempo vs Precision Trade-off

Boyd's emphasis on speed is often misread as "act fast at all costs." It is not. The full claim: **operate at a tempo your opponent (or the problem) cannot match, while keeping orientation honest.** A faster loop with bad orientation is worse than a slower loop with good orientation — it just commits errors faster.

Practical calibration:

- If predictions match observations 2+ loops in a row → you can speed up; orientation is reliable
- If predictions miss 2+ loops in a row → slow down; orientation is wrong, more speed compounds the error
- If stakes per loop are rising (closer to a one-way door) → slow down deliberately even if tempo was fine

## Anti-Patterns to Avoid

- **Act–Act–Act**: making changes without observing their effects between attempts
- **Observe–Observe–Observe**: collecting data forever; never deciding (analysis paralysis)
- **Stale orientation**: acting on a model that the last two observations contradicted
- **Big irreversible move with low orientation**: deploying, deleting, migrating before the picture is clear
- **Tempo blindness**: running 1-hour loops in a 5-minute incident
- **Confusing motion with progress**: many loops, no information gained
- **Implicit OODA in unfamiliar terrain**: skipping the explicit write-up when the situation isn't yet pattern-matchable
- **Loop without exit criteria**: not naming what would make you stop and switch modes

## Relationship to Other Skills

- Use `popperian-debug` inside an OODA loop to design Decide-phase falsification tests.
- Use `code-forensics` when orientation collapses and you need to rebuild the timeline.
- Use `assumption-audit` when orientation rests on premises you haven't checked.
- Use `differential-diagnosis-debugging` to structure the Orient phase when many causes compete.
- Use `bias-audit` when several loops in a row "confirm" the same orientation suspiciously easily.
- Use `formal-invariants` when an OODA loop reveals an invariant that should be made explicit so you stop re-discovering it.
