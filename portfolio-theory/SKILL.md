---
name: portfolio-theory
description: Apply Markowitz mean-variance portfolio theory to technical bets — diversify across uncorrelated risks rather than stacking many bets of the same kind.
user-invocable: true
---

# Portfolio Theory

Act as a portfolio manager evaluating a basket of technical bets. Your job is not to pick "the best" choice but to assemble a set of choices whose risks do not all fail together. Most engineering portfolios — dependencies, vendors, services, experiments — look diversified but secretly load up on a single hidden risk factor.

Success looks like: surviving the worst plausible correlated shock with acceptable damage. Failure looks like five "independent" bets that all crater on the same Tuesday because they shared an upstream maintainer, region, paradigm, or assumption. Quality of individual picks matters less than the correlation structure between them.

## When to Use This

- Choosing dependencies, vendors, cloud providers, or third-party APIs
- Designing a microservice or module split
- Allocating engineering effort across experiments, prototypes, or research bets
- Reviewing infrastructure for single-point-of-correlation failures
- Evaluating "we should standardize on X" proposals
- Deciding how many parallel approaches to run on an uncertain problem
- Reviewing an architecture where multiple components share a hidden dependency

**Escape hatch**: For a single isolated decision with no portfolio context (one tool, one bug, one PR), this lens adds little. Use it when you have *several* bets and want to reason about how they fail together.

## Core Mindset

Ask not "is this the best choice?" but "what does this choice add to the portfolio I already hold?"

- What is the **correlation structure** of my current bets?
- Which risks are **systematic** (affect every bet) vs **idiosyncratic** (affect one)?
- What is the **excess return** (alpha) for the **risk** taken (sigma)?
- Where am I getting **diversification for free**, and where am I paying for fake diversification?
- What single event would take down 3+ of these bets at once?
- Am I being paid to hold this risk, or am I taking it for free?

## Domain Vocabulary

| Term | Finance meaning | Engineering analog |
| --- | --- | --- |
| **Expected return** | Mean payoff of an asset | Expected value delivered by a bet |
| **Variance / sigma** | Volatility of returns | Uncertainty in outcome / time / cost |
| **Covariance** | How two assets move together | Whether two bets fail together |
| **Correlation (ρ)** | Normalized covariance, –1 to +1 | Shared failure mode strength |
| **Beta (β)** | Sensitivity to the market | Sensitivity to a shared factor (e.g., AWS us-east-1) |
| **Alpha (α)** | Excess return above benchmark | Differentiated value vs default choice |
| **Sharpe ratio** | (Return – risk-free) / sigma | Value per unit of uncertainty taken on |
| **Efficient frontier** | Best return for each risk level | Pareto frontier of bet portfolios |
| **Systematic risk** | Cannot be diversified away | Shared infra, shared paradigm, shared vendor |
| **Idiosyncratic risk** | Specific to one asset, diversifiable | Bug in one library, one team's mistake |
| **Tail risk** | Rare extreme events | Region outage, supply chain compromise |

## The Process

### Step 1: Enumerate the Portfolio

List every bet you currently hold or are considering. Be honest — bets you forgot about still count.

```
PORTFOLIO:
- Bet 1: [name] — what it does, expected payoff, expected cost
- Bet 2: ...
- Existing exposures (already-owned bets): ...
- Proposed additions: ...
```

Common engineering portfolios:
- npm dependencies in `package.json`
- Cloud regions and AZs you're deployed to
- Third-party SaaS vendors (auth, observability, email, payments)
- Active experiments / A-B tests
- In-flight refactors or migrations
- Services in your microservice graph

### Step 2: Identify Risk Factors

For each bet, list the underlying factors it is exposed to. The factors — not the bets themselves — are what correlate.

```
BET → FACTORS:
- Bet 1: [maintainer X, language Y, region Z, paradigm P, vendor V]
- Bet 2: ...
```

Common hidden factors that secretly bind "independent" bets:
- Same maintainer or org (e.g., five npm packages by `sindresorhus`)
- Same cloud region (us-east-1 outage takes down everything)
- Same upstream dependency (left-pad, log4j)
- Same paradigm assumption (everything assumes synchronous I/O)
- Same data store (Postgres outage = total outage)
- Same team (one team owns 4 of the 5 critical services)
- Same funding source / commercial backer

### Step 3: Build a Correlation Matrix

For each pair of bets, estimate correlation on a coarse scale.

```
        | Bet1 | Bet2 | Bet3 | Bet4 |
Bet1    | 1.0  | 0.9  | 0.2  | 0.0  |
Bet2    |      | 1.0  | 0.3  | 0.1  |
Bet3    |      |      | 1.0  | 0.7  |
Bet4    |      |      |      | 1.0  |
```

Coarse buckets are fine: 0.0 (independent), 0.3 (loose), 0.7 (tight), 0.9+ (effectively the same bet).

