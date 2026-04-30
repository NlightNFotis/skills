---
name: fatigue-and-stress-cycling
description: Cyclic loading failure below yield strength, applied to systems that work fine for years until they suddenly do not. Use when intermittent sub-threshold stress accumulates damage that single-event analysis misses.
user-invocable: true
---

# Fatigue and Stress Cycling

Act as a mechanical engineer inspecting a part that just failed in service after running fine for years. The instinct is to ask "what overload broke it?" — but in most such failures, no single load was anywhere near the part's static strength. The part accumulated microscopic damage from millions of sub-yield cycles until a crack initiated, propagated, and then went catastrophic without warning. Software systems exhibit the same pathology: a connection pool that worked for 18 months, a database that has never missed an SLA, a retry path that has never tripped — until they do, all at once, with no proximate trigger anyone can name.

Success looks like preemptive replacement *before* the cycle count exceeds the system's fatigue life. Failure is post-mortem language like "it just gave up" or "we'd never seen anything like it."

## When to Use This

- An incident where the immediate trigger is implausible as the cause ("the same query that ran a billion times")
- Reviewing a system that has been "rock solid" for a long time
- Designing a path that will be exercised at high frequency under low individual stress
- A pattern of intermittent issues that "self-heal" — and are therefore being ignored
- Capacity planning for a long-lived component (DB pool, file descriptors, ID space, log buffers, connection caches)
- On-call rotation design (humans fatigue too)
- Any system where age/cycle-count is high relative to design assumptions

**Escape hatch**: For one-shot, short-lived, or rapidly-replaced systems (a serverless function instance, a CI runner, an experiment), fatigue analysis is unnecessary; the part will be replaced long before its fatigue life. Use this skill when the component will accumulate cycles in production over months to years.

## Core Mindset

Distinguish **single-overload** failure from **fatigue** failure. They look different, demand different evidence, and require different fixes.

Ask:

- Has this system been running long enough to accumulate cycles?
- Was the last load before failure unusual, or routine?
- Are there micro-signals (occasional retries, transient errors, brief spikes) that are being ignored as noise?
- Where are the *stress concentrators* — the points where many cycles converge?
- Is there an endurance limit below which damage does not accumulate, or does every cycle count?
- When does this part get inspected or replaced?

## Domain Vocabulary

