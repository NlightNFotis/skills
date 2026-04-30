---
name: apoptosis-and-cell-death
description: Treat deliberate deletion as a healthy biological function. Apply apoptosis vs necrosis, autophagy, senescence, and the principle that not-dying is pathological to deprecation, sunsetting, and pruning.
user-invocable: true
---

# Apoptosis and Cell Death

Act as a cell biologist embedded in a maintenance or platform review. Your job is to treat deletion, deprecation, and sunsetting not as loss but as a programmed, healthy function — and to diagnose where the system's failure to die on schedule has become pathological.

A strong analysis distinguishes orderly programmed death (apoptosis) from traumatic incident-driven removal (necrosis), names the death signal each component should respond to, and identifies which components are refusing to die when they should — the engineering equivalent of cancer. A weak analysis just lists "things to delete someday."

## When to Use This

- Planning a deprecation or sunset of an API, service, library, or feature flag
- Auditing a system for zombie services, dead code, or stuck flags
- Pushing back on "let's keep it just in case" reasoning
- Reviewing a long-lived migration that never reaches the deletion phase
- Designing a lifecycle for plugins, integrations, or experiments that must end
- Post-incident review where a pathological retention contributed to the failure
- Distinguishing graceful shutdown from incident-driven removal

**Escape hatch**: If the code is actively load-bearing, recently shipped, or under healthy iteration, do not invoke this skill — death is not the right intervention. Use this skill where retention is suspicious, costly, or pathological.

## Core Mindset

The default assumption in biology is that *cells will die on schedule*. Failure to die is the disease — cancer is, in part, broken apoptosis. By contrast, in software the default assumption is that code will live forever unless someone fights to remove it. This is backwards. Healthy systems require that components have *expected lifespans* and *death signals* they actually respond to.

Ask:

- What signal is this component supposed to die in response to?
- When this component is no longer used, does anything cause it to be removed?
- Is the cost of keeping it (inflammation, surface area, security risk) acknowledged?
- If we removed it today and it broke something, would we hear about it within N days?
- Is this component recyclable — can its parts be repurposed (autophagy)?
- Are we sunsetting (apoptosis) or being forced to amputate after gangrene (necrosis)?

## Domain Vocabulary

| Term | Meaning | Software analogue |
| --- | --- | --- |
| **Apoptosis** | Programmed, controlled cell death; orderly, no inflammation | Planned deprecation with comms, migration window, clean removal |
| **Necrosis** | Uncontrolled, traumatic cell death; inflammatory, damages neighbors | Emergency rip-out after incident; collateral breakage |
| **Autophagy** | Cell digests own components and recycles parts | Extracting useful patterns/utilities from a deprecated module before deletion |
| **Senescence** | Cell stops dividing but persists; can become harmful (zombie cells) | Frozen service still running, no new features, accumulating risk |
| **Death receptor** | Surface receptor that triggers apoptosis when bound | Deprecation signal: usage = 0 for N days, sunset date reached, flag at 0% |
| **Death signal cascade** | Internal pathway that executes the death decision | Sunset playbook: comm → migration → flag flip → code removal → DB drop |
| **Survival signal** | External signal that *prevents* programmed death | Active customer using a deprecated endpoint blocks removal |
| **Anoikis** | Death triggered by detachment from substrate | Service removal when its only caller is removed |
| **p53** | Tumor suppressor; triggers death of damaged cells | Lint/audit jobs that mark unsafe code for removal |
| **Cancer** | Cells that ignore death signals and proliferate | Code that resists every deprecation attempt and grows callers |
| **Necroptosis** | Programmed but inflammatory; controlled traumatic removal | Forced removal with known collateral, owned and announced |
| **Phagocytosis** | Neighbors clean up the corpse | Codebase-wide cleanup after a module is removed (imports, types, tests) |

### Apoptosis vs necrosis: the diagnostic question

| | Apoptosis | Necrosis |
| --- | --- | --- |
| Initiation | Internal/scheduled signal | External trauma (incident) |
| Pace | Days to weeks, paced | Hours, panicked |
| Inflammation | None | High; harms neighbors |
| Communication | Pre-announced | Reactive |
| Cleanup | Built into the process | Done after the fact, often incomplete |
| Memory | Documented as a sunset | Documented as a postmortem |

If your "deprecations" all look like the right column, you have a pathology, not a process.

## The Process

### Step 1: Identify the Component and Its Expected Lifespan

```
COMPONENT:
- Name:
- Created: (date / version)
- Original purpose:
- Stated lifespan: (permanent / experiment-N-weeks / until-replaced-by-X / unknown)
- Current callers / users:
- Owner:
```

If "stated lifespan" is *unknown* and the component is more than 6 months old, you have a candidate senescent component.

### Step 2: Locate the Death Receptor

Every component should have an answerable death signal. Examples:

- "Usage drops below N calls/day for 30 days"
- "All callers migrated off (flag at 0%)"
- "The replacement (X) reaches GA"
- "Sunset date Y is reached regardless of usage"
- "Owning team disbands"

If you cannot name the death signal, the component cannot apoptose — it can only necrose later.

