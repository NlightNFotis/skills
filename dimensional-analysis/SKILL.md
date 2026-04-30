---
name: dimensional-analysis
description: Track units of measure across code, APIs, and data so unit-mismatch operations are caught at the type, spec, or review level rather than at runtime.
user-invocable: true
---

# Dimensional Analysis

Act as a physicist embedded in the engineering workflow. Treat every numeric quantity as a *dimensioned* value — it has a magnitude *and* a unit. Operations that violate dimensional homogeneity (adding bytes to milliseconds, multiplying a percentage by a ratio, comparing absolute time to a duration) are bugs even when the types compile.

The goal is to make unit mismatches structurally impossible or, failing that, immediately visible in review. The Mars Climate Orbiter was lost in 1999 because one team used pound-seconds and another used newton-seconds for the same impulse field; this skill exists so that the same class of error gets rejected before it ships.

## When to Use This

- Designing or reviewing APIs that exchange numeric quantities (timeouts, sizes, rates, prices)
- Working with time, money, geo coordinates, percentages, ratios, or normalized scores
- Storing or transmitting numbers across module, process, language, or service boundaries
- Reviewing config files, env vars, CLI flags, or protocol fields with numeric values
- Debugging "off by 1000x" or "off by 60" or "off by 100" errors
- Migrating between two libraries, formats, or databases with different unit conventions

**Escape hatch**: A truly unitless count in a single tightly-scoped function does not need this analysis. Use this skill where a quantity crosses a boundary, is persisted, or is combined with another quantity.

## Core Mindset

Every number has a dimension. "Unitless float" is almost always a lie — it usually means *the unit is implicit and unenforced*.

Ask:

- What is the unit of this number? Bytes? Bytes per second? Seconds? Milliseconds since epoch?
- Is this a *raw* value, a *normalized* value, a *ratio*, or a *percentage*?
- Is this an *absolute* point (timestamp, address) or a *relative* offset (duration, delta)?
- What unit do callers expect? What unit do we produce? Where is the conversion?
- Can two values with different units accidentally be added, compared, or passed in the wrong order?
- Is the unit encoded in the type, the name, the docstring, or nowhere?

## Dimension Categories

Classify every quantity into one of these families. Operations across families are almost always bugs.

| Family | Examples | Common confusions |
| --- | --- | --- |
| **Length / size** | bytes, KiB vs KB, characters vs code units | Bytes vs UTF-16 code units; KB (1000) vs KiB (1024) |
| **Time — duration** | ns, µs, ms, s, min | ms vs s; "timeout: 30" without unit |
| **Time — absolute** | epoch ms, ISO-8601, monotonic clock | Wall clock vs monotonic; UTC vs local |
| **Rate / frequency** | req/s, bytes/s, Hz | Per-second vs per-minute; instantaneous vs averaged |
| **Money** | minor units (cents), major units (dollars), currency code | Float dollars vs integer cents; missing currency |
| **Angle / geo** | radians, degrees, lat/lon order | rad vs deg; (lat, lon) vs (lon, lat); WGS84 vs other |
| **Percentage** | 0–100 with `%` suffix | "0.5" meaning 0.5% vs 50% |
| **Ratio / proportion** | 0.0–1.0 fraction | Confused with percentage; division by zero |
| **Normalized score** | model output [0,1], cosine [-1,1] | Treating logits as probabilities |
| **Count** | items, events | Cardinal count vs index; 0-based vs 1-based |
| **Force / pressure / energy** | N, Pa, J | Imperial vs metric (Mars Climate Orbiter) |

The Buckingham π theorem intuition: any physically meaningful equation can be rewritten in dimensionless groups. If your equation cannot be rewritten that way, you have a unit error.

## The Process

### Step 1: Inventory Every Numeric Quantity

For the code under review, list every numeric value that crosses a boundary or is stored.

```
QUANTITY:
- Name / variable / field:
- Family (from table above):
- Specific unit (ms, KiB, USD-cents, deg, ratio…):
- Source (input, computed, persisted, constant):
- Range / domain (≥0, [0,1], int32…):
- Where the unit is declared (type / name suffix / doc / nowhere):
```

If "where the unit is declared" is "nowhere", that is already a finding.

### Step 2: Check Dimensional Homogeneity

For every arithmetic, comparison, or conditional expression, verify both sides share a unit (or that the operation is a defined dimensional transform like `bytes / seconds = bytes/s`).

| Operation | Legal? |
| --- | --- |
| `duration_ms + duration_ms` | ✅ same dimension |
| `timestamp_ms - timestamp_ms` | ✅ produces a duration |
| `timestamp_ms + duration_ms` | ✅ produces a timestamp |
| `timestamp_ms + timestamp_ms` | ❌ meaningless |
| `bytes / seconds` | ✅ produces bytes/s |
| `percent * ratio` | ⚠️ define the result's unit |
| `ratio_a + ratio_b` (different denominators) | ❌ ratios are not composable across denominators |
| `percent_a + percent_b` (same base) | ✅ but watch for >100% |

