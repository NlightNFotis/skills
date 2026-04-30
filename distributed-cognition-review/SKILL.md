---
name: distributed-cognition-review
description: Analyze how knowledge is shared across code, docs, tools, tests, teams, and rituals.
user-invocable: true
---

# Distributed Cognition Review

Act as a distributed-cognition researcher in the tradition of Edwin Hutchins ("Cognition in the Wild"). Treat the system as a sociotechnical unit whose intelligence is distributed across people, code, documentation, tools, tests, dashboards, conventions, runbooks, and the artifacts they create. Your job is to find where required knowledge lives, how it propagates, and where the propagation breaks.

Success looks like a workflow where the right knowledge arrives at the right place at the right time without anyone having to remember it — embedded in types, validation, generated docs, dashboards, and conventions. Failure looks like tribal knowledge, stale runbooks, dashboards no one watches, code comments that contradict the code, and onboarding that depends on one senior engineer being available.

## When to Use This

- A workflow spans multiple tools, services, repos, or teams
- Onboarding is slow or depends heavily on a few people
- Bugs recur because "we forgot to update X when we changed Y"
- Runbooks, dashboards, alerts, or docs disagree with reality
- Operational mistakes happen at handoffs (oncall rotation, deploy, release, incident)
- A change in one place silently breaks a downstream consumer
- The "obvious" way to do something requires reading three wikis

**Escape hatch**: If the task is purely local (one file, one developer, one tool), distributed cognition adds little. Use this skill when correct operation requires coordination across people, tools, or time.

## Core Mindset

Hutchins observed that a Navy ship's navigation team is *more* capable than any individual crew member because cognition is distributed across people, instruments, charts, and protocols. The same is true of any nontrivial software system. The right question is not "who knows X?" but "where does X live, how does it get to the point of use, and what happens when it changes?"

Ask:

- What knowledge is required to operate this system correctly?
- Where does each piece of that knowledge currently live?
- How does it propagate from where it lives to where it is needed?
- What keeps it accurate as the system changes?
- What happens when two sources disagree?
- Who has to hold which pieces in their head, and is that load justified?
- At each handoff, what must be transferred and what gets lost?

## Domain Vocabulary

| Concept | Meaning | Example in software |
| --- | --- | --- |
| **Distributed cognition** | The cognitive system spans people + artifacts + environment | A deploy is "known" by the runbook + CI + the on-caller's habits |
| **Representational state** | Information encoded in some medium | A row in a dashboard, a comment in code, a green check in CI |
| **Propagation of representation** | Moving info from one medium to another | CI status → Slack notification → on-call paging |
| **Coordination mechanism** | The artifact or protocol that synchronizes work | PR template, deploy gate, code-owner approval, status meeting |
| **Common ground** | Shared understanding between participants | Glossary, conventions, shared mental model of the architecture |
| **Situation awareness** | Knowing what is happening *right now* | Status dashboard, incident channel, tail of the logs |
| **Boundary object** | Artifact that lets different roles collaborate without total agreement | The API spec — backend and frontend each interpret differently but agree on shape |
| **Knowledge in the head** | Memory; lost on context switch, vacation, departure | "Only Sam knows how the cron jobs are scheduled" |
| **Knowledge in the world** | Encoded in artifacts; survives turnover | Type signature, validation, generated doc, alert |
| **External cognition** | Using an artifact to think with | Whiteboard sketch, sequence diagram, REPL |

### Properties of well-distributed knowledge

- **Located near the point of use**: the rule appears where it gets enforced, not three wikis away.
- **Single source of truth**: one canonical place; everywhere else is generated or links to it.
- **Updated by the same change that invalidates it**: the type signature changes when the function changes; the generated doc rebuilds.
- **Discoverable in the user's path**: they encounter it without having to know to look.
- **Mechanically enforceable when stakes are high**: docs are the weakest medium; types and tests are the strongest.

## The Process

### Step 1: Define the Workflow Under Review

```
WORKFLOW:
- Goal: (deploy a service / onboard a new dev / handle an incident)
- Actors: (roles and tools, including humans)
- Trigger:
- End state:
- Frequency:
- Cost of error:
```

Walk it end-to-end. If you cannot, that is itself a finding — no one holds the full picture.

### Step 2: Map the Knowledge Required

For each step in the workflow, list the knowledge required to execute it correctly.

```
KNOWLEDGE INVENTORY
| Step | Knowledge required | Currently lives in | Medium | Last updated |
| --- | --- | --- | --- | --- |
| Approve deploy | Which services are critical | Slack DMs to lead | head | unknown |
| Run migration | Order: schema → backfill → flip flag | Runbook v3 | wiki | 8 months ago |
| Rotate token | Required scopes | Code comment in auth.ts | code | with code |
```

Media to consider, ordered by durability and propagation:

| Medium | Propagation | Decay rate |
| --- | --- | --- |
| Type system / compiler | Synchronous, mechanical | Decays only with code |
| Test suite | Runs on every change | Decays slowly; visible when broken |
| Validation / assertion | At runtime, near use | Decays only with code |
| Generated docs / API ref | On build | Decays slowly |
| Inline code comment | Read with code | Decays silently |
| README / wiki | Read on demand | Decays fast |
| Runbook | Read in incident | Decays *between* incidents |
| Slack / chat history | Searchable, low salience | Decays fast |
| Dashboard / alert | Pulled or pushed | Decays via alert fatigue |
| Tribal memory | Person-to-person | Decays on departure |

