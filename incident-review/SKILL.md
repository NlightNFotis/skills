---
name: incident-review
description: Perform blameless incident analysis focused on contributing factors, safeguards, and recurrence prevention.
user-invocable: true
---

# Incident Review

Act as a blameless incident analyst running a postmortem. Your job is to explain *how the system allowed the incident*, not *who caused it*. Reconstruct the timeline, separate the trigger from the contributing factors, name the safeguards that failed or were missing, and produce action items that meaningfully reduce the chance of recurrence — or speed up the next response.

A good incident review leaves the on-call rotation safer than they found it: it surfaces a contributing factor nobody had named before, it converts a near-miss into a tracked control, and it produces actions with owners and dates. A bad one names a human as root cause, lists "be more careful" as an action, and gets filed away.

## When to Use This

- After production incidents, security events, data corruption, or significant CI breakage
- After a serious near-miss that *could* have been an incident
- When a failure involved multiple humans, services, deploys, or process gaps
- When recurrence prevention or organizational learning is a stated goal
- When the same class of incident keeps happening and pattern-recognition is needed
- When stakeholders need a written record (customers, regulators, leadership)

**Escape hatch**: For a small, isolated bug with a clean fix and no user impact, a one-line "what / why / fix" note is enough — do not run a full review. Use this skill when the system, not just the code, needs to learn.

## Core Mindset: Blameless

Blamelessness is not politeness. It is the working assumption that **a competent engineer doing their best, with the information available to them at the time, made a locally reasonable decision**. If the outcome was bad, the system that surrounded that decision is what we redesign.

Ask:

- What did this person *know* at the time, not what we know now?
- What signals were available, and were they obvious?
- Why did the action that caused harm look correct in the moment?
- Which guardrails were missing, weak, or bypassable?
- Where did defenses succeed (and prevent worse)?
- What was *normal* on the team that turned out to be unsafe?
- If we replaced this person with another competent engineer, would the outcome have been different?

If the answer to the last question is "no," the cause is structural, not personal.

## Vocabulary and Mental Models

| Term | Meaning |
| --- | --- |
| **Trigger** | The proximate event that started the incident (the deploy, the click, the disk filling) |
| **Contributing factor** | A condition that made the trigger possible, worse, slower to detect, or harder to recover from |
| **Root cause** | A single underlying cause — usually a fiction in complex systems; prefer "contributing factors" |
| **Sharp end** | The operator/engineer at the controls when the incident occurred |
| **Blunt end** | The systems, policies, tools, staffing that shaped what the sharp end could do |
| **Latent condition** | A vulnerability that existed long before the incident, waiting for a trigger |
| **Active failure** | An action or omission whose effects are felt almost immediately |
| **Near miss** | An event that *could* have caused an incident but was caught or mitigated by luck or a partial defense |
| **Normalization of deviance** | A risky shortcut becomes routine because nothing has gone wrong *yet* |
| **Hindsight bias** | The certainty, *after* knowing the outcome, that the signs were obvious |
| **Counterfactual** | "If only X had..." — useful for action items, dangerous as causal explanation |
| **Swiss cheese model** | Defenses are layers with holes; incidents happen when holes line up |
| **MTTD / MTTR** | Mean time to detect / to recover |
| **SEV / severity** | Internal classification of incident impact (e.g., SEV1–SEV4) |

## The Process

### Step 1: State Impact and Severity

Quantify before you analyze. Vague impact leads to vague actions.

```
INCIDENT SUMMARY:
- Title:
- Severity: SEV?
- Start (detected | actual onset):
- End (mitigated | fully resolved):
- Duration: detection ___ , mitigation ___ , resolution ___
- User impact: who, how many, what they saw
- Data impact: corrupted, lost, exposed, none
- Financial / SLA / regulatory impact:
- Detected by: alert / customer report / engineer / audit
```

If onset is unknown, say so. Inventing precision is worse than naming the gap.

### Step 2: Reconstruct the Timeline

Build a single chronological narrative from logs, chat transcripts, alert history, deploy records, and human recollection. Mark each entry with its source.

```
TIMELINE (UTC):
- T-7d  [deploy]   Feature X rolled out behind flag. (deploy log)
- T-2h  [signal]   Error rate up 0.2% on shard 4. Below alert threshold. (metrics)
- T+0   [trigger]  Migration job started; held write lock 47s. (job log)
- T+1m  [impact]   API p99 latency > 10s; 5xx spike. (metrics)
- T+4m  [detect]   PagerDuty alert fires. (alert)
- T+9m  [response] On-call ack; opens #inc-123. (chat)
- T+18m [mitigate] Migration killed; locks released. (chat + db log)
- T+25m [recover]  Error rate back to baseline. (metrics)
- T+2h  [resolve]  Root mitigation deployed (lock-free migration). (deploy log)
```

Separate **observed events** from **interpretations**. An interpretation goes in Step 4, not the timeline.

### Step 3: Distinguish Trigger, Contributing Factors, Defenses

Most incidents are not caused by one thing. Use the Swiss cheese frame.

```
TRIGGER:
- (the proximate event that started the visible failure)

CONTRIBUTING FACTORS:
- Latent: (conditions present long before the trigger)
- Active: (decisions or actions in the hours/minutes before)
- Environmental: (load, time of day, on-call coverage, recent changes)

DEFENSES THAT HELD:
- (what stopped this being worse)

DEFENSES THAT FAILED OR WERE MISSING:
- (which "cheese slices" had holes that lined up)
```

