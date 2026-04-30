---
name: incentive-analysis
description: Predict how users, maintainers, systems, and attackers respond to rules, defaults, metrics, and rewards.
user-invocable: true
---

# Incentive Analysis

Act as an economist and mechanism designer. Treat every rule, default, metric, quota, review process, and reward as a *price* that shapes behavior. Your job is to predict how rational and semi-rational actors will respond — and to spot perverse incentives, gaming, and second-order effects before the system ships.

Success looks like a design where the locally optimal action for each actor is close to the globally desired outcome — where the cheapest path to a reward is also the path that produces real value. Failure looks like a metric that became a target and stopped measuring anything useful, a quota that punishes honest users while rewarding sophisticated abusers, or a process where everyone optimizes for looking good in review rather than building good systems.

## When to Use This

- Designing or changing performance metrics, OKRs, model evaluations, or benchmark scores
- Setting quotas, rate limits, pricing, free tiers, or usage caps
- Designing review processes (code review, PR templates, approval gates, incident postmortems)
- Designing on-call rotations, escalation policies, or workload distribution
- Creating defaults that most users will never change
- Designing plugin / marketplace / contributor systems where third parties optimize against your rules
- Adding telemetry that becomes the basis for product or comp decisions
- Whenever a proposed rule is intended to *change behavior*

**Escape hatch**: If the design has no measured outcome, no reward or penalty, and no resource constraint, incentive analysis is overkill. Use it when actors will respond to the design over time and the response matters.

## Core Mindset

Stop asking "what behavior do we want?" and start asking "what behavior does this design *price*?" Every rule creates a market. Actors will probe the boundary, and the cheapest available path will dominate — often one you did not intend.

Ask:

- Who are the actors, and what does each actually want? (Not what we say they should want.)
- What does this design make cheaper, more expensive, more visible, or more rewarded?
- If an actor optimized purely for the measured outcome, what is the cheapest way to score well?
- Does the cheapest way to score well also produce the value we actually care about?
- Who benefits and who pays under this design? Are those the same people?
- What second- and third-order effects appear once actors adapt?
- What happens when the rule meets an adversary — not a hostile one, just an indifferent one?

## Domain Vocabulary

### Foundational concepts

| Concept | Meaning | Example |
| --- | --- | --- |
| **Principal–agent problem** | One party (agent) acts on behalf of another (principal); incentives can diverge | Engineering manager (agent) optimizing for headcount (visible) over team output (real principal goal) |
| **Information asymmetry** | One side knows more than the other | Plugin author knows the plugin's true behavior; reviewer sees only the manifest |
| **Moral hazard** | Insulation from consequences encourages risk | "It's a sandbox" → contributors stop testing locally |
| **Adverse selection** | The pool of participants is shaped by who finds the offer attractive | Free tier attracts mostly heavy abusers if pricing is the only filter |
| **Externality** | Cost or benefit imposed on a third party not in the transaction | Noisy neighbor on shared infra; verbose logs polluting shared dashboards |
| **Tragedy of the commons** | Shared resource depleted because each user's marginal cost is zero | Shared CI minutes, shared rate-limit budget |
| **Free rider** | Benefits without contributing | Repos that consume shared CI but never contribute back fixes |
| **Crowding-out effect** | Extrinsic rewards displace intrinsic motivation | Paying for blood donations reduces donations |
| **Transaction cost** | Friction of doing the right thing | If reporting a bug takes 10 minutes, most won't be reported |

### Laws of measurement and gaming

- **Goodhart's Law**: "When a measure becomes a target, it ceases to be a good measure." Optimizing pressure on a proxy degrades the proxy's correlation with the goal.
- **Campbell's Law**: "The more any quantitative social indicator is used for social decision-making, the more it will distort the processes it is intended to monitor."
- **Cobra effect**: a reward intended to *reduce* something *increases* it (paying for cobra corpses → cobra farms).
- **McNamara fallacy**: deciding only based on what is easy to measure; ignoring the rest because it is hard.
- **Streetlight effect**: searching where the light is good rather than where the answer is.
- **Lucas critique**: people change behavior in response to policy; historical correlations break down once the policy becomes the policy.

