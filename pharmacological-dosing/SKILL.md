---
name: pharmacological-dosing
description: Apply pharmacology — dose-response, therapeutic window, half-life, titration, interactions — to system parameter changes, rollouts, and tuning.
user-invocable: true
---

# Pharmacological Dosing

Act as a clinical pharmacologist embedded in the engineering workflow. Your job is to treat configuration changes, feature flag rollouts, rate limits, retry budgets, parameter tunings, and telemetry sampling rates as **doses administered to a living system**. The system has a dose-response curve. There is a therapeutic window between "no effect" and "toxic." Some changes have a long half-life; others wash out immediately. Some interact with other doses already in the bloodstream.

The goal is to stop thinking of parameter changes as "just numbers" and start thinking of them as treatments with onset, peak, steady state, side effects, withdrawal, and contraindications. The principle "start low, go slow" is older than medicine and still the cheapest way to avoid catastrophe.

## When to Use This

- Rolling out a feature flag (especially one that changes load, latency, or behavior)
- Tuning a rate limit, retry budget, timeout, or backoff
- Changing a sampling rate, log level, or telemetry cardinality
- Adjusting an autoscaler threshold, queue depth, or pool size
- Tuning hyperparameters or model serving knobs
- Sequencing multiple config changes that may interact
- Designing an A/B test (sample size, exposure, washout)
- Reasoning about config changes that won't show effects for hours/days (caches, indexes, learned behavior)

**Escape hatch**: For parameter changes with no dose-response (boolean correctness toggles, code refactors with no behavioral surface), this skill doesn't apply — use `formal-invariants` or `mistake-proofing` instead.

## Pharmacological Vocabulary

| Concept | Meaning | System analogue |
| --- | --- | --- |
| **Dose** | Quantity of substance administered | Magnitude of the parameter change (delta, not absolute) |
| **Dose-response curve** | Effect as a function of dose | Latency vs concurrency, error rate vs retry budget, hit rate vs cache size |
| **ED50** | Dose producing 50% of max effect | The "knee" of the response curve |
| **LD50 / toxic dose** | Dose producing harmful effect in half the population | The point past which the system tips into instability |
| **Therapeutic window** | Range between effective and toxic | Operating envelope; where you want to live |
| **Therapeutic index** | LD50 / ED50; ratio of safety margin | Wide index = forgiving knob; narrow index = handle with tongs |
| **Half-life (t½)** | Time for concentration to halve | Cache TTL, EMA decay, CDN propagation, learned-model drift |
| **Steady state** | After ~5 half-lives, dose in ≈ dose out | When the change has fully expressed itself |
| **Loading dose** | Initial high dose to reach therapeutic level fast | Cache warm-up, pre-fill, big bang migration |
| **Maintenance dose** | Ongoing dose that holds steady state | Continuous tuning, regular adjustment |
| **Peak vs trough** | Highest and lowest concentrations between doses | p99 vs p50 of the parameter's effect over time |
| **Onset** | Time from administration to detectable effect | Propagation delay, deploy time, cache fill |
| **Synergistic interaction** | Combined effect > sum of individual | Two flags that together cause N×N behavior |
| **Antagonistic interaction** | Combined effect < sum | Retry budget cap masks rate-limit change |
| **Additive interaction** | Combined effect = sum | Independent levers |
| **Tolerance** | Diminishing response with continued dose | Operators ignore alerts after repeated cries-wolf |
| **Withdrawal** | Negative effect when dose removed | "Reverting" causes a spike (warmed cache lost, retry storms) |
| **Contraindication** | Condition under which dose must not be given | "Don't roll this flag during peak"; "don't tune GC during freeze" |
| **First-pass metabolism** | Dose partly cleared before reaching system | Edge layer absorbs the change before origin sees it |
| **Titration** | Stepwise dose increase guided by response | Gradual flag ramp: 1% → 5% → 25% → 100% |

## Core Questions

