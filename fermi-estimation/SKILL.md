---
name: fermi-estimation
description: Order-of-magnitude back-of-envelope reasoning for capacity, latency, cost, and feasibility — before optimizing or designing.
user-invocable: true
---

# Fermi Estimation

Act as Enrico Fermi at a whiteboard. Your job is to produce a defensible order-of-magnitude estimate for systems questions — capacity, latency, cost, throughput, feasibility — using base-10 arithmetic, conservative bracketing, and well-known reference points. The goal is not precision; it is to know whether a number is 10×, 100×, or 10,000× off, before anyone writes code.

A good Fermi estimate is wrong by less than a factor of 3 and arrives in under five minutes. It rules out entire design branches before they consume a sprint. A bad one is precise, untethered to physical limits, and confidently suggests building something that cannot work.

## When to Use This

- Sniff-testing a proposed design ("can this scale to 10M users?")
- Setting a latency or cost budget before writing a line of code
- Deciding whether an optimization is worth the effort
- Reviewing capacity claims in a design doc or RFC
- Sanity-checking a benchmark or performance regression
- Sizing a queue, pool, cache, batch, or rate limit
- Estimating cloud spend, bandwidth, or storage growth
- Asking "is this 10× or 1000× the budget?" when something feels wrong

**Escape hatch**: For a number you can simply measure cheaply, measure it. Fermi is for when measurement is impossible (future scale), expensive (production load tests), or premature (design phase).

## Core Mindset

- Round to powers of 10 early. Precision is fake confidence.
- Bracket: pessimistic estimate × optimistic estimate, take the geometric mean.
- Keep units explicit; dimensional analysis catches most errors.
- Anchor every step in something physical or well-known.
- One zero off is a worry. Two zeros off is a different problem entirely.

Ask:

- What is the unit of the answer?
- What is the upper bound (physics, light speed, RAM bandwidth)?
- What is the lower bound (one operation per request, minimum payload)?
- Is this within an order of magnitude of a reference number I trust?
- If I'm off by 10×, does the conclusion change?
- What single number, if I learned it, would tighten this most?

## Reference Points (Numbers Worth Memorizing)

Approximate, single-digit accuracy. Round generously.

### Latency ladder

| Operation | Time | In nanoseconds |
| --- | --- | --- |
| L1 cache reference | 1 ns | 1 |
| Branch mispredict | 5 ns | 5 |
| L2 cache reference | 4 ns | 4 |
| Mutex lock/unlock | 20 ns | 20 |
| Main memory reference | 100 ns | 100 |
| Compress 1 KB with zstd | 1–10 µs | 10³–10⁴ |
| Send 1 KB over 10 GbE | 1 µs | 10³ |
| SSD random read | 100 µs | 10⁵ |
| Round trip same datacenter | 500 µs | 5·10⁵ |
| HDD seek | 10 ms | 10⁷ |
| Round trip same continent | 30 ms | 3·10⁷ |
| Round trip cross-Atlantic | 80 ms | 8·10⁷ |
| Round trip cross-Pacific | 150 ms | 1.5·10⁸ |
| Light around the equator | 130 ms | 1.3·10⁸ |
| Cold-start a container | 1–10 s | 10⁹–10¹⁰ |

### Throughput / capacity

| Quantity | Approx |
| --- | --- |
| Sequential disk read | 1 GB/s SSD, 100 MB/s HDD |
| RAM bandwidth | 10–50 GB/s |
| 10 GbE | 1 GB/s, ~80k packets/s at MTU |
| HTTP/JSON request server, modest | 1k–10k req/s per core |
| Postgres simple read on commodity hw | 10k–50k QPS |
| Single Kafka partition | ~10 MB/s sustained |
| Search index, in-memory | 10k–100k QPS per node |
| Human reaction time | 200 ms |
| User-perceptible UI lag | 100 ms |
| "Feels instant" | 10 ms |

### Sizes & populations

| Thing | Approx |
| --- | --- |
| Seconds in a day | 86,400 ≈ 10⁵ |
| Seconds in a year | 3·10⁷ |
| ASCII chars per page | ~3·10³ |
| English words per book | ~10⁵ |
| World population | 8·10⁹ |
| US population | 3.3·10⁸ |
| Internet users | ~5·10⁹ |
| GitHub repos | ~5·10⁸ |
| Bytes in 1 GiB | ~10⁹ |

Memorize these. They convert vague scale claims into arithmetic.

## Estimation Patterns

| Pattern | Form | Example |
| --- | --- | --- |
| **Top-down population** | total ÷ rate | "How many piano tuners?" → households × pianos/household ÷ tunings/yr/tuner |
| **Bottom-up unit cost** | per-event cost × event rate | "Cost of telemetry?" → bytes/event × events/day × $/GB |
| **Rate × duration** | flow × time | "Storage growth?" → writes/s × bytes/write × seconds/year |
| **Capacity ÷ load** | resource ÷ per-user demand | "How many servers?" → req/s capacity per box ÷ peak req/s |
| **Speed-of-light bound** | distance / c | "Min cross-Atlantic RTT?" → 6000 km / c ≈ 20 ms one-way → 40 ms RTT |
| **Little's Law** | L = λW | concurrency = throughput × latency |
| **Amdahl** | speedup ≤ 1 / (s + (1−s)/p) | parallelism returns die at the serial fraction |
| **Pareto skew** | top 20% drives 80% | tail traffic vs head traffic |

