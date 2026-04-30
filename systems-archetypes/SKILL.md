---
name: systems-archetypes
description: Identify recurring system dynamics like fixes-that-fail, limits-to-growth, shifting-the-burden, and tragedy-of-the-commons.
user-invocable: true
---

# Systems Archetypes

Act as a systems thinker in the tradition of Senge, Meadows, and Forrester. Your job is to recognize the small set of recurring structural patterns — *archetypes* — that produce persistent, frustrating problems despite reasonable local decisions by everyone involved. Once an archetype is named, the right intervention is rarely to push harder on the symptom; it is to change structure: incentives, delays, information flow, ownership, or constraints.

Success looks like correctly naming the archetype, drawing the underlying loop, and proposing a structural intervention at a high-leverage point. Failure looks like prescribing yet another symptomatic fix, treating a structural problem as an individual performance issue, or optimizing a single actor at the expense of the system.

## When to Use This

- The same incident, bug class, or pain point keeps recurring despite fixes
- Each fix helps briefly, then the problem returns worse
- A team is locked in escalating effort with another team, vendor, or internal system
- Growth, adoption, throughput, or quality plateaus unexpectedly
- A shared resource (CI minutes, on-call attention, review capacity, budget) is being depleted
- Local incentives appear sane but the aggregate outcome is bad
- Reviewing organizational, process, or platform decisions — not just code

**Escape hatch**: If the issue is a one-off bug or a clear local defect, use `popperian-debug` or `code-forensics`. Archetypes are for *recurring* dynamics with feedback over time. If you cannot point to repetition, you may be pattern-matching prematurely.

## Core Mindset

Structure drives behavior. Ask:

- What is the loop? What feeds back into what, with what delay?
- Who benefits from the current structure (even if no one designed it that way)?
- Where are the delays between action and consequence?
- What information is missing from whoever has to act?
- Which "obvious" fix has been tried before and made things worse?
- What slow variable is being eroded while we focus on a fast one?
- Where is the high-leverage intervention — and why is it being avoided?

## The Archetypes

Senge's eight commonly cited archetypes, with software/engineering examples.

| Archetype | Pattern | Software example |
| --- | --- | --- |
| **Fixes that Fail** | Quick fix relieves symptom; unintended consequence makes underlying problem worse | Disabling a flaky test removes the signal that the production race exists |
| **Shifting the Burden** | Symptomatic solution is easier than fundamental one; capability for the fundamental fix atrophies | Always paging on-call instead of fixing root cause; team forgets how to debug it |
| **Limits to Growth** | Growth process bumps into a balancing constraint; effort to push harder fails | Adding more services without scaling the platform team; onboarding stalls |
| **Tragedy of the Commons** | Shared resource degrades as each actor maximizes individual use | Every team adds CI jobs; pipeline becomes unusable for everyone |
| **Success to the Successful** | Two parallel efforts share a resource; early winner gets more, locking in dominance | Whichever microservice launched first gets all the platform investment |
| **Escalation** | Two parties respond to each other's actions, each amplifying | Service A retries aggressively → Service B adds rate limits → A retries harder |
| **Drifting Goals** | When performance falls short, lower the standard rather than improve performance | "Acceptable" p99 keeps creeping up; SLO is rewritten instead of fixed |
| **Growth and Underinvestment** | Growth slowed by capacity limits; investment in capacity is delayed because performance "isn't bad enough yet" | Database is fine until it isn't; provisioning lead time exceeds collapse time |

Two more often added:

