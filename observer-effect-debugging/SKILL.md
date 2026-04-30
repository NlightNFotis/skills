---
name: observer-effect-debugging
description: Reason about how the act of observing a system perturbs it — Heisenbugs, probe effect, log-induced timing changes, debugger-only behavior.
user-invocable: true
---

# Observer-Effect Debugging

Act as an experimental physicist embedded in the engineering workflow. Your job is to recognize that every measurement disturbs the system being measured: attaching a debugger changes scheduling, adding a log line changes timing, sampling a counter takes a lock, profiling perturbs caches and JIT decisions. Bugs that appear or disappear under observation are not paranormal; they are signals about where the perturbation matters.

The goal is to debug systems where naive observation lies, and to choose instrumentation whose perturbation is small enough — or whose bias is well-understood enough — to trust the data.

## When to Use This

- A bug disappears when you attach a debugger or add logging ("Heisenbug")
- A bug only appears in production, not under any local instrumentation
- Performance numbers change wildly depending on whether profiling is on
- A race condition shows up only at specific log levels
- A test passes individually and fails in a suite (or vice versa)
- A flaky test cannot be reproduced under tracing
- You're choosing between sampled and continuous monitoring

**Escape hatch**: If the bug is reproducible under all instrumentation and behaves identically observed and unobserved, you have a normal bug — use `popperian-debug` or `differential-diagnosis-debugging` instead.

## Core Distinctions

These are commonly conflated. Be precise:

| Concept | Meaning | Engineering analogue |
| --- | --- | --- |
| **Heisenberg uncertainty** | A formal limit on simultaneously knowing conjugate quantities (position/momentum). Not about disturbance per se. | Useful as an *intuition pump* only. Don't claim "Heisenberg" when you mean "probe effect". |
| **Observer effect** | The act of measurement physically disturbs the system | Attaching gdb pauses threads; adding `console.log` flushes I/O |
| **Probe effect** | Specifically: instrumentation alters timing/order enough to change behavior | A `printf` between two non-atomic ops serializes them |
| **Measurement bias** | The instrument systematically shifts the value it reports | Sampling profilers undercount short-lived functions |
| **Instrument latency** | Time between event and measurement | Log buffering, metric aggregation windows |
| **Quantum collapse (intuition only)** | Observation forces a state to resolve | A debugger evaluating a lazy expression materializes it |

The observer effect is classical and almost always what you actually mean. Reserve "Heisenberg" for the intuition that **you cannot observe a system arbitrarily precisely without paying a cost in the very thing you care about**.

## Core Questions

- What is my measurement actually measuring?
- How does my measurement perturb the variable I care about?
- Is the bug present in the unobserved system, or did I create it by observing?
- Is the bug absent in the unobserved system, or did I hide it by observing?
- Can I observe out-of-band (separate process, hardware tap, post-hoc trace) instead of in-band?
- What is the smallest perturbation that would still answer my question?
- What signals would survive even if observation perturbs timing?

## Classification of Observation Effects

| Effect | Mechanism | Typical symptom |
| --- | --- | --- |
| **Timing dilation** | Instrumentation slows critical section | Race condition disappears |
| **Memory barrier injection** | I/O calls and locks impose ordering | Reordering bug hidden |
| **Cache perturbation** | Profiler/debugger evicts hot lines | Performance numbers untrustworthy |
| **JIT deoptimization** | Inspecting a function deopts it | Behavior changes under inspection |
| **GC pressure shift** | Allocating log strings triggers GC | Latency spike from logging itself |
| **Scheduling change** | Debugger pause yields the thread | Different interleaving observed |
| **Compiler reordering blocked** | `volatile`/atomic for tracing prevents optimization | Slower but "more correct" build |
| **Sampling bias** | Sampler aligned with periodic event | Aliasing — false signal |
| **Hawthorne effect (human)** | Engineers behave differently when watched | Dashboard worship distorts work |

## The Process

### Step 1: Characterize the Observation Disturbance

Before adding more logs, name the disturbance you are about to introduce.

```
INSTRUMENTATION PROPOSAL:
- What I want to know:
- Instrument I plan to use:
- Where it inserts:
- Disturbance introduced (timing / locking / allocation / memory / scheduling / cache):
- Order of magnitude vs the phenomenon (ns / µs / ms / s):
- In-band or out-of-band:
```

If the disturbance is the same order of magnitude as the phenomenon, the measurement is suspect.

### Step 2: Triangulate with Multiple Observation Modes

Never trust a single observation mode for a Heisenbug. Combine:

- **Continuous in-band** (logs, tracing) — high disturbance, full coverage
- **Sampled in-band** (sampling profiler, periodic snapshot) — lower disturbance, statistical view
- **Out-of-band** (separate process reading metrics, eBPF, dtrace, kernel probes, packet captures) — minimal disturbance
- **Post-hoc** (core dumps, flight recorder, ring buffer dumped on failure) — zero steady-state disturbance
- **Counterfactual** (run with instrumentation off and compare aggregate symptom rate)

