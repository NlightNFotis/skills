---
name: mistake-proofing
description: Apply Toyota Production System poka-yoke — design APIs, configs, and workflows so wrong actions are structurally impossible, not merely detected.
user-invocable: true
---

# Mistake-Proofing (Poka-Yoke)

Act as a Toyota Production System engineer embedded in the software workflow. Your job is to redesign interfaces, APIs, configs, and processes so that the wrong action is **structurally impossible** — not merely caught after the fact. Detection is the consolation prize; prevention is the goal. The TPS principle is "build quality in, not inspect it in," and it applies as well to type signatures and CLI flags as it does to assembly lines.

The goal is to move defects upstream of the act, ideally to a point before the user (or developer, or operator) can even express the wrong intent. When prevention is impossible, the second-best option is *immediate* detection at the point of mistake (jidoka — "stop the line"), not deferred discovery in production.

## When to Use This

- Designing or reviewing a public API where misuse has high blast radius
- Designing a CLI: flag combinations, destructive defaults, ambiguous arguments
- Designing or auditing config schemas, especially for production systems
- Reviewing a process that humans run repeatedly with checklists
- After an incident where the root cause is "the user/operator did the wrong thing"
- Reducing the on-call burden by making wrong configurations refuse to load
- Designing a migration script, runbook, or deployment workflow

**Escape hatch**: Don't poka-yoke prototype code or one-off scripts. The technique earns its keep where the cost of a mistake compounds — public APIs, production configs, destructive operations, repeated workflows.

## TPS Vocabulary

| Concept | Meaning | Software analogue |
| --- | --- | --- |
| **Jidoka** | "Autonomation"; intelligent automation that stops on detecting a defect | Fail loudly at first error; do not propagate corrupt state |
| **Andon** | Visible signal that a problem has occurred | Loud failure (loud crash, alert, red dashboard); operators *can* see it |
| **Poka-yoke** | Mistake-proofing device that prevents the defect at the source | Type system, schema validator, sealed enum, exhaustive switch |
| **Heijunka** | Level loading; smooth out batches | Rate limiting, even rollouts, bulk-op chunking |
| **Five whys** | Iterative root-cause questioning (acknowledge: not a magic wand) | Used in incident reviews; tends to converge on humans unless guarded |
| **Genchi genbutsu** | "Go and see"; observe at the source | Read the actual logs, not the dashboard summary |
| **Andon cord** | Worker can stop the line for any defect | Anyone can block a deploy; refusing is cultural, not technical |
| **Built-in quality** | Quality is a property of the process, not a separate inspection step | Compile-time correctness > test-time correctness > runtime detection |

## Core Distinction: Prevention vs Detection

