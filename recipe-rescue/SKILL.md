---
name: recipe-rescue
description: Real-time triage during execution failures — chef's instincts for which broken dishes can be saved, which must be abandoned, and which adjustments make things worse.
user-invocable: true
---

# Recipe Rescue

Act as a chef in the middle of service when a sauce breaks. The dish is already in the pan; the diners are seated. You have seconds to decide: rebuild the emulsion with a fresh yolk and cold stream, or scrape the pan and start over? In software, recipe rescue is the live-incident discipline of triaging a failure mid-execution: a deploy half-rolled-out, a migration half-applied, a backfill at 40% with corrupt rows. The choice is always the same shape — **save the salvageable, abandon the unrecoverable, and don't throw good resources after bad**.

Success looks like: a clear-eyed call between in-place patch, full restart, and partial rollback, made fast and stuck to. Failure looks like: thirty more minutes of trying to "fix" a sauce that broke ten minutes ago because nobody wanted to admit it was time to dump the pan.

## When to Use This

- A deploy or migration is in flight and showing failure signals
- A backfill or batch job is corrupting some fraction of records but not all
- Tests are red mid-refactor and the change is too large to revert cleanly
- An incident is unfolding and the team is debating "patch in place vs roll back vs restart"
- A long operation has a partial bad state and you must decide what to keep
- You are about to apply an adjustment to a degraded system and want to verify it won't make things worse

**Escape hatch**: For routine red tests during local development, just iterate. Use this skill when production state is at risk, when the cost of "keep cooking" is bounded by something other than time, or when the team is anchored on rescuing something that should be abandoned. Distinct from `incident-review` (post-hoc) and `resilience-engineering` (design-time).

## Core Mindset

Three principles govern rescue:

1. **Save the salvageable, abandon the unrecoverable.** Triage by what *can* be recovered, not by what you wish you could.
2. **Don't throw good resources after bad.** Every minute spent rescuing an unrecoverable dish is a minute not spent cooking the next one.
3. **The chef who can throw away has the strongest instincts.** The hardest skill is the willingness to abandon work in progress.

Ask:

- Is this dish broken in a way I have rescued before, or in a way I haven't?
- What ingredient (or state) is still good? What is contaminated?
- Will my rescue *add* to the damage if it fails?
- What is the cost of restarting from a known-good state?
- How much time do I have before the customer (or next step) needs the result?
- Am I rescuing because it can be rescued, or because I can't bear to dump the pan?
- If a colleague walked in fresh, what would they do?

## Failure Taxonomy and Rescue Patterns

Match the symptom to the rescue. Each cooking failure has a real software analogue.

| Cooking failure | What's happened | Rescue | Software analogue + rescue |
| --- | --- | --- | --- |
| **Broken emulsion** (split sauce) | Fat and water phase separated | Start fresh yolk in clean bowl, **stream in the broken sauce slowly** while whisking | Half-applied state migration; start fresh transaction, replay from clean snapshot, stream in the salvageable rows |
| **Over-salted** | Too much seasoning applied | Add starch (potato, rice), dairy, acid, OR **double the recipe** to dilute | Over-applied transform; dilute by mixing with un-transformed data, OR widen scope so the bad batch is a smaller fraction |
| **Burnt bottom** | Pan scorched; flavor will spread | **Do not scrape**; transfer un-burnt portion to a new pan immediately | Corrupted region of state; do not let the corruption spread by retry; quarantine bad rows, copy good rows to fresh table |
| **Curdled** (eggs scrambled in sauce) | Protein over-coagulated | Sieve out solids, rebuild with fresh emulsifier | Stuck queue / poison message; sieve out the poison, replay good messages to fresh queue |
| **Over-cooked** | Texture lost; cannot un-cook | Purée and re-purpose (soup, sauce) | Over-aggressive deploy reached too many users; can't un-ship; pivot the use case (compatibility shim, gradual fix-forward) |
| **Under-cooked** | Not done yet | Continue carefully at lower heat; **don't crank up to catch up** | Backfill behind schedule; resist temptation to raise concurrency; let it finish at safe rate |
| **Wrong seasoning entirely** | Recipe error | Stop. Discard. Restart from raw ingredients | Wrong migration script entirely; stop, restore from snapshot, redesign |
| **Cold spot** (uneven heat) | Some portions done, some not | Redistribute / finish in oven | Partial rollout; complete the rollout, or roll back the part that completed |
| **Sticking** | Food bonded to pan | Wait — it releases when ready; forcing it tears | Lock contention / retry storm; back off, don't force |

## Triage Decision Tree

Before any adjustment, run the triage:

```
Is the failure ACTIVELY MAKING THINGS WORSE right now?
├── Yes → STOP THE BURNER FIRST (kill the job, halt the rollout, pause the queue)
│         then triage
└── No  → Hold position; triage before changing anything

Is the bad state CONTAINED, or SPREADING?
├── Contained → can rescue in place
└── Spreading → quarantine first, rescue from quarantine

Is there a KNOWN-GOOD state to restart from (snapshot, prior version)?
├── Yes → restart-cost = (time to restore) + (time to redo)
│         rescue-cost = (time to fix in place) + (risk of secondary damage)
│         pick the smaller
└── No  → in-place rescue is the only option; proceed carefully

Is the rescue itself REVERSIBLE?
├── Yes → try it; observe; iterate
└── No  → treat as a new lock-in step; verify preconditions before firing
```

## The Process

### Step 1: Stop the Burner

The first move in any kitchen rescue is *off the heat*. Active damage compounds.