### Step 3: Find the Unit Boundary Crossings

Most unit bugs live at boundaries. For each boundary, identify the conversion:

- Function parameter → local variable
- API request → DTO → domain object
- Config / env var → typed setting
- Database column → ORM field → application value
- Network protocol → deserialized value
- Library A → library B (e.g. `setTimeout` ms vs Node `setInterval` ms vs `sleep` seconds)

```
BOUNDARY:
- From: [system / function / format] in unit [X]
- To: [system / function / format] in unit [Y]
- Conversion: [explicit factor / implicit / none]
- Risk if wrong:
```

### Step 4: Encode Units in the Type System

Prefer mechanical enforcement over discipline. In order of strength:

| Mechanism | Example |
| --- | --- |
| **Branded / nominal types** (TS, Flow) | `type DurationMs = number & { __brand: "DurationMs" }` |
| **Newtypes** (Rust, Haskell, Scala) | `struct DurationMs(u64);` |
| **Value objects** (any OO language) | `class Money { amount: bigint; currency: string }` |
| **Units libraries** | `uom` (Rust), `pint` (Python), `js-quantities` |
| **Suffixed names** (last resort) | `timeoutMs`, `priceUsdCents`, `latencyP99Seconds` |
| **Comment / docstring** (weakest) | `// in milliseconds` |

Prefer a single canonical internal unit (e.g. *all durations are ms internally*; convert at the boundary). Mixing units inside the system multiplies conversion sites.

### Step 5: Distinguish Absolute from Relative

This trap is so common it deserves its own step.

- **Absolute time** (timestamp, epoch ms): a *point* on a timeline. Cannot be added to another absolute time.
- **Duration** (ms, s): a *length*. Can be added, subtracted, scaled.
- Same applies to: addresses vs offsets, file positions vs lengths, prices vs price-deltas, scores vs score-deltas.

Weak:

```ts
function schedule(delay: number, when: number) { ... }
```

Strong:

```ts
function schedule(delay: DurationMs, when: TimestampMs) { ... }
```

### Step 6: Check Percentages and Ratios Carefully

- Percentages are *additive* only when their base is the same. "20% off, then 10% off" is not 30% off.
- Ratios are *not composable* across different denominators: `clicks/impressions` for two segments cannot be averaged into a global ratio.
- A "rate of change of a percentage" is in **percentage points**, not percent.
- "0.5" is ambiguous: probability, ratio, or 0.5%? Suffix names (`fraction`, `percent`, `pp`, `bps`).
- Basis points (bps): 1 bp = 0.01% = 0.0001 fraction. Common in finance; verify the unit before arithmetic.

### Step 7: Verify Normalization Status

Many ML, scoring, and analytics bugs come from mixing raw and normalized values.

For each numeric field, mark:

- Raw / unnormalized
- Normalized to [0,1]
- Normalized to [-1,1]
- Z-scored (mean 0, std 1)
- Logit / log-odds
- Probability (sums to 1 across alternatives)

A `score` field is meaningless unless normalization is documented.

### Step 8: Add a Round-Trip Test

For any conversion (parse, serialize, currency exchange, unit conversion):

- `convert(convert(x, A→B), B→A) ≈ x` within documented tolerance
- For lossy conversions (float → int, ms → s), document the tolerance and rounding policy

## Output Format

```
DIMENSIONAL ANALYSIS REPORT

Quantities inventoried:
1. [name] — family / unit / declared where

Boundary crossings:
1. [from → to] — conversion: [explicit factor / IMPLICIT / MISSING]

Dimensional violations found:
1. [expression] — [unit on left] vs [unit on right]

Recommended encoding:
- [branded type / newtype / value object / suffix] for [quantities]

Open ambiguities (need human decision):
- ...
```

## Anti-Patterns to Avoid

- **"Unitless float"** as a documented type — almost always means "unit is implicit"
- **Naming a variable just `timeout`, `price`, `latitude`** with no unit suffix or type wrapper
- **Mixing units within a module** — pick one canonical internal unit and convert at the edge
- **Storing money as float** — use minor-unit integers or a decimal type with explicit currency
- **Treating `Date.now()` and a duration as the same number type** — they are not
- **Adding ratios from different denominators** — Simpson's paradox lives here
- **Omitting the currency** when storing or transmitting money
- **Using percent and fraction interchangeably** in the same code path
- **Trusting that "the caller will pass it in the right unit"** — encode it

## Relationship to Other Skills

- Use `formal-invariants` to assert dimensional constraints (e.g. "duration ≥ 0", "probability ∈ [0,1]").
- Use `assumption-audit` to surface implicit unit assumptions at boundaries.
- Use `error-and-approximation-analysis` when the unit is correct but precision (float vs decimal) is the risk.
- Use `semantic-precision` when the unit is fine but the *meaning* of the field is ambiguous.
