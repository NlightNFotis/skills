---
name: market-microstructure
description: Apply order-book mechanics — bid/ask, queue position, latency arbitrage, batch vs continuous matching — to schedulers, load balancers, and any system that matches supply to demand.
user-invocable: true
---

# Market Microstructure

Act as a market microstructure analyst evaluating a matching engine. Markets and engineering systems both face the same core problem: matching heterogeneous supply (capacity, sellers) to heterogeneous demand (jobs, buyers) under latency, fairness, and adversarial pressure. The discipline that studies how the *rules of matching* — order types, priority, batching, tick size — affect outcomes is called market microstructure, and it transfers directly to schedulers, load balancers, autoscalers, ad systems, and queue-based resource allocation.

Success looks like: explicit choices about who waits, who jumps the queue, what counts as "fair," and how the rules will be gamed. Failure looks like a scheduler whose emergent behavior nobody understands, where high-priority jobs starve, latency arbitrage by clever clients destroys fairness, or batch dynamics create thundering herds.

## When to Use This

- Designing or tuning a job scheduler / queue / priority system
- Load balancer or routing policy review
- Autoscaler design (matches incoming demand to capacity)
- Ad serving, bidding systems, recommendation ranking
- GPU / accelerator scheduling for ML workloads
- Rate limiting and admission control
- Fairness vs throughput trade-offs in resource allocation
- Multi-tenant systems with priority tiers

**Escape hatch**: For systems with one consumer and one resource type, microstructure is overkill. Use when there are multiple producers, multiple consumers, contention, and the *rules of matching* are themselves a design choice.

## Core Mindset

Ask:

- Who is on the **bid** side (demand) and who is on the **ask** side (supply)?
- What is the **spread** — the gap between what demand offers and what supply requires?
- Who **makes** vs **takes** — provides liquidity vs consumes it?
- What **priority rules** govern the match (FIFO, price, size, age)?
- How does **queue position** translate to outcome, and is the queue visible?
- Is matching **continuous** or **batched** — and what dynamics does each create?
- Where can **latency arbitrage** extract value, and at whose expense?

## Microstructure Vocabulary

| Term | Market meaning | Engineering analog |
| --- | --- | --- |
| **Order book** | Sorted list of outstanding bids and asks | Queue of pending jobs and available workers |
| **Bid / ask** | Buyer's price / seller's price | Job's willingness to wait / worker's capacity cost |
| **Spread** | Ask – bid | Idle capacity sitting alongside unserved jobs |
| **Depth of book** | Volume at each price level | Queue length at each priority tier |
| **Market order** | Take any available price now | Run-now job, accepts any available worker |
| **Limit order** | Trade only at specified price or better | Job with deadline / SLO constraint |
| **Maker** | Posts a resting order, provides liquidity | Worker waiting for jobs |
| **Taker** | Crosses the spread, removes liquidity | Job matching the next available worker |
| **Tick size** | Minimum price increment | Time/resource quantization (1ms, 1 vCPU) |
| **Price-time priority** | Best price wins; ties broken by who arrived first | Highest priority first; FIFO within tier |
| **Queue position** | Your rank in the queue at your price | Your rank in the priority tier |
| **Latency arbitrage** | Exploit speed advantage to skim | Fast clients consistently beating slow ones for same resource |
| **Slippage** | Price moves against you while executing | Job's effective cost rises (waiting longer than expected) |
| **Continuous matching** | Match on each event arrival | Standard scheduler |
| **Batch auction** | Collect orders, match periodically | Window-based scheduling, batch billing, periodic GC |
| **Price discovery** | Process by which the clearing price emerges | Implicit: where queues actually clear |

## The Process

### Step 1: Identify the Market

Make the matching problem explicit.

```
MARKET:
- What's being matched: [jobs ↔ workers, requests ↔ servers, bids ↔ impressions]
- Bid side (demand): who/what, arrival rate, willingness to wait
- Ask side (supply): who/what, availability rate, cost per unit
- Match unit (tick): smallest divisible unit (1 request, 1 GPU-hour, 1 ms)
- Visible state: what does each side know about the order book?
```

If you can't describe both sides in market terms, you may not actually have a matching system — you might just have a queue.

### Step 2: Map the Order Book

Sketch the current state of demand and supply.

```
DEMAND SIDE (bids):
- Tier 1 (highest priority): N jobs, avg wait W
- Tier 2: ...
- Tier 3: ...

SUPPLY SIDE (asks):
- Pool A: N workers, capacity C
- Pool B: ...

SPREAD:
- Are there idle workers while jobs wait? (positive spread = matching inefficiency)
- Are there pending jobs while no workers exist? (capacity shortfall)
```

A positive spread (idle supply + waiting demand) is a microstructure red flag — the matching rules are failing even though aggregate capacity is sufficient.

### Step 3: Choose the Priority Rule

The single most consequential decision. Common rules and their failure modes:

| Rule | Engineering example | Failure mode |
| --- | --- | --- |
| **FIFO** | Plain queue | High-priority jobs starve behind low-priority |
| **LIFO** | Stack | Old jobs starve forever |
| **Price-time** | Bid-weighted with FIFO tie-break | Wealthy/high-priority dominate; needs anti-gaming |
| **Strict priority** | Multi-level queue | Lower tiers can starve indefinitely |
| **Weighted fair queueing** | Proportional share | Complex; harder to predict tail latency |
| **Earliest deadline first** | Deadline scheduling | Cascading missed deadlines under overload |
| **Shortest job first** | Throughput-optimal | Starves long jobs; gameable by underestimating size |
| **Random** | Lottery | Fair in expectation; high variance |

