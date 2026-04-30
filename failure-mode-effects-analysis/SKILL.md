---
name: failure-mode-effects-analysis
description: Enumerate failure modes, effects, severity, detectability, and mitigations before risky changes.
user-invocable: true
---

# Failure Mode and Effects Analysis (FMEA)

Act as a reliability engineer running a structured FMEA. Your job is to enumerate every plausible way a component, change, or operation can fail, trace the effect of each failure to the user or downstream system, and rank failures by a defensible risk score so that mitigations land where they pay off most.

A successful FMEA produces a prioritized table that a reviewer can act on: it has caught at least one non-obvious silent failure, has named at least one single point of failure (SPOF), and has converted at least one "we'd notice" assumption into a concrete detection control. Failure looks like a list of "the server crashes" entries — no specificity about cause, no detection score, no mitigation that can be implemented.

## When to Use This

- Before risky releases, schema migrations, auth changes, or data backfills
- Reviewing a new external dependency or a new critical path
- Designing rollback, validation, monitoring, or kill-switch behavior
- Hardening a workflow that has caused recurring incidents
- Evaluating an architecture proposal where reliability is a stated goal
- Before introducing automation around irreversible operations (deletes, payments, sends)

**Escape hatch**: If the change is low-blast-radius (a typo fix, a refactor with strong tests, a doc edit), do not run a full FMEA — skim for SPOFs and move on. Use this skill when the cost of a missed failure mode is meaningfully higher than the cost of the analysis.

## Core Mindset

Think like a pessimist with a spreadsheet. Every component will eventually fail; the question is *how*, *who notices*, and *how bad it gets before someone does*.

Ask:

- What is the smallest unit of failure here — a function call, a network hop, a config value, a human step?
- For each failure, what does the user / next service / persistent store actually see?
- Could this fail *silently* — wrong answer, no exception?
- If this fails, is there any other independent path, or is it a single point of failure?
- How would we learn it failed: alert, user report, audit job, never?
- Is the existing "control" actually preventive, or does it only help us clean up afterward?

## Variants and Vocabulary

| Term | Meaning |
| --- | --- |
| **FMEA** | Failure Mode and Effects Analysis: enumerate modes, effects, controls, scores |
| **FMECA** | FMEA + Criticality: adds a separate criticality dimension beyond severity |
| **Design FMEA (D-FMEA)** | Applied to a design or architecture before it ships |
| **Process FMEA (P-FMEA)** | Applied to an operational workflow (deploys, on-call, migrations) |
| **Failure mode** | The way something fails (e.g., "returns stale value", "drops message") |
| **Failure cause** | Why the mode occurs (e.g., "cache TTL longer than refresh interval") |
| **Failure effect** | What the user / downstream observes (e.g., "user sees deleted item") |
| **SPOF** | Single point of failure — one component whose failure takes the whole system down |
| **Common-mode failure** | Multiple "redundant" components that fail together (same dep, same AZ) |
| **Detection control** | Mechanism that surfaces the failure (alert, healthcheck, audit, user report) |
| **Preventive control** | Mechanism that stops the failure happening (validation, type, rate limit) |
| **Mitigation** | Reduces severity *given* the failure occurs (fallback, circuit breaker) |

## Scoring: S, O, D, RPN

Each failure mode gets three scores on a 1–10 scale, then a Risk Priority Number.

```
RPN = Severity (S) × Occurrence (O) × Detection (D)
```

| Score | Severity (S) | Occurrence (O) | Detection (D) |
| --- | --- | --- | --- |
| 1–2 | Negligible / cosmetic | Extremely rare | Caught instantly, automatically |
| 3–4 | Minor user impact, easily reversible | Rare, observed historically | Caught by tests/CI before prod |
| 5–6 | Significant degradation, partial outage | Occasional under known conditions | Caught by monitoring within minutes |
| 7–8 | Major outage, data corruption, security exposure | Frequent / likely with normal use | Caught only by user reports or audits |
| 9–10 | Catastrophic, irreversible, regulated, safety | Near-certain | Effectively undetectable |

**Important inversion**: a *higher* Detection score means *worse* detection. RPN is a triage heuristic, not a precise number — use it to sort, not to decide.

Beyond RPN, always escalate any failure with **S ≥ 9** regardless of O and D, and any **single point of failure** regardless of RPN.

## The Process

### Step 1: Define the Scope

State exactly what you are analyzing. Avoid "the whole system."

```
SCOPE:
- Component/operation:
- Trigger (deploy, request, scheduled job, user action):
- Inputs and trust boundaries:
- Outputs and side effects:
- Persistent state touched:
- Dependencies (services, libraries, infra):
- In scope: ...
- Out of scope: ...
```

### Step 2: Decompose into Steps or Functions

Break the operation into the smallest reasoning units that can fail independently. For a deploy: build → publish → migrate → cutover → verify. For a request: parse → authn → authz → fetch → mutate → emit event → respond.

Each step is a row (or block of rows) in the FMEA table.

### Step 3: Enumerate Failure Modes per Step

For each step, brainstorm modes using these archetypes:

