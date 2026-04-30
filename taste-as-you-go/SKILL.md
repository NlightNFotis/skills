---
name: taste-as-you-go
description: Continuous tasting and verification at every step of a process — the discipline of checking intermediate state because bland is recoverable but over-salted is not.
user-invocable: true
---

# Taste As You Go

Act as a chef tasting a sauce mid-reduction. The defining discipline of professional cooking is not following a recipe — it is **tasting at every stage** and adjusting. A teaspoon of broth tells you whether to add salt now (cheap) or whether you've already over-seasoned (expensive, sometimes fatal to the dish). In software, taste-as-you-go is the practice of verifying intermediate state — at each migration step, after the first 1% of a backfill, between each deploy phase, after each refactor commit — because the cost of a check is always far less than the cost of an unrecoverable end-state.

Success looks like: errors caught at step 2 of an 8-step plan, when reversal is cheap; an over-salt detected at the first taste, before it reaches the plate. Failure looks like: end-to-end tests pass, the deploy completes, and a corruption is discovered Monday that began at step 2 on Friday.

## When to Use This

- Multi-step operations (migrations, refactors, deploys, backfills) where each step changes durable state
- Long-running batch jobs where the first records reveal whether the rest will be correct
- Code changes whose effect can be sampled at multiple intermediate points
- Pipelines (CI, ETL, build) where each stage emits checkable artifacts
- Reviews of plans that have only an end-state assertion ("after, X should be true") with no mid-state checks
- After any "it works in dev" claim, before scaling to "it works in prod"

**Escape hatch**: For atomic, fast-reversible operations (a single transaction, a feature flag toggle), end-state checking is enough. Use this skill when intermediate state matters because reversal cost grows with each step.

## Core Mindset

Two cost asymmetries drive this discipline:

1. **The cost of a single check is nearly free.** A spoonful of soup, a `SELECT count(*)`, a curl to a health endpoint — pennies.
2. **The cost of an unrecoverable mistake is unbounded.** Over-salted soup is thrown out. A corrupted backfill that ran for six hours can take days to undo.

> "Bland is recoverable. Over-salted is not."

Therefore: **bias toward more frequent, cheaper tastes** — especially before any irreversible step. The recipe never tells you exactly when to taste; the chef tastes constantly.

Ask:

- What is the cheapest evidence that step N worked, available right now?
- If step N is wrong, when will I find out — at N+1, or at the end?
- Is the next step reversible? If not, what would I want to know before firing it?
- What is the smallest amount of work I can do to expose drift — 1%? 10 records? One tenant?
- Have I been running for so long that my "palate" has drifted — am I judging weird as normal?
- Is there a colleague who can taste with fresh judgment?
- Am I checking the dish, or just checking that the timer rang?

## What Tasting Looks Like in Software

| Cooking taste | Software equivalent |
| --- | --- |
| Spoon of broth | `SELECT * LIMIT 10` after step N |
| Pinch of finished filling | Diff first 100 backfilled rows against expected |
| Bread crust tap | Curl health endpoint, check status |
| Sauce on the back of a spoon (nappe) | Latency / error-rate observation for 60 seconds |
| Smell test | Scan logs for unexpected warning patterns |
| Second cook tastes | Pair-review the intermediate state |
| Plate up a single portion to check | Canary 1%, observe before going further |
| Check the resting juices | Drain queue, inspect what's left |

## The Two Most Powerful Adjustments

In cooking, **salt** and **acid** are the two adjustments that change everything else's perception. In software, the analogues are:

- **Salt = correctness adjustments**: changing values, fixing data, applying transforms. Cheap to add, expensive to remove. *Add salt slowly.*
- **Acid = scope adjustments**: rolling back, reducing concurrency, narrowing the rollout, rate-limiting. Cuts through and makes other things palatable again. *Use acid to rescue over-salted dishes.*

Most failed migrations are over-salted (too much transformation applied before tasting). The rescue is almost always acid (narrow scope, slow down, partial rollback).

## The Process

### Step 1: Identify Tasting Points

For the operation under way, list every point where intermediate state is observable.

```
TASTING POINTS:
- After step N: [what is checkable] via [cheapest method]
- After 1% of batch: [what is checkable]
- Between deploy phase A and B: [what is checkable]
```

A plan with no tasting points between trigger and end-state cannot be tasted. Add some before proceeding.

### Step 2: Define What "Tastes Right" at Each Point

For each tasting point, write down the expected observation **before running it**. Otherwise you'll rationalize whatever you see.

```
TASTING POINT: After backfill of 1% of users
- Expected: 100% of sampled rows have email_verified_at populated, NULL count = 0 in sampled range
- Cheapest check: SELECT COUNT(*) FROM users WHERE id IN (sample) AND email_verified_at IS NULL
- Disqualifying signal: any non-zero count
```

Weak: "Check that the backfill looks right."
Strong: "After 1% (~10k rows), verify: zero NULL in `email_verified_at`, zero rows where `email_verified_at < created_at`, P50 backfill rate ≥ 500 rows/sec."

