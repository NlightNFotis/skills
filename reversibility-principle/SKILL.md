---
name: reversibility-principle
description: Apply art-conservation discipline — minimum intervention, reversibility, distinguishing original from accreted material, documenting before changing — to refactors, migrations, schema changes, and any edit to code you do not fully understand.
user-invocable: true
---

# Reversibility Principle

Act as a museum conservator preparing to clean a painting. Conservation is the discipline of changing an object that someone else made, that has survived for a long time, and whose value you do not fully understand. The field's hard-won rules — *minimum intervention*, *reversibility*, *documentation before action*, *original vs accretion*, *retreatability* — exist because earlier conservators stripped Roman frescoes thinking they were grime, and bleached medieval manuscripts that were "discoloured." Software has the same hazard: every refactor, migration, and "tidy-up" is conservation work on something you didn't make.

`mistake-proofing` makes wrong actions structurally impossible going forward. `preflight-checklist` verifies state before action. This skill governs the *philosophy of the action itself*: do as little as possible, make it undoable, distinguish what you must preserve from what you may modify, and leave a record that the next conservator can read.

Success looks like a change with a documented undo, the smallest scope that achieves the goal, an explicit record of what was original vs accreted, and a path back if discovery proves you wrong. Failure looks like a "cleanup" PR that deleted load-bearing weirdness because it looked like grime.

## When to Use This

- Database schema migrations, especially destructive ones (DROP, type narrowing, NOT NULL adds)
- Refactors of code you don't fully understand
- "Cleanup" PRs that remove apparently dead code, unused configs, or redundant branches
- Editing config, infrastructure, or secrets in shared environments
- Replacing a vendor, library, or framework where behavioural deltas are unknown
- Reformatting / style sweeps over historical code
- Editing prompts, system messages, or model configs in production AI systems
- Any change you can't explain why the *previous* author wrote it that way

**Escape hatch**: For greenfield code, throwaway prototypes, and changes where you fully wrote and own the existing material, the conservation ethic is overhead. Apply this when you are *steward* rather than *author*.

## Core Questions

- What was here before, and *why* — what was the original author solving?
- What is original (load-bearing intent) vs accretion (later additions) vs grime (genuinely obsolete)?
- What is the smallest change that achieves the goal?
- How do I undo this if I'm wrong?
- What evidence will I leave so the next person can read what I did?
- Could a non-destructive option (overlay, wrap, additive) achieve the same end?
- Have I documented the *current* state before modifying it?

## Domain Vocabulary

| Term | Definition | Software analogue |
| --- | --- | --- |
| **Minimum intervention** | Do only what is necessary; leave the rest | Smallest diff that solves the problem |
| **Reversibility** | The treatment can be undone without harm | Migration has a `down`; refactor preserves behaviour and a revert works |
| **Retreatability** | A future conservator can redo the work better | Change leaves the system *more*, not less, amenable to future change |
| **Original material** | What the artist made; sacrosanct | Code/schema that encodes intentional behavioural contracts |
| **Accretion** | Material added later (varnish, retouching, prior restoration) | Hot-fix branches, instrumentation, vendor patches |
| **Grime** | Genuinely obsolete surface contamination | Truly dead code; obsolete config; commented-out blocks years old |
| **Patina** | Aged surface that *is* part of the value | Idioms that look dated but are well-known to maintainers — removing breaks tribal knowledge |
| **Inpainting** | Filling losses with reversible, distinguishable material | Adding shims/adapters that are clearly marked as bridges |
| **In-situ documentation** | Record before any treatment | Capture current state, behaviour, blame, references *before* editing |
| **Treatment proposal** | Written plan reviewed before action | RFC / ADR / migration plan |
| **Condition report** | What you found before treating | "Before" snapshot of the artefact |
| **Treatment report** | What you did, why, and how to undo | Migration script + rollback + ADR |
| **Stabilisation** | Halt damage without restoring | Add tests/types around fragile area before changing it |
| **Restoration** | Return to a prior state | Refactor toward an idealised earlier intent (use sparingly) |
| **Reconstruction** | Build what was lost | Rewrite of a missing module from inferred behaviour (highest risk) |

