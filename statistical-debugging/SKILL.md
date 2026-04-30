---
name: statistical-debugging
description: Reason about flaky tests, noisy metrics, confidence, base rates, false positives, and experiment interpretation.
user-invocable: true
---

# Statistical Debugging

Act as a statistician embedded in the engineering workflow. Treat flaky tests, noisy metrics, intermittent failures, A/B results, and CI signals as **probabilistic observations from an unknown distribution**, not as ground truth. Your job is to separate signal from noise before anyone changes code.

Success looks like: claims are quantified ("this fails 3% of runs, n=200"), confounders are named, and the next action is the cheapest measurement that materially shifts confidence. Failure looks like reading one green CI run as proof a flake is fixed, or attributing a metric movement to a deploy without checking the base rate.

## When to Use This

- A test is suspected of being flaky
- A metric moved and someone wants to attribute it to a change
- An intermittent bug appears under unknown conditions
- A perf regression is claimed but variance is high
- Bisection results conflict across runs
- A deploy "fixed" something but the fix can't be explained
- You need to express **confidence**, not certainty

**Escape hatch**: If the failure is deterministic and reproduces every time, this skill is overkill — use `popperian-debug` instead. If a metric move is huge (10×), ordinary engineering judgment beats statistics; reach for this skill when effects are subtle or intermittent.

## Core Mindset

Ask:

- What is the **base rate** of this event in normal conditions?
- How many independent observations do I have? (n=1 is anecdote)
- What is the **noise floor** — the variance I would see even with no real change?
- What **confounders** could explain this without my hypothesis being true?
- Could **selection bias** explain why I'm seeing only these cases?
- Am I about to commit a Type I error (false alarm) or Type II error (missed real signal)?
- Would a fair coin produce this pattern with reasonable probability?

## Statistical Vocabulary

| Concept | Software-debugging meaning |
| --- | --- |
| **Base rate** | How often the event happens with no intervention |
| **Sample size (n)** | Number of independent runs/observations |
| **Variance / noise floor** | The natural spread when nothing has changed |
| **Confidence interval** | A range that likely contains the true rate; widens as n shrinks |
| **Type I error** | False positive: claiming a fix/regression that isn't there |
| **Type II error** | False negative: missing a real fix/regression |
| **Confounder** | A third variable that moves with both cause and effect |
| **Simpson's paradox** | An aggregate trend reverses when split by a subgroup |
| **Regression to the mean** | Extreme observations are followed by less extreme ones, with no cause |
| **Survivorship bias** | Conclusions drawn only from cases that "survived" some filter (e.g., only green CI) |
| **Selection bias** | The sample isn't representative of the population you care about |
| **p-hacking** | Trying many comparisons until one looks significant |
| **Multiple comparisons** | More tests → more false positives by chance alone |
| **Stationarity** | Whether the underlying distribution is changing over time |
| **Bisection as binary search** | Each test halves the suspect space; flakiness breaks the invariant that bisect requires |

## The Process

### Step 1: Define the Random Variable

State precisely what is being measured.

```
OBSERVATION:
- Variable: [what is observed each trial]
- Unit of trial: [single test run / single request / single user-day]
- Outcome space: [pass/fail | latency in ms | count of errors | ...]
- How a trial is independent of others:
```

If trials are not independent (same machine, same warm cache, same flaky upstream), say so. This bounds how much information n trials actually give you.

### Step 2: Establish the Baseline (Pre-Intervention)

You cannot detect signal without a noise floor.

- How often does this fail / spike / regress under **normal** conditions?
- What is the historical variance over the last N days/runs?
- Has the baseline itself drifted (non-stationary)?

If you don't know the baseline, your first action is to **measure it**, not to fix anything.

### Step 3: Plan the Sample

Before collecting more data, decide how much you need.

| Effect size you want to detect | Rough sample order |
| --- | --- |
| Failure rate ~50% changing to ~25% | tens of runs |
| Failure rate ~5% changing to ~1% | hundreds of runs |
| Latency p50 shift of >5% | hundreds with paired runs |
| Latency p99 shift | thousands; tail estimation is hard |
| One-in-a-thousand rare bug | thousands, plus instrumentation |

n=1 proves nothing. n=3 with all-pass proves almost nothing about a 5% flake. Decide the budget *before* looking at the next result, to avoid stopping when you like the answer.