- Halt the rolling deploy
- Pause the migration / backfill
- Disable the cron / scheduler
- Drain the queue (do not delete it)
- Put up a feature flag stop

This is not the rescue; this is **buying time to triage**. Many teams skip it because halting feels like commitment to rollback. It isn't — it's pausing the cook.

### Step 2: Inventory the Damage

Be precise about what is broken and what is not.

```
DAMAGE INVENTORY:
- What is corrupted: [tables, rows, files, services]
- What is uncertain: [things that may be corrupted but unverified]
- What is intact: [confirmed good]
- What is downstream of the damage: [things that read from / depend on it]
- What is upstream: [things that feed it; might re-corrupt if rescue is partial]
- Time the damage began: [first bad event]
- Time noticed: [first alert / report]
- Damage rate: [per second / per row / bounded]
```

Without this inventory you will rescue what doesn't need rescuing and miss what does.

### Step 3: Match to a Rescue Pattern

Compare the failure to the taxonomy. Most production failures map to one or two named patterns. Naming the pattern unlocks the rescue:

- "This is broken-emulsion shape" → restart with fresh state, stream in salvageable
- "This is burnt-bottom" → quarantine and copy out, do not scrape
- "This is over-salted" → dilute or widen
- "This is wrong-recipe" → abandon and restart

If no pattern matches, treat as **wrong-recipe** by default. Novel failures rarely have improvised rescues.

### Step 4: Estimate Rescue vs Restart

Make the trade-off explicit:

```
RESTART:
- Cost: [time to restore from snapshot + redo + announce delay]
- Risk: [what's lost; window the system is unavailable; user impact]
- Confidence: [how known is the restart path? has it been tested?]

IN-PLACE RESCUE:
- Cost: [time of rescue + risk of secondary damage]
- Risk: [could the rescue itself fail / make things worse?]
- Confidence: [have we done this rescue before?]

DECISION: [restart / rescue], because [...]
```

A useful heuristic: **if the restart path is known and tested, prefer restart**. Most "rescue in place" attempts under time pressure compound the original mistake.

### Step 5: Stage the Rescue (Mini-Mise)

Before firing the rescue, stage what it needs — even under time pressure. A rushed rescue is the most common source of secondary incidents.

- Fresh snapshot ID confirmed
- Rollback command typed and proofread
- Affected rows identified by query, not by guess
- One person executes; one person observes
- Rollback-of-the-rescue ready in case the rescue itself fails

### Step 6: Execute, Tasting Continuously

Apply the rescue in the smallest unit possible:

- Restart a single shard, not all shards
- Restore one tenant first, verify, then proceed
- Replay 100 messages, verify, then the rest

Between each unit, taste (see `taste-as-you-go`). A rescue without intermediate verification is a second cook without a second taste.

### Step 7: Know When to Throw Away

The hardest call. Signs the rescue should be abandoned for restart:

- The rescue has failed once already
- New damage is appearing during the rescue
- The team is improvising with no named pattern
- "Just one more thing and it'll work" has been said twice
- The salvage is taking longer than the restart would have

> The chef's instinct: a sauce broken twice is a sauce you start over. Do not be the cook who plates a third attempt at the same emulsion when the kitchen needs to send out the next course.

### Step 8: Note What's Lost, Move On

Every rescue has a residue — the dish you didn't save, the rows you couldn't recover, the customers who saw the error. Acknowledge explicitly:

- What was lost (data, time, trust)
- What was preserved
- What the next service (cook, deploy, on-call) needs to know
- What the postmortem should investigate (not now — later)

Then return to the rest of service. Lingering on the lost dish risks the next one.

## Output Format

```
RECIPE RESCUE

Symptom:
Failure pattern matched: [from taxonomy]

Damage inventory:
- Corrupted:
- Uncertain:
- Intact:
- Spread risk:

Burner status: [stopped / running / paused]

Decision: [restart / in-place rescue], because:
- Restart cost vs rescue cost: ...
- Confidence in restart path: ...

Rescue plan (smallest unit first):
1. ...
2. ...

Tasting between units:
- After unit 1: check ...
- After unit 2: check ...

Throw-away criteria:
- Abandon and restart if: ...

Residue / loss:
- ...

Handoff to postmortem:
- ...
```

## Anti-Patterns to Avoid

- **Cooking on a burning pan**: trying to rescue without first halting the active damage
- **Improvised rescue**: applying steps that match no known pattern under time pressure
- **Sunk-cost rescue**: continuing to fix because you've already spent so much time fixing
- **Hidden restart cost**: assuming "restore from snapshot" is fast without checking whether it is
- **Solo rescue**: not bringing in a second pair of eyes for a high-stakes triage
- **Scraping the burnt bottom**: aggressive retry / cleanup that spreads contamination
- **Cranking the heat to catch up**: raising concurrency, parallelism, or scope to recover lost time
- **Plating the broken sauce**: shipping the rescued state without honest disclosure of what was lost

## Relationship to Other Skills

- `incident-review` is the *post-hoc* analysis; recipe-rescue is the *in-the-moment* triage. Always pair: rescue captures evidence the review will need.
- `resilience-engineering` is the *design-time* discipline that makes rescue cheaper by ensuring restart paths exist and graceful degradation is possible.
- `mise-en-place` staged the rollback / snapshots that rescue now reaches for.
- `taste-as-you-go` is what verifies each rescue unit between applications.
- `sequencing-and-temperature` informs whether the failure is at a lock-in (forward-only) or a switch (rollback-able).
- `differential-diagnosis-debugging` helps select the rescue pattern when symptoms are ambiguous.
