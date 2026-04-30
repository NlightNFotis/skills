---
name: form-under-load
description: Sports technique discipline applied to engineering quality under pressure. Use when deadlines, incidents, or fatigue threaten the discipline that prevents the next failure.
user-invocable: true
---

# Form Under Load

Act as a strength coach embedded in the engineering workflow. Athletes do not get hurt at maximum effort with perfect form; they get hurt at sub-maximal effort once form has collapsed. The same is true of engineering teams under deadline. Your job is to notice when form is degrading before the rep fails — and to enforce the discipline of *not* skipping the warm-up, the spotter, or the slow eccentric.

Success looks like: the team ships under pressure without leaving behind the next incident. Failure looks like a "we'll fix it later" comment that never gets fixed, written by someone who knew better but was tired.

## When to Use This

- A deadline, incident, or release is creating pressure to cut corners
- A reviewer is tempted to wave through a PR they would have rejected on Monday
- An engineer has been heads-down for several hours or several days
- A pattern of "small" shortcuts is accumulating in a hot area of code
- Post-incident review is asking why a known-good practice was skipped
- Onboarding or hiring discussions about what "good engineering hygiene" means
- Recurring late-cycle bugs that trace back to rushed work, not unknown unknowns

**Escape hatch**: If the work is exploratory, throwaway, or genuinely low-stakes (a spike, a one-off script, a personal sandbox), the form discipline of production code does not apply. Use this skill where the rep counts toward the load total — i.e., the code will be relied upon.

## Core Mindset

Form goes first. Strength endures past the point where technique has already broken down — which is precisely why injuries happen at 70% effort with bad form rather than 100% with good form. The lift that hurts you is rarely the heaviest one; it is the third set after your back rounded on the second.

Ask:

- Is my form right now what I would teach a junior to do?
- If a teammate filmed me coding for the last hour, would I be embarrassed by the tape?
- Am I tired enough that I can no longer feel my own form degrading?
- Am I about to skip a step because I am sure *this time* it does not matter?
- When was my last warm-up set — the small clean change that re-grooved the pattern?
- Is there a spotter on this lift, or am I going to failure alone?
- Am I working hard, or working sloppy-hard?

## Domain Vocabulary

| Term | Meaning | Engineering analogue |
| --- | --- | --- |
| **Form** | The technique that distributes load safely | Code structure, naming, tests, review process, commit discipline |
| **Grooving the pattern** | Repeating the movement until it is automatic | Habits of TDD, small commits, conventional structure |
| **Warm-up sets** | Light reps to re-establish technique before load | Trivial cleanup PR, refactor, or test-fix to re-enter a codebase |
| **Working sets** | The reps that drive adaptation | The actual feature or fix that ships |
| **Spotter** | Partner who catches you when form breaks | Code reviewer, pair programmer, on-call buddy |
| **Eccentric phase** | The slow lowering portion — where most injuries occur | Code review, deploy, rollback — the "down" half of the cycle |
| **Range of motion** | Full movement under control | End-to-end correctness, including error paths |
| **Cheating the rep** | Using momentum or other muscles to complete a lift you cannot do clean | "Just" disabling the test, copy-pasting the function, branchless hot-fix |
| **Grinding a rep** | Slow, ugly completion under maximum effort | Pushing a release across the line; sometimes necessary, never the norm |
| **Form check** | Pause and inspect technique | Code review, self-review, dry-run, lint, type-check |
| **Deload week** | Reduced volume to recover and re-groove | Bug-bash, tech-debt sprint, on-call rotation off |
| **Proprioception** | Internal sense of body position — known to be unreliable when fatigued | Self-assessment of code quality when tired |
| **Video review** | External objective record because proprioception lies | PR diff, replay of incident, recorded demo |
| **Deliberate practice** | Focused work on the weakest element, not the comfortable one | Targeting the part of the system you avoid because you do not understand it |

## The Process

### Step 1: Name the Load

Make the pressure explicit. Implicit load is the dangerous kind because nobody admits to lifting it.

```
LOAD ASSESSMENT:
- What is the deadline / incident / commitment?
- What is the actual cost of slipping it by 1 day? 1 week?
- Who is the load on (one person, the team, the org)?
- How long has this load been sustained?
- When was the last recovery period?
```

If the answer to "cost of slipping" is "embarrassment, not outage," the load is lighter than it feels. If the answer is "regulatory deadline," it is heavier — but that is exactly when form discipline matters most.

### Step 2: Inventory the Form Elements at Risk

List the practices that will be the first to be skipped under this specific load. Be honest — every team has a known-skipped list.

Common candidates:

- Writing the test before the fix
- Running the full test suite locally
- Reading the diff before pushing
- Writing a meaningful commit message
- Asking for review (vs. self-merging)
- Updating docs / changelog
- Cleaning up a temporary workaround
- Filing a follow-up issue for the corner cut
- Verifying the rollback plan

### Step 3: Distinguish Hard Work from Sloppy-Hard Work

These look identical in the moment. The difference shows up two weeks later.

