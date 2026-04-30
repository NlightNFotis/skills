---
name: commissioning-and-decommissioning
description: Apply engineering bring-up and tear-down protocols (FAT, SAT, punchlist, LOTO, mothballing) to service launches and sunsets so systems start clean and end cleanly.
user-invocable: true
---

# Commissioning and Decommissioning

Act as a commissioning engineer responsible for handing a system from construction to operations, and later from operations to disposal. Your job is to design the protocol that brings a service safely into production, and the protocol that retires it without leaving energized debris behind.

The goal is to treat launch and sunset as engineering work with phases, acceptance tests, sign-offs, and dispositions — not as informal "we flipped the switch" events. A successful commissioning ends with a documented, accepted, operations-ready system. A successful decommissioning ends with a system that is verifiably inert and whose remains have a known disposition.

## When to Use This

- Launching a new service, pipeline, integration, or major subsystem to production
- Sunsetting a service, deprecating an API, or removing a feature
- Migrating a workload off a platform that itself will be decommissioned
- Handing a system from a build team to an operations team
- Pausing a system that may need to be restarted later (mothballing)
- Cleaning up after a failed project, abandoned experiment, or acquired codebase
- Auditing what is actually still running versus what is documented as running

**Escape hatch**: For routine deploys of an already-commissioned service, use `preflight-checklist` instead. Use this skill when the *system itself* is being introduced, retired, or transferred — not for repeated operational actions.

## Core Questions

Ask:

- What does "accepted" mean for this system, and who accepts it?
- What must be tested in the factory (dev/staging) versus on site (production)?
- What is the punchlist of known defects we will tolerate at launch, and who owns each one?
- Who operates this after handover, and have they actually agreed to?
- Is "off" the same as "removed"? Could it be restarted by accident?
- Is there a possibility of restart? If so, mothball; if not, decommission fully.
- What energy sources, data, secrets, and dependencies must be isolated before tear-down?
- What do we owe legally, contractually, or environmentally after retirement (data retention, audit logs, customer notice)?

## Domain Vocabulary

| Term | Meaning | Software analogue |
| --- | --- | --- |
| **Pre-commissioning** | Cleaning, flushing, calibration before energizing | Seeding fixtures, schema migration dry-run, secret rotation |
| **FAT (Factory Acceptance Test)** | Vendor-side test before shipment | Staging/CI acceptance against production-like data |
| **SAT (Site Acceptance Test)** | Test in the installed environment | Production smoke + canary with real traffic |
| **Wet commissioning** | Run with real working fluid | Run with real (or shadowed) production traffic |
| **Dry commissioning** | Run without working fluid (mechanical only) | Run with synthetic traffic, no real data |
| **Punchlist** | Defects to resolve before final sign-off | Launch-blocker vs post-launch backlog |
| **Sign-off / handover** | Formal transfer of responsibility | Runbook + on-call rotation + ownership entry |
| **As-built documentation** | What was actually built (vs designed) | Architecture diagram reflecting reality, not the RFC |
| **Decommissioning** | Planned retirement, system removed from service | Deprecate + drain + delete |
| **Demolition** | Physical removal and disposal | Repo archived, infra destroyed, DNS released |
| **Mothballing** | Preserved in inert state for possible restart | Code archived, infra scaled to zero but recoverable |
| **LOTO (Lockout-Tagout)** | Physical isolation before maintenance | Disable credentials, revoke tokens, block deploys |
| **Zero-energy verification** | Confirm no stored energy remains | Confirm no traffic, queues drained, no scheduled jobs |
| **Asset disposition** | What happens to each part (reuse/recycle/scrap) | Code → archive, data → export/delete, infra → release |
| **Abandoned in place** | Left physically but disconnected | Code left in repo but unrouted — usually a smell |

## The Process

### Step 1: Define the System and Its Boundary

Before you can commission or decommission, you must know what *it* is.

```
SYSTEM BOUNDARY:
- Name and purpose:
- Components included:
- Components explicitly excluded:
- Inputs (traffic, data, events, schedules):
- Outputs (responses, writes, side effects):
- Dependencies (upstream/downstream):
- Owners and operators:
```

Vague boundaries cause partial commissioning ("we forgot the cron job") and partial decommissioning ("the queue is still draining into a deleted consumer").

### Step 2: Choose the Protocol — Commissioning, Decommissioning, or Mothballing

| Choice | Use when |
| --- | --- |
| **Commissioning** | New system entering service |
| **Decommissioning (full)** | Retirement is permanent; restart is not anticipated |
| **Mothballing** | Retirement is likely permanent but restart is plausible within a known horizon |
| **Demolition** | Decommissioning plus physical removal of all artifacts (repo, infra, data) |
| **Abandoned in place** | Anti-pattern; choose mothball or demolish instead |

Mothballing is a real option, not a failure of nerve. A mothballed service has explicit preservation instructions: which code, which data snapshot, which secrets vault entry, and the cost/time-to-restore.

### Step 3 (Commissioning): Pre-Commissioning

Before traffic touches the system, perform the equivalent of cleaning and calibration:

- Schema migrations applied to production database against a dry-run snapshot
- Secrets provisioned to the secret store and rotation tested
- Feature flags created in the off position
- Telemetry pipelines verified to receive events end-to-end
- Backups verified to actually restore (a backup that has not restored is a hope)
- Capacity provisioned and load test executed against staging at expected peak
- Runbooks drafted; on-call rotation populated; paging tested