## The Process

### Step 1: State the Question Precisely

```
QUESTION:
- Unknown:
- Unit of the answer:
- Time horizon (now / peak / 1 year):
- Acceptable error: ±2× / ±10× / order of magnitude
```

Vague questions ("can it scale?") produce vague answers. Replace with: "Can this serve 10M DAU at p99 < 200 ms within a $100k/mo budget?"

### Step 2: Decompose into Knowns and Sub-Estimates

Break the number into a product or sum of factors that are individually easier to estimate.

```
DECOMPOSITION:
answer = factor_1 × factor_2 × factor_3 / factor_4
- factor_1 = ... (known / estimated / referenced)
- factor_2 = ...
```

If a factor itself needs a Fermi estimate, recurse — but stop at 2–3 levels deep, or you've replaced one guess with five.

### Step 3: Bracket Each Factor

For each unknown factor, give a low and high estimate that you'd bet 9-to-1 brackets the truth.

```
factor_x: low = 10², high = 10⁴, geomean ≈ 10³
```

The geometric mean of low and high is your point estimate. Multiplying geomeans through gives a calibrated central estimate; multiplying low-to-low and high-to-high gives a credible range.

### Step 4: Multiply, Tracking Powers of 10

Work in scientific notation. Add exponents, multiply mantissas, round.

```
N events/day = 10⁷
bytes/event  = 10³
days/year    = 10²·⁵   (wait — ~3·10², so 10²·⁵)
total/year   = 10⁷ × 10³ × 10²·⁵ = 10¹²·⁵ ≈ 3·10¹² bytes/yr ≈ 3 TB/yr
```

Always sanity-check the units of the final number.

### Step 5: Sanity-Check Against Physical and Reference Limits

Compare your answer to:

- Speed of light over the relevant distance
- RAM / disk / network bandwidth of one machine
- Known scale of similar systems
- Per-event minimum bytes (a TCP packet has overhead; a row has indexes)
- Human-perceptible time scales

If your answer claims sub-RTT cross-region latency, sub-disk-seek random reads, or more bytes than fit on the planet's drives, the estimate or the design is broken.

### Step 6: Decide Whether the Conclusion Survives an Order of Magnitude

Ask: **if I'm wrong by 10× in the worst direction, does the design still work?**

| Case | Action |
| --- | --- |
| Robust at 10× worse | Ship the design |
| Borderline at point estimate, broken at 10× | Re-estimate the load-bearing factor with measurement |
| Broken at point estimate | Redesign before measuring |
| Works only if every factor is best-case | Redesign |

Most arguments are won at this step, not at step 4.

### Step 7: Identify the Highest-Leverage Unknown

Which single factor, if measured, would shrink the bracket most? That is what you should go measure or look up next. Don't waste effort tightening factors that don't move the answer.

## Output Format

```
FERMI ESTIMATE

Question:
- ...

Decomposition:
- answer = a × b × c / d

Per-factor brackets:
- a: [low, high] → point
- b: [low, high] → point
- c: [low, high] → point
- d: [low, high] → point

Result:
- Point estimate: ~ X (order of magnitude 10^N)
- 90% bracket: [low, high]

Sanity checks:
- vs physical limit (e.g., light, RAM bandwidth):
- vs reference system:
- units check:

Conclusion:
- Robust to 10×? yes / no
- Decision: proceed / redesign / measure first

Highest-leverage unknown to measure next:
- ...
```

## Worked Mini-Example

> Can we serve 1M DAU of a chat app from one region with one Postgres primary?

- DAU = 10⁶, peak factor 10× over avg → peak concurrent ~ 10⁵
- Messages/user/day = 10² → 10⁸ msgs/day = ~10³ msgs/s avg, ~10⁴ peak
- Each msg = 1 write + ~3 reads (sender, recipient, history) → ~5·10⁴ QPS peak
- Single Postgres reference: ~10⁴–5·10⁴ QPS for simple ops
- Conclusion: at the edge; not robust to 10× growth or to slower queries. Plan a read replica path now; redesign for sharding before 10M DAU.

## Anti-Patterns to Avoid

- **False precision** — "we'll need 4,832 cores" from estimates good to 3×
- **Ignoring units** — bytes vs bits, per-second vs per-day, peak vs average
- **Single-point estimates with no bracket** — you cannot tell if you're robust
- **Anchoring on a vendor's marketing number** as a reference point
- **Forgetting peak-to-average ratios** — daily peaks are 5–20× the daily average for human-driven traffic
- **Mistaking p99 budgets for averages** — p99 latency budget ≠ mean budget
- **Adding when you should multiply** (or vice versa) — write the formula in symbols first
- **Not sanity-checking against the speed of light or disk seek** — these are non-negotiable
- **Estimating only the happy path** — failure modes (retries, recoveries) often dominate

## Relationship to Other Skills

- Use `constraint-analysis` once you've identified the bottleneck factor — Fermi tells you which one.
- Use `failure-mode-effects-analysis` to extend estimates into failure regimes (retry storms, fallback paths).
- Use `feedback-loop-analysis` when an estimate must account for retry amplification or queueing.
- Use `statistical-debugging` when comparing estimates to measured distributions.
- Use `signal-detection-review` to set thresholds whose budget you've estimated here.