| Term | Definition | Software analogue |
| --- | --- | --- |
| **Yield strength** | Stress at which permanent deformation begins on a single load | Capacity at which a system overloads on a single request |
| **Ultimate strength** | Stress at which the part fails on a single load | Saturation / OOM / hard limit |
| **Fatigue strength** | Stress level vs cycles to failure (read off S-N curve) | Sustainable repeated load level |
| **Endurance limit** (σ_e) | Stress below which infinite cycles cause no failure | Truly safe per-request load — exists for some materials, not all |
| **S-N curve** | Plot of stress amplitude (S) vs cycles to failure (N), log-log | Repeated-load capacity vs longevity |
| **Low-cycle fatigue** | < 10⁴ cycles to failure; high stress, often near yield | Daily near-saturation events |
| **High-cycle fatigue** | > 10⁵ cycles; stress well below yield | Per-request small stress; the dangerous regime in software |
| **Crack initiation** | Microscopic damage starts at a stress concentrator | First leak, first ignored retry, first descriptor not closed |
| **Crack propagation** | Damage grows per cycle (Paris' law) | Slow degradation: pool gets slower, error rate creeps |
| **Stress concentrator** | Notch, hole, sharp corner — locally amplifies stress | Hot row, contended lock, popular queue, single-region dependency |
| **Mean stress** | The DC component of cyclic load | Baseline traffic level |
| **Stress amplitude** | The AC component | Spike height above baseline |
| **Goodman diagram** | Mean-stress correction to fatigue limit | Spike tolerance shrinks as baseline rises |
| **Miner's rule** | Σ (n_i / N_i) ≥ 1 → failure (cumulative damage from variable amplitude) | Damage budget across heterogeneous events |
| **Fretting fatigue** | Tiny relative motion accelerates fatigue at interfaces | Repeated reconnects, repeated cache evictions |
| **Corrosion fatigue** | Environmental attack lowers fatigue life | Memory pressure, noisy neighbour, degraded dependency |
| **Inspection interval** | Time between checks for crack growth | Health check, capacity audit, on-call review |

### S-N curve intuition

For ferrous materials, the S-N curve flattens to a horizontal asymptote (the endurance limit) at ~10⁶ cycles. Below σ_e, life is essentially infinite. For non-ferrous materials (aluminum, software), there is no endurance limit — the curve keeps falling, and given enough cycles, *any* repeated stress causes failure.

**Most software has no endurance limit.** Connection churn, retry events, GC cycles, log writes — there is no per-cycle stress level so small that infinite repetition is safe. Plan accordingly.

### Miner's rule worked example

A pool is rated for 10⁶ cycles at "normal" load and 10⁴ cycles at "burst" load. In a year it sees:

- 8 × 10⁵ normal cycles → damage = 8e5 / 1e6 = 0.80
- 3 × 10³ burst cycles → damage = 3e3 / 1e4 = 0.30
- Total damage = 1.10 → predicted failure within the year

The 3000 bursts (0.4% of cycles) contributed 27% of the damage. **Rare high-amplitude events dominate fatigue damage.** Counting only the common case under-predicts failure.

## The Process

### Step 1: Distinguish Overload from Fatigue

Before treating a failure as fatigue, rule out single-event overload.

```
FAILURE CLASSIFICATION:
- Was the last load before failure within historical normal? (yes/no)
- Has the load profile changed materially in the last 30 days? (yes/no)
- Has the part been in service > 6 months? (yes/no)
- Are there prior micro-symptoms (intermittent, "self-healing")? (yes/no)
- Was the failure sudden with no degradation curve? (yes/no)
```

Pattern:

- Last load *abnormal* + recent change → overload; use forensics, not fatigue
- Last load *normal* + long service + prior micro-symptoms + sudden failure → **fatigue signature**

The fatigue signature is the dangerous one because the proximate cause looks innocuous and gets dismissed.

### Step 2: Identify Stress Concentrators

In metal, fatigue cracks initiate at notches, holes, and surface defects — anywhere that geometry concentrates the nominal stress. In software, the analogues are wherever many cycles converge through a small interface:

- A hot row in a database
- A single-instance cache that all callers hit
- A coordinator process all workers report to
- A shared lock / mutex / leader
- An ID generator
- A connection pool serving N upstream callers
- A log file or buffer with a single writer

These are the points where fatigue analysis matters most. Stress *amplification* at a concentrator can be 3–5×; in software it can be far more if the concentrator serialises many independent callers.

### Step 3: Characterise the Cycle

A cycle is one full load-unload of the stress. For each suspect path:

```
CYCLE PROFILE:
- Cycle definition (what is one cycle?):
- Cycle rate (cycles/sec, /day, /year):
- Mean stress (baseline load level):
- Stress amplitude (spike above baseline):
- Variable-amplitude events (rare bursts, restarts, deploy storms):
- Total cycles accumulated to date:
- Total cycles expected over remaining service life:
```

Without a cycle count, you cannot place yourself on the S-N curve.

### Step 4: Estimate Fatigue Life

You will rarely have a real S-N curve for a software component. You can still bracket:

- Vendor / RFC / docs may state "N reconnects per minute supported", "max writes per file before rotate", "expected life of pool"
- Empirical: when has this component, or a close analogue, failed under similar load?
- Inferred: under high-cycle conditions in software (no endurance limit), a *factor of 10* on observed cycle count to next failure is a reasonable starting estimate

Apply Miner's rule across the load spectrum. Rare high-amplitude events likely dominate; do not omit them because they are infrequent.

### Step 5: Look for the Micro-Symptoms (Crack Initiation)

Fatigue does not jump from "fine" to "failed". It goes through a long, observable propagation phase that is usually mis-classified as noise.

Crack-initiation signals to *not* dismiss:

| Symptom | Often dismissed as | Actually means |
| --- | --- | --- |
| Occasional retry that succeeds | "The retry handled it" | A failed cycle that left damage |
| Transient timeout, "self-healed" | "Network blip" | A cycle that ran past spec |
| Slow creep in p99 latency | "It's within SLO" | Crack growth |
| Intermittent restart of a process | "Auto-recovery worked" | A cycle that broke something not-quite-fatal |
| Periodic lock contention spikes | "Brief contention" | Fretting at the concentrator |
| Memory usage trending up but reset by deploy | "Deploys clear it" | Damage hidden by replacement, not absent |

The discipline: every dismissed micro-symptom is a data point on the S-N curve. Log them, count them, plot them. The trend is more diagnostic than the absolute level.

### Step 6: Decide on Treatment

The four classical responses to fatigue, with software translations:

| Mechanical | Software |
| --- | --- |
| **Reduce stress amplitude** (shock absorbers, smoothing) | Backpressure, smoothing, batching, debouncing |
| **Reduce mean stress** (lower baseline load) | Capacity headroom, sharding, caching upstream |
| **Eliminate stress concentrators** (fillets, polish, shot-peening) | Remove single points; widen interfaces; shard the hot row |
| **Inspect and replace before fatigue limit** | Restart cadence, rolling replacement, periodic rebuild |

Note that "more capacity" treats *mean stress*, not *amplitude* — it postpones failure but does not eliminate the cycling. For systems that genuinely cycle (deploys, scaling events, scheduled jobs), amplitude reduction is the leverage.

### Step 7: Set Inspection and Replacement Intervals

Aircraft do not wait for a wing spar to crack; they pull the part on a schedule because the consequence of fatigue failure is unacceptable. Software equivalents:

- **Rolling restart** of long-lived processes (treats unbounded resource creep)
- **Pool rotation** (cycle out connections after N uses)
- **Periodic rebuild** of caches, indexes, runtime state
- **Scheduled inspection**: review error logs, retry counts, latency distributions for trend, not just threshold

Set the interval below the estimated fatigue life with margin — the same FoS principle, applied in time rather than load.

### Step 8: Recognise Fatigue in People

The same analysis applies to on-call humans. Below are the signatures:

| Mechanical fatigue | On-call fatigue |
| --- | --- |
| Crack initiation at concentrator | Burnout starts at the most-paged person |
| Sub-yield repeated stress | Below-threshold pages that "weren't real outages" |
| No proximate trigger of failure | The departure that "came out of nowhere" |
| Inspection / replacement | Rotation, real PTO, actual page-load metrics |

Treat human fatigue with the same discipline: count cycles (page volume), enforce intervals (rotation), eliminate concentrators (do not let one person own a system).

## Output Format

When using this skill, produce:

```
FATIGUE ANALYSIS

Component:
- Function:
- Time in service:
- Stress concentrators identified:

Cycle profile:
- Cycle definition:
- Cycle rate:
- Estimated cycles to date:
- Mean stress / amplitude / variable-amplitude events:

Crack-initiation signals (micro-symptoms):
1. ...

Estimated fatigue life:
- Basis:
- Remaining cycles:
- Confidence:

Treatment plan:
- Amplitude reduction:
- Mean stress reduction:
- Concentrator removal:
- Inspection interval:
- Replacement / rotation cadence:

Monitoring:
- Trend metrics added (not just threshold):
- Re-evaluation trigger:
```

## Anti-Patterns to Avoid

- **Dismissing self-healing intermittents** — they are the propagation phase, not noise
- **Single-event thinking** — looking for "what overloaded it" when the answer is "10⁸ small loads did"
- **Confusing yield with fatigue strength** — passing a load test does not predict survival under cyclic load
- **Ignoring rare high-amplitude events** in cycle count — Miner's rule says they dominate
- **Threshold alerting only** — fatigue shows in the *trend*, often well inside threshold
- **Assuming an endurance limit exists** — software materials usually have no horizontal asymptote
- **Treating restart as a fix** — restart resets the cycle count but does not address why cycles damage the system
- **Forgetting human fatigue** — on-call rotation, burnout, and turnover follow the same arithmetic

## Relationship to Other Skills

- Use `entropy-and-code-rot` when the degradation is *monotone* (one-directional decay) rather than *cyclic*. Fatigue is specifically about damage from repeated up/down loading.
- Use `factor-of-safety` to dimension the static margin; fatigue analysis is the *time* dimension that FoS alone does not address.
- Use `feedback-loop-analysis` when the cycling itself is generated by the system (retry storms, scaling oscillation) rather than by external load.
- Use `incident-review` after a fatigue-suspected failure to reconstruct the cycle history.
- Use `failure-mode-effects-analysis` to identify which fatigue failures are catastrophic (no warning) vs graceful.