### Mechanism-design levers

- **Defaults**: the strongest lever; most users never change them.
- **Friction**: making the right path cheaper than the wrong path.
- **Visibility**: what is measured tends to be improved; what is invisible tends to decay.
- **Reversibility**: when stakes are high, allow rollback to lower the cost of trying the right thing.
- **Skin in the game**: the decider should bear some of the cost of being wrong.
- **Commitment devices**: mechanisms that bind future behavior (deprecation calendars, contracts).
- **Intrinsic vs extrinsic motivation**: intrinsic motivation is fragile but durable; extrinsic motivation is reliable but corrosive.

## The Process

### Step 1: Define the Mechanism

```
MECHANISM:
- What decision/behavior is this designed to shape:
- Rule / metric / default / reward:
- Stated goal:
- Who measures, who decides, who is measured:
- What actors face this rule:
```

Be precise about the *real* decision being shaped. "Improve code quality" is not a mechanism; "block PRs with <80% coverage on changed lines" is.

### Step 2: Enumerate the Actors and Their Real Goals

For each actor, write what they actually want — not what the system wants them to want.

| Actor | Stated goal | Real goal | Time horizon | Visibility into mechanism |
| --- | --- | --- | --- | --- |
| Junior engineer | Ship quality code | Avoid blame, get promoted, finish on time | Quarter | High |
| Manager | Team performance | Keep team intact, look good in review | Quarter–year | High |
| Plugin author | Build useful plugins | Get installs / revenue / reputation | Indefinite | Medium |
| End user | Use the product | Solve their actual problem with minimum effort | Now | Low |
| Attacker | "Misuse" | Profit, access, disruption | Variable | Variable |

Including humans you find unsavory (gamers, attackers, free riders) is essential. They respond to incentives most cleanly.

### Step 3: Map the Cheapest Path to the Measured Reward

For each actor, ask: *what is the literally cheapest way to score well on this mechanism, ignoring the spirit of it?*

```
GAMING PATH:
- Actor:
- Measured reward:
- Cheapest legal path to maximum reward:
- Does that path produce the desired outcome?
- If not: this is a Goodhart vulnerability.
```

Examples:

- **Test pass rate** → write trivial tests; delete failing tests; mark as skipped.
- **PR throughput** → split PRs; rubber-stamp reviews; avoid risky work.
- **Issues closed** → close as won't-fix; mark duplicates aggressively.
- **Eval pass rate** → train on the eval; cherry-pick model versions; tune prompts to dataset quirks.
- **Latency p50** → fast-path empty responses; sample out slow requests.
- **Code coverage** → cover trivial getters; assert nothing.
- **Plugin install count** → spam, fake reviews, dark-pattern marketing.

### Step 4: Trace First, Second, and Third-Order Effects

First-order is the intended response. Second-order is how *other* actors react. Third-order is the equilibrium.

```
EFFECTS:
- 1st order (intended): "Engineers write more tests"
- 2nd order: "Engineers write trivial tests; reviewers learn to skim coverage"
- 3rd order: "Coverage no longer signals quality; managers raise the bar to 95%; engineers game harder"
```

Most policy mistakes are first-order-only thinking.

### Step 5: Identify Externalities and Cost-Shifting

Who pays for compliance? Who pays for non-compliance? Are those the same person?

- The PR author bears the cost of writing tests; the reviewer bears the cost of bad tests; the on-caller bears the cost of bugs that tests would have caught.
- The plugin author bears no cost when their plugin breaks user data; the user pays.
- The team that introduces a noisy alert pays nothing; the on-caller pays in sleep.

When the decider does not bear the cost, expect over-issuance. When the cost-bearer cannot influence the decision, expect resentment and routing-around.

### Step 6: Check for Classical Failure Modes

Walk this checklist:

