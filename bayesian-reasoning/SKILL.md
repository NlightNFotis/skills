---
name: bayesian-reasoning
description: Update beliefs about bugs, hypotheses, and triage decisions using priors, likelihoods, and posteriors rather than gut anchoring on the latest piece of evidence.
user-invocable: true
---

# Bayesian Reasoning

Act as a working Bayesian embedded in the engineering workflow. Beliefs are not binary; they have *credences* between 0 and 1. Each new piece of evidence should *update* a credence, not replace it. The goal is to make belief updates explicit, proportionate to evidence strength, and resistant to the dramatic-but-rare evidence that humans systematically overweight.

Where `statistical-debugging` is about *gathering* observations to reduce noise, this skill is about *what to believe* once observations are in hand. It is the antidote to "the latest log line must be the cause" and "this fix worked once so it must be right".

## When to Use This

- Multiple plausible bug hypotheses, with partial and conflicting evidence
- Triaging incoming reports: is this real, a flake, or user error?
- Weighing a single dramatic data point against a large body of routine evidence
- Deciding whether to ship a fix that "seems to work" after one or two trials
- Reviewing a postmortem claim like "the cause was X" — how strong is the inference?
- Evaluating an LLM-generated suggestion that contradicts a long-standing convention

**Escape hatch**: When the evidence is overwhelming and one-sided (a deterministic stack trace pointing at a specific line you just changed), do not perform a formal update. This skill earns its keep when evidence is partial, conflicting, or counterintuitive.

## Core Vocabulary

| Term | Meaning | Example |
| --- | --- | --- |
| **Prior** P(H) | Belief in hypothesis H *before* seeing the evidence | "1% of incoming bug reports turn out to be in this module" |
| **Likelihood** P(E\|H) | Probability of seeing evidence E *if* H is true | "If the bug is here, the test fails 90% of the time" |
| **Marginal** P(E) | Probability of evidence E across all hypotheses | "Tests fail 5% of the time for any reason" |
| **Posterior** P(H\|E) | Updated belief in H *after* seeing E | "Given the test failed, probability the bug is here is …" |
| **Bayes factor** P(E\|H) / P(E\|¬H) | How much E favours H over ¬H | "10x more likely under H than not-H" |
| **Base rate** | The unconditional frequency of H in the population | "1 in 1000 deploys cause an incident" |
| **Credence** | A degree of belief, [0,1] | Distinct from objective probability |
| **Conjugate prior** | A prior whose posterior has the same family | Beta prior + Bernoulli data → Beta posterior |
| **Uniform / informative prior** | Flat (no info) vs shaped (uses known structure) | Use uniform only when you truly have no info |

Bayes' rule: `P(H|E) = P(E|H) · P(H) / P(E)`. The shorthand: posterior ∝ likelihood × prior.

## The Prosecutor's Fallacy (worked example)

A test for a rare disease is "99% accurate". A patient tests positive. What is the chance they have the disease?

- Prior: P(disease) = 1/10,000 = 0.0001
- Likelihood of positive given disease: P(+|D) = 0.99
- Likelihood of positive given no disease: P(+|¬D) = 0.01

Posterior:

```
P(D|+) = 0.99 · 0.0001 / (0.99 · 0.0001 + 0.01 · 0.9999)
       ≈ 0.0098
```

Less than 1%. The "99% accurate test" produces ~99 false positives for every true positive when the base rate is low. The fallacy is treating P(E|H) as if it were P(H|E).

The engineering analogue: "the linter flagged this — therefore it's a bug" ignores how often the linter flags non-bugs (the base rate of false positives) and how rare the true-bug class actually is.

## Core Questions

Before updating any belief, ask:

- What is my prior on this hypothesis, *before* seeing the new evidence?
- How likely is this evidence under the hypothesis?
- How likely is this evidence under the alternatives (especially "nothing unusual")?
- What is the Bayes factor — is this evidence weakly, moderately, or strongly diagnostic?
- After updating, what is the posterior — and is it strong enough to act on?
- Am I anchoring on vivid evidence and ignoring the base rate?

## The Process

### Step 1: Enumerate Hypotheses (Including the Boring Ones)

A Bayesian update is only as good as the hypothesis space. Always include:

- The leading hypothesis you are excited about
- 2–4 alternatives that are materially different
- A "boring" hypothesis: flake, environment difference, test fixture, user error, already-known issue

```
HYPOTHESES:
H1: [exciting new theory]
H2: [alternative cause]
H3: [boring: known flake / fixture / env]
H_other: [residual probability for unknown causes]
```

### Step 2: Set Priors Honestly

Use base rates from the actual system, not from the abstract universe.

- What fraction of incidents in this codebase are in this module? In this layer?
- What fraction of failed CI runs in the last week were flakes?
- What fraction of "the cache is broken" reports turn out to be cache bugs vs upstream bugs?