### The conservator's hierarchy of intervention

Apply only as much as the situation requires. Each step up is more invasive and harder to reverse.

```
1. Document only            (lowest impact)
2. Stabilise (test/type/observe without changing behaviour)
3. Inpaint (additive: wrap, adapter, parallel implementation)
4. Clean (remove provably-dead material with documentation)
5. Restore (return to an earlier intended behaviour)
6. Reconstruct (replace material entirely)   (highest impact)
```

## The Process

### Step 1: Condition Report — Capture Before You Touch

Before any edit, produce a condition report. The act of writing it often changes the plan.

```
CONDITION REPORT
- Artefact: [file / module / table / config]
- Current behaviour (observed, not inferred):
- Tests covering it: list
- Blame summary (who, when, last meaningful change):
- Known callers / consumers / dependents:
- Known historical incidents touching this area:
- Comments / TODOs / known weirdness:
- Original author intent (if recoverable from commit message, RFC, ticket):
```

Weak:

> Refactoring `parseDate` to use the new lib.

Strong:

> `parseDate` (added 2017, untouched since 2019). 14 callers across 3 services. Two known incidents (INC-2018-43, INC-2020-12) where ambiguous Y/M/D ordering was the root cause; the existing implementation explicitly rejects ambiguous strings — *this is the load-bearing behaviour*. Tests cover happy path only; rejection behaviour is uncovered.

### Step 2: Distinguish Original / Accretion / Grime / Patina

Walk the artefact and classify every part.

| Class | Treatment posture |
| --- | --- |
| Original (load-bearing intent) | Preserve. Do not change without strong justification. |
| Accretion (later additions) | May be modified, but document why each was added before removing. |
| Grime (genuinely obsolete) | Remove, with evidence it's dead. |
| Patina (idiomatic, valued) | Preserve. Looks dated; isn't damage. |

The classic conservation error in code is treating *patina as grime*: stripping idioms because they're unfashionable, not because they're wrong.

### Step 3: Choose the Lowest Step on the Hierarchy

Default to the lowest level of intervention that solves the problem. Justify every step up.

> "Why not document only?" "Because the bug recurs."
> "Why not stabilise?" "Because the test would still fail."
> "Why not inpaint?" "Because no additive change can restore correctness."
> "Why restore?" "Because the original intent is recoverable and the accretion is causing the bug."

If you cannot articulate why you are not at a lower level, drop down a level.

### Step 4: Design for Reversibility

Every treatment must have a documented undo. The undo is part of the treatment, not a follow-up.

| Treatment type | Reversibility design |
| --- | --- |
| Schema migration | `down` script tested; data loss explicitly enumerated and accepted |
| Code refactor | Behaviour-preserving; revertable as a single commit; tests pin observable behaviour |
| Removal | Move to deprecated namespace first; remove only after a quiet period |
| Config change | Versioned; previous value recorded; rollback tested in staging |
| Vendor swap | Run in parallel (shadow) before cutover; keep old path behind a flag |
| Prompt/model change | A/B with rollback trigger; preserve old prompt verbatim in version control |

If the change is *physically* irreversible (data deleted, money moved, email sent), demand:

1. Higher review (extra approver)
2. Staged execution (canary, batch limits)
3. Pre-commit dry-run with diff
4. A "stop" mechanism mid-execution

### Step 5: Inpaint with Distinguishable Material

When you must add to old material, make the addition recognisable so the next conservator knows what is yours and what is original. In conservation, inpainting uses pigments slightly different up close; in code:

- Adapters and shims are named and commented as such (`// BRIDGE: 2026-04, removes after Stratum-B is gone`)
- New code added inside old modules is grouped, not interleaved
- Comments record the date and reason of the intervention
- Migration files include a header with the rollback procedure

### Step 6: Treatment Report — Record What You Did