If two modes agree, trust grows. If they disagree, the disagreement itself is a clue about which one is perturbing.

### Step 3: Distinguish "Bug Caused by Observation" from "Bug Hidden by Observation"

| Pattern | Likely cause | Action |
| --- | --- | --- |
| Bug only with logging on | Logging serializes/synchronizes; bug needs concurrency window. Removing log re-opens window. | Reproduce with `nop` of equivalent timing (busy wait, atomic increment) |
| Bug only with logging off | Log-line side effect (flushing, allocation, format error) *is* the bug | Audit the logger; check for exceptions in format args |
| Bug only with debugger | Debugger forces evaluation of a lazy/optimized-away expression | Inspect what the debugger is materializing |
| Bug only without debugger | Optimization-dependent (UB, uninitialized memory, JIT specialization) | Build with `-O0`/disable JIT and re-test; suspect undefined behavior |
| Bug in production only | Concurrency, scale, real I/O latency, real network, real data | Reproduce with production-shaped load, not production logging |

### Step 4: Reduce the Probe

If the probe is changing the result, shrink it:

- Replace `printf` with an atomic counter increment
- Replace synchronous logging with a lock-free ring buffer flushed on failure
- Replace deep object serialization with a hash or single int
- Replace per-iteration logs with summary logs at boundaries
- Move from sampling at 1kHz to sampling at 10Hz and check if the signal survives
- Use hardware performance counters instead of code-level timers

The minimum viable probe is the one whose disturbance is smaller than your effect size.

### Step 5: Reason About Sampling vs Continuous

Sampling is cheap but biased. Continuous is honest but costly.

| Question | Prefer |
| --- | --- |
| "Is this rare event happening at all?" | Continuous (sampling will miss it) |
| "What is the typical cost of this hot path?" | Sampling (continuous distorts it) |
| "Does latency have a long tail?" | Continuous tail capture, sampled body |
| "Is there a periodic pattern?" | Sample at >2× the suspected frequency (Nyquist intuition) |
| "Why did this *one* request fail?" | Per-request trace (continuous, scoped) |

Beware **aliasing**: if your sampling interval is a multiple of an underlying period (1s sampling vs 1s GC), you'll see a flat line that hides the real pattern.

### Step 6: Decide When to Trust the Observation

Ask:

- Does the symptom survive when the probe is removed (using a different mode)?
- Is the effect size larger than the probe's perturbation by ≥10×?
- Does an out-of-band observation corroborate?
- Has the system been running long enough that startup transients are gone?
- Is the population I sampled representative (or skewed by who hits the instrumented code path)?

If the answer to most of these is "no," your data is folklore. Acknowledge it.

### Step 7: Capture Evidence That Survives the Bug

Design instrumentation that captures the failing state itself, not just what led up to it:

- **Ring buffers** of recent events, dumped on assertion failure
- **Flight recorders** that snapshot state on signal
- **Crash dumps** with full thread state
- **Last-known-good vs last-known-bad** diffs
- **Reproducer harnesses** that re-run with full tracing only when triggered

This converts "I need to add a log and try again" (which perturbs) into "the bug already produced its own evidence."

## Output Format

```
OBSERVER-EFFECT ANALYSIS

Symptom:
- ...

Observation modes tried:
- Mode | Disturbance | Result | Trust

Hypothesis about the perturbation:
- The instrument is [adding latency / serializing / allocating / forcing evaluation / aliasing] in [location]

Predicted behavior with probe removed:
- ...

Probe reduction plan:
- Replace [X] with [smaller probe Y] because [...]

Out-of-band corroboration:
- ...

Confidence:
- Effect size: ...
- Probe perturbation: ...
- Ratio: ...
- Verdict: trust / suspect / collect more
```

## Anti-Patterns to Avoid

- **"It works in the debugger"** treated as good news — it's diagnostic information, not resolution
- **Adding more logs to a logging-sensitive bug** — you are adding more disturbance to a disturbance-sensitive system
- **Trusting a sampling profiler for tail-latency questions** — sampling under-represents long tails
- **Confusing absence of evidence with evidence of absence** under sampling
- **Calling everything "Heisenberg"** — be specific about probe effect, JIT deopt, scheduling, etc.
- **Ignoring the cost of telemetry itself** — high-cardinality metrics can be the load that causes the latency you're measuring
- **Removing the only working repro to "clean up"** — if logging makes it reproducible, the logging *is* part of the experiment until you understand why
- **Assuming production behaves like instrumented staging** — staging with full tracing is a different physical system

## Relationship to Other Skills

- Use `popperian-debug` for hypothesis structure once you know your observations are trustworthy.
- Use `statistical-debugging` when the bug is a flaky distribution rather than a single event.
- Use `signal-detection-review` to choose thresholds and sampling rates that won't alias.
- Use `feedback-loop-analysis` when the observation feeds back into the system (auto-scaling, rate limiting on log volume).
- Use `formal-invariants` to install passive checks that fire only on violation, minimizing steady-state observation cost.
