---
name: hedging-and-insurance
description: Risk transfer and pooling — design redundancy, error budgets, multi-region, backups, and on-call as deliberate insurance instruments with explicit premiums.
user-invocable: true
---

# Hedging and Insurance

Act as a corporate treasurer designing the firm's risk-transfer program. Every redundancy, replica, backup, multi-region deployment, vendor contract, and on-call rotation is a form of **insurance**: you pay a recurring premium so that, when a specific bad event occurs, someone or something else absorbs the loss.

Engineering teams routinely buy insurance accidentally (over-provisioning everything) or fail to buy obvious insurance (one DB, no backups, single-vendor). The treasurer's job is to make the policies **explicit**: what is the premium, what is the deductible, what's the payout, what's the basis risk, and is the cost of insurance justified by the cost of the loss it covers?

Success looks like: every redundancy has a named risk it covers, an explicit premium, and a clear failure mode it does *not* cover. Failure looks like paying premiums on irrelevant policies (multi-region for a tool nobody uses) while the real risk (the one Postgres) sits uninsured.

## When to Use This

- Designing redundancy, replication, or multi-region architecture
- Setting SLO error budgets, retry budgets, or rate limits
- Choosing backup strategy and disaster recovery posture
- Multi-vendor / multi-cloud decisions
- On-call rotation design and team coverage
- Reviewing "what if X fails?" arguments
- Negotiating SLAs with vendors
- Deciding when to self-insure (accept the loss) vs transfer (pay someone else)

**Escape hatch**: For systems where downtime/data-loss has trivial cost, formal insurance analysis is overkill. Use this when the cost of the worst-case event is real and the cost of the insurance is non-trivial.

## Core Mindset

Ask:

- What **specific risk** does this redundancy / backup / contract cover?
- What is the **premium** (recurring cost: $, eng-time, complexity)?
- What is the **deductible** (loss you absorb before insurance kicks in)?
- What is the **payout** (loss avoided when event occurs)?
- What is the **basis risk** (does your hedge actually pay when you need it)?
- Are you creating **moral hazard** (cheap insurance making people careless)?
- Is this risk best **transferred, pooled, hedged, or self-insured**?

## Risk Transfer Vocabulary

| Term | Finance meaning | Engineering analog |
| --- | --- | --- |
| **Hedge** | Offsetting position to reduce exposure | Multi-region, multi-AZ, multi-vendor |
| **Long position** | You profit if X goes up | You depend on vendor X being available |
| **Short position** | You profit if X goes down | Rare in engineering — chaos engineering is a kind of "going short" your own resilience |
| **Protective put** | Right to sell at a fixed price | Backup that lets you "sell back" to a known-good state |
| **Premium** | Cost paid for insurance | Multi-AZ cost, replica cost, eng complexity tax |
| **Deductible** | Loss you absorb first | Error budget; brief outages you accept |
| **Coverage limit** | Max payout from policy | RTO/RPO; max recovery time/data loss |
| **Reinsurance** | Insurer's insurance | Vendor's vendor (e.g., your SaaS uses AWS) |
| **Basis risk** | Hedge doesn't perfectly track exposure | Multi-region but shared control plane fails together |
| **Moral hazard** | Insurance reduces care | "We have backups" → less care with prod |
| **Adverse selection** | Only the worst risks buy insurance | Only the unreliable services get extra alerting |
| **Risk pooling** | Many parties share idiosyncratic risk | On-call rotation; shared incident response |
| **Self-insurance** | Set aside reserves vs buying policy | Accept downtime; budget for incident response |

## The Process

### Step 1: Name the Specific Risk

Insurance only works when the covered event is precisely defined. "Things might go wrong" is not insurable.

```
RISK:
- Event: [precise: "Postgres primary unavailable for >5 min"]
- Probability per period: [annualized estimate]
- Loss if event occurs: [revenue / SLA / reputation / data]
- Detection time: [how long until we notice]
```

If you can't write this down, you can't price insurance for it.

### Step 2: Inventory Existing Policies

For each redundancy/backup/contract, write the policy out in insurance terms.

```
POLICY: Cross-AZ Postgres replica
- Covers: AZ-level outage (one of 3 AZs goes down)
- Does NOT cover: regional outage, logical corruption, accidental DROP
- Premium: ~$X/month + replica lag complexity
- Deductible: ~30 sec failover time
- Coverage limit: full DB
- Basis risk: shared control plane in same region
```