- What dose am I giving? (delta, not absolute, and per what unit — per node, per request, per user)
- What is the dose-response curve? Linear, exponential, threshold, U-shaped?
- Where is the therapeutic window?
- What is the half-life of this change? When will I see steady state?
- What is the loading dose vs maintenance dose?
- What other "drugs" are already in the system that this might interact with?
- What is the contraindication? When must I refuse to dose at all?
- Is there a withdrawal effect when I revert? Is reversion symmetric?

## Dose-Response Curve Shapes

Recognizing the shape determines the dosing strategy.

| Shape | Looks like | Examples | Dosing strategy |
| --- | --- | --- | --- |
| **Linear** | Effect ∝ dose | More CPU = more throughput up to limit | Easy; titrate freely |
| **Diminishing returns (log)** | Effect ∝ log(dose) | Cache size vs hit rate beyond working set | Find the knee; stop |
| **Sigmoidal** | Flat, knee, plateau | Most biological/system responses; concurrency vs throughput | Find ED50; stay in the steep region |
| **Threshold** | No effect, then sudden | Triggering rate limits; queue tipping into backlog | Either-or; small steps near threshold |
| **U-shaped / biphasic** | Beneficial low, harmful high | Retries (some help, many cause storms); GC tuning | Sweet spot exists; over- and under-dose both harm |
| **Hysteretic** | Different up vs down | Autoscaler with cooldown; user habit change | Cannot reverse by undoing dose |
| **Tachyphylactic** | Effect decreases with repeated dose | Alert tolerance; cache warming after eviction | Plan rotation, not constant dosing |

## The Process

### Step 1: Characterize the Drug

```
DRUG PROFILE:
- Parameter name:
- Current value (trough / steady-state):
- Proposed value:
- Delta (% change, absolute, per-unit):
- Mechanism of action (what does it actually change in the system):
- Onset time:
- Half-life:
- Time to steady state (~5 × t½):
- Reversible? (and at what cost):
```

Without onset and half-life, you cannot read the response curve.

### Step 2: Map the Dose-Response Curve

What is the expected shape of the response? Sketch it before dosing.

```
DOSE-RESPONSE:
- X axis: parameter value
- Y axis: outcome metric of interest
- Shape: linear / sigmoidal / threshold / U-shaped / ...
- Known reference points: (dose, response) pairs from history or experiment
- Believed ED50:
- Believed LD50 (toxic threshold):
- Therapeutic window:
- Therapeutic index (LD50/ED50): wide / narrow
```

Narrow therapeutic index demands titration and monitoring. Wide index permits bigger steps.

### Step 3: Decide on Loading vs Maintenance

| Situation | Strategy |
| --- | --- |
| Need effect immediately, system can absorb shock | Loading dose (full value, all at once) |
| Need effect immediately, system cannot absorb shock | Loading dose with **dilution**: ramp over t½, then hold |
| Effect can wait | Maintenance only; titrate up over multiple half-lives |
| Effect required only transiently | Pulse: short loading, no maintenance |

Cache pre-warming, index back-fill, and migration dual-writes are loading-dose patterns. Gradual rate-limit relaxation is maintenance dosing.

### Step 4: Titrate — "Start Low, Go Slow"

Default ramp pattern:

```
TITRATION PLAN:
- Step 1: 1%   for ≥ 1 × t½, observe peak/trough
- Step 2: 5%   for ≥ 1 × t½
- Step 3: 25%  for ≥ 1 × t½
- Step 4: 50%  for ≥ 1 × t½
- Step 5: 100%

At each step, check:
- Outcome metric in expected range
- No new alerts
- No interactions with existing doses
- No tolerance / habituation effects
```

Hold each step for at least one half-life. Faster ramps are tempting and frequently disastrous near a sigmoidal knee.

### Step 5: Audit Drug Interactions

List every other "drug" currently in the bloodstream and predict the interaction.

```
INTERACTIONS:
- Existing dose 1 (e.g., retry budget = 3) ↔ proposed dose (rate limit ↓)
  - Type: synergistic / antagonistic / additive / unknown
  - Predicted combined effect:
  - Mitigation:
- Existing dose 2 ...
```

