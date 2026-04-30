---
name: differential-diagnosis-debugging
description: Use differential diagnosis to triage possible causes by likelihood, severity, and test cost.
user-invocable: true
---

# Differential Diagnosis Debugging

Act as a clinician triaging a software failure. A patient (the system) presents with a chief complaint (the symptom). Your job is to construct a **differential** — a ranked list of candidate diagnoses — then run targeted tests to converge on the actual cause without missing anything dangerous along the way.

Success looks like: a working diagnosis supported by positive evidence, with severe alternatives explicitly ruled out. Failure looks like: anchoring on the first plausible cause ("treating the chart, not the patient"), missing a "must not miss" diagnosis, or jumping to treatment before the disease is named.

## When to Use This

- A symptom has many plausible causes and you need triage rather than deep root-cause proof
- The cost of missing a severe cause is high (data loss, security, outage, corruption)
- The failure could live in code, data, environment, dependency, infra, or user workflow
- Multiple symptoms appear together and you need to decide if they share one cause (Occam) or several (Hickam)
- A previous fix attempt addressed a symptom but the patient is still sick
- You need to communicate uncertainty to others before committing to a fix

**Escape hatch**: If the stack trace points to a single defect with an obvious fix, skip this. If exactly one cause fits the evidence after the first 60 seconds of inspection, go straight to verification — do not manufacture a differential.

## Core Mindset

Diagnose before you treat. Ask:

- What is the chief complaint, in the patient's own words?
- What are the vitals — the cheap, always-collectable signals?
- What is the **pre-test probability** of each candidate, given this codebase, this team, this week?
- Which candidates are "must not miss" — low probability but high severity if true?
- What test would most efficiently **discriminate** between the top candidates (high sensitivity *and* specificity)?
- Am I anchoring on the first diagnosis I considered?
- Is this one disease (Occam's razor) or two coincident diseases (Hickam's dictum)?

## Diagnostic Vocabulary

| Term | Meaning in software debugging |
| --- | --- |
| **Chief complaint** | The exact symptom as observed (error text, wrong output, latency spike) |
| **History of present illness** | What the user/system was doing when it appeared; recent changes |
| **Vitals** | Cheap always-on signals: stack trace, exit code, log level, CPU/memory, version |
| **Pre-test probability** | How likely each diagnosis is *before* you run any new test, given context |
| **Sensitivity** | A test's ability to detect the condition when present (few false negatives) |
| **Specificity** | A test's ability to exclude the condition when absent (few false positives) |
| **Pathognomonic sign** | An observation that is essentially diagnostic on its own |
| **Must not miss** | Diagnoses with severe consequences that justify ruling them out even at low probability |
| **Occam's razor** | Prefer one diagnosis that explains all symptoms |
| **Hickam's dictum** | "A patient can have as many diseases as they damn well please" — coincident bugs are real |
| **Premature closure** | Stopping the differential as soon as one candidate fits |
| **Anchoring** | Letting the first hypothesis distort the weight of later evidence |
| **Treating the chart, not the patient** | Fixing what the dashboard says without confirming on the running system |

## Diagnostic Categories

When generating a differential, draw from multiple etiological buckets so you don't list four flavors of the same idea:

- **Code defect**: logic error, off-by-one, wrong branch, missing case
- **Data**: malformed input, schema drift, encoding, null/empty, unexpected scale
- **State**: stale cache, leftover file, uncommitted migration, corrupt index
- **Concurrency**: race, deadlock, ordering, retry storm, cancellation
- **Environment**: OS, version, locale, timezone, filesystem, permissions
- **Dependency**: upstream library/service change, version skew, network partition
- **Configuration**: feature flag, env var, secret rotation, limits
- **Interface contract**: caller/callee disagree on shape, units, ownership
- **User workflow**: action sequence the design didn't anticipate
- **Observation artifact**: the bug is in the measurement, not the system

## The Process

### Step 1: Take the History and Chief Complaint

Write the symptom verbatim. Resist paraphrasing into your favorite hypothesis.

```
CHIEF COMPLAINT:
- Exact observed behavior:
- Expected behavior:
- First seen:
- Reproducibility (every time / sometimes / once):
- Recent changes (deploys, merges, config, data):
- Who/what is affected:
```

### Step 2: Collect Vitals

Cheap, broad-spectrum data before any expensive workup.

- Exit code, error class, full stack trace
- Log lines around the failure (±30s)
- Version of code, runtime, key dependencies
- Resource state: disk, memory, file descriptors, connections
- Was this path ever working? When did it last work?

