---
name: control-systems-pid
description: PID controllers and classical control theory applied to autoscalers, congestion control, rate limiters, and any feedback-driven regulator. Use when a system must drive a measured variable to a setpoint without oscillating, overshooting, or stalling.
user-invocable: true
---

# Control Systems and PID

Act as a control engineer reviewing a regulator. A thermostat, a cruise control, an autoscaler, and a TCP congestion window are the same problem in different clothes: measure something, compare to a setpoint, decide an actuation, repeat — without oscillating, without sticking, without overshooting, in the presence of dead time and disturbances. The PID controller and its surrounding theory are the standard tool. Most software regulators that misbehave (autoscalers that flap, retry storms that synchronise, rate limiters that thrash) are reinventing control theory poorly.

Success looks like a regulator that converges quickly to setpoint, rejects disturbances, does not oscillate, and degrades gracefully when the actuator saturates. Failure looks like sustained oscillation, integral windup after an outage, or a system that "tunes itself" by being constantly re-tweaked by humans.

## When to Use This

- Designing or reviewing an autoscaler
- Tuning a rate limiter, retry budget, or backoff schedule
- Diagnosing oscillation, flapping, or instability in any feedback-driven system
- Congestion control / flow control design
- Thermal or resource throttling
- Queue-length controllers, admission controllers
- Any time a system must keep a measured variable near a target while disturbances and delays exist

**Escape hatch**: If the system is open-loop (no feedback) or operates as a one-shot decision rather than continuous regulation, control theory is the wrong tool. Use this skill where the structure is *measure → compare → actuate → repeat*.

## Core Questions

Ask:

