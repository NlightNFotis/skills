---
name: tolerance-stack-up
description: Combining variances across an assembly, applied to multi-hop integration, end-to-end latency budgets, and SLA/SLO cascades. Use when each component has its own tolerance and the question is what the *whole assembly* will do.
user-invocable: true
---

# Tolerance Stack-Up

Act as a mechanical engineer doing a tolerance analysis on an assembly. A shaft fits into a bearing which sits in a housing which bolts to a frame; each part is made to a tolerance, and whether the assembly works depends on how those tolerances *combine*. The same arithmetic governs whether your end-to-end latency budget holds when each hop has its own p99, whether your error budget survives a chain of 99.9% dependencies, and whether accumulated rounding across a pipeline preserves the answer.

Success looks like an explicit per-stage budget that sums (or RSS-sums) to the end-to-end requirement. Failure looks like every team meeting their own SLO while the user-visible behavior misses the target.

## When to Use This

- Designing or reviewing an end-to-end latency budget across N hops
- Composing SLOs/SLAs across a chain of dependencies
- Allocating error budgets across services
- Numerical pipelines where rounding or quantisation accumulates
- Integration testing where each component passes alone but the assembly fails
- Negotiating which team gets the loose tolerance and which gets the tight one
- Post-incident analysis where "everyone was within spec" but the user saw a violation

**Escape hatch**: For a single-stage system or a system where one stage dominates (one hop is 95% of the latency), stack-up analysis is overkill — optimise the dominant term. Use this skill when at least 3 stages contribute meaningfully to a combined output.

## Core Questions

Ask:

- What is the end-to-end requirement (mean? p99? max?)
- What is each stage's tolerance, and is it specified the same way?
- Are stage tolerances independent, or correlated?
- Do stages compose linearly (latency adds) or multiplicatively (availability multiplies)?
- Which stage has the loose tolerance, and is that the right choice?
- What is the *worst-case* stack? What is the *statistical* (RSS) stack?
- Do I have a per-stage *budget*, or only a per-stage *measurement*?

## Domain Vocabulary

| Term | Definition | Software analogue |
| --- | --- | --- |
| **Nominal** | The intended value | The target latency, the SLO |
| **Tolerance** | Allowable deviation from nominal | p99 spread, jitter, error rate |
| **Bilateral tolerance** | ±X around nominal (50 ± 0.1) | Symmetric jitter |
| **Unilateral tolerance** | +X / −0 or +0 / −X | One-sided latency budget (only "too slow" matters) |
| **Worst-case stack-up** | Σ |t_i| — assumes all tolerances at extreme simultaneously | Pessimistic combined budget |
| **Statistical stack-up (RSS)** | √(Σ t_i²) — assumes independent normal distributions | Realistic combined budget |
| **Datum** | Reference surface from which measurements are taken | The clock/origin against which latency is measured |
| **GD&T** | Geometric Dimensioning and Tolerancing — a notation for how parts may deviate | Per-stage SLI/SLO specification |
| **True position** | Allowed deviation of a feature's location | Allowed deviation of a stage's behaviour |
| **Fit class** | Clearance / transition / interference between mating parts | API contract: loose / exact / strict |
| **Six-sigma** | Process spread of ±6σ → 3.4 defects per million opportunities | High-reliability per-stage target |
| **Process capability** (Cp, Cpk) | Spec width / process spread; Cpk also penalises off-centre | Headroom of a stage's actual variance against its spec |
| **Tolerance allocation** | Deciding which dimension gets which fraction of the total budget | Latency budget per service |

### Stack-up arithmetic cheat sheet

| Combination | Worst case | Statistical (independent, ~normal) |
| --- | --- | --- |
| Latency adds across hops | T_total = Σ t_i | T_total ≈ Σ μ_i ; σ_total = √(Σ σ_i²) |
| Availability across serial chain | A_total = Π A_i | (same; deterministic) |
| Error rate across serial chain | E_total ≈ Σ E_i (small E_i) | (same) |
| Rounding error per op | E_total = Σ |e_i| | E_total ≈ √(Σ e_i²) for independent rounding |