For each rule, ask: who **starves**? Every priority rule starves *someone* under contention — be explicit about who.

### Step 4: Continuous vs Batch Matching

Continuous: match on every arrival. Predictable per-event but susceptible to latency arbitrage and microbursts.

Batch: collect over a window, match in one shot. Eliminates latency arbitrage within the window, but creates thundering herd at window boundary and adds latency floor.

```
WHEN BATCH BEATS CONTINUOUS:
- Latency arbitrage is destroying fairness
- Matching has high fixed cost (amortize across batch)
- Throughput > latency (analytics, billing)
- Need to clear with a single price (auctions)

WHEN CONTINUOUS BEATS BATCH:
- Latency-sensitive (interactive requests)
- Demand is bursty and you must absorb spikes immediately
- Workers are heterogeneous and matching is per-pair
```

Hybrid systems (frequent micro-batches) often capture most of the benefit of each.

### Step 5: Watch for Latency Arbitrage

If clients/jobs at different latencies see the same order book, fast clients will consistently beat slow ones for the most desirable matches. This is fine in HFT (markets price it in) but usually unintended in engineering.

Symptoms:
- Same-priority jobs with different physical proximity systematically get different outcomes
- Polling-loop clients dominate event-driven clients
- A "fair" scheduler that consistently favors clients in one region/datacenter

Mitigations:
- Batch matching (eliminates intra-window latency advantage)
- Random tie-breakers within priority tier
- Latency floor (no match faster than T)
- Per-client throttling so latency advantage doesn't compound

### Step 6: Check for Slippage and Queue Visibility

**Slippage**: the cost of executing was worse than expected. In engineering: the job waited longer or used more resources than the user planned for.

**Queue visibility**: do users see the depth of book? Visible queues let users self-throttle and back off. Invisible queues lead to retry storms (users who can't see the queue retry, growing it).

```
QUEUE VISIBILITY CHECK:
- Do callers know their queue position?
- Do they know expected wait time?
- Do they see overall load?
- If not: are they likely to retry, making it worse?
```

Returning `429` with a `Retry-After` is exposing queue depth. Returning `500` with no signal invites retry storms.

### Step 7: Stress Test the Matching Rules Under Adversarial Load

Microstructure failures usually appear under stress, not normal load. Run thought experiments:

```
SCENARIOS:
- 10× normal demand: who starves first? does priority hold?
- 10× normal supply (idle): is the spread fully closed, or do matches still wait?
- One client sends 1000× normal volume: do they starve other clients?
- One worker is 100× faster: does it dominate the match flow?
- Adversarial client games priority signals (claims max priority, tiny size): can they?
- Demand briefly drops to zero, then bursts: does batching create a thundering herd?
```

Note any case where the matching outcome is "surprising" — that's where bugs and customer escalations live.

### Step 8: Recommend Microstructure Changes

For each identified failure mode, choose targeted changes:

| Problem | Microstructure intervention |
| --- | --- |
| Lower tier starves | Add minimum share / aging boost |
| Latency arb | Switch to micro-batch; add jitter; uniform latency floor |
| Thundering herd at batch boundary | Sub-batches; randomized batch start times |
| Retry storms | Expose queue depth; return `Retry-After`; backoff |
| Gameable signals | Verify claimed priority/size; price abuse |
| Idle supply + waiting demand | Reduce match granularity; relax constraints |
| Tail latency | Speculative execution; hedge requests; redundant ask |

Prefer surgical rule changes (priority adjustment, batch window) over architectural rewrites.

## Output Format

```
MICROSTRUCTURE REVIEW

Market description:
- Bid side: ...
- Ask side: ...

Order book snapshot:
- Demand by tier: ...
- Supply by pool: ...
- Current spread: ...

Matching rule:
- Priority: ...
- Continuous / batch: ...

Who starves under contention:
- ...

Latency arbitrage exposure:
- ...

Queue visibility to clients:
- ...

Stress test failures:
- ...

Recommended interventions:
1. ...
```

## Anti-Patterns to Avoid

- **Default-FIFO without thought**: FIFO is a choice, not the absence of one — it has specific failure modes
- **Strict priority with no aging**: lower tiers starve forever; no one notices until they complain
- **Gameable size/priority signals**: anything self-reported and uncosted will be inflated
- **Hidden queues**: clients can't back off if they can't see depth → retry storms
- **Continuous matching with high coordination cost**: amortize via batching
- **Batch matching for latency-sensitive paths**: imposes latency floor, creates herds
- **Treating fairness as a single concept**: per-job, per-tenant, per-priority fairness conflict; pick one
- **Ignoring adversarial clients**: any tier system you ship will be gamed; design for it

## Relationship to Other Skills

- Use `feedback-loop-analysis` when retries, backoff, and queue depth interact dynamically
- Use `constraint-analysis` to identify whether the bottleneck is supply, demand, or the matching engine itself
- Use `incentive-analysis` to predict how clients respond to priority/pricing rules
- Use `signal-detection-review` for the alerting that detects starvation, queue blowups, and unfair matches
- Use `failure-mode-effects-analysis` for the broader catalog of how the matching system can fail