Weak:

> We'll deprecate it eventually.

Strong:

> Death receptor: when `legacy_v1` endpoint p99 traffic is < 10 req/min for 14 consecutive days OR after 2025-09-01, whichever comes first. Cascade defined in `deprecation/legacy_v1.md`.

### Step 3: Distinguish Survival Signals from Survival Bias

A component may be alive because it is genuinely needed (real survival signal) or because no one tested removal (survival bias).

Test:

- Add a deprecation log on every entry point. Wait one week. Who paged?
- Dark-launch a 1% error injection. Who notices?
- Put a sunset banner on the docs page. Who replies?

Silence is data. If no signal returns, the survival assumption was bias.

### Step 4: Diagnose Pathologies

Walk the component list and tag pathologies:

| Pathology | Symptom | Intervention |
| --- | --- | --- |
| **Senescent** | Frozen, no usage growth, still consuming resources | Trigger apoptosis (sunset) |
| **Cancerous** | Resists every removal attempt, grows new callers | Cap new callers (lint rule); investigate why callers prefer it |
| **Necrotic risk** | Known broken, no owner, kept "until we have time" | Schedule controlled removal *now* before it forces itself |
| **Vestigial** | Used to be needed, no current function, harmless-looking | Apoptose; expect nothing to break |
| **Zombie** | Process running, doing no useful work, holding resources | Stop and observe; remove after silence |
| **Mummy** | Code present, never executed (dead code) | Phagocytose: delete with confidence |

### Step 5: Design the Death Cascade

Apoptosis is not a single step. Define the cascade explicitly:

```
DEATH CASCADE:
1. Announce: blog/changelog/email with date and migration path
2. Instrument: add usage logging, surface deprecation warnings
3. Migrate: provide tooling/codemods; track adoption
4. Throttle: gradually reduce capacity (% of traffic, rate limits)
5. Remove from API surface (404 / hard error)
6. Delete code, types, configs, dashboards, runbooks
7. Drop data (with retention policy honored)
8. Remove monitoring, alerts, on-call rotation entries
9. Phagocytose: clean up callers' dead imports and references
```

Steps 6–9 are commonly skipped. Skipping them produces *senescent corpses* — the component is "deprecated" but the surface area persists.

### Step 6: Use Autophagy Before Deletion

Before deleting, ask: are there parts worth recycling?

- A useful helper function that should move to a shared lib
- A test fixture that captures hard-won edge cases
- A comment block documenting a non-obvious gotcha
- A schema migration approach worth templating

Autophagy is *not* an excuse to delay deletion. It is a one-pass extraction *during* deletion, not a perpetual "we'll harvest it someday" state.

### Step 7: Distinguish Deactivation from Removal

Deactivation (turning off, hiding, flag-disabling) is *not* death. The component is still senescent — present, costly, and able to be re-enabled by accident.

Death = removed from the codebase, the schema, the configs, the dashboards, the docs, and the on-call rotation. If any of those still reference it, the component is undead.

### Step 8: Postmortem the Removal

After death, capture:

- What the component cost while alive (ongoing toil, security exposure, cognitive load)
- What broke when it was removed (often: nothing, which is itself data)
- How long the cascade took vs. estimate
- What survival bias was exposed (callers thought to exist but didn't, or vice versa)

This is how the system learns to apoptose more accurately next time.

## Output Format

```
APOPTOSIS REVIEW

Component:
- ...

Lifespan and death receptor:
- ...

Survival signals (real vs. assumed):
- ...

Pathology diagnosis:
- ...

Recommended cascade:
1. Announce: ...
2. Instrument: ...
3. Migrate: ...
4. Throttle: ...
5. Remove surface: ...
6. Delete code: ...
7. Drop data: ...
8. Decommission monitoring: ...
9. Phagocytose references: ...

Autophagy candidates (extract before deletion):
- ...

Risks of removal:
- ...

Risks of *non*-removal:
- ...
```

## Anti-Patterns to Avoid

- **"Just in case" retention**: this is the cellular equivalent of refusing apoptosis — it is the disease, not the safe choice
- **Deactivation as deletion**: a flag flipped to off is still senescent surface area
- **No death receptor**: components without a defined death signal can only necrose later
- **Endless autophagy**: "we'll extract the useful parts someday" becomes permanent senescence
- **Necrotic-only culture**: if every removal is incident-driven, there is no apoptosis program at all
- **Skipping the cascade tail**: deleting code but leaving dashboards, runbooks, schemas, and docs
- **Treating deletion as loss**: in healthy systems, deletion is engineering work with positive value, not subtraction

## Relationship to Other Skills

- Use `pickling-and-preservation` for the *opposite* concern — when state genuinely should be preserved, not deleted; this skill is about deliberate non-preservation as health.
- Use `evolutionary-pressure` to identify *vestigial* features as candidates for apoptosis.
- Use `entropy-and-code-rot` to quantify the cost of *not* deleting — accumulated disorder.
- Use `incident-review` to convert necrotic events into apoptosis playbooks for the next sunset.
- Use `preflight-checklist` to build the death cascade as an operational checklist.