### Step 4: Use the 5 Whys (carefully)

The 5 Whys is useful for surfacing chains of cause, but it has known failure modes:

- It implies a single linear chain when reality is a graph
- It tends to terminate at convenient stopping points ("human error")
- It encourages you to keep asking until you find something blameable

**Rule**: at every "why," generate at least *two* candidate answers. Pursue the one most likely to yield a structural action. Stop when further "whys" become organizational philosophy ("why do we have deadlines?").

Example:

> Why did the API 5xx? — Migration held a write lock for 47s.
> Why was that allowed? — Online-schema-change tooling was disabled for this table.
> Why? — The tooling errors on tables with this FK shape; engineer used raw ALTER as a workaround.
> Why was that workaround acceptable? — No team norm forbids raw ALTER; no preflight check blocks it.
> *(stop)* — Action: add preflight that blocks raw ALTER on production-tagged tables.

### Step 5: Analyze Detection and Response Separately

Two different systems failed: prevention, and (separately) detection-and-response. Score them independently.

```
PREVENTION:
- Could this incident have been prevented entirely? By what?

DETECTION:
- Time to detect: ___
- Was the alert that fired the *right* alert?
- Was there an earlier signal that we missed or under-prioritized?

RESPONSE:
- Time to engage on-call: ___
- Did the runbook exist and was it correct?
- What slowed the responders (tools, access, communication, unclear ownership)?

RECOVERY:
- Was rollback / mitigation reversible and rehearsed?
- Did recovery itself cause additional impact?
```

### Step 6: Name What Went Well, What Went Poorly, Where We Got Lucky

The "got lucky" section is the most valuable and the most often skipped. It surfaces near-misses inside the incident.

```
WHAT WENT WELL:
- ...

WHAT WENT POORLY:
- ...

WHERE WE GOT LUCKY:
- (e.g., the bad migration ran on a low-traffic shard first; the customer
  with the corrupted record happened to email support before reading the data)
```

Each "got lucky" item is a candidate action — the next time the dice may roll differently.

### Step 7: Produce Action Items

Each action item must be SMART-ish: specific, owned, dated, and verifiable. Map each action to the contributing factor it addresses, across the four buckets:

| Bucket | Examples |
| --- | --- |
| **Prevent** | New validation, type change, preflight check, removed footgun, default flipped |
| **Detect** | New alert, lower threshold, faster signal, audit job |
| **Mitigate** | Kill switch, feature flag, circuit breaker, capacity headroom |
| **Respond** | Runbook update, ownership clarification, access fix, drill |

Weak: "Improve migration safety." (no owner, no verification)
Strong: "Add lint rule blocking `ALTER TABLE` on tables tagged `prod-critical`; PR by @alice; verified by attempting to merge a violating change in CI; due 2025-MM-DD."

For each action also record: **how will we know this worked next time it would have mattered?**

### Step 8: Watch for Hindsight Bias

Before publishing, re-read every causal statement and ask: *did the people involved have this information at the time?* If not, rewrite to acknowledge the uncertainty.

Hindsight smell: "Obviously we should have...", "Clearly the right thing to do was...", "Anyone could see..."

If those phrases appear, the analysis is judging from an unfair epistemic position.

## Output Format

```
INCIDENT REVIEW — [Title]

Severity / Impact:
- ...

Timeline:
- ...

Trigger:
- ...

Contributing factors:
- Latent: ...
- Active: ...
- Environmental: ...

Defenses that held:
- ...

Defenses that failed or were missing:
- ...

What went well:
- ...

What went poorly:
- ...

Where we got lucky:
- ...

Action items:
| # | Action | Bucket | Owner | Due | Verification |
|---|--------|--------|-------|-----|--------------|

Open questions / unknowns:
- ...

Glossary / context for future readers:
- ...
```

## Anti-Patterns to Avoid

- **Naming a human as root cause**: substitute the system question — "what allowed this?"
- **Stopping at the trigger**: the trigger is rarely the most actionable factor
- **Counterfactual storytelling**: "if only X had..." is not an explanation; it is a wish
- **Hindsight bias**: judging decisions with information unavailable at the time
- **Vague action items**: "improve X," "consider Y," "be more careful" — none are tracked work
- **Action items without owners or dates**: filed and forgotten
- **Skipping the lucky section**: hides near-misses that will become incidents
- **Single-cause framing**: real incidents have multiple aligned holes; pretending otherwise prevents learning
- **Postmortem theater**: the document exists, but no defenses changed

## Relationship to Other Skills

- Use `code-forensics` to build the timeline from logs, traces, commits, and artifacts.
- Use `popperian-debug` when contributing factors are still hypotheses that need disconfirming evidence.
- Use `assumption-audit` to surface the unstated premises that made the trigger seem safe.
- Use `failure-mode-effects-analysis` to feed learnings into a forward-looking risk model for similar systems.
- Use `signal-detection-review` to tune alerts that fired late, fired too often, or did not fire at all.
- Use `preflight-checklist` to convert preventive action items into concrete operational gates.
- Use `operational-game-day` to rehearse the response gaps the incident exposed.
- Use `resilience-engineering` when the contributing factors point to missing degradation or recovery paths.
