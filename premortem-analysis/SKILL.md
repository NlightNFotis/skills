---
name: premortem-analysis
description: Gary Klein's prospective hindsight — imagine the project has already failed and work backwards to identify the causes, before committing.
user-invocable: true
---

# Premortem Analysis

Act as a project anthropologist from six months in the future, called in to write the incident review for a project that has just failed catastrophically. Your job is to narrate, in the past tense, the specific story of how the failure unfolded — what was missed, what was rationalized away, who was overloaded, which assumption broke. Then bring that narrative back to the present and use it to change the plan.

The goal is not a generic risk list. The goal is a **structured failure narrative** that names actors, sequences, and turning points. Klein's research showed that prospective hindsight (imagining failure has happened) increases the number of plausible causes identified by roughly 30% over standard "what could go wrong?" prompts, because it shifts mode from prediction to explanation, which the brain is much better at.

## When to Use This

- Before kicking off a multi-week project, migration, or launch
- During RFC / design-doc review, before commitments are made
- Before a risky deployment, schema change, or cutover
- When the team is unusually optimistic ("this will be straightforward")
- When the cost of failure is high and the cost of stopping is low
- When the plan has been shaped by a strong proponent and dissent has been quiet
- Before re-running a project that previously failed in some form

**Escape hatch**: Don't premortem trivial reversible changes. The technique earns its keep when the change is irreversible, public, expensive to revert, or politically sticky.

## How This Differs From Adjacent Skills

| Skill | Mode | Output | When |
| --- | --- | --- | --- |
| `premortem-analysis` (this) | Imaginative, narrative, prospective | Failure stories with named turning points | Before starting |
| `failure-mode-effects-analysis` | Mechanical enumeration | FMEA table: mode × effect × severity × detectability | Before risky changes |
| `incident-review` | Retrospective, evidence-based | Contributing factors of an actual failure | After |
| `adversarial-design-review` | Attacker model | Abuse cases, exploits | Security-relevant |
| `bias-audit` | Reasoning-level | Cognitive biases in the plan | Whenever reasoning is suspect |

Premortem is **narrative and imaginative**; FMEA is **systematic and tabular**. Use both for high-stakes work; they catch different things.

## Core Mindset

- Switch from "what might go wrong?" to "we are writing the postmortem of a failure that has already happened."
- Embrace **pessimistic visualization** — the Stoics called this *premeditatio malorum*; the Roman generals walked their own funerals before campaigns.
- Failure stories should have actors, sequences, and a moment where things tipped from "concerning" to "doomed."
- Look for **weak signals that were rationalized away** — those are the real findings.
- The team must feel safe to imagine. Anyone who says "that won't happen" in a premortem has missed the point of the exercise.

## Categories of Failure Narratives

Use these to seed the imagination. Aim for at least one narrative from each category that applies.

| Category | Example narrative seed |
| --- | --- |
| **Scope drift** | "We kept adding 'just one more' requirement until the launch slipped past the dependent team's deadline." |
| **Hidden dependency** | "We didn't realize service X had a cron that read the old schema, until production began silently dropping rows." |
| **Wrong abstraction** | "Three weeks in we discovered the chosen abstraction didn't model the multi-tenant case at all." |
| **Performance cliff** | "It was fine for our test data; production data hit a quadratic path and the first heavy customer DOSed us." |
| **Migration left the door open** | "The dual-write window worked, but cutover revealed two writers had been racing the entire time." |
| **Rollback impossible** | "We discovered at incident time that the migration had no reverse — there was no plan to roll back." |
| **Org / staffing** | "The one person who understood the legacy code went on leave the week of cutover." |
| **Adversarial / abuse** | "Within hours of launch, users discovered the rate limit could be bypassed by [...]" |
| **Compliance / legal** | "Privacy review came back two days before launch and required a redesign." |
| **External vendor** | "Provider Y deprecated the API we depended on, with 30 days notice, in the middle of the project." |
| **Documentation lied** | "The doc we built on was 18 months stale; the actual behavior differed in [...]" |
| **Adoption failure** | "We shipped it and nobody used it because the workflow assumed [...]" |
| **Silent success failure** | "It 'worked' but the metric we were optimizing wasn't what users actually wanted." |

## Core Questions

- It's six months from now and this project is the cautionary tale of the year. What does the postmortem headline say?
- Which weak signal are we currently dismissing that ends up in the contributing-factors list?
- Which person is single-point-of-failure for this plan, and what happens when they're unavailable?
- What is the worst plausible time for things to go wrong (Friday cutover, holiday freeze, demo day)?
- What can break that we will not notice for weeks?
- Where has the team gone quiet — silence is sometimes worse than dissent?
- What did we optimistically assume about a dependency we don't control?

## The Process

### Step 1: Frame the Premortem

```
PREMORTEM FRAME:
- Project / change:
- Decision being committed:
- Time horizon for "failure" (e.g., 3 / 6 / 12 months):
- Definition of failure:
  - Catastrophic (rolled back, public incident, regulatory):
  - Severe (missed deadline by 2x, broken trust, attrition):
  - Quiet (shipped but unused, failed to move metric):
- Who is participating:
```