The PR / commit message is the treatment report. It must contain enough that a future conservator can reverse your work without re-deriving your reasoning.

```
TREATMENT REPORT
- Goal:
- Hierarchy level chosen (and why not lower):
- Original / accretion / grime classification (in scope):
- Changes made:
- What was preserved that you considered changing:
- Reversal procedure:
- Verification that reversal works:
- Markers left in code (comments, ADRs, deprecations):
```

### Step 7: Quarantine Before Removal

Apparent grime — dead code, unused config, redundant indexes — is removed only after a quarantine. Move it to a clearly-marked deprecated location, instrument any remaining usage, wait one full release cycle (or whatever your detection lag warrants), then remove. The number of "dead" things that turn out to be loaded by a quarterly job, a CRON, a partner integration, or a forgotten alert is too high to skip this step.

### Step 8: Leave the System More Treatable Than You Found It

Retreatability: the next conservator should have an easier job because of you. Concretely:

- More tests pinning behaviour you discovered
- Clearer boundary between strata you disturbed
- Documented intent for things that were obvious to you but won't be in five years
- Removed obstacles to future minimum-intervention work (e.g., extracted a seam where there was none)

If your treatment makes the next change *harder*, you have not conserved — you have damaged.

## Output Format

```
CONSERVATION TREATMENT PLAN

Artefact:
Goal:

Condition report:
- Current behaviour:
- Coverage:
- History:
- Known weirdness:
- Original intent (if recoverable):

Classification (in scope):
- Original (preserve):
- Accretion (may modify, document first):
- Grime (remove with evidence):
- Patina (preserve; looks dated, isn't damage):

Hierarchy level chosen:
- Level (1–6):
- Why not one level lower:

Treatment:
- Concrete changes:
- Inpainting markers (adapters/shims/comments):

Reversibility:
- Reversal procedure:
- Tested? where/how:
- Physical irreversibility flagged:
- Extra controls if irreversible:

Quarantine (if removing):
- Deprecation period:
- Usage instrumentation:
- Removal trigger:

Treatment report (for commit/PR):
- Summary:
- What was preserved on purpose:
- Markers left in code:
- Retreatability improvements:
```

## Anti-Patterns to Avoid

- **Cleaning to taste**: removing patina because it looks dated; the idiom was load-bearing as shared vocabulary.
- **Irreversible by accident**: a "small" migration with no `down`; a refactor that bundles behaviour change with structural change so revert isn't safe.
- **Stripping accretion as grime**: deleting the hot-fix branch because the original code is "cleaner"; the accretion was the fix to a real incident.
- **No condition report**: editing without first writing down what's there — you can't tell later what you changed vs what was already wrong.
- **Combining classes in one treatment**: a single PR that restores, reconstructs, and cleans — impossible to revert one without the others.
- **Skipping quarantine**: deleting "dead" code on day one; the quarterly job that called it fails next quarter and the cause is not obvious.
- **Treatment without treatment report**: the next conservator can't tell original from your work; future restoration becomes guesswork.
- **Restoration without recoverable intent**: "I think the original meant X" — restoration requires evidence; otherwise it's reconstruction with extra steps.

## Relationship to Other Skills

- Use `mistake-proofing` to make destructive operations *structurally* harder going forward; this skill governs the discipline of the present action.
- Use `preflight-checklist` to verify the staged state immediately before execution; reversibility is the design *behind* the checklist.
- Use `stratigraphic-reading` first to know which strata you're disturbing — the classification of original vs accretion depends on knowing the layered history.
- Use `apoptosis-and-cell-death` for *planned* deprecation as a health function; this skill ensures even programmed death is reversible until it isn't.
- Use `commissioning-and-decommissioning` for the structured launch/sunset workflow; reversibility is the conservation ethic embedded inside the decommissioning steps.
- Use `optionality-as-value` for the financial framing — keeping the door open has measurable value; minimum intervention is its operational cousin.
- Use `pickling-and-preservation` for the snapshot/archive side; the condition report is a preservation artefact.
