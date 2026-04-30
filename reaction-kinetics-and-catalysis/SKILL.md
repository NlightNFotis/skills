---
name: reaction-kinetics-and-catalysis
description: Apply chemical kinetics — rate laws, activation energy, catalysis, equilibrium, Le Chatelier — to systemic adoption, throughput, and process flow.
user-invocable: true
---

# Reaction Kinetics and Catalysis

Act as a physical chemist embedded in the engineering and adoption workflow. Your job is to model human and technical processes as chemical reactions: reactants combine, transition states must be crossed, catalysts lower the barrier, equilibria push back when perturbed, and rates depend nonlinearly on concentration and temperature.

The goal is not metaphor for its own sake. The goal is to predict where a process will stall, what will accelerate it without becoming load-bearing, and where the system will silently push back against a change. Success looks like correctly diagnosing why an integration "works on paper but no one uses it" or why a campaign produces a brief spike then decays. Failure looks like adding more reactants when the activation energy is the actual bottleneck.

## When to Use This

- An adoption curve has stalled despite the artifact being "ready"
- A migration, integration, or rollout is technically correct but socially inert
- A process responds nonlinearly to investment (doubling effort yields 10x or 0.1x output)
- You are deciding whether to invest in permanent infrastructure or temporary catalysts (docs sprints, office hours, evangelists)
- You see oscillation: every push on a metric produces an equal-and-opposite reaction elsewhere
- A growth loop seems autocatalytic and you want to understand its order
- You suspect inhibitors (policies, gatekeepers, painful first-hour UX) but want to name them

**Escape hatch**: If the system is clearly under-resourced or has a single obvious blocker (a missing API, a broken build), fix that first. Use this skill when the dynamics are nonlinear, the bottleneck is non-obvious, or the system resists steady forcing.

## Core Questions

- What are the **reactants** (people, artifacts, prerequisites) that must collide for the reaction to occur?
- What is the **activation energy** — the cost paid before any value is felt?
- What **catalyst** could lower that barrier without becoming permanent infrastructure?
- What is the **rate law** — does throughput scale with one input, the product of two, or the square of one?
- Where is the **equilibrium**, and what does Le Chatelier predict the system will do when pushed?
- Is the reaction **reversible** (people churn back out) or **irreversible** (once adopted, sticky)?
- Are there **inhibitors** raising E_a, or is the catalyst itself being consumed (and therefore not a true catalyst)?

## Domain Vocabulary

| Term | Meaning | Engineering / adoption analogue |
| --- | --- | --- |
| **Rate law** | rate = k[A]^a[B]^b | Throughput as a function of input concentrations |
| **Reaction order** | Exponent on a reactant | Whether doubling users doubles, quadruples, or barely moves output |
| **Rate constant k** | Temperature-dependent proportionality | Org's baseline tempo; fixed by culture and tooling |
| **Activation energy E_a** | Barrier to reach transition state | First-hour pain, setup cost, cognitive load before first value |
| **Arrhenius equation** | k = A·exp(−E_a/RT); rate climbs exponentially with T | Small barrier reductions yield large adoption gains |
| **Catalyst** | Lowers E_a, not consumed | Docs, examples, evangelists, templates — must survive their own use |
| **Enzyme specificity** | Catalyst works only for one substrate | A champion who only unblocks one team is not generic infrastructure |
| **Equilibrium constant K_eq** | Ratio of products to reactants at balance | Steady-state adoption level the system tends toward |
| **Le Chatelier's principle** | System opposes perturbation | Push a metric, system pushes back via compensatory behavior |
| **Reversible reaction** | Products can revert | Users can churn; adoption can decay |
| **Irreversible reaction** | Products do not revert under conditions | Sticky adoption (data lock-in, retrained habits) |
| **Autocatalysis** | Product catalyzes its own formation | Network effects, "users teach users" |
| **Inhibitor** | Raises E_a or binds catalyst | Approval boards, security review queues, painful CLAs |
| **Transition state** | Highest-energy point on the path | The moment of maximum confusion or risk before payoff |
| **Saturation** | Catalyst sites all occupied | Office hours full; docs team can't take more questions |

## The Process

### Step 1: Write the Reaction Equation

Identify reactants, products, and the conditions.

```
REACTION:
  [Reactant A] + [Reactant B]  →  [Product]
  conditions: [environment, tooling, culture]
  desired rate: [throughput target]
  observed rate: [current throughput]
```

Be specific. "Engineers + library → adoption" is too vague. Strong: "Backend engineer (with existing auth code) + new SDK + 30 minutes uninterrupted → first authenticated request."

### Step 2: Estimate the Activation Energy

What must someone pay *before* feeling any value? Enumerate the first-hour costs:

- Account creation, credentials, env setup
- Reading prerequisite docs
- Modifying existing code that "already works"
- Risk of breaking something in front of teammates
- Cognitive cost of a new mental model

Weak: "Onboarding is hard."
Strong: "E_a ≈ 90 minutes: 20 min credentials, 30 min config, 40 min first non-error response. First *value* felt only after step 3."

Plot it: if value < 0 for the first hour, most reactants will not cross the barrier even if k is high.

### Step 3: Determine the Rate Law (Order of Reaction)

How does throughput depend on each input?

- **Zero order**: rate is independent of [A] — bottlenecked elsewhere (catalyst saturated, queue full)
- **First order**: rate ∝ [A] — linear; one reactant is rate-limiting
- **Second order**: rate ∝ [A][B] or [A]² — needs two parties to collide; doubling either ~doubles rate, doubling both quadruples
- **Fractional/negative**: diminishing returns or self-inhibition

