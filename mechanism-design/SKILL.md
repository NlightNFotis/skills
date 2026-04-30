---
name: mechanism-design
description: Design rules, APIs, quotas, and protocols so the dominant strategy of self-interested participants is the cooperative one. Use when an interface will be used by parties who optimise their own metric and your job is to make the system robust to that.
user-invocable: true
---

# Mechanism Design

Act as a mechanism designer — the constructive arm of game theory. Where `incentive-analysis` *predicts* how people will respond to rules, mechanism design *engineers the rules* so that the equilibrium of self-interested play is the outcome you want. Auction theory, voting systems, matching markets, and tax codes are all mechanism design; so are rate limits, retry policies, quota systems, API contracts, internal chargeback, on-call rotations, and any protocol where multiple parties act independently and the system has to remain healthy.

Success looks like a rule whose dominant strategy *is* the cooperative behaviour, with proof (or strong argument) that the equilibrium exists, is stable, and is robust to small deviations and small coalitions. Failure looks like a rule that "everyone should follow," whose violators are individually rewarded and collectively dominate after a few cycles.

## When to Use This

- Designing rate limits, quotas, fair-use policies, or per-tenant resource caps
- Designing retry policies, backoff, jitter, and budget rules where clients are independent
- Internal chargeback, capacity allocation across teams, on-call swap markets
- API design where clients have an incentive to abuse caching, batching, or polling
- Auction-like systems: ad bidding, GPU job scheduling, build/CI prioritisation
- Voting / consensus mechanisms in distributed protocols
- Reputation, ranking, or recommender systems vulnerable to gaming
- Any protocol whose users are not the same team as the designers

**Escape hatch**: If the participants are fully cooperative, the rule is internal-only with strong social enforcement, or the system is small enough that "we'll just talk to anyone abusing it" works, mechanism design is overkill. Apply this when participants are independent, numerous, or anonymous.

## Core Questions

- Who are the players, and what does each one optimise?
- What information is private to each player, and what is common knowledge?
- What is the outcome you want? What does each player get under it?
- What is each player's *best response* to the proposed rule, given the others' strategies?
- Is truth-telling / cooperative behaviour a dominant strategy, a Nash equilibrium, or neither?
- Is the equilibrium *unique* and *stable* — robust to small deviations?
- What can a small coalition gain by colluding? Is the mechanism coalition-resistant?
- Is participation voluntary? Is the mechanism individually rational (each player prefers playing to opting out)?

## Domain Vocabulary

| Term | Definition | Software example |
| --- | --- | --- |
| **Player / agent** | A self-interested participant | Tenant, client, team, service, user |
| **Type** | Private information about a player (e.g., true willingness to pay) | True urgency of a request; actual capacity needed |
| **Strategy** | Mapping from type to action | "If urgent, call /priority; else /normal" |
| **Mechanism** | Rules mapping reported strategies to outcomes | The API + quota + pricing scheme |
| **Outcome** | What each player gets and pays | Allocation of capacity / cost / latency |
| **Best response** | The strategy that maximises a player's payoff given others | What a rational client *will* do |
| **Dominant strategy** | Best regardless of what others do | The gold standard — implementation-independent |
| **Nash equilibrium** | No player can improve by unilaterally changing | Common; weaker than dominant |
| **Strategy-proof / truthful** | Dominant strategy is to report true type | Designer's dream — clients don't game |
| **Individually rational (IR)** | Each player weakly prefers participating | Otherwise they opt out / build a workaround |
| **Budget-balanced** | Total payments net to zero (or non-negative for designer) | Internal chargeback, ad auctions |
| **Pareto efficient** | No reallocation makes everyone better off | "No money left on the table" |
| **VCG (Vickrey–Clarke–Groves)** | A general truthful mechanism family | Each player pays the externality they impose |
| **Vickrey (second-price) auction** | Highest bidder wins, pays second-highest bid | Truthful: bid your true value |
| **Revelation principle** | Any equilibrium of any mechanism can be implemented by a truthful direct mechanism | Justifies focusing on truthful designs |
| **Mechanism-induced behaviour** | What the rule causes players to do | The actual production of "the rule" |
| **Coalition-resistance** | No subset can improve by jointly deviating | Critical when collusion is cheap |
| **Sybil attack** | One real player masquerading as many | Punctures any per-account limit |
| **Externality** | A cost imposed on others by one player's action | Noisy-neighbour load on a shared queue |
| **Side payment / transferable utility** | Players can compensate each other | Available in money systems; rare in pure tech protocols |