A worked numerical example for end-to-end latency across 4 hops, each with μ=20ms, σ=5ms:

- Worst-case (μ + 3σ) per hop = 35ms; serial worst-case = 4 × 35 = **140ms**
- Statistical: μ_total = 80ms, σ_total = √(4 × 25) = 10ms; p99 (≈ μ + 3σ) = **110ms**
- The 30ms gap is the cost of treating independent variances as if they aligned.

For 3 hops at 99.9% availability each: serial product = 0.999³ ≈ **99.70%**, not 99.9%. To deliver 99.9% end-to-end across 3 serial hops, each must be ≈ 99.967%.

## The Process

### Step 1: Identify the Assembly and the Output Spec

Define the boundary precisely. An "end-to-end" requirement only has meaning if you state where it starts and ends.

```
ASSEMBLY:
- Output requirement (one of: mean, p50, p95, p99, max, total error, total availability):
- Target value:
- Direction (≤, =, ≥):
- Datum (where the measurement starts):
- End point (where the measurement ends):
- Stages in the path (ordered):
```

If the spec says "fast" or "reliable" without a number and a percentile, stop and refine before doing arithmetic.

### Step 2: Specify Each Stage's Tolerance the Same Way

Stack-up arithmetic only works when units agree. Stages often have heterogeneous specs ("p99", "average", "max", "5-nines"). Convert to a common form first.

```
PER-STAGE TABLE:
| Stage | Nominal | Tolerance type | σ or spread | Distribution shape | Independence |
```

If a stage cannot give you a distribution, get at least:

- A nominal (mean or median)
- A tail point (p95, p99, max-observed)

You can then approximate σ ≈ (p99 − μ) / 3 for rough RSS work. Document the approximation.

### Step 3: Choose Worst-Case vs Statistical

Decision matrix:

| Situation | Use |
| --- | --- |
| Stages are mechanically correlated (same DB outage hits all hops) | Worst case |
| Stages are independent and reasonably normal | RSS |
| Safety-critical, no tolerance for failure | Worst case |
| Cost-of-margin is high, statistical assumption defensible | RSS |
| Few stages (≤ 3) | Worst case (RSS savings small) |
| Many stages (≥ 5) | RSS (worst case is needlessly pessimistic) |
| Distributions heavy-tailed (latency often is) | Worst case, or RSS with explicit p99 inflation factor |

A common sin: using RSS in code review because it gives the answer that fits the budget, while the real workload is correlated (a slow shared cache makes every hop slow).

### Step 4: Allocate the Budget

This is where stack-up becomes design rather than analysis. Given a total budget, decide how to split it. Three common policies:

| Policy | Rule | When to use |
| --- | --- | --- |
| **Equal split** | t_i = T / N | Default; no information about cost |
| **Weighted by cost** | Loose tolerance to the stage where tightening is expensive | Most production systems |
| **Weighted by capability** | Loose tolerance to the stage that is already noisier | When some stages are physically harder |

Worked example: 200ms end-to-end p99 budget across 5 hops, statistical stack-up.

- Equal split: each σ_i = √((200/3)² / 5) ≈ 30ms. Tight, may be infeasible for the DB hop.
- Cost-weighted: give the DB hop σ = 50ms (it's expensive to tighten), give the cache hop σ = 5ms (it's already fast). Verify: √(50² + 5² + 20² + 20² + 20²) ≈ 60ms; 3σ ≈ 180ms. Within budget.

Document the allocation as a *contract* with each owning team.

### Step 5: Distinguish Bilateral, Unilateral, and One-sided Stack

Latency budgets are usually unilateral (only "too slow" matters); time-sync budgets may be bilateral (both early and late are bad); error budgets are one-sided (only "too many" matters).

When stacking unilateral tolerances, you cannot let one stage absorb another's "underspend" automatically. A hop being faster than its budget does not give the next hop more room *unless* the system is designed to pipeline that slack. Otherwise treat each as a hard cap.