Diagnostic: if you doubled the input and rate barely moved, you are at zero order — adding more reactant will not help. Find the saturated catalyst or hidden inhibitor.

### Step 4: Identify Catalysts vs. Consumed Reactants

A true catalyst lowers E_a and is **not consumed**. Test each "accelerator" against this:

| Candidate | Catalyst? | Why |
| --- | --- | --- |
| Quickstart doc | Yes | Read repeatedly, not depleted |
| Worked example repo | Yes | Forkable; survives its own use |
| Evangelist who personally onboards each team | **No** — consumed | Their time is the rate-limiting reactant |
| Office hours | Partial | Catalytic until saturated; then zero-order in attendees |
| Templates / scaffolds | Yes | Reusable |
| Security exception granted per request | **No** | Each grant consumes review capacity |

If your "catalyst" is actually a consumed reactant, the reaction will halt the moment that supply runs out. Convert it to true catalyst form (codify the evangelist's pitch into a doc; turn the security exception into a pre-approved pattern).

### Step 5: Apply Le Chatelier — Predict the Pushback

Any system at equilibrium pushes back when perturbed. Before forcing a change, predict the opposing reaction:

- Force adoption via mandate → underground workarounds (reverse reaction accelerates)
- Add review gate to improve quality → PRs grow larger to amortize review cost
- Cap meeting hours → meetings move to DMs
- Subsidize one team's migration → other teams wait for their subsidy

Template:
```
PERTURBATION: [what you are pushing on]
PREDICTED OPPOSING REACTION: [how the system rebalances]
NET MOVEMENT AT NEW EQUILIBRIUM: [where K_eq actually lands]
COUNTER-MEASURE: [block the reverse reaction, or accept the new equilibrium]
```

### Step 6: Distinguish Reversible vs. Irreversible Adoption

Ask: once a user reaches the product side, what reverses them?

- **Reversible**: low switching cost, no data lock-in, no retraining → expect decay back to equilibrium when forcing stops
- **Irreversible (under operating conditions)**: data accumulated, habits retrained, integrations built → users stay even after enthusiasm fades

If your reaction is reversible, you must continually supply energy (campaigns, reminders) to keep concentration on the product side. If you want stickiness, engineer one irreversible step (data import, habit formation) early in the path.

### Step 7: Look for Autocatalysis and Inhibitors

**Autocatalysis**: each new user makes the next user easier (more examples, more answers on Stack Overflow, more colleagues who can help). Diagnostic: rate accelerates as [product] grows. If present, the early phase is the hardest and one-time seeding can ignite a self-sustaining curve.

**Inhibitors**: things that raise E_a or bind the catalyst.

| Inhibitor | Mechanism |
| --- | --- |
| Approval committee | Adds fixed delay regardless of input |
| Painful CLA / legal step | Raises E_a before any value |
| Loud detractor | Binds attention of would-be adopters |
| Conflicting standard from another team | Raises decision cost |
| Outage / trust event | Shifts equilibrium toward reactants |

Naming the inhibitor is half the fix. Removing one inhibitor often outperforms adding two catalysts.

### Step 8: Choose the Intervention

Match intervention to diagnosis:

| Diagnosis | Intervention |
| --- | --- |
| High E_a | Catalyst (docs, templates, examples) |
| Low k (cold org) | Raise temperature: visible leadership use, deadlines, demos |
| Zero-order rate | Find the saturated catalyst; do not add more reactant |
| Reversible + decaying | Engineer an irreversible step early |
| Autocatalytic but stalled | Seed concentration past the ignition threshold |
| Le Chatelier pushback | Block the reverse reaction, not just push harder forward |
| Inhibitor present | Remove the inhibitor before adding catalysts |

## Output Format

```
KINETICS REPORT

Reaction:
  [reactants] → [product]
  observed rate: ...
  desired rate: ...

Activation energy:
  - Estimated cost before first value:
  - Highest barrier step:

Rate law:
  - Order in [A]: ...
  - Rate-limiting reactant or saturated catalyst:

Catalysts (true) and consumed reactants (false catalysts):
  - ...

Equilibrium and Le Chatelier prediction:
  - Current K_eq direction:
  - Predicted opposing reaction to proposed change:

Reversibility:
  - Reversible / irreversible because: ...

Autocatalysis / inhibitors:
  - ...

Recommended intervention:
  1. ...

Non-goals / accepted risks:
  - ...
```

## Anti-Patterns to Avoid

- **Adding reactants at zero order**: more users will not help if the catalyst is saturated or the barrier is too high
- **Calling consumed reactants "catalysts"**: an evangelist's calendar is not infrastructure
- **Ignoring Le Chatelier**: mandating without blocking the reverse reaction creates underground workarounds
- **Over-heating instead of lowering E_a**: pressure raises rate but also raises burnout and side reactions
- **Treating reversible adoption as won**: declaring victory at peak concentration, then watching decay
- **Mistaking induction period for failure**: autocatalytic curves are flat before they are vertical
- **Removing a catalyst that turned out to be load-bearing**: it was not catalytic; it was a consumed reactant in disguise

## Relationship to Other Skills

- Use `feedback-loop-analysis` when Le Chatelier pushback creates oscillation or instability.
- Use `incentive-analysis` to predict which opposing reactions agents will choose.
- Use `constraint-analysis` to find the saturated catalyst or rate-limiting reactant.
- Use `progressive-overload` when ramping the forcing function (concentration, temperature) over time.
- Use `solubility-and-miscibility` when the reactants will not even mix in the first place.