### A few classical results worth knowing

- **Vickrey auction** is truthful: bidding your true value is dominant. Used in ad systems, GPU spot markets.
- **VCG** generalises Vickrey: charge each agent the cost their participation imposes on others. Truthful for many allocation problems.
- **Gibbard–Satterthwaite**: any deterministic, non-dictatorial voting rule with ≥3 outcomes is manipulable. Be honest that perfect strategy-proofness is rare.
- **Myerson’s revenue-equivalence**: for the auction-theory case, expected revenue depends on the allocation rule and the lowest type's payment, not the surface form.

## The Process

### Step 1: Specify the Players, Types, and Payoffs

Write down, in this order:

```
PLAYERS:
- [class of agent, count, repeatability]

TYPES (private info):
- For each player: what they know that you don't

ACTIONS:
- The set of moves available

PAYOFFS:
- For each (action profile, type profile): what each player gets
- The designer's objective (efficiency, revenue, fairness, robustness)
```

If you cannot fill this in, you are not designing a mechanism — you are wishing.

Weak:

> The rate limit is 100 req/s per tenant. Tenants should self-regulate to fairness.

Strong:

> Players: tenants, ~500, repeated daily. Types: each tenant's true peak demand (private). Actions: choose request rate, optionally prepay for higher tier, batch into bulk endpoint. Payoffs: tenant utility = throughput − latency cost − dollars; system payoff = aggregate utility minus saturation cost. Self-regulation is *not* an action — there is no payoff for restraint without a mechanism that rewards it.

### Step 2: Trace the Best Response to the Naive Rule

Before designing the mechanism, examine what the naive rule *induces*. This usually exposes the gap.

```
Naive rule: "100 req/s per tenant, drop excess"
Best response:
- Open multiple tenant accounts (Sybil)
- Push the rate to exactly 100 always (claim the buffer)
- Retry aggressively on drop (amplify load)
- Lobby for a higher cap rather than reduce demand
```

The naive rule's induced behaviour *is* the production system. Design for it, not for the cooperative wish.

### Step 3: Choose the Mechanism Family

Match the problem to a known family:

| Problem | Mechanism family |
| --- | --- |
| Allocate scarce capacity to highest-value uses | Auction (Vickrey, VCG) |
| Match two-sided populations | Stable matching (Gale–Shapley) |
| Enforce externality costs | Pigouvian pricing / VCG payments |
| Bound consumption with truthful priority | Token buckets + priority lanes with cost |
| Decentralised consensus among self-interested nodes | Cryptoeconomic mechanism (stake, slashing) |
| Aggregate preferences into a decision | Voting (with full awareness of Gibbard–Satterthwaite) |
| Provide a public good with voluntary contribution | Quadratic funding, matching pools |

If your situation matches a classical family, *use it* — the equilibrium analysis is done. Resist re-deriving.

### Step 4: Verify the Equilibrium

For the proposed mechanism, check:

1. **Best response of each player given others' strategies** — write it out.
2. **Is there a dominant strategy?** If yes, the mechanism is strategy-proof and you're done up to robustness.
3. **If not, is there a Nash equilibrium?** Is it unique? Is it the cooperative one?
4. **Is participation individually rational?** A truthful mechanism that drives players to opt out is useless.
5. **Is the equilibrium stable** under small perturbations and noisy execution?

```
EQUILIBRIUM ANALYSIS:
- Each player's best response:
- Equilibrium concept (dominant / Nash / mixed):
- Uniqueness: yes / no / multiple — which is selected?
- Individual rationality: yes / no
- Stability under noise:
```

If you cannot identify the equilibrium, you don't yet have a mechanism — you have a wish dressed as a rule.

### Step 5: Stress-Test for Manipulation

For each player class, attempt to design a manipulating strategy. Have someone red-team adversarially.

| Manipulation | Mitigations |
| --- | --- |
| Sybil (one real player, many accounts) | Identity binding, per-org limits, costly identity, proof-of-work/stake |
| Collusion (small coalition coordinates) | Coalition-resistant mechanism (e.g., VCG is partially robust); detection of correlated behaviour |
| Misreporting type | Make truthful reporting dominant, or audit + penalise |
| Ballot-stuffing / spam | Cost of action, captcha, rate-limit on identity |
| Exploiting tie-breakers | Randomise tie-breaks; document; don't reward a particular strategy with deterministic ties |
| Off-path behaviour the model didn't consider | Explicit "any other behaviour gets no benefit" defaults |