Common dangerous combinations:

| Dose A | Dose B | Interaction |
| --- | --- | --- |
| Retry budget ↑ | Rate limit ↓ | Synergistic toward retry storm |
| Cache TTL ↑ | Schema change | Antagonistic; stale clients, longer rollout |
| Autoscaler sensitivity ↑ | Latency-sensitive endpoint | Synergistic toward flapping |
| Sampling rate ↑ | High-cardinality dimension added | Synergistic toward telemetry bill spike |
| Timeout ↑ | Concurrency cap fixed | Antagonistic; longer requests starve queue |

### Step 6: Define Contraindications

When must this dose **not** be given?

```
CONTRAINDICATIONS:
- During [peak hours / freeze / incident / migration window]
- While [other dose X] is also active
- On [population Y] (specific tenant, region, customer tier)
- If [precondition] is not met
```

A "do not dose during peak" rule is cheaper than the postmortem.

### Step 7: Plan Steady State and Withdrawal

After the change, ask:

- When will steady state be reached? (≈ 5 × t½)
- What does steady state look like — peaks, troughs, mean?
- How will we know we are at steady state, not still in transient?
- If we withdraw the dose, is the effect symmetric (concentration just decays) or asymmetric (cache cold, learned model gone, users habituated)?
- Is there a "withdrawal syndrome" — a spike on revert?

If revert is asymmetric, you have prescribed a treatment with no exit; document this as a contraindication for the dosing decision itself.

### Step 8: Watch for Tolerance

Some doses lose effect over time:

- **Alert thresholds** — if the alert fires often, on-call habituates; the dose has no effect even though concentration is unchanged
- **Cache effectiveness** — workload drift erodes hit rate at constant size
- **A/B test novelty** — initial lift fades as users habituate
- **Telemetry signal** — added log line is noticed once, then ignored

Plan rotation, escalation, or mechanism changes — not just bigger doses.

## Output Format

```
DOSING PLAN

Drug:
- Parameter / current / proposed / delta / mechanism

Pharmacokinetics:
- Onset / half-life / time-to-steady-state / reversibility

Dose-response:
- Curve shape / ED50 / LD50 / therapeutic window / therapeutic index

Strategy:
- Loading / maintenance / titration steps

Interactions:
- ...

Contraindications:
- Do not dose when ...

Monitoring during titration:
- Metric | Expected range | Stop condition

Withdrawal plan:
- Symmetric? / Withdrawal effects / Mitigation

Tolerance considerations:
- ...
```

## Anti-Patterns to Avoid

- **Big-bang flag flips** for any parameter on a sigmoidal or threshold curve
- **Ignoring half-life** — declaring success before steady state, or reverting before onset
- **Dosing during contraindication windows** — peak hours, freezes, ongoing incidents
- **Single-dose thinking for chronic problems** — a one-time tuning of an autoscaler doesn't solve drift
- **Ignoring drug interactions** — changing two related parameters simultaneously, then unable to attribute the effect
- **No washout between A/B treatments** — residual effect of treatment A contaminates treatment B
- **Tolerance ignored** — repeating the dose that no longer works
- **Asymmetric reversion treated as symmetric** — "we can always revert" without checking whether revert is actually safe
- **Confusing peak with steady state** — early loading-dose effects misread as the new normal
- **No therapeutic window stated** — every parameter change should declare its expected operating range and toxic threshold

## Relationship to Other Skills

- Use `feedback-loop-analysis` to model retry, autoscale, and queueing dynamics that determine the response curve.
- Use `signal-detection-review` to set monitoring thresholds for the titration window.
- Use `statistical-debugging` for sample-size and confidence in A/B (clinical-trial) dosing.
- Use `failure-mode-effects-analysis` for the toxic-dose scenarios.
- Use `premortem-analysis` for "what does the postmortem of this rollout look like?"
- Use `fermi-estimation` to size loading doses, queue depths, and sampling budgets before dosing.
