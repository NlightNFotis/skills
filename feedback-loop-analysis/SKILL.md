---
name: feedback-loop-analysis
description: Analyze retries, queues, rate limits, cancellations, streaming, and reactive loops for stability.
user-invocable: true
---

# Feedback Loop Analysis

Act as a control-theory and cybernetics reviewer embedded in the engineering process. Whenever a system uses its own output to influence its next input — through retries, autoscaling, rate limits, queue feedback, backpressure, polling, or learning — a feedback loop exists. The stability and behavior of those loops are governed by well-understood principles: gain, delay, saturation, and damping. Most "the system suddenly fell over" incidents are loop-stability failures.

Success looks like identifying every relevant loop, classifying it, estimating gain and delay, and either proving it stable or recommending a control mechanism (jitter, backoff, hysteresis, circuit breaker, admission control). Failure looks like adding more retries to fix a retry storm, ignoring loop delays, or designing controllers that drive their own input.

## When to Use This

- Designing or reviewing retries, polling, queues, rate limits, backpressure, autoscaling, cancellation, streaming, or agent loops
- Systems oscillate, thrash, overload, or never settle
- A local recovery mechanism is suspected of amplifying the failure it was meant to fix
- Latency or queue depth shows ringing or sustained oscillation
- Designing any controller (autoscaler, scheduler, allocator, learner)
- A subsystem worked at low load and collapsed at high load
- Reviewing post-incident reports mentioning "death spiral", "thundering herd", or "metastable"

**Escape hatch**: If the bug is a single-shot logic error with no feedback (no retries, no shared queue, no controller adjusting based on output), this skill is overkill — use `popperian-debug`. Loop analysis is for systems where today's behavior is shaped by yesterday's behavior.

## Core Mindset

A feedback loop is stable when its corrections damp out, unstable when they amplify, and metastable when it has more than one stable regime. Ask:

- What is the signal, the controller, the action, the system response, the feedback path?
- Is the loop **balancing** (negative feedback, seeks setpoint) or **reinforcing** (positive feedback, runs away)?
- What is the loop **gain**? Per unit of error, how much correction?
- What is the **delay** from action to observed feedback? Long delays + high gain = oscillation.
- What **saturates**? Beyond what point does additional correction stop helping?
- What is the **dead time** before any response is observed?
- Does the controller's action change the very signal it measures (instrumentation reflexivity)?

## Control-Theory Vocabulary

| Concept | Meaning | Software example |
| --- | --- | --- |
| **Open loop** | Action without feedback | Fire-and-forget request |
| **Closed loop** | Action adjusted based on outcome | Retry until success |
| **Setpoint** | Desired value | Target queue depth, target p99 |
| **Gain** | How strongly a controller responds to error | Retry count per failure |
| **Dead time** | Delay before any response is seen | Health-check interval, propagation delay |
| **Hysteresis** | Different thresholds for entering vs leaving a state | Scale-up at 70%, scale-down at 40% |
| **Saturation** | Output capped; further error doesn't increase response | Connection pool maxed |
| **Integral windup** | Accumulated error grows during saturation, causes overshoot on release | Backed-up retry queue dumps when service recovers |
| **Ringing / oscillation** | Repeated overshoot/undershoot around setpoint | Autoscaler bouncing pod count |
| **Damping** | Mechanism that reduces oscillation | Smoothing, EWMA, slower reaction |
| **Phase margin** | How close the loop is to instability | Headroom before oscillation |
| **AIMD** | Additive Increase, Multiplicative Decrease | TCP congestion control |
| **Token bucket** | Burst-tolerant rate limit | API rate limiter with refill rate |
| **Leaky bucket** | Smoothed-output rate limit | Egress shaper |
| **Backpressure** | Downstream slowness propagates upstream as slowdown | Reactive streams, blocking enqueue |
| **Circuit breaker** | Open the loop entirely under sustained failure | Stop calling a known-down dependency |

### PID intuition (you don't need the math)

- **P** (proportional): respond in proportion to current error → simple, can ring
- **I** (integral): respond to accumulated error → kills steady-state offset, prone to windup
- **D** (derivative): respond to rate of change → predictive, anticipates overshoot, sensitive to noise

Most software controllers are crude P controllers. Many failures come from missing the I or the D — or from having effective I (an unbounded queue) without the windup discipline.

### Canonical instability patterns

- **Retry storm**: failure → retries → more load → more failure (R loop, no damping)
- **Thundering herd**: synchronized waiters wake on one event, swamp downstream (no jitter)
- **Cache stampede**: synchronized TTL expiry → mass recompute (no coalescing)
- **Autoscaler thrashing**: scale-up triggers metrics that look like overload, scale up again
- **Death spiral**: a slow node gets more retries → gets slower → gets more retries
- **Metastable failure** (Bronson et al.): trigger creates a load pattern that persists after the trigger is removed
- **Bufferbloat**: large buffers hide congestion; latency soars while throughput drops
- **TCP collapse style**: aggregate behavior collapses despite each actor following local "best effort"
- **Ariane 5 style**: control loop driven by data outside its design envelope

## The Process

### Step 1: Identify the Loop

Make the loop explicit. If you can't draw it in five lines of text, the boundary is wrong.