- What is the **process variable** (PV) being measured?
- What is the **setpoint** (SP)?
- What is the **manipulated variable** (the actuator's output)?
- What is the **dead time** between actuation and observation?
- Are there disturbances I am rejecting, or am I just tracking a setpoint?
- What is the actuator's range, and what happens when it saturates?
- What is the cost of overshoot vs the cost of slow convergence?
- How will I tune the gains, and how will I prove stability?

## Domain Vocabulary

| Term | Definition | Software example |
| --- | --- | --- |
| **Process variable** (PV) | The measured quantity being regulated | CPU%, queue length, request rate |
| **Setpoint** (SP) | The target value | 70% CPU, 100 in-flight, 1000 RPS |
| **Error** (e = SP − PV) | Signed deviation | Drives the controller |
| **Manipulated variable** (MV) | What the controller adjusts | Replica count, send window, token rate |
| **Plant** | The system being controlled | The service whose CPU we are regulating |
| **Dead time** (transport delay) | Lag between MV change and PV response | Pod startup, metric scrape interval, RTT |
| **Time constant** (τ) | How fast the plant responds, once it starts | Warm-up time, queue-drain rate |
| **Proportional** (P) | MV ∝ error | Reacts to *now* |
| **Integral** (I) | MV ∝ ∫ error dt | Eliminates *steady-state* offset |
| **Derivative** (D) | MV ∝ d(error)/dt | Dampens *oscillation*, reacts to *trend* |
| **Gain** (K_p, K_i, K_d) | Tunable multiplier per term | The "tuning knobs" |
| **Setpoint tracking** | Driving PV to follow a changing SP | Auto-tune scaling target |
| **Disturbance rejection** | Holding PV against external load changes | Holding latency under traffic spike |
| **Feedforward** | Open-loop adjustment based on a known disturbance | Pre-scale before a known marketing event |
| **Cascade control** | Outer loop's output is inner loop's setpoint | Outer: latency target; inner: replica count |
| **Integral windup** | I-term grows huge during actuator saturation | Autoscaler stuck at max queues up "wanted more" |
| **Anti-windup** | Clamp I-term while saturated | Stop integrating when MV is at the rail |
| **Derivative kick** | D spikes when SP changes step-wise | Replace d(error)/dt with −d(PV)/dt |
| **Bumpless transfer** | Smooth handover between manual and auto modes | Initial I-term seeded from current MV |
| **Gain margin** | How much K can grow before instability (in dB) | Stability headroom |
| **Phase margin** | How much extra phase lag before instability (in deg) | Robustness to added delay |
| **Hunting / oscillation** | PV swings around SP without settling | Autoscaler flapping between N and N+5 replicas |

### What each term does (the one-line summary)

- **P alone**: responds to current error, leaves a steady-state offset, can oscillate at high gain.
- **PI**: eliminates offset, slower than P-only, can wind up if actuator saturates. **The standard for most software regulators.**
- **PID**: adds damping via D, but D amplifies measurement noise; rarely needed in software because dead time usually dominates.
- **Tip**: if a software regulator is misbehaving, the problem is almost always (a) too much P gain, (b) windup of I during saturation, or (c) trying to control through too much dead time. Reach for tuning before reaching for D.

### Tuning rules of thumb

| Method | When | How |
| --- | --- | --- |
| **Ziegler–Nichols (closed-loop)** | Plant tolerates oscillation during tuning | Find K_u (gain at sustained oscillation) and period T_u, then K_p = 0.6 K_u, T_i = T_u/2, T_d = T_u/8 |
| **Cohen–Coon** | Plant has significant dead time (typical for software) | Use plant's step response to compute gains; better than Z–N when dead-time/τ > 0.3 |
| **IMC / lambda tuning** | You want predictable closed-loop response time | Choose desired closed-loop τ, derive gains analytically |
| **Empirical halving** | Production system, no model | Halve K_p until oscillation stops, then add I slowly |

## The Process

### Step 1: Name the Loop Precisely

Before any tuning, write the loop down.

```
LOOP DEFINITION:
- Process variable (PV): [units, sample rate]
- Setpoint (SP): [value, how it is set]
- Manipulated variable (MV): [units, range, rate-limit]
- Plant: [what physical/logical system responds]
- Dead time: [estimate]
- Time constant: [estimate]
- Disturbances: [external loads that shift PV independently of MV]
- Sample period: [Δt]
```

Many bad regulators come from a missing entry in this table — usually dead time or actuator range.

### Step 2: Decide Which Terms You Need

Default to PI. Add D only if you have proven the case.

| Symptom | Add | Note |
| --- | --- | --- |
| Persistent steady-state offset | I | The classic reason to add I |
| Slow oscillation (period > 5× dead time) | More D *or* less P | Often reducing P is better |
| Fast oscillation (period ~ dead time) | Reduce P, do not add D | Dead time dominates; D will not save you |
| Noisy PV causing actuator chatter | Filter PV; do *not* add D | D amplifies noise |

In software, P-only causes offset; PID causes high-frequency chatter unless PV is well-filtered. PI is usually the right answer.

### Step 3: Confront Dead Time

Dead time is the thing that kills control loops. The Smith predictor and similar techniques exist precisely because dead time makes simple PID nearly ungovernable when it dominates.

Software dead times are often huge:

- Pod startup: 30–120s
- Metric scrape interval: 15–60s
- Aggregation window: 60–300s
- DNS / config propagation: tens of seconds

If dead time T_d is comparable to or greater than the time constant τ, no amount of PID tuning will yield a fast loop. Options:

- **Reduce dead time** (cache warm pools, shorter scrape, shorter aggregation window) — usually highest leverage
- **Slow the loop** to match dead time — controller cycle ≥ 3 × dead time, gains scaled accordingly
- **Feedforward** for disturbances you can predict (scheduled traffic, known release patterns)
- **Cascade control** — fast inner loop on a proxy variable, slow outer loop on the real target

### Step 4: Bound the Actuator and Plan for Saturation

Every real actuator has a range. Replica counts have min/max; rate limiters have a token bucket size; congestion windows have an MSS floor. The controller must know this range.

When the actuator saturates (MV pinned at min or max):

- **Anti-windup**: stop integrating error during saturation, or back-calculate I to the value that would just unsaturate the MV
- **Mode awareness**: tell the rest of the system "I am asking for more than I can deliver" — surface as a metric or alert
- **Rate limit on MV change**: protects the plant from violent moves (e.g., do not double replica count in one tick)

Without anti-windup, an autoscaler that hits max during a 20-minute traffic spike will request "tens of thousands" of additional replicas internally; when the spike ends, it will then *under-provision* for an hour as the I-term unwinds.

### Step 5: Avoid Derivative Kick

If D is on the error term and SP changes step-wise, the derivative spikes to a huge value, slamming the actuator. The fix is to take the derivative on the **measurement** instead of the error:

```
Standard (kicks):     D = K_d * d(SP - PV)/dt
Derivative-on-PV:     D = -K_d * d(PV)/dt
```

For SP-tracking applications (autoscaler whose target moves), this is essential. For pure disturbance-rejection applications (SP fixed), the difference vanishes.

### Step 6: Choose Setpoint Tracking vs Disturbance Rejection

These have different optimal tunings.

| Goal | Tuning bias | Example |
| --- | --- | --- |
| **Setpoint tracking** (SP changes; follow it) | Higher P, lower I; consider feedforward | "Scale to match a forecast" |
| **Disturbance rejection** (SP fixed; reject load) | Lower P, higher I; aggressive on offsets | "Hold latency under spike" |

One controller can do both, but the tuning is a compromise. Cascade or parallel structure can break the compromise.

### Step 7: Verify Stability Before Deploying

Before pushing a tuned loop to production:

- **Simulate** with a plant model (even a crude first-order-plus-dead-time model is enough)
- Check **gain margin** ≥ 6 dB (factor of 2) and **phase margin** ≥ 45° as defaults
- Test **disturbance step**: how does PV respond to a sudden load change?
- Test **setpoint step**: how fast does it converge, with what overshoot?
- Test **actuator saturation recovery**: deliberately starve it, then release, watch for windup
- **Stress** the dead time by adding 50% more — does it still converge?

The 50% dead-time stress test catches loops that work in lab but fail when production scrapes lag.

### Step 8: Bumpless Manual / Auto Switching

A loop will be put into manual mode (during incidents, during deploys, during tuning). Initialise the controller's internal state when re-engaging auto so the actuator does not jump:

- Seed the I-term such that the immediate MV equals what the operator was producing
- Reset D-term history
- Log the transition

This is the difference between "we re-enabled the autoscaler and it kept working" and "we re-enabled the autoscaler and it instantly halved the fleet."

## Output Format

When using this skill, produce:

```
PID CONTROL DESIGN

Loop:
- PV / SP / MV / units
- Plant model: dead time = ..., time constant = ...
- Sample period:

Controller structure:
- P / PI / PID / cascade / feedforward
- Why this structure (vs simpler):

Gains:
- K_p =
- K_i = (or T_i)
- K_d = (or T_d)
- Tuning method used:

Saturation handling:
- MV range:
- Anti-windup strategy:
- Rate limit on MV:

Stability check:
- Simulated step response: settling time / overshoot:
- Gain margin / phase margin:
- Dead-time stress (×1.5):

Operational concerns:
- Bumpless transfer logic:
- Manual override metric:
- Alert on persistent saturation:
```

## Anti-Patterns to Avoid

- **P-only with offset hidden by humans** — operators tweak SP to hide steady-state error; just add I
- **Derivative on noisy PV without filtering** — amplifies noise into actuator chatter
- **No anti-windup** — saturation during outages causes wild swings on recovery
- **Tuning through dead time** — no gain combination saves a loop where T_d >> τ; shorten dead time first
- **Ignoring actuator rate limits** — controllers that issue impossibly fast MV changes destabilise the plant
- **Setpoint kick** — letting SP step changes drive D-term spikes
- **Treating "we reduced gains until it stopped oscillating" as tuning** — it is not; you have lost disturbance-rejection performance
- **Hidden cascades** — two regulators acting on the same PV with conflicting setpoints (autoscaler vs HPA vs custom controller)
- **Tuning in production without a model** — at least sketch a first-order-plus-dead-time fit before turning knobs

## Relationship to Other Skills

- This is a **deep specialisation of `feedback-loop-analysis`**. Use that skill for the broader question of whether a loop exists, is stable, and is appropriately bounded; reach for this skill when the loop is identifiably a regulator and you need to design or tune it.
- Use `factor-of-safety` to set the gain margin and phase margin targets — they are the FoS of a control loop.
- Use `tolerance-stack-up` when the dead-time budget is itself the sum of several stages (scrape + aggregate + decide + actuate).
- Use `signal-detection-review` when the controller's *measurement* (PV) is itself a noisy classifier whose threshold matters.
- Use `resilience-engineering` for what happens when the controller itself fails or is disabled — degraded modes, fallback policies, manual override paths.