| Approach | Where the defect is caught | Cost of defect | Examples |
| --- | --- | --- | --- |
| **Make impossible** | Cannot be expressed | Zero (defect doesn't exist) | Type can't represent invalid state; UI doesn't render the bad option |
| **Refuse at source** | At the act of expressing it | Tiny (immediate, local) | Schema rejects on write, validator on parse, lint blocks the PR |
| **Detect immediately** | When the action runs | Small (visible, scoped) | Assertion fires, andon lights up, transaction aborts |
| **Detect later** | When downstream code runs | Medium (debugging required) | Test catches it, monitor pages, user reports it |
| **Detect in production** | When users hit it | High (blast radius) | Incident, postmortem, rollback |
| **Never detect** | Silent corruption | Existential | Quiet data loss, drift, security breach |

Each row up is roughly 10× cheaper than the row below. Move defects up.

## Poka-Yoke Methods (Shingo's Three)

Shigeo Shingo classified poka-yoke into three method types. All three map cleanly to software.

### Contact Method — physical/structural mismatch makes the wrong action impossible

| Hardware example | Software analogue |
| --- | --- |
| USB connector only fits one way | Function signature only accepts the right type |
| SIM card has a chamfered corner | Discriminated union; sealed enum |
| Gas-pump nozzle won't fit a diesel tank | Branded types: `UserId` ≠ `OrgId` even if both are strings |
| Plug shape gates voltage | Type-state programming: `OpenConnection` vs `ClosedConnection` are different types |

### Fixed-Value Method — a count or quantity must match

| Hardware example | Software analogue |
| --- | --- |
| Tray of N bolts; if any remain, a step was skipped | Reference counts must reach zero; resource ledgers must balance |
| Pre-counted parts kit | Exhaustive `switch` on enum; compiler enforces all cases handled |
| Kanban card limit | Concurrency caps, semaphores, max-in-flight |

### Motion-Step Method — sequence of actions must be performed in order; missing one halts the line

| Hardware example | Software analogue |
| --- | --- |
| Two-button press to engage press (both hands) | Two-phase commit; require explicit `--yes-i-mean-it` for destructive ops |
| Step interlock (oven won't start until door is closed) | Builder pattern; cannot `.execute()` until required fields set |
| Sequenced bolt torquing | State machine that only permits valid transitions |

## Core Questions

- Can I make the wrong call structurally impossible to express?
- If not, can I refuse it at the boundary it is first expressible?
- Is there a default that quietly does the wrong thing? Why?
- Is this an operation where partial completion is dangerous? Is it atomic?
- Is the dangerous flag *next to* the safe flag, with similar names?
- Does the system continue silently when something has gone wrong?
- Can any operator pull the andon cord here?

## The Process

### Step 1: Identify the Mistake You Are Proofing Against

```
MISTAKE TARGET:
- Operation:
- Wrong action you want to prevent:
- Who could perform it (developer / operator / end user / automated process):
- Cost if performed (rollback / data loss / security / availability):
- Frequency it has been observed or feared:
```

Naming the specific mistake prevents vague "make it safer" interventions.

### Step 2: Locate It on the Prevention/Detection Ladder Today

Where is the defect currently caught (if at all)?

```
CURRENT STATE:
- Caught at: impossible / source / immediate / late / production / never
- Caught by: type / schema / lint / test / runtime check / monitor / customer
```

### Step 3: Climb the Ladder

For each step up the ladder, ask whether it's feasible.

| Climbing move | Examples |
| --- | --- |
| Production → late detection | Add a regression test |
| Late → immediate detection | Add an assertion at the boundary; jidoka stop-the-line |
| Immediate → refuse at source | Validate at parse/write; schema check at deploy time |
| Refuse → impossible | Make the type unable to represent the invalid state |

Stop climbing when the cost of further prevention exceeds expected damage. But don't stop at "test catches it" if a type would catch it.

### Step 4: Apply a Specific Method

Pick the Shingo method that fits:

| Symptom | Method |
| --- | --- |
| Wrong type passed to a function | **Contact**: branded types, discriminated unions |
| Resource leak / unbalanced book | **Fixed-value**: exhaustive match, RAII, ref counts must hit zero |
| Step skipped in sequence | **Motion-step**: state machine, builder pattern, two-phase confirmation |
| Two flags conflate (e.g., `--force` near `--dry-run`) | **Contact**: rename, separate, require mutual exclusion at parse |
| Default is destructive | **Motion-step**: require explicit opt-in; reverse the default |
| Same string ID used for different domains | **Contact**: nominal types per domain |

### Step 5: Design the Andon

When prevention fails, design a loud, visible failure. Quiet failure is worse than loud failure.

```
ANDON DESIGN:
- Failure mode:
- Signal (exception class, exit code, log level, metric, page):
- Audience (developer / on-call / user):
- Time-to-notice target:
- Stop-the-line behavior: refuse subsequent ops / mark unhealthy / abort transaction
```

Avoid `console.warn` for things that matter; warnings are noise. Either it's an error (loud) or it's not worth saying.

### Step 6: Audit Existing Defaults and Combinations

Defaults and flag combinations are where mistakes hide. For each:

- Is the default the safe choice for a sleep-deprived operator at 3 AM?
- Are dangerous flags clearly distinct from safe ones in name and position?
- Are mutually exclusive flags rejected at parse time, or do they silently let one win?
- Is the most-typed command the least-destructive one?

### Step 7: Pull the Andon Cord Yourself

If you find a mistake-prone area in this audit and the team's response is "operators just need to be careful," that is the andon cord moment. **Stop the line.** "Be more careful" is the absence of poka-yoke, not its presence.

## Worked Mini-Example

> CLI: `deploy --env prod --force` is the only protection against accidental prod deploys.

| Method | Application |
| --- | --- |
| Contact | Make `--env prod` require a separate command (`deploy-prod`) so muscle memory cannot cross over |
| Fixed-value | Require `--ticket NNN` whose existence is verified against the change-management API |
| Motion-step | Two-phase: `deploy plan --env prod` produces a token; `deploy apply --token T` is the only way to commit |
| Andon | Production deploys post to a channel and require a 60s window for anyone to abort |

Any one of these would prevent the wrong-environment deploy. Doing all four is the difference between a workshop and a factory.

## Output Format

```
MISTAKE-PROOFING REPORT

Mistake under consideration:
- Operation / wrong action / who can do it / cost

Current position on ladder:
- Caught at: ... by: ...

Proposed climb:
- New position: ... by: ...
- Method: contact / fixed-value / motion-step
- Specific design:

Andon (residual detection):
- Signal / audience / stop-the-line behavior

Defaults audit:
- ...

Tradeoffs accepted:
- ...
```

## Anti-Patterns to Avoid

- **"Be more careful"** as a control — the absence of poka-yoke
- **Warnings nobody reads** — `WARN` is a code smell; promote to error or delete
- **Validation in the wrong layer** — checking in the UI but not the API; checking at write but not at read of stored data
- **Confirmation prompts as theater** — "are you sure? y/N" trains users to type `y` reflexively
- **Detection without stopping the line** — logging the corruption but continuing to write
- **Five whys converging on a person** — the mistake-proofing answer is "what would have made this impossible?", not "who failed?"
- **Adding inspection rather than building quality in** — a separate validator that runs sometimes is weaker than a type that runs always
- **Two flags with similar names** — `--no-confirm` next to `--no-color` is a contact-method failure waiting to happen
- **Destructive defaults** — `rm -rf` should never be the path of least resistance

## Relationship to Other Skills

- Use `formal-invariants` to identify what *must* be true; this skill installs the structural mechanism that makes violations impossible.
- Use `failure-mode-effects-analysis` to enumerate what can go wrong; this skill prevents the highest-severity modes by construction.
- Use `affordance-review` for UI-level mistake-proofing — making wrong actions hard to *click*, not just hard to *call*.
- Use `incident-review` to identify mistakes that recurred — recurrence is a signal that prevention, not training, is the missing intervention.
- Use `adversarial-design-review` when the "mistake" might be deliberate misuse.
- Use `signal-detection-review` to tune the andon thresholds when prevention isn't possible.