### Step 6: Check Composition and Side Markets

Mechanisms compose, often badly. A truthful mechanism for one resource may interact perversely with the truthful mechanism for the next.

- Does this mechanism create incentives at the boundary with another mechanism? (e.g., quota system + retry budget — clients arbitrage between)
- Is there a side market that subverts the mechanism? (e.g., reselling allocations off-platform)
- Does the mechanism produce private information that becomes the lever for the next manipulation?

When composition risk is high, prefer mechanisms that are self-contained with explicit boundaries.

### Step 7: Specify the Mechanism in Implementation Terms

A mechanism only works if implemented faithfully. Translate:

```
IMPLEMENTATION SPEC:
- Inputs (reports / actions accepted from each player):
- Allocation function (who gets what):
- Payment / penalty function (who pays / loses what):
- Tie-breaking rule:
- Logged evidence (for dispute and audit):
- Invariants the implementation must preserve:
```

Implementation deviations from the spec break the equilibrium proof. The most common bug class: tie-breaking rule under-specified, attackers exploit the deterministic implementation choice.

### Step 8: Plan for Monitoring and Re-Equilibration

Mechanisms drift. Players learn. The world changes types. Plan:

- **Telemetry on actions**: distribution of behaviours by player class. Drift is the leading indicator of manipulation.
- **Audit cadence**: re-derive the equilibrium analysis under current observed behaviour.
- **Re-equilibration**: a process for changing the rule when drift is confirmed, ideally with notice and migration to avoid breaking individual rationality of existing players.

A rule deployed and never re-examined becomes a manipulation surface within 1–2 player learning cycles.

## Output Format

```
MECHANISM DESIGN

Problem statement:
- Designer objective:
- Constraint set (budget-balance, IR, fairness, robustness):

Players:
- Class, count, repeatability, anonymity, observability

Types:
- Private information per player

Actions:
- Action set per player

Payoffs:
- Per (action profile, type profile)

Naive rule and its induced behaviour:
- Rule:
- Best response:
- Why it fails:

Proposed mechanism:
- Family:
- Allocation function:
- Payment / penalty function:
- Tie-breaking:

Equilibrium analysis:
- Best responses:
- Equilibrium concept:
- Uniqueness, IR, stability:

Manipulation analysis:
- Sybil:
- Collusion:
- Misreporting:
- Tie-break exploitation:
- Off-path behaviour:

Composition risks:
- Adjacent mechanisms:
- Side markets:

Implementation spec:
- Inputs / allocation / payment / tie-break / logging / invariants

Monitoring & re-equilibration:
- Telemetry:
- Audit cadence:
- Change procedure with player notice:
```

## Anti-Patterns to Avoid

- **"Users should…"**: any rule whose enforcement depends on cooperative restraint is not a mechanism — it is wishful thinking, and the deviators dominate within a few cycles.
- **Designing for the average player**: equilibrium is set by the *most strategic* player, not the median. The well-behaved 95% are irrelevant if the 5% capture all the rents.
- **Skipping the best-response trace**: deploying a rule without writing out what a rational player will do is the most common failure mode.
- **Ignoring Sybils and side markets**: per-account limits punctured by free signup; allocations resold off-platform.
- **No tie-breaking spec**: deterministic implementation tie-breaks become the lever of manipulation; randomise or specify.
- **No re-derivation**: deploying once and never re-examining as players learn — the mechanism that worked at launch is the manipulation surface a year later.
- **Assuming truthful reporting without paying for it**: only specific mechanism families *make* truth dominant; "we asked them to be honest" doesn't.
- **Composing mechanisms without analysis**: each is fine alone; together they create arbitrage.

## Relationship to Other Skills

- Use `incentive-analysis` to *describe* what players will do under a rule; use this skill to *construct* the rule so the description is the desired behaviour.
- Use `adversarial-design-review` to red-team the proposed mechanism — players are adversaries with their own objectives.
- Use `feedback-loop-analysis` for the dynamics: equilibria assume convergence; the loop tells you whether the system actually settles.
- Use `market-microstructure` for the schedulers and matchers in particular — order books are mechanisms with their own well-studied equilibria.
- Use `mistake-proofing` for the implementation: tie-breaks and edge cases that can be made structurally unexploitable should be.
- Use `factor-of-safety` for the resource side — even an incentive-aligned mechanism needs margin for the tail of strategic play.
- Use `signal-detection-review` to set thresholds for "behavioural drift" alerts that trigger re-equilibration.