- **Accidental Adversaries** — partners who should cooperate end up undermining each other through local optimization (e.g., dev team optimizes for velocity, ops team for stability; their actions make each other's job harder).
- **Eroding Goals** — same mechanism as Drifting Goals; sometimes called "boiled frog".

## Meadows' Leverage Points (Abridged, Weakest → Strongest)

Donella Meadows' famous list. Lower-numbered items in her ranking are higher leverage:

12. Constants, parameters, numbers (e.g., a timeout value)
11. Buffer sizes
10. Stock-and-flow structure
9. Length of delays
8. Strength of negative feedback loops
7. Gain on positive feedback loops
6. Structure of information flow (who has access to what)
5. Rules of the system (incentives, punishments, constraints)
4. Power to add, change, or self-organize structure
3. Goals of the system
2. Mindset/paradigm out of which goals arise
1. Power to transcend paradigms

Most engineering interventions live at 12–8. The biggest unlock is usually 6 (information flow) or 5 (incentives).

## The Process

### Step 1: Describe the Recurring Problem

State the pain plainly, with evidence of recurrence.

```
RECURRING PROBLEM:
- Symptom:
- How often it recurs:
- Previous fixes attempted (and their effect over time):
- Who feels the pain, and who currently pays the cost of the fix:
```

If you cannot list at least two prior fix attempts, this may not yet be archetypal — gather more history first (`code-forensics` can help).

### Step 2: Draw the Loops

Sketch the causal loop diagram in text. Use `→` for "increases" and `⊣` for "decreases". Mark delays with `[delay]`.

```
LOOPS:
B1 (balancing): On-call pages → quick mitigation → symptom reduced ⊣ pages
R1 (reinforcing): Quick mitigation → root-cause skill atrophies → bigger incidents → more pages [delay: months]
```

### Step 3: Match an Archetype

Compare the loop structure to the table above. The match should be structural, not metaphorical.

- "It's like Tragedy of the Commons" is not enough. Identify: the commons (shared resource), the actors, the depletion mechanism, the missing feedback.
- More than one archetype can be active at once (e.g., Shifting the Burden often sits inside Fixes that Fail).

### Step 4: Identify the Slow Variable

Most archetypes hide a slow variable being eroded while everyone watches a fast one.

- Fast: incident count this week
- Slow: institutional ability to debug the subsystem

Naming the slow variable usually reveals the high-leverage point.

### Step 5: Find the Leverage Point

Walk Meadows' list from low to high leverage and ask: which level is currently being touched, and what would the next level look like?

```
LEVERAGE ANALYSIS:
- Current intervention is at level: [12 / 11 / ...]
- Next-higher leverage would be: ...
- Reason it is being avoided: cost / political / unknown / sacred
```

The honest answer to "why is it being avoided" is often the actual problem.

### Step 6: Propose the Structural Change

State the intervention in terms of structure, not exhortation.

Weak:

> Teams should be more responsible with CI usage.

Strong:

> Allocate a per-team CI budget enforced by quota. Surface daily usage in the team's own dashboard. Reclaim unused budget weekly so the feedback loop closes within the team's planning horizon.

The structural fix usually changes one of: information flow, incentives, ownership, delay, or constraints.

### Step 7: Predict the New Failure Mode

Every structural change creates a new system. Predict how *this* one will fail and design observability for it.

- "If we add CI quotas, the new failure mode is teams gaming the quota by …"
- "If we add a circuit breaker between A and B, the new failure mode is …"

If you cannot name the next failure mode, you don't yet understand the new structure.

## Output Format

```
SYSTEMS ARCHETYPE REVIEW

Recurring problem:
- ...

History of attempted fixes and their decay:
- ...

Causal loops (B = balancing, R = reinforcing):
- B1: ...
- R1: ... [delay: ...]

Matched archetype(s):
- Primary: ...
- Reason for match (structural, not metaphorical):

Slow variable being eroded:
- ...

Leverage point (Meadows level):
- Currently intervening at: ...
- Higher-leverage option: ...

Recommended structural change:
1. ...

Predicted next failure mode and observability:
- ...

What this is NOT (alternatives ruled out):
- ...
```

## Anti-Patterns to Avoid

- **Repeating the same symptomatic fix and expecting different results**
- **Pushing harder on a balancing loop**: more effort against a constraint produces more resistance, not more output
- **Ignoring delays**: assuming the absence of immediate consequence means there is none
- **Treating structural problems as individual failures**: blaming the on-call when the structure guarantees burnout
- **Optimizing one actor at system expense**: local KPIs that destroy global outcomes
- **Pattern-matching prematurely**: naming an archetype without drawing the loop
- **Stopping at the diagnosis**: an archetype without a structural intervention is just vocabulary
- **Pretending the high-leverage fix is free**: name the political/organizational cost honestly

## Relationship to Other Skills

- Use `feedback-loop-analysis` to formalize the gain, delay, and stability of the loops you identify.
- Use `emergence-analysis` when many actors with the same local rule produce the system-level dynamic.
- Use `constraint-analysis` when "Limits to Growth" is the matched archetype — find the binding constraint.
- Use `system-ecosystem-analysis` when the archetype involves multiple interacting "species" (services, teams, dependencies) competing for resources.
- Use `code-forensics` to substantiate the claim that the problem is recurring with timeline evidence.
- Use `assumption-audit` to surface the implicit goals and incentives that make the current structure stable.
