---
name: signal-detection-review
description: Tune alerts, tests, warnings, and classifiers around false positives, false negatives, sensitivity, and thresholds.
user-invocable: true
---

# Signal Detection Review

Act as a signal detection theorist embedded in the engineering workflow. Your job is to review any system that distinguishes signal from noise — alerts, tests, warnings, classifiers, anomaly detectors, lint rules, fraud scores, content moderation, captcha — and tune it so the costs of false positives and false negatives are balanced for the *actual* base rate, not the imagined one.

A successful review names the four outcomes (TP / FP / FN / TN) in the system's own terms, estimates their costs, computes (or sketches) the precision and recall implied by current thresholds, and identifies whether the right move is a threshold change, a feature change, two-stage detection, deduplication, escalation, or "delete this alert." A failing review chases "more accurate" without asking *accurate at what, given how rare the thing is*.

## When to Use This

- Alerts are noisy (responder fatigue) or missing real incidents
- Tests are flaky (false positives) or fail to catch real regressions (false negatives)
- A heuristic, classifier, or rule flags too many things — or too few
- A new automated check is being introduced and a threshold needs choosing
- An alert has been muted "temporarily" for more than a week
- The same incident keeps recurring and the alert that should catch it does not
- You are choosing between two detectors and need a principled comparison

**Escape hatch**: Do not run a full signal detection review for a one-off check with obvious cost asymmetry and a near-zero base rate (e.g., "alert me if this DB drops"). Use this skill when there is a real trade-off to make and when responder time, user trust, or test signal is being eroded.

## Core Mindset

Every detector is a **gamble against a base rate**. Even a 99% accurate test is worse than useless when the thing it detects happens 1 in 10,000 times — most of its positives will be wrong. The instinct to "make it more sensitive" is almost always wrong without first asking three questions:

1. How often does the real thing happen? (base rate)
2. What does each kind of mistake cost?
3. Where in the pipeline is this detector — first line or final?

Ask:

- What exactly is "signal" here, and what is "noise"? Define both.
- Out of every 1,000 fires, how many do we think are real?
- What does a missed real one cost? What does a false alarm cost?
- Are responders / users / consumers losing trust in this detector? (Alert fatigue is a *failure mode*, not an inconvenience.)
- Could this be two detectors — a cheap noisy first stage and an expensive precise second stage?

## The Confusion Matrix and Its Vocabulary

Every binary detector lives in a 2×2 table. Learn it cold.

```
                    Reality
                  +-----------+-----------+
                  |  Positive |  Negative |
        +---------+-----------+-----------+
        | Positive|     TP    |     FP    |   ← predicted positives
Predict +---------+-----------+-----------+
        | Negative|     FN    |     TN    |   ← predicted negatives
        +---------+-----------+-----------+
                       ↑           ↑
                  real positives  real negatives
```

| Metric | Formula | Plain English | Also called |
| --- | --- | --- | --- |
| **Sensitivity** | TP / (TP + FN) | Of real positives, how many we caught | Recall, true positive rate |
| **Specificity** | TN / (TN + FP) | Of real negatives, how many we correctly ignored | True negative rate |
| **Precision** | TP / (TP + FP) | Of our positive calls, how many were real | PPV (positive predictive value) |
| **NPV** | TN / (TN + FN) | Of our negative calls, how many were correct | Negative predictive value |
| **False positive rate** | FP / (FP + TN) | Of real negatives, how many we falsely flagged | 1 − specificity |
| **False negative rate** | FN / (TP + FN) | Of real positives, how many we missed | 1 − sensitivity |
| **F1** | harmonic mean of precision & recall | Single score when both matter | |
| **AUC / ROC** | Area under sensitivity-vs-FPR curve | Threshold-free quality of the detector | |

Two of these matter most in operations: **precision** (will the on-call trust me?) and **recall** (am I actually catching the bad thing?). They trade off against each other along the detector's operating point.

## The Base Rate Fallacy — the most important worked example

Suppose you have a really good test for a rare condition:

- Sensitivity: 99% (catches 99% of true cases)
- Specificity: 99% (correctly ignores 99% of non-cases)

Base rate: 1 in 1,000 events is a real positive.

Out of 100,000 events:

- 100 real positives. The detector catches 99. (TP = 99, FN = 1)
- 99,900 real negatives. The detector falsely flags 1% = 999. (FP = 999, TN = 98,901)

**Precision = 99 / (99 + 999) ≈ 9%.**