```
LOOP:
- Signal measured: ...
- Controller / decision rule: ...
- Action taken: ...
- System response: ...
- Feedback path back to signal: ...
- Loop period (action → observable feedback): ...
```

There may be multiple loops on the same plant. List each.

### Step 2: Classify Each Loop

- **Balancing (negative)**: pushes back toward setpoint — usually desired
- **Reinforcing (positive)**: amplifies — desired for growth, dangerous for failure
- **Nested**: inner loop fast, outer loop slow (e.g., inner retry, outer circuit breaker)
- **Competing**: two controllers chasing different setpoints on the same actuator
- **Hidden**: feedback that wasn't intended (logs causing disk pressure causing GC causing latency)

### Step 3: Estimate Gain, Delay, and Saturation

For each loop:

```
LOOP CHARACTERISTICS:
- Gain: per unit of error, how much action? (retries per failure, pods per RPS)
- Dead time: how long before action's effect is visible?
- Saturation point: where does the action stop helping?
- Noise floor: variability that the controller will chase as if real?
```

Rule of thumb: **High gain + long delay = oscillation**. Either reduce gain, reduce delay, or add damping.

### Step 4: Look for Amplification of Failure

The most common production-killing pattern. Walk through:

- Does failure cause more requests (retries, fall-through to another path)?
- Do retries share fate (all hit the same dependency)?
- Does the retry budget refresh per-request (effectively infinite retries)?
- Does a circuit breaker exist, and is its threshold tuned for *aggregate* not per-instance behavior?

Apply Little's Law (`L = λ × W`) to estimate queue growth: if mean arrival rate exceeds service rate even briefly, the queue grows linearly with time.

### Step 5: Check for Synchronization

Stability often depends on actors *not* being aligned. Search for:

- Backoff without jitter
- Identical TTLs set at deploy time
- Identical poll intervals
- Identical health-check periods
- Synchronized restarts (rolling deploy with too-narrow window)

The fix is almost always **add jitter** — randomize timing within a band.

### Step 6: Evaluate the Controller's Reflexivity

A controller that changes the signal it measures has a problem:

- Adding logs to debug latency increases latency
- Health checks that themselves cause load
- Autoscaler metrics that include autoscaler activity
- Sampling that biases the next sampling decision

Either decouple the measurement (separate path) or model the reflexivity explicitly.

### Step 7: Choose Controls

Match control mechanism to instability mechanism:

| Instability | Control |
| --- | --- |
| Retry amplification | Exponential backoff with jitter, retry budget, circuit breaker |
| Thundering herd | Jitter, request coalescing, randomized stagger |
| Cache stampede | Single-flight, jittered TTL, probabilistic early refresh |
| Autoscaler thrashing | Hysteresis (different scale-up/down thresholds), cooldown, EWMA on input metric |
| Bufferbloat / unbounded queue | Bounded queue + drop or shed policy (CoDel-style) |
| Integral windup | Reset on circuit-open, cap accumulated state |
| Death spiral routing | Outlier ejection, slow-start, load-aware LB |
| Metastable lock-in | Load shedding on entry to bad regime, kill switch |
| Hidden feedback | Decouple measurement from action |

### Step 8: Verify with a Mental Step Response

For each control you propose, walk through:

> Step input: failure rate jumps from 0% to 50%. After 1s/10s/1m, what does the loop do? Does it converge, oscillate, or diverge?

If you can't answer this, the control isn't yet specified well enough.

## Output Format

```
FEEDBACK LOOP ANALYSIS

Loops identified:
1. [name]
   - Signal:
   - Controller:
   - Action:
   - Feedback path:
   - Loop period:
   - Type: balancing / reinforcing / nested / competing / hidden

Per-loop characteristics:
- Gain / delay / saturation / noise floor

Amplification risks:
- ...

Synchronization sources:
- ...

Controller reflexivity issues:
- ...

Recommended controls (matched to instability):
1. ...

Step-response sketch (post-fix):
- t=0 perturbation: ...
- t=1×period: ...
- t=10×period: ...
- Steady state: converges / oscillates / diverges

Observability for the loop:
- What metric proves the loop is stable in production?
```

## Anti-Patterns to Avoid

- **Adding retries to fix a retry storm**: more of the amplifier
- **Backoff without jitter**: just delays the synchronized retry
- **Tuning a single number without modeling the loop**: timeout/threshold whack-a-mole
- **Ignoring delayed feedback**: long dead time + high gain → oscillation
- **Using the same signal for progress and control**: the signal becomes meaningless
- **Letting failure create more load**: retries, fall-through, eager re-fetch
- **Unbounded queues as "buffers"**: bufferbloat hides the problem until collapse
- **Per-request retry budgets**: effectively infinite when failure rate is high
- **Assuming open-loop is safe**: silent degradation is its own failure mode

## Relationship to Other Skills

- Use `emergence-analysis` to spot when many independent loops produce a system-level dynamic (synchronized retries → herd).
- Use `systems-archetypes` when the loop matches a named pattern (Escalation, Fixes that Fail).
- Use `constraint-analysis` to identify where the loop saturates — that bottleneck is often the right control point.
- Use `network-topology-review` to map which dependents share fate when a hub's loop saturates.
- Use `code-forensics` to reconstruct the timing of an oscillation or metastable incident from logs.
- Use `formal-invariants` to encode bounds (queue length, in-flight count, retry budget) as runtime checks.