### Step 6: Account for Correlation

The biggest source of stack-up errors is assuming independence when stages are coupled.

Common couplings:

- Shared dependency (DB, cache, identity service)
- Shared infrastructure (same AZ, same NIC, same noisy neighbour)
- Shared upstream input (one slow user request inflates every downstream hop)
- Shared scaling trigger (autoscaler ramps everything together)
- Shared retry policy (retries pile up when any stage is slow)

If correlation ρ > 0, the RSS underestimates the combined spread. The corrected combined variance for two correlated stages is:

> σ²_total = σ_1² + σ_2² + 2 · ρ · σ_1 · σ_2

For ρ = 1 (perfect correlation), this collapses to (σ_1 + σ_2)² — i.e., worst-case stack-up. For ρ = 0, it's RSS. Most real systems sit between.

### Step 7: Handle Pass/Fail Per Stage vs Continuous Stack

Some stack-ups are continuous (latency); some are pass/fail (a stage either succeeds or returns an error). For pass/fail chains:

- Serial availability: A_total = Π A_i
- Serial error rate: E_total ≈ Σ E_i (when E_i are small)
- Parallel availability (any one suffices): A_total = 1 − Π (1 − A_i)
- k-of-n availability: use the binomial sum

A common error: averaging availabilities ("our services average 99.9%") when the user experiences the *product* of dependencies on their critical path.

### Step 8: Validate the Stack with Real Measurement

Stack-up is a design tool; it must be checked against observed end-to-end. Plot:

- Predicted end-to-end distribution (from per-stage stack-up)
- Observed end-to-end distribution

If they diverge:

- Worst-case predicted >> observed → tolerances are not aligning at the extreme; consider RSS
- RSS predicted >> observed → stages are negatively correlated (rare, often misleading)
- Predicted << observed → hidden correlation, missed stage, or per-stage spec is optimistic

Iterate the per-stage tolerances until predicted matches observed within a sensible factor.

## Output Format

When using this skill, produce:

```
TOLERANCE STACK-UP REPORT

Assembly:
- End-to-end metric:
- Target / direction:
- Datum / endpoint:

Stages:
| # | Stage | Nominal | σ (or p99) | Distribution | Independence assumption |

Stack-up method chosen:
- Worst case / RSS / hybrid — because [...]

Predicted end-to-end:
- Mean:
- σ:
- p99 / worst-case:

Comparison to target:
- Headroom or shortfall:

Allocation policy:
- Equal / cost-weighted / capability-weighted

Per-stage budget contracts:
| Stage | Allocated tolerance |

Correlation risks:
- ...

Validation plan:
- Predicted vs observed comparison
- Re-derivation triggers (new stage, dep change, traffic shift)
```

## Anti-Patterns to Avoid

- **Mixing units** — averaging availability percentages, averaging p99 with mean, etc.
- **Assuming independence** when stages share a dependency, AZ, or scaling trigger
- **Per-stage thinking only** — every team meets its SLO and the user still sees a violation
- **No allocated budget** — without a per-stage cap, no team owns the end-to-end target
- **Worst-case everywhere** — over-spends margin and forces unnecessary cost
- **RSS to fit the answer** — using statistical stack-up because worst-case did not fit
- **Optimistic per-stage specs** — pretending a hop is normal when its real distribution is heavy-tailed
- **No re-validation** — predicted stack-up never reconciled against observed end-to-end

## Relationship to Other Skills

- Use `error-and-approximation-analysis` when the per-stage error is *numerical* (rounding, quantisation) rather than *temporal* — the stack-up arithmetic is the same but the per-stage characterisation differs.
- Use `factor-of-safety` to decide each stage's headroom against its allocated tolerance.
- Use `feedback-loop-analysis` when the per-stage variance is amplified by retries or backpressure (which breaks the independence assumption).
- Use `network-topology-review` to surface hidden serial dependencies that turn a "parallel" architecture into a serial stack.
- Use `signal-detection-review` when the per-stage threshold itself is a tunable spec rather than a fixed tolerance.