A 99% accurate detector produces 10 false alarms for every real one. This is exactly why anomaly-detection alerts on rare events are usually noise. The fix is not "more accurate." The fix is: raise the bar for positive (lower recall in exchange for much higher precision), use a two-stage detector, or stop alerting on this at all and rely on a downstream check.

## Vocabulary Beyond the Matrix

| Term | Meaning |
| --- | --- |
| **Operating point** | The threshold at which the detector currently fires; choosing it is a values-laden trade-off |
| **ROC curve** | Trace of TPR vs FPR as the threshold sweeps from strict to permissive |
| **AUC** | Area under the ROC curve; threshold-independent measure of separability |
| **Calibration** | Whether predicted probability matches observed frequency (e.g., does a "70% confidence" alert really fire 70% of the time on real events) |
| **Prevalence** | The base rate in the population the detector sees |
| **Drift** | Over time, the distribution (or base rate) changes; the detector silently degrades |
| **Alert fatigue** | Responders learn to ignore a noisy channel, missing real signals; precision matters because of this |
| **Two-stage detection** | A cheap noisy first stage funnels candidates to an expensive precise second stage |
| **Suppression / deduplication** | Many fires for the same underlying issue collapse to one |
| **Escalation policy** | Different recipients / urgency by confidence, time-of-day, or duration |
| **Signal-to-noise (SNR)** | Useful info ÷ noise; in alerts, real-action-required ÷ total-fires |
| **Actionability** | An alert is actionable if the responder both *can* and *should* do something about it |

## Cost Matrix — make the asymmetry explicit

For every detector, write the cost of each error in the *units that matter to the operator*. Examples:

- **CI test**: FP = engineer wastes 20min investigating; FN = bug ships, costs 4h to root-cause + customer impact
- **Pager alert**: FP = on-call woken at 3am for nothing (compounding fatigue); FN = SEV missed for hours
- **Fraud rule**: FP = legitimate user blocked, refund + support; FN = chargeback + fraud loss
- **Lint rule**: FP = annoying comment, ignored over time; FN = real bug class slips through
- **Spam classifier**: FP = good email lost (catastrophic for some users); FN = inbox noise

If FP and FN have very different costs, they should not have the same threshold treatment. F1 (which weights them equally) is often the wrong metric to optimize.

## The Process

### Step 1: Define Signal and Noise Concretely

Replace "the detector should be accurate" with operational definitions.

```
DETECTOR: ___
SIGNAL (what we want to catch): ___
NOISE (what we want to ignore): ___
SCOPE: when does the detector run, on what data?
```

Weak: "the alert should fire when the service is unhealthy."
Strong: "alert fires when API success rate over rolling 5min window drops below 99.0% on any prod cell — *signal* is a customer-affecting outage; *noise* is single-pod restarts, deploy blips < 60s, dependency-side hiccups already covered by other alerts."

### Step 2: Estimate Base Rate

How often does the real thing actually happen, in the population the detector sees? Use historical incidents, audit reports, sampled review. If you have no estimate at all, *that itself* is the finding — go gather data before tuning.

```
BASE RATE:
- Real positives observed in the last [period]: N
- Detector fires in the same period: M
- Implied current precision (if all real positives were caught): N / M
```

### Step 3: Build the Confusion Matrix from Real Data

Pull the last [N] fires of the detector. For each, classify as TP or FP. Pull the last [M] known incidents (or known regressions, fraud cases, etc). For each, ask: did the detector fire? If not, FN. Sample some negatives to estimate TN.

You will rarely have all four cells precisely; estimates with explicit uncertainty beat hand-waving.

### Step 4: Cost Each Outcome

```
COST PER OUTCOME:
- TP: (value created, e.g., averted incident)
- FP: (in time, money, trust — name the *unit*)
- FN: (impact of the missed event)
- TN: (usually free; sometimes there is opportunity cost)
```

The *expected cost per fire* drives the threshold:

```
E[cost] = P(real | fire) × cost(handle TP) + P(false | fire) × cost(FP)
```

If this is dominated by FP cost, you need higher precision. If by FN cost, higher recall.

### Step 5: Diagnose — What Class of Problem Is This?

