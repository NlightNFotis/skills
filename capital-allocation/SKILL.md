---
name: capital-allocation
description: Decide where to spend engineering effort across competing demands using ROI, hurdle rates, opportunity cost, and zero-based budgeting — and ignore sunk cost.
user-invocable: true
---

# Capital Allocation

Act as a CFO allocating a finite engineering budget across competing demands: feature work, tech debt, infrastructure, research, security, hiring runway, and oncall coverage. Engineering capacity is the firm's scarcest capital — every hour spent on one thing is an hour not spent on something else, and the right question is rarely "is this worth doing?" but "is this the best use of the next available engineer-hour?"

Success looks like: an explicit allocation across categories, every active project clearing a stated hurdle rate, sunk costs ignored on go/no-go decisions, and a credible answer to "what would we cut to fund a new bet?" Failure looks like incremental drift (last year's budget plus 5%), zombie projects continued because they've already cost so much, and 30 simultaneous priorities that all get under-resourced.

## When to Use This

- Quarterly or annual roadmap planning
- "Should we keep going on X or kill it?" decisions
- Tech debt vs feature work split arguments
- Allocating headcount across teams
- Deciding what NOT to do
- Reviewing a portfolio of in-flight projects for thinning
- Pushback on "we should also do Y" requests
- Choosing between multiple candidate investments competing for the same eng-week

**Escape hatch**: For a single isolated decision (one PR, one bug), this lens is too heavy. Use when there are multiple competing demands on the same scarce engineering capacity.

## Core Mindset

Ask:

- What is the **total engineering budget** for this period?
- What is the **return** for each candidate investment?
- What is the **hurdle rate** — the minimum return that justifies funding?
- What is the **opportunity cost** — what gets *not* done?
- Is the **sunk cost** influencing the decision (it shouldn't)?
- If we **zero-based** the budget, would we still fund this?
- What allocation across **run / grow / transform** are we implicitly making?

## Vocabulary

| Term | Finance meaning | Engineering analog |
| --- | --- | --- |
| **ROI** | Return on investment | Value delivered per eng-week |
| **Hurdle rate** | Min ROI to approve a project | Bar a project must clear to be funded |
| **Opportunity cost** | Value of next-best alternative | The project we declined to fund this one |
| **Sunk cost** | Already spent, irrecoverable | Past eng-time on the project — irrelevant going forward |
| **Capital rationing** | Budget cap forces choosing | Headcount and quarter both finite |
| **Zero-based budgeting** | Re-justify every line from $0 | Re-justify each project as if proposed today |
| **Incremental budgeting** | Last year + delta | Last quarter's roadmap + new asks |
| **Run / Grow / Transform** | Standard enterprise allocation buckets | Maintain / expand / reinvent |
| **70/20/10 model** | 70% core, 20% adjacent, 10% transformative | Reasonable default split for innovation portfolios |
| **NPV** | Net present value | Discounted total value of a project |

## The Process

### Step 1: Establish the Total Budget

Be specific about capacity. Vague budgets produce 1.5x-overcommitted plans.

```
BUDGET (this period):
- Headcount: N engineers
- Person-weeks available: N × weeks − holidays − meetings × overhead
- Realistic delivery capacity (after oncall, support, interruptions): ~60-70% of nominal
```

The "realistic" line is critical. Most teams plan against nominal capacity and chronically miss. A 10-engineer team rarely delivers more than 6-7 engineers' worth of project work per week.

### Step 2: Inventory Demand

List every demand on the budget — including the implicit ones.

```
DEMANDS:
- Feature A: ~4 eng-weeks, sponsor: ...
- Tech debt B: ~6 eng-weeks
- Security C: ~2 eng-weeks (compliance deadline)
- Migration D: ~12 eng-weeks (in flight)
- On-call: ~10% of capacity always
- Support escalations: ~10% of capacity always
- Hiring/interviews: ~5% of capacity always
- Meetings/reviews: already deducted above
```

Make implicit costs (oncall, support, interviews) line items. They're real capital usage.

### Step 3: Set a Hurdle Rate

The hurdle rate is the minimum return a project must offer to justify funding. Below it, the eng-week is better deployed elsewhere.

Heuristic anchors:
- A "normal" feature delivers ~1× its cost in value over its lifetime — too low to fund unless strategic
- The hurdle rate should be set high enough that 30-50% of proposals fail it
- If everything clears the hurdle, the hurdle is too low (or the team is under-demanded)

State the hurdle explicitly: "This quarter, projects need >2× expected return on eng-cost to be funded above maintenance work."

### Step 4: Score Each Demand

For each demand, capture:

```
DEMAND: [name]
- Expected value: [revenue / users / cost-saved / risk-reduced]
- Cost: [eng-weeks]
- ROI: value / cost
- Confidence: high / medium / low
- Strategic fit: core / adjacent / experimental
- Sunk cost so far: [eng-weeks already spent — IGNORE for go/no-go]
- Reversibility: one-way door / two-way door
```

Critically: **sunk cost is recorded for accounting honesty but does not factor into go/no-go**. The right question is always "is the *next* dollar best spent here?", not "have we already spent so much we should keep going?"

### Step 5: Allocate Across Categories (Run / Grow / Transform)

Beyond per-project ROI, ensure the allocation pattern is healthy. A common framework:

| Bucket | Description | Typical % | Risk profile |
| --- | --- | --- | --- |
| **Run** | Keep the lights on; oncall, security, compliance, infra, bug fixing | 40-60% | Low risk, mandatory |
| **Grow** | Expand existing successful products | 25-40% | Medium risk, well-understood |
| **Transform** | Net-new bets, research, paradigm shifts | 5-20% | High risk, high variance |

Variants: Google's 70/20/10 (core / adjacent / transformative) for innovation portfolios.

Diagnose:
- 100% Run: team is in maintenance death spiral; no new value being built
- 100% Grow: under-investing in foundations; debt building
- 100% Transform: ignoring existing users; runway risk
- Healthy: explicit, intentional split that matches the firm's stage

### Step 6: Apply Zero-Based Budgeting Periodically

Once or twice a year, instead of "last quarter + delta," do a zero-based pass:

```
ZERO-BASED PROMPT (apply to each in-flight project):
- If this project did not exist today, would we start it now?
- If yes: how much budget would we approve?
- If no: stop, and reallocate the saved capacity
```

This breaks incremental drift and surfaces zombie projects — work that continues only because it's already going. Most teams have 1-3 zombies they should kill but won't because of sunk-cost bias.

### Step 7: Apply Sunk-Cost Discipline

Zombie indicators:
- "We've already spent 6 months, we can't stop now"
- The original sponsor has left
- The original justification no longer applies (market changed, strategy changed)
- The project's expected value has dropped below its remaining cost
- People defending it talk about past investment more than future value

Decision rule for go/no-go:
- Only **future** cost vs **future** value matters
- Past cost is information about your estimation skills, not an input to this decision
- Killing a project is not a "loss" — it's redirecting capital

Have a kill ritual: explicit "we're stopping X" announcement, retrospective on what was learned, redirect of freed capacity. This makes future kills easier.

### Step 8: Decide What NOT to Do

The hardest output of capital allocation is the explicit "no" list. Most roadmaps fail because they say yes to everything and quietly under-resource everything.

```
ALLOCATION DECISION:
- Funded (this quarter):
  1. ...
  2. ...
- Explicitly NOT funded (and the team agrees not to sneak it in):
  - ...
- Killed (in-flight projects stopping):
  - ... — sunk cost: X eng-weeks; future cost saved: Y eng-weeks
- Re-evaluation trigger for "no" list:
  - ...
```

A roadmap without an explicit "no" list is incremental, not strategic.

## Output Format

```
CAPITAL ALLOCATION

Period and budget:
- ...

Demands inventoried:
- ...

Hurdle rate (this period): ...

Scored demands (ranked by ROI):
1. ...

Run / Grow / Transform allocation:
- Run: X% (current and target)
- Grow: ...
- Transform: ...

Zero-based pass — projects that would not be started today:
- ...

Recommended decisions:
- Fund: ...
- Defer: ...
- Kill: ...
- Explicitly NOT funding: ...

Sunk costs disclosed (informational only):
- ...
```

## Anti-Patterns to Avoid

- **Sunk-cost continuation**: "we've already spent so much" — past spend is irrelevant going forward
- **Yes-to-everything roadmaps**: lacking an explicit "no" list, every project gets under-resourced
- **Incremental drift**: last quarter's roadmap + 5% — never re-justified from zero
- **Zombie projects**: in-flight work no one would start today, but no one will kill
- **Ignoring opportunity cost**: approving projects without naming what gets bumped
- **Hurdle rate of zero**: if everything clears, the hurdle isn't real
- **Implicit category drift**: drifting to 100% Run while telling leadership "we're transforming"
- **Confusing busy with productive**: 100% capacity utilization is over-allocation; queueing theory predicts sharp throughput collapse above ~80%

## Relationship to Other Skills

- Use `time-value-of-money` for per-project NPV / payback computation that feeds into ROI scores here
- Use `portfolio-theory` to check that the funded set is not all correlated (e.g., 5 projects all on the same risky platform)
- Use `optionality-as-value` when deciding whether to fund exploratory bets (preserve options) vs commit to one
- Use `constraint-analysis` to identify which engineering resource is actually the bottleneck — usually not eng-hours in the obvious sense
- Use `bias-audit` to check the allocation discussion for sunk-cost, anchoring, and status-quo bias
- Distinct from `time-value-of-money` (per-decision discounting) and `portfolio-theory` (correlation across bets)
