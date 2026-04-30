---
name: error-and-approximation-analysis
description: Reason about absolute and relative error, floating-point precision, condition numbers, and accumulated error in iterative methods, money, timestamps, geo, and ML pipelines.
user-invocable: true
---

# Error and Approximation Analysis

Act as a numerical analyst embedded in the engineering workflow. Every numeric computation in finite precision carries error. The question is never "is there error?" — it's *how much, in which direction, and does it matter for this use case?* The wrong answer to that question is what produces money rounded into thin air, GPS positions off by a city block, ML pipelines whose results depend on input order, and clocks that drift past their alert thresholds.

The goal is to choose representations and algorithms whose error budget fits the problem, and to flag every place where "looks fine in the test" hides accumulated error that will surface in production.

## When to Use This

- Working with money, prices, exchange rates, or financial calculations
- Storing or comparing timestamps across systems with clock skew
- Geo coordinates, distances, bearings, or coordinate-system transforms
- ML pipelines, gradient updates, normalization, softmax, log-likelihoods
- Iterative numerical methods (root finding, optimization, simulation)
- Aggregations: sums, averages, variances over many values
- Comparing floats with `==`
- Converting between representations (float ↔ decimal ↔ integer)
- Hash-based partitioning where precision affects which shard receives a value

**Escape hatch**: Pure integer arithmetic in a bounded range with no division has no approximation error. Use this skill when fractional values, conversions, or accumulations are involved.

## Core Vocabulary

| Term | Definition |
| --- | --- |
| **Absolute error** | `|measured − true|` |
| **Relative error** | `|measured − true| / |true|` |
| **Precision** | How finely a representation distinguishes nearby values |
| **Accuracy** | How close to the true value the result is |
| **ULP (unit in the last place)** | Spacing between adjacent representable floats at a given magnitude |
| **Machine epsilon (ε)** | Smallest `ε` such that `1 + ε ≠ 1` (≈ 2.22e-16 for double) |
| **Significand / mantissa** | Bits encoding the leading digits |
| **Catastrophic cancellation** | Subtracting nearly-equal numbers loses most significant digits |
| **Condition number** | How much the output changes per unit change in input |
| **Ill-conditioned** | High condition number — small input perturbation, large output change |
| **Well-conditioned** | Low condition number — output is robust to input noise |
| **Stable algorithm** | Computes a result close to the exact answer of a slightly perturbed input |
| **Round-off error** | Error from representing a real number as the nearest float |
| **Truncation error** | Error from stopping an infinite series / iteration early |
| **Sensitivity** | How output varies with each input (the gradient, in practice) |

Precision ≠ accuracy. A scale that always reads 0.001 g too high is precise but inaccurate.

## The Three Error Sources

| Source | Mechanism | Example |
| --- | --- | --- |
| **Representation** | True value isn't representable | `0.1` is not exactly representable in binary floating point |
| **Computation** | Each operation rounds | `(a + b) + c ≠ a + (b + c)` for floats |
| **Truncation** | Stopping before convergence | Iterating Newton's method 5 times, not until ε |

All three accumulate. The job is to bound each and decide whether the total fits the use case.

## Core Questions

- What is the *required* accuracy for this output? (Down to a cent? A pixel? A nanosecond? An ε?)
- What is the largest number you'll see? The smallest non-zero? The dynamic range?
- Will values of very different magnitudes be added or subtracted?
- Is the algorithm stable (well-conditioned) for *your* input range?
- How many operations accumulate before output? Each contributes ~ε relative error.
- Are floats ever compared with `==`?
- Are you converting between float and decimal? Both ways?
- For money: are you using floats *anywhere*?

## The Process

### Step 1: Set the Error Budget

State the maximum acceptable error explicitly.

```
ERROR BUDGET:
- Quantity:
- Acceptable absolute error:
- Acceptable relative error:
- Worst case the user will notice:
- Cost of being wrong by 1 ULP / 1 cent / 1 ms / 1 m:
```

Without a budget, "is this precise enough?" cannot be answered.

### Step 2: Pick the Right Representation

| Domain | Use | Avoid |
| --- | --- | --- |
| Money | Integer minor units (cents) or arbitrary-precision decimal | `float`/`double` |
| Timestamps (compare/order) | Int64 nanos or ms since epoch | float seconds |
| Time durations (sub-second math) | Int64 nanos | float seconds |
| Geo coordinates | Float64 *plus* knowledge of CRS, or fixed-point µ-degrees | Float32, naive lat/lon arithmetic |
| Probabilities (small values) | Log-space (sum of logs, logsumexp) | Direct probabilities (underflow) |
| Counts, indexes, sizes | Integers (`u64`/`i64` as appropriate) | floats |
| Scientific quantities, signal | float64 (rarely float32) | decimals |
| Hashing / partitioning | Integers | floats |

The single highest-leverage rule: **never use float for money**. Use `Decimal` (Python), `BigDecimal` (JVM), `decimal.js`, or — best — store cents as integers. Floats and money produce silent rounding losses that compound across millions of transactions.

### Step 3: Watch for Catastrophic Cancellation

Subtracting two nearly-equal floats wipes out leading digits.

Weak (loses precision near `x = 0`):

```python
def f(x):
    return (1 - cos(x)) / x**2     # numerator near zero for small x
```

Strong (algebraically equivalent, numerically stable):