### Step 4 (Commissioning): FAT then SAT

**FAT (Factory Acceptance Test)** — runs in your environment, with synthetic or shadowed inputs, against acceptance criteria written *before* the build:

- Functional criteria (does it do what was specified)
- Non-functional criteria (latency, error rate, resource budget)
- Failure-mode criteria (does it degrade as designed under dependency loss)

**SAT (Site Acceptance Test)** — runs in production, typically as a canary or dark launch:

- Real traffic, real dependencies, real secrets
- Comparison against the incumbent system if one exists (differential SAT)
- Defined rollback trigger and rollback rehearsal

A FAT pass without a SAT pass is not commissioning — it is hope. Do both.

### Step 5 (Commissioning): Punchlist and Sign-Off

Generate a punchlist of known defects. Classify each:

```
PUNCHLIST ITEM:
- Description:
- Severity:
- Blocks sign-off? (yes/no)
- Owner:
- Target resolution date:
- Workaround in place:
```

Sign-off requires:

1. Acceptance criteria met (or explicit waiver, signed)
2. Punchlist items either resolved or accepted with owners
3. As-built documentation matches reality
4. Operations team has acknowledged ownership in writing (runbook merged, on-call updated, alert routes set)

Until sign-off, the build team owns the pager. After sign-off, operations does. There is no ambiguous interregnum.

### Step 6 (Decommissioning): Drain, Isolate, Verify Zero-Energy

Software decommissioning mirrors industrial LOTO:

1. **Announce deprecation** — notify users, partners, downstream services, with a date
2. **Stop new traffic** — remove from service discovery, return deprecation headers, update docs
3. **Drain in-flight work** — let queues, jobs, sessions finish; set a deadline
4. **Lockout** — revoke credentials, disable deploy pipelines, remove from CI, lock the repo
5. **Tagout** — label every remaining artifact with retirement status and contact
6. **Zero-energy verification** — confirm no traffic, no scheduled jobs, no consumers, no alerts firing, no reads against the data store

Skipping LOTO produces *zombie services*: things technically retired but quietly running because a forgotten cron, a cached DNS entry, or an internal client never got the memo.

### Step 7 (Decommissioning): Asset Disposition

For every asset, decide its disposition explicitly:

| Asset type | Disposition options |
| --- | --- |
| Source code | Archive repo (read-only), delete, transfer ownership |
| Data | Export to long-term store, anonymize, delete (with proof), retain for legal hold |
| Infrastructure | Destroy (terraform destroy), release reserved capacity, return to pool |
| Secrets | Revoke, delete from vault, rotate any shared credentials |
| Domains / DNS | Release, redirect permanently, retain to prevent takeover |
| Documentation | Mark deprecated with link to successor, archive, delete |
| Monitoring / alerts | Delete dashboards, remove alert routes, decommission synthetics |
| Contracts / vendors | Cancel, renegotiate, transfer |

"Abandoned in place" is the absence of a disposition decision. Treat it as a defect.

### Step 8: Produce As-Built / As-Removed Documentation

Whether commissioning or decommissioning, the final artifact is documentation that reflects reality:

- **As-built**: the system as it actually exists at handover, including deviations from design and accepted punchlist
- **As-removed**: confirmation of what was decommissioned, what was preserved (mothball), and where the dispositioned assets went

This document is the only durable evidence that the work was done.

## Output Format

```
COMMISSIONING / DECOMMISSIONING PLAN

Mode: commission | decommission | mothball | demolish

System boundary:
- ...

Protocol phases:
1. ...
2. ...

Acceptance criteria (commission) / Exit criteria (decommission):
- ...

Punchlist (commission) / Open obligations (decommission):
1. ...

LOTO / isolation steps (decommission):
- ...

Asset disposition table:
- ...

Sign-off / handover:
- Accepting owner:
- Date:
- As-built / as-removed doc location:

Risks and explicit waivers:
- ...
```

## Anti-Patterns to Avoid

- **Soft launch as the whole plan**: shipping without acceptance criteria or sign-off; nobody knows when "launched" became true
- **Punchlist creep**: treating every found defect as a launch blocker, or treating none as blockers
- **Handover by silence**: assuming operations owns it because the build team stopped working on it
- **"Off" mistaken for "removed"**: scaling to zero is not decommissioning; the artifact, credentials, and DNS still exist
- **Skipping LOTO**: deleting the service before draining traffic produces user-visible failures and ghost alerts
- **Abandoned in place**: leaving code, data, infra, or DNS undecided is a future incident waiting to happen
- **Mothball without preservation plan**: "we might restart it" with no snapshot, no docs, and rotated secrets means it cannot be restarted
- **As-built that matches the design instead of reality**: documentation is worthless if it lies

## Relationship to Other Skills

- Use `preflight-checklist` for per-action verification *within* an already-commissioned system; this skill is for the system itself entering or leaving service.
- Use `mise-en-place` for staging the workspace and tools immediately before a task; commissioning is at a larger scope and longer horizon.
- Use `pickling-and-preservation` for long-term archival of artifacts produced during decommissioning (the disposition itself); this skill decides *that* preservation happens, `pickling` decides *how*.
- Use `failure-mode-effects-analysis` to inform acceptance criteria and the punchlist (which failure modes block sign-off).
- Use `operational-game-day` to validate that handover to operations actually works under stress, not just on paper.