If you have no data, prefer a *weakly informative* prior over a uniform one. Uniform priors over many hypotheses make every observation look more decisive than it is.

```
PRIORS:
H1: 0.10  (rationale: similar bugs occur ~once a quarter)
H2: 0.30
H3: 0.55  (rationale: 55% of red CI in this repo is flake)
H_other: 0.05
```

Priors must sum to 1.

### Step 3: Estimate Likelihoods

For each hypothesis, estimate P(evidence | hypothesis). Be willing to write 0.5 ("I have no idea") when honest.

```
EVIDENCE: test fails only on Linux CI, passes locally on macOS
LIKELIHOODS:
- P(E | H1: race condition)         ≈ 0.6
- P(E | H2: linux-specific syscall) ≈ 0.9
- P(E | H3: known flake)            ≈ 0.4
- P(E | H_other)                    ≈ 0.3
```

### Step 4: Compute the Posterior

`posterior_i ∝ prior_i · likelihood_i`. Normalize so they sum to 1.

```
unnormalized: 0.10·0.6 + 0.30·0.9 + 0.55·0.4 + 0.05·0.3
            = 0.06 + 0.27 + 0.22 + 0.015 = 0.565

POSTERIORS:
H1: 0.06  / 0.565 ≈ 0.11
H2: 0.27  / 0.565 ≈ 0.48
H3: 0.22  / 0.565 ≈ 0.39
H_other: 0.015 / 0.565 ≈ 0.03
```

H2 is now the leading hypothesis but H3 ("flake") is still nearly as likely. Acting decisively on H2 is premature; cheap evidence to discriminate H2 from H3 is the next move.

### Step 5: Use Bayes Factors for Quick Updates

For a binary hypothesis (H vs ¬H), `BF = P(E|H) / P(E|¬H)`.

| Bayes factor | Strength of evidence (Jeffreys) |
| --- | --- |
| 1–3 | Barely worth mentioning |
| 3–10 | Substantial |
| 10–30 | Strong |
| 30–100 | Very strong |
| >100 | Decisive |

A single "it worked once" trial is rarely BF > 3 against a strong prior. "Extraordinary claims require extraordinary evidence" formalized: to overturn a prior of 0.001, you need a Bayes factor of ~1000 to reach a posterior of 0.5.

### Step 6: Watch for Regression to the Prior

After dramatic evidence, beliefs often spike, then should *regress* as later evidence is more typical. If a single anomalous data point convinced you, the next few normal data points should pull you back. Track whether you are giving later, equally-weighted evidence its due.

### Step 7: Choose When to Act

Acting is not the same as believing. Decide a *threshold*:

- For cheap reversible actions (run another test, add a log): act at posterior > 0.3
- For costly actions (revert, page on-call): act at posterior > 0.7 *and* a clear winner
- For irreversible actions (drop a table, change a contract): demand posterior > 0.95 or further evidence

If two hypotheses are close, the right move is usually to *gather discriminating evidence*, not to pick.

### Step 8: Record the Update Trail

For postmortems and review: document the prior, the evidence, and the posterior. This makes future updates calibrated against past ones.

## Output Format

```
BAYESIAN UPDATE

Question:
- ...

Hypothesis space:
H1: ...
H2: ...
H3 (boring): ...

Priors (and rationale):
- ...

Evidence:
- ...

Likelihoods:
- ...

Posteriors:
- ...

Leading hypothesis:
- ... (posterior X.XX)

Action threshold:
- Met / not met because [...]

Next discriminating evidence to gather:
- ...
```

## Anti-Patterns to Avoid

- **Ignoring the base rate** (prosecutor's fallacy): treating P(E|H) as P(H|E)
- **Confusing P(H|E) with P(E|H)**: the test's accuracy is not the patient's risk
- **Uniform priors over many hypotheses**: makes every observation look decisive
- **Updating only on confirming evidence**: disconfirming evidence must update too
- **Ignoring the boring hypothesis** (flake, env, fixture) — it usually has the highest prior
- **Acting on weak evidence because it is dramatic**: vividness is not a Bayes factor
- **Updating to certainty (0 or 1)**: nothing comes back from the dead, leave residual probability
- **Re-using the same evidence twice** in a chain of updates: double-counting

## Relationship to Other Skills

- Use `statistical-debugging` to *gather* observations; use this skill to *update beliefs* on what was gathered.
- Use `popperian-debug` to design tests that produce *high Bayes factor* evidence (i.e. predictions that strongly differ between H and ¬H).
- Use `differential-diagnosis-debugging` to enumerate the hypothesis space before updating.
- Use `signal-detection-review` when the question is about thresholds and false-positive/negative rates rather than belief in a single hypothesis.
- Use `bias-audit` to catch anchoring and availability bias that contaminate priors.