A premortem with no shared definition of failure produces incompatible narratives. Define it first.

### Step 2: Solo Generation Before Group Discussion

Each participant writes 3–5 failure narratives **silently and independently** for 10 minutes. This avoids anchoring on the loudest voice and surfaces dissent that wouldn't survive open discussion.

Each narrative should be a short past-tense story:

```
FAILURE NARRATIVE (past tense, 3–5 sentences):
- Headline (one line, what the postmortem is titled):
- Setup (state at T0 that contained the seed):
- Sequence (key events in order):
- Tipping point (the moment recovery became impossible):
- Aftermath (what the team said, what users saw):
```

### Step 3: Cluster and De-duplicate

Group narratives by failure category. Look for:

- Stories told by multiple people independently → high-confidence risks
- Stories from one person that the group dismisses → check for groupthink before discarding
- Categories with **zero** stories → ask whether that's because the risk is genuinely absent or because the team is blind to it

### Step 4: Identify Weak Signals Already Present

For each clustered narrative, ask: **what evidence of this failure mode is already in front of us?**

| Narrative | Weak signal already visible |
| --- | --- |
| "Vendor deprecation" | Vendor's recent changelog had two breaking changes |
| "Hidden dependency" | Three teams asked about this service in standup last month |
| "Single-point-of-failure" | Only one person reviewed the design doc |
| "Performance cliff" | Test data is 100× smaller than production |
| "Adoption failure" | No user has actually said they'd use this |

A weak signal that maps to a premortem narrative is the most valuable output of the exercise. Treat it as a near-miss in advance.

### Step 5: For Each High-Confidence Narrative, Choose a Treatment

| Treatment | Use when |
| --- | --- |
| **Eliminate** the risk by changing the plan | The narrative is plausible and avoidable cheaply |
| **Mitigate** by adding a control | The risk cannot be removed but the blast radius can |
| **Detect** earlier with telemetry / canary | You can't prevent it but you can shorten exposure |
| **Rehearse** with a game day or dry run | The risk exists at cutover and is recoverable if practiced |
| **Accept** explicitly with a written tradeoff | The cost of mitigation exceeds expected loss |
| **Defer** the decision until a gate is passed | The risk depends on info you don't yet have |

"Be careful" is not a treatment.

### Step 6: Identify the Stop Conditions

Decide now what evidence would cause you to **stop or change course**. Pre-committing to stop conditions is the antidote to sunk-cost escalation later.

```
STOP CONDITIONS:
- If [observable signal] by [date/milestone], we will [pause / pivot / abort]
- If [metric] does not reach [threshold] by [gate], we will [...]
- If [dependency] is not in place by [date], we will [...]
```

Without stop conditions, every problem will be reframed in-flight as "manageable."

### Step 7: Assign Owners and Re-Visit Triggers

For each treatment, assign:

- An owner (one person, not a team)
- A by-when date
- A trigger for re-running this premortem (e.g., scope grows by 50%, key person leaves, dependency changes)

Premortems decay. Re-run when the plan materially changes.

## Output Format

```
PREMORTEM REPORT

Frame:
- Project / decision / failure horizon / definition of failure

Failure narratives (clustered):
1. [Headline]
   - Sequence: ...
   - Tipping point: ...
   - Weak signal already visible: ...
   - Confidence (independent voices): ...
   - Treatment: eliminate / mitigate / detect / rehearse / accept / defer
   - Owner / by when:
2. ...

Stop conditions:
- ...

Risks accepted explicitly:
- [risk] — accepted because [...]

Re-run trigger:
- Re-run this premortem if [...]
```

## Anti-Patterns to Avoid

- **Generic risk list** ("scope might grow", "things might break") — narratives need actors and sequences
- **Skipping silent generation** — group discussion anchors on the first voice
- **"That won't happen"** — disallowed in premortem; the exercise assumes it has happened
- **Optimism rebound** — listing risks then reassuring yourselves they're handled, without changing the plan
- **No stop conditions** — leaves the team unable to pull the cord later
- **Treating it as a checkbox** — a 15-minute premortem before a 6-month migration is theater
- **Confusing premortem with FMEA** — premortem is narrative; FMEA is enumeration. Both have their place.
- **Devil's advocate framing** — premortem is not "argue against," it is "narrate the failure"
- **Premortem without re-run trigger** — the plan changes; the analysis should too

## Relationship to Other Skills

- Use `failure-mode-effects-analysis` alongside, for systematic mechanical enumeration where premortem produces narrative.
- Use `bias-audit` to surface the optimism, planning fallacy, and sunk-cost biases that premortem is designed to counter.
- Use `preflight-checklist` to convert premortem treatments into operational steps at cutover.
- Use `incident-review` after the fact and compare to the premortem — the gap is where the team's imagination failed.
- Use `adversarial-design-review` for the abuse-case narratives premortem may underweight.