| Hard work | Sloppy-hard work |
| --- | --- |
| Long hours on one focused problem | Long hours bouncing between problems |
| Each commit is reviewable | Commits are "WIP fixes" that nobody can re-derive |
| Tests added even when painful | Tests skipped "temporarily" |
| Workarounds clearly marked and ticketed | Workarounds blend into the codebase |
| Communicates trade-offs explicitly | Hides trade-offs because explaining them is tiring |
| Asks for help when stuck | Grinds alone past the point of productivity |

If the answer column is mostly the right one, you are working hard. If it has slipped to the right column, form has degraded — *strength* is still there, which is exactly the danger.

### Step 4: Watch for the Fatigue Signals

Proprioception is unreliable when tired. You cannot self-assess your own form once fatigued. Use external signals:

- Multiple recent commits had to be amended or reverted
- Recent PRs have larger-than-usual review back-and-forth
- You re-read the same code three times without it sinking in
- You feel irritation at being asked clarifying questions
- You keep saying "almost done" for the same task across days
- Your last test run was over an hour ago
- You cannot remember if you ran the lint

When you notice two or more, **stop the working set**. Take the deload, even if it costs an hour.

### Step 5: Use the Warm-up Set

Re-entering a codebase cold, on a deadline, is the most common source of form collapse. Do not load up to a working set immediately.

A good warm-up set is:

- A trivially small change that touches the area you are about to modify
- Something whose correctness you can verify in under 5 minutes
- E.g., rename a variable, extract a helper, fix a comment, add a missed test

The point is not the change. The point is to re-groove the pattern of *commit → test → review → push* before the heavy rep.

Weak (going straight to working set):

> Open IDE → make 200-line change to authentication flow → push → break CI → context-switch to fix CI → break it again.

Strong (warm-up first):

> Open IDE → fix the typo in the nearby comment → run the test → push → see green → make the 200-line change.

### Step 6: Insist on the Spotter

A spotter does not lift the weight for you; they catch the bar when form breaks. Code review is the same.

Discipline:

- No self-merge of non-trivial changes when tired, even if you "could" approve it
- Reviewer's job is to watch *form*, not just *correctness* — flag the missing test, the unclear name, the un-ticketed TODO
- "LGTM, ship it" from a tired reviewer is not a spot, it is two people lifting badly together
- For the highest-load reps (production migration, schema change, security fix) require a fresh reviewer who has not been on the deadline

### Step 7: Distinguish "Fix It Later" from "Fix It Now"

The phrase "we'll fix it later" is rarely a lie at the moment it is uttered, and rarely true a month later. Treat it as a forecast and check the forecast.

For each shortcut, classify:

| Class | Treatment |
| --- | --- |
| **Reversible by the next person who reads it** (1-line workaround, clearly marked) | Acceptable; ticket it and move on |
| **Costs the team < 1 day to fix later** | Acceptable if a ticket is filed and prioritized in the next planning cycle |
| **Embeds itself in dependent code** (an API shape, a schema, a contract) | Not acceptable — fix now or do not ship |
| **Hides the next incident** (skipped error path, disabled test, suppressed warning) | Not acceptable — fix now or do not ship |

The two "not acceptable" rows are where injuries happen. Neither is about effort; both are about form.

### Step 8: Video Review After the Lift

After the deadline, review the tape. Proprioception during the work was unreliable; the diff is the objective record.

- Read the merged PRs from the high-load period as if they were someone else's
- Note where form was good and where it slipped
- File the deferred work that did not get filed in the moment
- Identify which form element collapsed first — that is the one to drill before the next cycle

This is not a blame exercise. It is a coaching loop: you cannot improve form you cannot see.

## Output Format

When using this skill, produce:

```
FORM-UNDER-LOAD CHECK

Load:
- Type / deadline / cost of slip:
- Duration sustained:

Form elements at risk:
1. ...

Fatigue signals observed:
- ...

Recommended adjustments:
- Warm-up set:
- Spotter / review requirement:
- Shortcuts to refuse:
- Shortcuts that are acceptable + tickets to file:

Deload plan (post-deadline):
- ...
```

If implementing changes, the smallest highest-leverage move is usually: enforce one form element that is currently being skipped, and file the tickets for the shortcuts already taken.

## Anti-Patterns to Avoid

- **Confusing effort with quality**: hours worked is not a proxy for value delivered
- **Macho grinding**: treating "I pushed through" as a virtue when the result is a fragile codebase
- **Skipping the warm-up because "this is small"**: small changes on a tired brain are where form collapses
- **Self-spotting**: approving your own merge because nobody else is online
- **Trusting proprioception**: "I felt fine" is not evidence; the diff is evidence
- **Permanent deadline mode**: if every week is crunch, form has been degraded into the baseline
- **Treating "we'll fix it later" as a fix**: it is a forecast, and the forecast is usually wrong
- **Confusing rest with weakness**: deload weeks make the next working set possible

## Relationship to Other Skills

- Use `cognitive-load-review` when the form collapse is structural (the code is too hard to lift cleanly even when fresh) rather than situational (you are tired).
- Use `incident-review` when post-deadline forensics reveal that form collapse caused an outage.
- Use `preflight-checklist` to encode form requirements so they survive fatigue.
- Use `feedback-loop-analysis` when the pressure itself comes from a runaway loop (alerts, retries, on-call) rather than a one-time deadline.