**The Markowitz insight**: portfolio variance is not the average of variances — it depends heavily on covariances. Two bets with ρ = 0.9 give you almost no diversification. Two bets with ρ = 0.0 cut variance in half. Two bets with ρ = –0.5 (rare in engineering!) actively reduce risk.

### Step 4: Decompose Systematic vs Idiosyncratic

For each bet, split risk:

- **Systematic** (β-driven): risk shared across the portfolio — cloud provider down, language ecosystem dies, JS runtime breaks
- **Idiosyncratic** (α-driven): risk unique to that bet — bug in this one library

Diversification removes only idiosyncratic risk. If 80% of your portfolio risk is systematic (e.g., "everything is AWS us-east-1"), adding more AWS us-east-1 services does not diversify you.

### Step 5: Score Each Bet — Sharpe-Style

For each candidate bet, ask:

```
BET: [name]
- Expected value (return):
- Uncertainty (sigma):
- Correlation with existing portfolio (avg ρ):
- Marginal diversification benefit (high if ρ low):
- Sharpe-like score: (expected value) / (sigma × (1 + correlation penalty))
```

A mediocre bet that is uncorrelated with your current holdings often beats a great bet that piles onto an existing exposure.

Weak reasoning: "Library X is the best parser." → Adopt it.
Strong reasoning: "Library X is the best parser, but we already use 3 packages by the same maintainer. The marginal diversification is negative — a maintainer compromise takes out 4 deps. Use Y, which is 80% as good but uncorrelated."

### Step 6: Stress Test Correlated Shocks

Diversification is most needed precisely when it disappears. In financial crises, correlations spike toward 1.0 — assets that "never moved together" suddenly all crash. Engineering equivalent: in a major incident, risks compound.

Run scenarios:

```
SCENARIO: us-east-1 down for 4 hours
- Which bets fail? [list]
- What is left running? [list]
- Is the surviving subset enough to operate?

SCENARIO: maintainer X publishes malicious version
- Which bets fail? ...

SCENARIO: a 0-day in the JS runtime
- Which bets fail? ...
```

If a single scenario takes down >50% of the portfolio, you have a hidden concentration.

### Step 7: Recommend Rebalancing

For each high-correlation cluster, choose one:

| Action | When |
| --- | --- |
| **Reduce exposure** | Cluster is too large; trim or replace one bet |
| **Hedge** | Add an explicitly anti-correlated bet (multi-region, alt vendor) |
| **Accept** | Concentration is intentional, cost of diversifying exceeds benefit |
| **Insure** | Buy a fallback (see `hedging-and-insurance`) |
| **Disclose** | Document the concentration so future decisions account for it |

Prefer fewer, more uncorrelated bets over many bets of the same flavor.

### Step 8: Mind the Limits of Diversification

- Diversification cannot eliminate systematic risk — only redistribute idiosyncratic risk
- More bets ≠ more diversification if correlations are high
- Diversification has costs: cognitive load, integration surface, ops burden
- Past correlation is an estimate, not a guarantee — assume ρ rises in a crisis
- A perfectly diversified portfolio of garbage is still garbage; quality and diversification multiply, they don't substitute

## Output Format

```
PORTFOLIO REVIEW

Portfolio under review:
- ...

Risk factors identified:
- Systematic: ...
- Idiosyncratic: ...

Correlation hot spots:
- Cluster 1: [bets] sharing factor [X]
- ...

Stress test results:
- Scenario: [event] — [N]/[total] bets fail

Recommended rebalancing:
1. ...

Concentrations explicitly accepted:
- ...

Open questions:
- ...
```

## Anti-Patterns to Avoid

- **Counting bets, not factors**: "We have 10 vendors" means nothing if 8 are on the same cloud
- **Confusing variety with diversification**: 5 different ORMs all hitting the same Postgres is one bet
- **Optimizing each bet in isolation**: locally optimal picks can be globally concentrated
- **Ignoring correlation spikes in tails**: "they've never failed together" is not evidence about extreme events
- **Diversification theater**: multi-cloud where 99% of traffic is on one cloud is single-cloud
- **Adding bets to "diversify"**: more bets only help if they are uncorrelated; otherwise they add cost without reducing risk
- **Forgetting the maintainer dimension**: deps don't fail at random; they fail by author, ecosystem, or supply chain

## Relationship to Other Skills

- Use `failure-mode-effects-analysis` to enumerate per-bet failure modes before correlating them
- Use `hedging-and-insurance` once concentrations are identified and you want to transfer risk
- Use `system-ecosystem-analysis` for the broader cascading-failure view across the dependency graph
- Use `network-topology-review` to find hidden shared nodes that drive correlation
- Distinct from `incentive-analysis`, which is about how actors respond to rules, not how risks co-move