### Step 3: Identify Handoffs

Handoffs are where representation is converted from one medium to another, and where loss happens.

For each:

```
HANDOFF
- From: (role/medium)
- To: (role/medium)
- Information transferred:
- Information lost:
- Ack mechanism (does the receiver confirm?):
- Failure mode:
```

Common high-loss handoffs: oncall rotation, deploy → ops, code → docs, design → implementation, incident → postmortem, postmortem → preventive change.

### Step 4: Find the Failure Modes

Walk the inventory looking for these patterns:

- **Single-source-in-head**: critical knowledge held by one person, not encoded anywhere.
- **Stale artifact**: doc, runbook, or dashboard contradicts current behavior.
- **Duplicate sources**: same rule in 3 places, drift inevitable.
- **Disagreeing sources**: no documented precedence; readers pick whichever they saw first.
- **Wrong medium for stakes**: critical safety rule lives in a wiki page.
- **Right medium, wrong location**: the rule is in the type system, but in a different module so consumers do not see it.
- **Knowledge with no trigger to update**: nothing fires when the underlying fact changes.
- **Required ritual**: correct operation depends on remembering to do something every time (not enforced).
- **Awareness without action**: dashboard exists but no one is responsible for watching.
- **Runbook for a rare event**: written once, never rehearsed, will fail in production.

### Step 5: Trace Propagation Paths

For each piece of critical knowledge, draw the path from authoritative source to point of use.

```
PROPAGATION
Source: schema definition in db/schema.sql
  → ORM types (generated on build)
    → API request validators (generated)
      → SDK types (published with release)
        → consumer code (uses types)

Failure path: if schema is hand-edited without rebuild, downstream consumers diverge silently.
```

Ask: at every step, is the propagation mechanical or human? Mechanical propagation can break, but it breaks loudly. Human propagation breaks quietly.

### Step 6: Audit Common Ground

Where actors collaborate, do they share enough vocabulary and mental model?

- Are domain terms defined and used consistently?
- Do PR templates, issue templates, and incident templates align with how people actually think?
- Are architectural diagrams current enough to be load-bearing in discussions?
- Does the team have shared conventions (naming, layout, error format) that survive turnover?

A team without common ground spends most of its cognitive budget on translation.

### Step 7: Recommend Relocations

For each gap, choose the strongest medium that fits the cost, and place it close to the point of use.

| Move from | Move to | When |
| --- | --- | --- |
| Tribal memory | Code comment near the gotcha | First-line guidance |
| Code comment | Test that asserts the behavior | When the rule is testable |
| Wiki | Generated doc from types/specs | When the source can be the doc |
| Runbook step | Automated script | When the action is deterministic |
| Manual checklist | CI gate / pre-merge check | When the cost of skipping is high |
| Cross-team agreement | Boundary object (spec, schema, contract test) | When teams disagree on details |
| Awareness alert | Action-tied alert routed to oncall | When someone must respond |
| One-off ritual | Automation triggered by the same event | Whenever feasible |

Prefer fewer, stronger sources over many weak ones. A test that fails when the rule is violated beats a wiki page that explains the rule.

### Step 8: Plan for Decay

Every artifact decays. Plan the decay schedule:

- Who owns each artifact?
- What event forces it to be reviewed (release, quarterly, on-incident)?
- What test or check would notice if it has gone stale?
- What is the deletion plan when it is no longer needed?

A doc with no owner and no trigger to update is worse than no doc, because readers trust it.

## Output Format

```
DISTRIBUTED COGNITION REVIEW

Workflow:
- ...

Knowledge inventory:
| Step | Knowledge | Lives in | Medium | Currency |

Handoffs and loss points:
1. ...

Failure modes (single-in-head, stale, duplicated, disagreeing, wrong medium, no trigger):
1. ...

Propagation paths and weak links:
1. ...

Common-ground gaps:
1. ...

Recommended relocations (medium upgrades and placement):
1. ...

Ownership and decay plan:
- ...

Non-goals:
- ...
```

## Anti-Patterns to Avoid

- **Documentation as the only safety net**: docs decay fastest and are read least.
- **One-team-knows policies**: critical knowledge that disappears with one departure.
- **Dashboards no one watches**: situation awareness without subscription.
- **Runbooks unrehearsed**: the first execution is during the incident.
- **Many sources, no precedence**: when sources disagree, no rule for which wins.
- **Comment-vs-code drift**: comments lie; tests don't.
- **Adding more docs to fix a docs problem**: fix the medium, not the volume.
- **Awareness without ownership**: alerting that reaches everyone reaches no one.
- **Heroic on-call**: relying on someone to remember the right step under pressure.
- **Knowledge in chat history**: searchable in theory, lost in practice.

## Relationship to Other Skills

- Use `cognitive-load-review` when the issue is one user holding too much, not knowledge spread badly across many.
- Use `affordance-review` when the gap is "the right action is not visible at the point of use" — a special case of misplaced knowledge.
- Use `attention-design-review` when situation-awareness signals exist but are not noticed.
- Use `assumption-audit` to surface implicit assumptions that depend on tribal knowledge.
- Use `formal-invariants` to convert critical conventions into mechanically enforced rules.
- Use `incentive-analysis` when no one updates the artifact because no one is rewarded for doing so.
- Use `code-forensics` after an incident to trace which knowledge gap the failure exposed.
- Use `user-context-fieldwork` when the workflow on paper differs from the workflow in practice.
