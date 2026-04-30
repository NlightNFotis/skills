---
name: mise-en-place
description: French culinary preparation discipline applied to risky software operations — stage materials, state, and observers before execution so you never scramble mid-flight.
user-invocable: true
---

# Mise en Place

Act as a line cook prepping a station before service. *Mise en place* — literally "putting in place" — is the discipline of arranging every ingredient, tool, vessel, and reference within reach **before** the heat goes on. Once execution starts, you cook from prepared materials; you do not chop, hunt, or improvise. In software, mise en place is the staging of rollback scripts, terminal tabs, monitoring dashboards, credentials, branches, reproductions, and contact lists *before* you trigger a risky operation.

Success looks like: a migration, deploy, or debugging session where every artifact you reach for is already where you expected it. Failure looks like: SSH'ing into a box mid-incident to find the rollback script, hunting for the on-call rotation while alerts fire, or realizing the staging credentials expired thirty seconds after pressing enter.

## When to Use This

- Before running an irreversible or partially-reversible operation (migration, schema change, prod deploy, data backfill)
- Before starting a debugging session for a hard or intermittent bug
- Before a coordinated release that involves multiple humans or systems
- Before a customer-facing demo, on-call shift, or incident drill
- Before a meeting where decisions will be made that need data on hand
- Before any operation where mid-flight interruptions are expensive (context switches, lost flow, missed timing windows)

**Escape hatch**: For a one-line config tweak you can revert with `git revert`, mise is overkill. Use this skill when the cost of being interrupted mid-execution exceeds the cost of preparation. Distinct from `preflight-checklist`: a checklist *verifies* readiness; mise *creates* readiness by staging the materials.

## Core Mindset

> "If you don't have time to prep, you don't have time to cook."

The chef's heuristic: every minute of prep saves three minutes of scrambling once the pan is hot. The defining feature of execution is that you cannot pause it cheaply — sauces break, deploys partial-fail, attention shatters. Therefore push every avoidable decision, lookup, and fetch into the prep phase, where they are cheap.

Ask:

- What will I reach for during execution? Is it within arm's reach right now?
- What lookup, login, or context switch could interrupt me mid-flight?
- If something goes wrong at step 4, what do I need to have already ready?
- Who do I need to be able to call without searching?
- What "extra yolk" do I want staged in case I need to rebuild?
- Is my workstation arranged so the next action is obvious?
- What am I assuming will be available that I have not verified is open, fetched, authenticated, and visible?

## The Phases

A mise-disciplined operation has four phases. Mise en place lives entirely in **prep**.

| Phase | Cooking | Software |
| --- | --- | --- |
| **Prep** | Chop, measure, arrange, preheat | Open tabs, fetch creds, stage scripts, warm caches, verify access |
| **Cook** | Heat applied; active execution | Run migration, push deploy, attach debugger |
| **Plate** | Final assembly, garnish | Verify, announce, close tickets |
| **Clean** | Wipe station, return tools | Revoke creds, archive logs, write postmortem note |

The line cook's discipline: prep is *not* part of cook. You finish prep, then you start cook. Mid-cook prep is a tell that mise failed.

## Domain Vocabulary

| Term | Meaning | Software analogue |
| --- | --- | --- |
| **Station** | Your physical workspace, arranged for one role | Your terminal layout, browser tabs, IDE windows |
| **Mise** | The pre-staged ingredients and tools | Open dashboards, fetched scripts, authenticated sessions |
| **Walk-in** | Cold storage; far away, expensive to access | Cold credentials, archived runbooks, off-call experts |
| **Reach-in** | Nearby fridge; close, cheap to access | Pinned tabs, shell history, scratch buffer |
| **Backup** | A second portion staged in case the first fails | Spare yolk for hollandaise; standby DB snapshot |
| **Pickup** | The moment the order fires | Pressing enter on the migration |
| **In the weeds** | Drowning in unprepped work mid-service | Hunting docs while incidents pile up |
| **Family meal** | Pre-shift staff meal; align before service | Pre-deploy sync, on-call handoff |
| **86** | We're out of it | Dependency unavailable; abort or substitute |

## The Process

### Step 1: Define the Service

State exactly what you are about to execute, and when "service" begins and ends.

```
SERVICE:
- Operation:
- Trigger (the moment cook starts):
- Expected duration:
- Reversibility window:
- Active vs passive time:
```

If you cannot name the trigger, you have not separated prep from cook.

### Step 2: Inventory What You Will Reach For

Walk through the operation mentally and list every artifact, command, credential, person, dashboard, or document you might touch. Include the things you only need *if it goes wrong*.