### Step 3: Generate the Differential (3–6 Candidates)

Aim for **materially distinct** diagnoses across categories. A list of "maybe it's a typo / maybe it's an off-by-one / maybe it's wrong logic" is one diagnosis dressed up as three.

```
DIFFERENTIAL:
D1: [diagnosis] — category: [code/data/env/...] — pre-test prob: [H/M/L]
D2: ...
D3: ...
```

Always include at least one **"must not miss"** entry even if its probability is low: data corruption, security boundary breach, silent data loss, irreversible side effects.

### Step 4: Rank by Likelihood × Severity ÷ Test Cost

For each candidate, score:

- **Likelihood** given vitals and history
- **Severity** if true and missed
- **Cost** of the test that would confirm or rule out

Test the candidates that maximize information per unit cost first — but rule out "must not miss" candidates early even if they rank lower on probability.

### Step 5: Choose Discriminating Tests

A good diagnostic test changes your mind. Prefer tests with both high sensitivity and high specificity for the candidate at hand.

| Test type | Good for |
| --- | --- |
| Re-run with verbose logging | Distinguishing transient vs deterministic |
| `git bisect` | Attributing regression to a commit |
| Run on a clean environment | Separating env from code |
| Replay with captured input | Separating data from code |
| Toggle a feature flag | Confirming a configuration cause |
| Diff passing vs failing run | Surfacing the one variable that matters |
| Add a single targeted assertion | Confirming a specific state hypothesis |

Weak test: "I'll add some logs and look around." Strong test: "If D2 is true, the request_id will appear in the queue twice; I'll grep the log for duplicates."

### Step 6: Update the Differential After Each Result

After each test, **rewrite** the differential. Mark candidates as confirmed, ruled out, or still open. Add new candidates if the test surfaced unexpected facts.

```
AFTER TEST T1:
- D1: ruled out (evidence: ...)
- D2: still open
- D3: promoted (new evidence: ...)
- D5: new candidate (...)
```

### Step 7: Converge and Treat

Treat only when:

- A working diagnosis is supported by **positive** evidence (not just absence of contradiction)
- All "must not miss" candidates are explicitly ruled out
- The diagnosis explains **all** the chief complaints, not just the loudest one

If two coincident diagnoses fit better than one (Hickam), say so explicitly. If you must act before certainty (active incident), apply the safest reversible intervention and continue diagnosing.

### Step 8: Verify and Document

- Re-run the original repro after the fix
- Confirm the fix is causal: the failure returns when the fix is reverted
- Note which candidates were ruled out and how, so the next on-call doesn't repeat the workup

## Output Format

```
DIFFERENTIAL DEBUGGING

Chief complaint:
- ...

Vital signs:
- ...

Differential (ranked):
1. D1 — likelihood / severity / discriminating test
2. D2 — ...
3. D3 — ...
   (must-not-miss): ...

Tests run and results:
1. T1 → D? ruled out / confirmed / inconclusive

Working diagnosis:
- ... (Occam: one cause / Hickam: coincident causes)

Treatment:
- ...

Verification plan:
- Reproduce original failure ✓
- Confirm causality by revert ✓
- Regression check: ...

Open questions / follow-ups:
- ...
```

## Anti-Patterns to Avoid

- **Premature closure**: accepting the first plausible diagnosis without ruling out alternatives
- **Anchoring**: weighting later evidence by how well it fits the first hypothesis
- **Treating the chart, not the patient**: fixing what the dashboard says without checking the running system
- **Zebra hunting**: reaching for exotic causes before ruling out common ones (footsteps usually mean horses, not zebras)
- **Missing "must not miss"**: ignoring low-probability, high-severity diagnoses
- **Symptomatic treatment**: silencing the alarm without naming the disease
- **Confounded tests**: changing several variables at once, so the result discriminates nothing
- **Single-source diagnosis**: trusting one signal (one log line, one stack frame) without corroboration

## Relationship to Other Skills

- Use `popperian-debug` once the differential narrows to 1–2 candidates that need rigorous falsification.
- Use `code-forensics` to build the timeline that powers your "history of present illness."
- Use `assumption-audit` when a diagnosis depends on premises about inputs, env, or upstreams.
- Use `bias-audit` when you suspect anchoring or premature closure on a favored diagnosis.
- Use `statistical-debugging` when the chief complaint is intermittent and base rates matter.