### Step 3: Taste Early

The first taste matters most. The first 1% of a backfill, the first canary box, the first migrated tenant — these are the cheapest places to discover that the recipe is wrong.

- Run a dry-run if available
- Run on a single shard / tenant / table partition first
- Process the first batch and **stop**; inspect; resume only if it tastes right
- Promote 1% canary; soak; observe; then 10%

The cook who tastes only at the end is the cook who throws away dinner.

### Step 4: Taste Between Lock-Ins

Per the sequencing discipline, lock-in steps are irreversible. Always taste **immediately before** every lock-in.

```
BEFORE LOCK-IN ("DROP COLUMN old_email"):
- Verify: zero application reads from old_email in last 7 days
  Source: app log query, distributed trace span counts
- Verify: backfill parity is 100% (NEW = OLD for all live rows)
  Source: parity check job
- Verify: rollback path is staged and tested on staging
- Decision: proceed only if all three pass
```

Without a taste before lock-in, you are seasoning blind.

### Step 5: Watch for Palate Fatigue

Chefs lose calibration after long sessions — everything starts tasting under-seasoned, so they over-salt. Software equivalents:

- Engineer who has been staring at a dashboard for two hours and stops noticing the slow climb
- On-call who has acked the same alert 30 times today and acks #31 reflexively
- Reviewer on the 12th PR of the day rubber-stamping
- "It's been like this for a while" — drift normalized into baseline

Counter-measures:
- Hand the spoon to a colleague: "tell me if this looks weird to you"
- Compare to a baseline captured *before* the session started
- Set absolute thresholds, not relative ones ("alert if > 200ms" vs "alert if 2× recent")
- Force a fresh read by closing and reopening the dashboard / reloading the data

### Step 6: Distinguish Recoverable from Unrecoverable Drift

Not every off-taste needs a stop. Classify what you taste:

| Observation | Recoverable? | Action |
| --- | --- | --- |
| Bland (under-applied effect) | Yes | Add more, taste again |
| Slightly off but trending right | Yes | Continue, watch closely |
| Over-applied but bounded | Sometimes | Apply acid (rollback / dilute) |
| Wrong dish entirely | No | Stop, rebuild |
| Burnt / corrupted | No | Stop, restore from snapshot, restart |

The discipline is the **stop**. A chef who keeps cooking a burnt sauce hoping it improves is the engineer who keeps a broken backfill running because "we're already 60% through".

### Step 7: Taste the Recipe, Not Just the Dish

End-to-end tests check the dish. They do not check whether each step was sound. A plan can have:

- Green E2E suite + corrupted intermediate state (the bug surfaces months later)
- Red mid-state check + green E2E (you caught a latent issue)

Therefore: build mid-state checks into CI gates, not just terminal assertions. Examples:

- After migration step N, run a parity check job before the next step starts
- After deploy phase A, require a 5-minute soak with error-rate < threshold before phase B
- After each file in a batch refactor, run unit tests; commit only if green

### Step 8: Record the Tastes

Each taste should produce a small artifact: a query result, a screenshot, a count, a timestamp. These become:

- Evidence for the postmortem if something goes wrong later
- A baseline for the next time someone runs this operation
- A handoff for whoever owns the next step

A taste with no record is a taste that didn't happen as far as the next cook is concerned.

## Output Format

```
TASTE PLAN

Operation:

Tasting points (in order):
1. After step X
   - Expected: ...
   - Check: ...
   - Disqualifying signal: ...
2. ...

Pre-lock-in tastes:
- Before [lock-in step]: ...

Palate-fatigue mitigations:
- ...

Recovery thresholds:
- Recoverable observations: continue with adjustment
- Unrecoverable observations: stop and ...

Recorded artifacts:
- ...
```

## Anti-Patterns to Avoid

- **End-only tasting**: only checking after the operation completes
- **Tasting after the lock-in**: discovering the salt level after the dish is plated
- **No baseline**: judging "weird" without knowing what "normal" is
- **Confirmation tasting**: looking for evidence the recipe is right rather than open observation
- **Sunk-cost cooking**: continuing because you're already 60% in
- **Solo palate**: never asking a fresh tongue when you've been staring for hours
- **Recipe trust**: assuming the steps must be right because they were last time
- **Taste-without-record**: no artifact, no handoff, no postmortem evidence

## Relationship to Other Skills

- `sequencing-and-temperature` defines the steps; taste-as-you-go is the verification *between* them.
- `mise-en-place` should stage the tasting tools (queries pre-typed, dashboards open) before cook.
- `recipe-rescue` is what to do when a taste reveals trouble; tasting catches it early enough for rescue to be cheap.
- `signal-detection-review` tunes the thresholds that distinguish a bland taste from a bad one.
- `statistical-debugging` informs how big a sample you need for a tasting to be meaningful.
- `feedback-loop-analysis` provides the underlying model of how mid-state observations feed back into go/no-go decisions.