- **Crash / exception**: throws, panics, OOMs
- **Timeout / hang**: never returns, exceeds budget
- **Wrong result**: returns plausible but incorrect value (most dangerous — silent)
- **Stale result**: returns outdated value (cache, replica lag)
- **Partial completion**: did half the work, left inconsistent state
- **Out-of-order / duplicate**: replayed, retried, reordered
- **Resource exhaustion**: connection pool, disk, file handles, quota
- **Authorization slip**: returned data the caller should not see
- **Misconfiguration**: feature flag, env var, secret rotation
- **Dependency failure**: upstream returns 5xx, slow, or wrong shape
- **Human error in process FMEA**: wrong env targeted, skipped step, copy-paste

### Step 4: Trace Effects to the User

For each mode, follow the consequence outward until it hits a person, a customer system, or a persistent record. Stop at the most severe stable observation.

Weak: "the request fails"
Strong: "the order is created in our DB but never sent to fulfillment; user sees 'success', merchant ships nothing, support ticket arrives 24–48h later"

### Step 5: Build the FMEA Table

Use one row per (step, failure mode) pair.

```
| # | Step | Failure mode | Cause | Effect (user/system) | S | O | D | RPN | Existing controls | Recommended action | Owner |
|---|------|--------------|-------|----------------------|---|---|---|-----|--------------------|--------------------|-------|
| 1 | migrate | ALTER blocks writes > 30s | long-running scan on hot table | API 5xx storm, queues back up | 8 | 5 | 4 | 160 | none | run during low-traffic window; pt-online-schema-change | @db |
| 2 | cutover | new pods take old config | configmap not bumped | 50% of traffic served stale flag, silent wrong pricing | 9 | 3 | 8 | 216 | manual verify | bake config hash into pod label; alert on mismatch | @plat |
```

Sort by RPN descending; then re-sort by Severity to make sure no S≥9 row is buried.

### Step 6: Distinguish Prevention, Detection, Mitigation, Recovery

For each high-RPN row, name controls in each bucket. Most teams over-invest in one and skip the others.

| Bucket | Question | Examples |
| --- | --- | --- |
| **Prevent** | Can we stop the failure happening? | input validation, types, idempotency keys, capacity headroom |
| **Detect** | If it happens, how fast do we know? | alerts, healthchecks, reconciliation jobs, canary analysis |
| **Mitigate** | Can we shrink the blast radius given it happens? | circuit breaker, feature flag kill switch, rate limit, bulkhead |
| **Recover** | How do we restore correctness? | rollback, replay, manual reconcile, customer remediation |

A row with only a Recovery control means "we'll find out from a customer and clean up." That is rarely acceptable for S ≥ 7.

### Step 7: Identify SPOFs and Common-Mode Failures

Scan the table for:

- A single dependency cited in many rows → SPOF
- "Redundant" components sharing a library version, region, secret, or config → common-mode
- Detection controls that themselves depend on the failing component (alerting through the system being alerted on)

Call these out separately, even if their per-row RPN is low.

### Step 8: Convert Top Risks into Concrete Actions

Each action must have an owner, a verification, and a deadline relative to the change. Vague actions ("improve monitoring") do not count.

Weak: "Add better alerting on the migration."
Strong: "Add Prometheus alert `migration_lag_seconds > 30 for 2m` wired to #db-oncall; dry-run alert in staging before launch; @alice by Fri."

## Output Format

```
FMEA REPORT

Scope:
- Component/operation:
- Type: D-FMEA / P-FMEA / FMECA
- Out of scope:

Steps analyzed:
1. ...

Failure mode table:
| # | Step | Mode | Cause | Effect | S | O | D | RPN | Controls | Action | Owner |
|---|------|------|-------|--------|---|---|---|-----|----------|--------|-------|
...

Top risks (sorted by RPN, then by S):
1. #N — [mode] — RPN=... — recommended action: ...
2. ...

Single points of failure:
- ...

Common-mode failures:
- ...

Action plan (prevent / detect / mitigate / recover):
1. ...

Residual risk accepted:
- ... (and by whom)
```

## Anti-Patterns to Avoid

- **Listing only crashes**: silent wrong answers and partial completions are usually worse
- **Treating detection as mitigation**: knowing the house is on fire is not the same as putting it out
- **One-bucket controls**: only-prevent or only-recover analyses both miss the middle
- **RPN theater**: tweaking scores to make a row look acceptable; the failure mode does not change
- **Ignoring the human in P-FMEA**: "the operator will notice" is not a control unless the operator has an unmissable signal
- **Common-mode blindness**: assuming N replicas mean N independent failure probabilities
- **Stale FMEA**: written once at design time, never revisited after the architecture changed
- **No owner, no date**: an action item without both is a wish

## Relationship to Other Skills

- Use `formal-invariants` to turn high-severity "wrong answer" modes into runtime assertions or property tests.
- Use `assumption-audit` when failure causes rest on unstated premises ("the upstream is idempotent").
- Use `resilience-engineering` to design the mitigation and recovery columns in depth.
- Use `signal-detection-review` to tune the detection controls so they actually fire on real incidents and not on noise.
- Use `preflight-checklist` to encode the highest-RPN preventive controls into a checklist before the operation.
- Use `operational-game-day` to validate that detection and recovery controls work under realistic conditions.
- Use `incident-review` after the fact to feed learnings back into the FMEA.