```python
def f(x):
    return 0.5 * (sin(x/2)/(x/2))**2
```

Common engineering instances:

- Computing variance with `E[X²] − E[X]²` (use Welford's online algorithm)
- Time differences across very far-apart timestamps stored as floats
- Geometric tests using cross products of similar vectors
- Differences of large dollar amounts in float

If two operands have similar magnitude, expect cancellation; rearrange the formula or change the representation.

### Step 4: Estimate Accumulated Error in Loops

For `n` floating-point operations, naive bound on relative error is roughly `n · ε`.

| Operations | Typical accumulated relative error (double) |
| --- | --- |
| 1 | ~1e-16 |
| 1,000 | ~1e-13 |
| 1,000,000 | ~1e-10 |
| 1,000,000,000 | ~1e-7 |

For aggregations (sum, mean, variance) over very large datasets, naive summation can drift noticeably. Use:

- **Kahan summation**: maintains a running compensation term; near-O(1) error for sums
- **Pairwise summation**: O(log n) error
- **Welford's algorithm** for variance — no `E[X²] − E[X]²`

If the application sums millions of small numbers (impressions, telemetry, dollars), default `sum()` may be inadequate.

### Step 5: Estimate the Condition Number

For a function `f` of input `x`, the condition number near `x` is roughly `|x · f'(x) / f(x)|`. Engineering shorthand:

- If a 1% input change produces ≪ 1% output change → well-conditioned
- If it produces ≫ 1% output change → ill-conditioned

Ill-conditioned operations include:

- Subtraction of nearly-equal numbers
- `tan(x)` near `π/2`
- Matrix inversion when the matrix is near singular
- Solving polynomial roots near a multiple root
- Probabilistic divisions where the denominator is near zero

Even a perfect algorithm cannot rescue an ill-conditioned problem — it amplifies input noise. Sometimes the right answer is "reformulate the problem", not "use more bits".

### Step 6: Never Compare Floats with `==`

```python
if x == 0.1 + 0.2:        # always False
if abs(x - target) < tol: # right idea
if math.isclose(x, target, rel_tol=1e-9, abs_tol=0.0): # better
```

For convergence checks, use both relative and absolute tolerance:

```python
abs(x_new - x_old) <= abs_tol + rel_tol * abs(x_old)
```

For sorting / hashing keys, do not use floats at all — use integer or decimal keys.

### Step 7: Reason About Distributed Clock Skew

Clocks across machines drift. Treat any `t1 − t2` from different sources as carrying an *uncertainty band*, not an exact duration.

- Use **monotonic clocks** for "how long did this take" (single process)
- Use **NTP-synced wall clocks** with explicit ± tolerance for cross-machine ordering
- Use **logical clocks / vector clocks** when "happens-before" matters more than wall time
- A "1 ms" alert threshold across services without sub-ms clock sync is meaningless

### Step 8: Document the Rounding Policy

Whenever a value crosses a representation boundary (display, storage, payment), state:

- Direction: round half-up / half-even (banker's) / toward zero / toward +∞
- Position: how many decimal places / which ULP
- Sign behavior: how negatives are handled
- Tie-breaking

Banker's rounding (round half to even) is the default for `IEEE 754` and `decimal` in many libraries; round-half-up is what most people expect. Picking the wrong default for invoices flips pennies.

## Output Format

```
ERROR & APPROXIMATION ANALYSIS

Quantity / pipeline:
- ...

Error budget:
- Absolute: ...
- Relative: ...

Representation choice:
- Current: ...
- Recommended: ... (justification)

Risk inventory:
- Catastrophic cancellation sites: ...
- Accumulation hot spots: ...
- Float-equality comparisons: ...
- Cross-clock comparisons: ...
- Ill-conditioned operations: ...

Rounding policy:
- Direction / position / tie-break:

Recommended changes:
- ...

Tests to add:
- Round-trip ...
- Boundary at ULP / cent / ms ...
- Adversarial input (huge + tiny mixed) ...
```

## Anti-Patterns to Avoid

- **Floats for money** — silent rounding losses compound over millions of transactions
- **Float `==`** — almost always wrong for non-trivial computations
- **`E[X²] − E[X]²` for variance** — catastrophic cancellation; use Welford
- **Naive `sum()` over millions of floats** — drift; use Kahan or pairwise
- **Comparing wall-clock timestamps across machines without a tolerance**
- **Storing latitude/longitude as float32** — ~1m error at the equator
- **Probabilities multiplied many times** — underflow; work in log space
- **Treating ULP as a constant** — it grows with magnitude
- **Believing `0.1 + 0.2 == 0.3`** — it's not
- **Using float as a hash/partition key** — different computations give slightly different floats → different shards
- **Mixing rounding policies across ingest and display** — pennies vanish
- **Ignoring condition number** — "more bits" cannot rescue an ill-conditioned formulation

## Relationship to Other Skills

- Use `dimensional-analysis` first — wrong units beat any precision discussion. Once units are right, this skill addresses precision.
- Use `formal-invariants` to assert error bounds and rounding policies as runtime checks.
- Use `fixed-point-reasoning` for termination of iterative numerical methods — pair it with this skill's analysis of accumulated error.
- Use `signal-detection-review` when the question is alert-threshold tuning rather than computational precision.
- Use `assumption-audit` to surface implicit assumptions about precision, range, and clock sync.