This format alone reveals when a policy is misnamed (e.g., a replica being marketed internally as a "backup," when it doesn't cover deletes).

### Step 3: Match Policies to Risks

Build a matrix:

```
                    | AZ outage | Region outage | Logical corruption | Accidental delete | Vendor bankruptcy |
Cross-AZ replica    |    ✓      |       ✗       |         ✗          |         ✗         |         ✗         |
Cross-region replica|    ✓      |       ✓       |         ✗          |         ✗         |         ✗         |
Daily snapshot      |    ✓      |  partial      |         ✓          |         ✓         |     partial       |
PITR (WAL archive)  |    ✓      |  partial      |         ✓          |         ✓         |     partial       |
Multi-vendor SaaS   |    ✗      |       ✗       |         ✗          |         ✗         |         ✓         |
```

The point is to find:
- **Uninsured risks** (a column with no ✓): you're self-insuring whether you intended to or not
- **Over-insured risks** (a column with many ✓): you may be paying multiple premiums for the same coverage
- **Misnamed policies**: a "backup" that doesn't cover delete is not a backup

### Step 4: Compute the Premium-vs-Loss Trade-off

For each policy, ask: is the premium less than (probability × loss)?

```
INSURANCE WORTH IT?
- Annual premium: $P
- Annual probability of event: p
- Expected annual loss without insurance: L
- Worth it if: P < p × L (very roughly)
- Adjust upward for: variance aversion, regulatory requirements, tail risk
- Adjust downward for: imperfect coverage (basis risk), moral hazard cost
```

Worked example:
- Multi-region active/active premium: ~30% infra cost + significant complexity tax
- Probability of full-region outage per year: ~1%
- Expected loss in a regional outage: 4 hours × $X/hour
- Worth it only if you're risk-averse beyond expected value (regulatory, brand, contractual SLA)

Most multi-region setups are bought for **variance reduction** and **SLA compliance**, not pure expected-value math. Be honest about which.

### Step 5: Identify Basis Risk

Basis risk = your hedge doesn't actually fire when the bad event occurs. The most common engineering failure.

Examples:
- Multi-region active/passive — but the failover is untested and doesn't work
- Cross-AZ replica — but both AZs depend on the same regional control plane
- Multi-cloud DNS failover — but the DNS provider itself goes down
- Backups exist — but no one has tested restore in 18 months
- On-call exists — but the alert routing is broken

Stress test:

```
BASIS RISK CHECK:
- When was this hedge last exercised in anger?
- When was it last tested in a drill?
- What hidden dependencies does it share with the thing it protects?
- Does the failover path itself depend on the failed system?
```

An untested hedge is a hedge with unknown basis risk — assume it's high.

### Step 6: Watch for Moral Hazard and Adverse Selection

**Moral hazard**: insurance changes behavior. If "we have backups" leads to careless `DELETE` queries, the insurance has created the very risk it covers. Mitigate with deductibles (manual restore is painful) and audit logs.

**Adverse selection**: only the riskiest things end up insured. The shaky service gets extra alerting and runbooks; the rock-solid one is ignored — until the rock-solid one fails and no one knows what to do. Mitigate by insuring proportionally to *value*, not just *current trouble*.

### Step 7: Decide: Transfer, Pool, Hedge, or Self-Insure

For each significant risk, choose:

| Strategy | When | Engineering example |
| --- | --- | --- |
| **Transfer** (buy insurance) | High loss, low frequency, premium reasonable | Backup vendor, managed DB with SLA |
| **Pool** (share with others) | Many parties have similar idiosyncratic risk | On-call rotation, shared SRE team |
| **Hedge** (offsetting position) | Continuous exposure to a price/availability risk | Multi-region, multi-vendor |
| **Self-insure** (accept) | Loss is small, frequent, or premium too high | Internal tools, beta features |
| **Avoid** (don't take risk) | Loss intolerable, no good insurance | Don't store the data in the first place |

A risk treated with the wrong strategy is wasted money: self-insuring a catastrophic loss is reckless; buying insurance for a trivial loss is wasteful.

### Step 8: Set the Deductible Explicitly

SLOs and error budgets are the engineering version of deductibles. They define the loss you absorb before the policy kicks in.

```
DEDUCTIBLE DESIGN:
- SLO target: 99.9% (43 min/month deductible)
- What triggers escalation: deductible exhausted
- What triggers feature freeze: deductible exhausted 2 months running
- What triggers postmortem: any single event > N% of monthly budget
```

A deductible that is never enforced is not a deductible — it's a wish. Tie it to actual decisions.

## Output Format

```
HEDGING & INSURANCE REVIEW

Risks identified:
- ...

Existing policies:
- Policy: [name]
  - Covers: ...
  - Does NOT cover: ...
  - Premium: ...
  - Deductible: ...
  - Basis risk: ...

Coverage matrix (risks × policies):
- ...

Uninsured risks:
- ...

Over-insured risks:
- ...

Recommended changes:
1. Add coverage for [risk] via [transfer/pool/hedge]
2. Drop premium on [over-insured policy]
3. Test [hedge] to reduce basis risk

Self-insured risks (explicitly accepted):
- ...
```

## Anti-Patterns to Avoid

- **Untested hedges**: insurance you never claim against has unknown basis risk
- **Unnamed policies**: redundancy without an explicit covered risk is theater
- **Calling replicas backups**: a replica that propagates `DROP TABLE` is not a backup
- **Premium creep**: adding redundancies without ever removing obsolete ones
- **Moral hazard ignored**: cheap recovery breeds careless production behavior
- **Self-insuring catastrophes**: accepting risks whose realized loss you cannot survive
- **Insuring trivia**: paying real premiums for losses you'd happily absorb
- **Deductibles on paper only**: error budgets that are never enforced are wishes, not policies

## Relationship to Other Skills

- Use `failure-mode-effects-analysis` to enumerate the risks before pricing insurance for each
- Use `resilience-engineering` for the broader graceful-degradation design — insurance is one tool inside it
- Use `portfolio-theory` to check whether your hedges share hidden correlation (multi-region in same provider)
- Use `operational-game-day` to actually test hedges and discover basis risk
- Use `signal-detection-review` to ensure the alerts that trigger insurance payouts (failover, paging) are calibrated