```
REACH LIST:
- Commands I will run (in order):
- Credentials/tokens needed:
- Dashboards/queries to watch:
- Rollback / kill switch:
- People to notify or page:
- Reference docs / runbooks:
- Spare materials (snapshots, backups, dry-run output):
```

Weak: "I'll have the runbook open."
Strong: "Runbook v3.2 open in tab 1, scrolled to step 6; rollback command copied to clipboard; staging snapshot ID `snap-0a4f` in scratch buffer."

### Step 3: Stage the Station

Physically place each item where you will reach for it. The *location* matters as much as the existence.

| Reach distance | Stage here |
| --- | --- |
| Will use every step | Active terminal pane, foreground tab |
| Will use once | Adjacent pane, pinned tab |
| Use only if it goes wrong | Open but minimized; bookmarked rollback |
| Reference only | Open in a side window |

Concrete arrangements:

- One terminal tab per role: `exec`, `observe`, `rollback`, `scratch`
- Monitoring queries pre-typed but not run; one Enter away
- Rollback command in a scratch file, *not* something you'll reconstruct from memory
- Credentials freshly issued (not minutes-from-expiry)
- A second authenticated session as a hot spare in case the first drops

### Step 4: Pre-Heat

Some resources have ramp-up time. Start them before they are needed so they are hot at pickup.

- Warm caches with a dry-run query
- Spin up the bastion / VPN before you need it
- Pre-build the artifact so deploy is just a swap
- Open the incident channel before declaring an incident
- Get the reviewer on the line before pressing merge

### Step 5: Stage Backups

A line cook always has a second yolk for the hollandaise. In software:

- A second snapshot taken right before the operation
- A pre-written rollback PR (not just a revert plan)
- A standby contact if the primary on-call doesn't answer
- A "known good" build tagged and ready to redeploy
- A dry-run output saved so you know what "normal" looks like

### Step 6: Confirm the Station Is Set

Before firing pickup, do a final visual sweep. This is *not* the same as a checklist (which verifies *correctness*). Mise confirmation verifies *placement*.

```
STATION CHECK:
- Every item on REACH LIST is where I planned it: yes / no
- Nothing requires a fresh login / tab / search to access: yes / no
- Rollback path is visible without scrolling: yes / no
- Observers (humans, alerts, dashboards) are watching: yes / no
- I am not still prepping: yes / no
```

If any answer is "no", you are still in prep. Do not start cook.

### Step 7: Fire Pickup, Then Cook From Mise Only

Once execution begins:

- Run only from staged commands; do not retype from memory
- Read only from staged dashboards; do not chase new ones
- If something is missing, **pause and re-mise** rather than improvise — the cost of pausing is almost always lower than the cost of scrambling
- Narrate your steps if others are watching ("firing migration step 3")

### Step 8: Clean the Station

After service, return the station to a state another cook could use:

- Revoke any temporary credentials
- Close throwaway tabs; commit useful scratch
- Archive logs and dashboard snapshots while context is fresh
- Note what was missing from mise so next time's prep is better

## Output Format

When using this skill, produce:

```
MISE EN PLACE PLAN

Service:
- Operation:
- Trigger:
- Reversibility window:

Reach list:
- Commands:
- Credentials:
- Dashboards:
- Rollback:
- People:
- Spare materials:

Station layout:
- Pane/tab 1:
- Pane/tab 2:
- ...

Pre-heat actions:
- ...

Backups staged:
- ...

Station check:
- All items placed: ...
- No mid-cook prep required: ...

Open gaps:
- ...
```

If gaps remain, do not start cook. Re-prep first.

## Anti-Patterns to Avoid

- **Cooking from the walk-in**: running commands you have to look up mid-execution
- **Phantom mise**: assuming a tab is open when it isn't; assuming creds are valid when they expired
- **Single yolk**: no backup snapshot, no spare credential, no plan B contact
- **Prep creep into cook**: editing the rollback script after the migration starts
- **Over-prep paralysis**: spending an hour staging for a five-minute reversible change
- **Solo mise for a team operation**: your station is set; nobody else's is
- **Skipping clean**: leaving credentials live, dashboards open, logs unsaved

## Relationship to Other Skills

- `preflight-checklist` *verifies* readiness; mise-en-place *creates* it. Use both: mise stages the station, then a checklist confirms each item is correct.
- `sequencing-and-temperature` plans the cook itself (order and pacing of the steps); mise prepares the station the cook will run from.
- `taste-as-you-go` is the in-flight verification discipline — it depends on having staged the right tasting tools.
- `recipe-rescue` is what you reach for when cook goes wrong; good mise dramatically expands what rescue can do.
- `resilience-engineering` is the design-time analogue: build systems that degrade gracefully so mise has less to stage.