| Symptom | Likely problem | Likely treatment |
| --- | --- | --- |
| Many fires, few real | Threshold too sensitive *or* base rate too low | Raise threshold; or stop alerting and use a derived SLO; or two-stage detection |
| Misses real cases | Threshold too strict, or wrong feature | Lower threshold; add feature; longer window; combine signals |
| Noisy bursts during incidents | No deduplication | Group by incident / suppress while parent alert active |
| Alert fires on every deploy | Detector doesn't model deploy as a known state | Suppress during deploy window or compare to deploy-cohort baseline |
| Used to work, getting worse | Drift in base rate or feature distribution | Re-baseline; calibration check; periodic retune |
| Different responders, different reactions | Actionability unclear | Add explicit playbook; if no action exists, delete the alert |
| Two alerts fire for one cause | Redundancy without dedup | Merge or chain; keep the more actionable one |

### Step 6: Choose the Operating Point

Trade off precision vs recall *given the costs you wrote down*. Concrete moves, in order of cheapness:

1. **Raise/lower the threshold** — instant, but only as good as the underlying signal
2. **Lengthen the window / require sustained breach** — kills transient FPs cheaply
3. **Combine features (AND/OR)** — e.g., "error rate up AND latency up AND traffic > X"
4. **Two-stage detection** — cheap noisy first stage triggers precise second stage; only second stage pages
5. **Conditional escalation** — log only at low confidence, ticket at medium, page at high
6. **Suppress under known states** — deploys, maintenance, parent alert active
7. **Re-engineer the underlying signal** — better metric, better feature, model retrain
8. **Delete the detector** — if there is no action it can drive, it is pure cost

### Step 7: Add Suppression, Dedup, and Escalation

Most operational alerts need not just a threshold but a routing policy:

```
ROUTING:
- Group by: (incident key — same service + same symptom collapse)
- Suppress when: (deploy in progress, parent alert firing, scheduled maintenance)
- Escalate: low → log, medium → ticket, high → page
- After-hours rule: (only X severity pages overnight)
- Auto-resolve when: (signal recovers for N minutes)
```

### Step 8: Plan to Re-Measure (Drift)

Detectors decay. Schedule a re-measurement of the confusion matrix. Track precision and recall *as metrics over time*. When precision drops below an agreed floor (often 50% for pages), the detector is broken regardless of how it was originally designed.

## Output Format

```
SIGNAL DETECTION REVIEW — [Detector]

Definitions:
- Signal: ...
- Noise: ...
- Scope (where it runs):

Base rate:
- Real events per [period]: ...
- Detector fires per [period]: ...

Confusion matrix (current):
|         | Real + | Real − |
| Pred +  |   TP   |   FP   |
| Pred −  |   FN   |   TN   |
Precision: ...   Recall: ...   FPR: ...   F1: ...

Cost of errors:
- FP cost (units): ...
- FN cost (units): ...
- Cost asymmetry favors: precision / recall / balanced

Diagnosis:
- ...

Recommended changes (cheapest first):
1. ...

Routing changes (suppression / dedup / escalation):
- ...

Re-measurement plan:
- Cadence:
- Owner:
- Floor (delete or redesign below):

Open questions:
- ...
```

## Anti-Patterns to Avoid

- **Optimizing accuracy on rare events**: ignores base rate; produces high accuracy with terrible precision
- **Treating all errors as equally costly**: F1 by default, regardless of the cost matrix
- **"Just turn up sensitivity"**: trades a known cost (misses) for a hidden cost (alert fatigue)
- **Alerting on non-actionable signals**: if there's no playbook, it's a notification, not an alert
- **Same threshold for all severities**: paging and ticketing have different precision requirements
- **Ignoring drift**: the detector that worked last quarter may be silently failing now
- **No dedup**: one incident, fifty pages
- **Adding more alerts as a fix for missed alerts**: addresses recall by destroying precision
- **No FN measurement**: precision is easy (look at fires); recall requires looking at known events that *should* have fired
- **Muting indefinitely**: a muted alert is a deleted alert — make the deletion explicit and document why

## Relationship to Other Skills

- Use `incident-review` to identify FNs (alerts that should have fired) and FPs (alerts that fired but did not help).
- Use `failure-mode-effects-analysis` to catalogue which failure modes need detection at all, and at what severity.
- Use `resilience-engineering` to build the degradation indicators the detector observes (degraded vs down requires distinct signals).
- Use `operational-game-day` to test whether the detector fires on real injected failures — and only on those.
- Use `assumption-audit` when the detector's correctness depends on unstated premises ("the metric is sampled at 1Hz," "the dashboard is timezone-correct").
- Use `formal-invariants` when the "signal" is really a violated invariant — sometimes the right detector is an assertion, not a metric threshold.