### Step 4: Collect Under Controlled Conditions

Hold confounders constant where you can; record them where you can't.

- Same machine, same commit, same data, same time window
- Record: machine, commit, OS, CPU load, network, time of day, concurrent jobs
- Run interleaved (A,B,A,B,...) rather than blocked (AAA,BBB) to absorb temporal drift
- For flaky tests: run in a tight loop; record pass/fail sequence, not just summary

### Step 5: Separate Signal from Noise

Compare the observation to what noise alone would produce.

- Could this difference happen by chance given n and baseline variance?
- For pass/fail: a binomial sanity check. If baseline flake is 5% and you saw 1/20 fails, that is entirely consistent with no change.
- For metrics: report the distribution, not just the mean. Medians and tails tell different stories.
- For attribution: if a metric moved, check whether it was already drifting *before* the suspected change.

If the observed effect is within the noise floor, the honest answer is **"insufficient evidence,"** not "no effect."

### Step 6: Hunt Confounders and Biases

Before declaring a cause, list what else could explain it.

| Confounder type | Example |
| --- | --- |
| **Temporal** | Deploy and traffic spike happened together |
| **Selection** | You only retried failed tests, then noticed they pass |
| **Survivorship** | Crashed runs never reached the metric reporter |
| **Simpson's** | Overall pass rate up, but down for every subgroup |
| **Instrumentation drift** | The logger/metric definition changed, not the system |
| **Regression to mean** | Yesterday's outlier looked huge; today's normal looks like a fix |
| **Observer effect** | Adding logs slowed the race condition into hiding |

For each, state how you ruled it in or out.

### Step 7: Quantify the Conclusion

Replace vague claims with bounded ones.

Weak:

> The test is flaky.

Strong:

> The test failed 7/200 runs on commit `abc123` (3.5%, 95% CI ~1.4%–7.0%) on the standard CI image. Failure rate before that commit was 0/200.

Weak:

> The deploy made it slower.

Strong:

> p50 latency rose from 42ms to 47ms (+12%) over 10k requests, with non-overlapping bootstrap CIs. p99 was unchanged. The shift began within 60s of the deploy and persisted for 2h.

### Step 8: Decide the Cheapest Next Measurement

Pick the action that maximally shifts your posterior:

- More n at current settings (cheap, narrows CI)
- Run on a different machine/region (tests environment confounder)
- Revert the suspect change and remeasure (tests causality)
- Add instrumentation to capture the missing variable
- Stratify the existing data by a suspected confounder

For a flaky test, the question is rarely "is it flaky?" but **"what's the failure rate, and what variable predicts it?"** Run it 100× under each suspected condition and compare.

## Output Format

```
STATISTICAL DEBUGGING REPORT

Observation:
- Variable, unit of trial, outcome space:

Baseline:
- Historical rate / distribution (with n):

Samples collected:
- n, conditions held constant, conditions recorded:

Result:
- Point estimate + interval / distribution summary:

Noise floor check:
- Is the effect distinguishable from chance? Why:

Confounders considered:
- [name] → [ruled in/out, with evidence]

Conclusion (with confidence):
- ...

Next measurement (cheapest, most informative):
1. ...
```

## Anti-Patterns to Avoid

- **n=1 conclusions**: declaring a flake fixed because one rerun passed
- **Stopping at the first green**: optional stopping inflates Type I error
- **Confusing absence of evidence with evidence of absence**: low n means low power, not "no effect"
- **Bisecting through flakiness**: each step needs a deterministic signal; bisecting noise gives garbage commits
- **Mean-only reporting**: tails and medians often disagree with means, especially for latency
- **Ignoring the base rate**: a 1% rare event happens often at scale; rarity ≠ cause
- **Survivorship blindness**: only looking at runs that completed, jobs that logged, users who returned
- **p-hacking**: running 20 comparisons and reporting the one significant result
- **Post-hoc storytelling**: inventing a causal narrative for what is actually regression to the mean

## Relationship to Other Skills

- Use `popperian-debug` once you've isolated a deterministic repro from the statistical noise.
- Use `code-forensics` to align timestamps and changes with metric movements.
- Use `differential-diagnosis-debugging` when several causes could each produce the same statistical pattern.
- Use `assumption-audit` to question what your trials are actually independent of.
- Use `bias-audit` when results feel "too good" or selectively support a preferred theory.