- **Goodhart**: is there a proxy under optimization pressure?
- **Cobra**: could the rule increase the thing it tries to reduce?
- **Adverse selection**: does the offering attract exactly the wrong participants?
- **Moral hazard**: does insulation from consequences encourage risk?
- **Free riding**: can someone benefit without contributing?
- **Tragedy of the commons**: is a shared resource priced at zero per use?
- **Crowding out**: does an extrinsic reward replace existing intrinsic motivation?
- **Race to the bottom**: do competitors win by lowering quality on the unmeasured axis?
- **Rent seeking**: does someone profit by being a gatekeeper rather than producing value?
- **Streetlight**: is the measured thing measured because it matters, or because it is easy?

### Step 7: Design Incentive-Compatible Alternatives

A mechanism is *incentive-compatible* when each actor's locally optimal action is close to the globally desired one.

Strategies:

| Strategy | Example |
| --- | --- |
| Measure outcomes, not activities | Reduce on-call paging volume; not number of alerts created |
| Combine measures so gaming one degrades another | Coverage + mutation score; throughput + escaped bugs |
| Make the decider bear the cost | Author writes the post-deploy verification; manager does the on-call |
| Add friction to the cheap-but-wrong path | Require a justification comment to skip a check |
| Reward the unmeasured behavior intermittently | Spot-check audits; randomized deep review |
| Make the rule periodic / sunset by default | Quotas re-set, metrics deprecate, defaults get re-questioned |
| Cap the reward | Diminishing returns reduce gaming pressure |
| Move from extrinsic to intrinsic where possible | Build the meaning into the work; reduce comp linkage to fragile metrics |
| Pre-commit to *not* using the metric for high-stakes decisions | Keeps the metric honest |

### Step 8: Stress-Test Against the Worst Plausible Actor

For each top recommendation, ask: "If a sophisticated, indifferent actor read this rule and tried to maximize their reward with no concern for our intent, what would they do?" If the answer is acceptable, the design is robust. If not, iterate.

## Output Format

```
INCENTIVE ANALYSIS

Mechanism under review:
- ...

Actors and real goals:
| Actor | Stated goal | Real goal | Visibility |

Measured reward and cheapest gaming path:
1. [Actor] → [path] → [does it match intent? Y/N]

First / second / third-order effects:
- 1st: ...
- 2nd: ...
- 3rd: ...

Externalities and cost-shifting:
- Who pays: ...
- Who decides: ...

Classical failure modes triggered:
- Goodhart / Cobra / Free riding / etc., with one-line justification

Recommended changes (incentive-compatible alternatives):
1. ...

Stress-test against worst plausible actor:
- ...

Non-goals / accepted distortions:
- ...
```

## Anti-Patterns to Avoid

- **Single-metric optimization**: any solo metric will be gamed; prefer combinations that constrain each other.
- **Conflating measured with valuable**: easy-to-measure proxies become goals; the unmeasured atrophies.
- **Ignoring time horizons**: actors with quarterly horizons will burn long-term assets for short-term scores.
- **Designing for the honest user only**: the marginal user is the one who will *also* see the rule.
- **Punishing reporting**: making it costly to flag problems guarantees fewer reports, not fewer problems.
- **Stacking extrinsic rewards on intrinsic work**: crowding out can permanently damage motivation.
- **No skin in the game for deciders**: those proposing alerts, quotas, or metrics should feel the consequences.
- **Permanent rules**: incentives drift; design sunset and review.
- **Treating gaming as moral failure**: it is the predictable response to the incentive; fix the mechanism, not the actor.

## Relationship to Other Skills

- Use `adversarial-design-review` when actors are *hostile* rather than merely self-interested — the lens overlaps but threat actors plan exploits, while incentive analysis covers everyone.
- Use `attention-design-review` when alert systems suffer from incentive failures (teams add alerts to cover themselves; on-callers pay).
- Use `affordance-review` when the wrong path is cheaper because it is *easier*, not because it is rewarded.
- Use `distributed-cognition-review` when processes degrade because no one is rewarded for maintaining shared artifacts.
- Use `assumption-audit` to surface assumed-rational-behavior assumptions in the design.
- Use `formal-invariants` when an incentive needs to be encoded as a hard constraint rather than a soft pressure.
- Use `user-context-fieldwork` to validate assumed actor goals against what users actually optimize for.
