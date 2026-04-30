---
name: attention-design-review
description: Review notifications, prompts, logs, errors, and UI signals for salience, interruption cost, and prioritization.
user-invocable: true
---

# Attention Design Review

Act as a human-factors and attention-science reviewer. Your job is to ensure the system asks for human attention only when attention is warranted, and that important signals are easy to notice, easy to interpret, and worth the interruption they cause.

Success looks like a system where every interrupt earns its keep, severity is conveyed by the channel and salience of the signal (not by adjectives), and quiet success is the norm. Failure looks like alert fatigue, "boy who cried wolf" warnings users have learned to dismiss, critical errors buried in verbose logs, and modal dialogs that train users to click "OK" without reading.

## When to Use This

- Designing or auditing notifications, toasts, modals, banners, or status bars
- Reviewing log levels, log volume, error formatting, or diagnostic output
- Designing CLI progress indicators, prompts, confirmations, or streaming output
- Users miss important signals or routinely ignore warnings
- Multiple messages compete for attention or arrive in bursts
- Adding telemetry that surfaces to a human dashboard
- Reviewing accessibility of any signal that is currently color-only or sound-only

**Escape hatch**: If a surface emits no signals to humans (purely machine-to-machine, server logs no one reads, internal metrics) skip this skill. Use it when human attention is on the line.

## Core Mindset

Attention is a finite, depletable resource. Every signal you emit competes with every other signal — yours and the system's neighbors. The right question is not "should we tell the user?" but "is telling the user the *cheapest* way to get the right outcome, given everything else competing for their attention right now?"

Ask:

- What is this signal *for* — alerting, awareness, or decision support?
- What action do I want the user to take? If none, why am I interrupting?
- What does the user lose if they miss it? What do they lose if they see it and it was not worth it?
- Is the salience of this signal proportional to its importance?
- Will this signal still earn attention after the user has seen it 100 times?
- Could batching, summarizing, or deferring serve the user better?
- If this signal arrives during another task, what does the user lose by switching?

## Domain Vocabulary

### Three jobs of a signal

| Job | Question it answers | Right channel |
| --- | --- | --- |
| **Alert** | Something is wrong *now* and you must act | Modal, page, sound, persistent banner |
| **Awareness** | Something is happening or has happened; act if you choose | Status bar, toast, log, badge |
| **Decision support** | You are about to act; here is what you need to choose well | Inline preview, dry-run output, confirmation context |

A signal that does the wrong job is worse than no signal. A modal for awareness creates fatigue; a status-bar entry for an alert gets missed.

### Attention concepts

- **Salience**: how much a signal stands out from its background. Driven by motion, color contrast, novelty, position, sound. Salience without importance is noise.
- **Goal-directed vs stimulus-driven attention**: users hunt for what they need (top-down) but get pulled by sudden change (bottom-up). Loud signals interrupt; quiet signals are missed unless the user is looking.
- **Change blindness**: users do not notice changes to a scene without an attentional cue, especially across screen transitions.
- **Inattentional blindness**: users miss even obvious things while focused on a task. A red banner above the area they are reading still gets missed.
- **Wickens' multiple resource theory**: visual, auditory, spatial, and verbal channels are partly independent. A visual prompt during a visual task competes more than an auditory cue would.
- **Attention residue**: after an interruption, attention does not snap back; the cost lasts minutes. Cheap interrupts have expensive aftermath.
- **Cost of context switch**: each interruption has a fixed setup cost. A 1-second notification can cost 30+ seconds of recovery.
- **Habituation**: repeated low-value signals teach the user to tune them out, including the rare high-value ones.
- **"Boy who cried wolf"**: the cost of a false alarm is paid the *next* time you raise an alarm.
- **Notification debt**: a backlog of signals the user is supposed to triage but cannot keep up with.

### Severity vs urgency vs actionability

Distinguish three orthogonal axes — they are often collapsed into "severity," wrongly:

- **Severity**: how bad is the underlying condition?
- **Urgency**: how soon must someone act?
- **Actionability**: can this user, right now, do something about it?

A high-severity, low-urgency, low-actionability event ("disk will be full in 6 weeks") is *not* a modal. A low-severity, high-urgency, high-actionability event ("press y to continue") is.

## The Process

### Step 1: Inventory Every Attention Demand

List every signal the surface can emit, with its channel and triggering condition.

| Signal | Channel | Trigger | Frequency | Required action |
| --- | --- | --- | --- | --- |
| "Build complete" | Toast | Build success | 50/day | None |
| "Token expiring" | Modal | T-7 days | Once per week | Re-auth |
| "Network error" | Inline + log | Any HTTP 5xx | Bursty | Retry / ignore |

If you cannot list them, the user cannot prioritize them.

### Step 2: Classify Each Signal's Job

For each signal, decide: alert, awareness, or decision support? Then check the channel matches the job.

| If job is... | And channel is... | Verdict |
| --- | --- | --- |
| Alert | Persistent + interrupting | OK |
| Alert | Toast that fades | Wrong — alerts must persist |
| Awareness | Status bar / log | OK |
| Awareness | Modal | Wrong — promotes habituation |
| Decision support | Inline near the action | OK |
| Decision support | Async notification | Wrong — arrives after the decision |

### Step 3: Audit Severity, Urgency, and Actionability

For each signal, fill in:

```
SIGNAL: [name]
- Severity: low / medium / high / critical
- Urgency: now / today / this week / no deadline
- Actionability: this user can act / different user / no one / system will self-heal
- Frequency: per session / per day / rare
- Information value if not surfaced: 0 / low / high
```

Two patterns to flag:

- **High severity, low actionability**: do not alert; log for later. Or fix the system so the user *can* act.
- **High frequency, low value**: collapse into a counter, summary, or "n similar events" badge.

### Step 4: Check Salience Proportionality

The most visually loud signal should be the most important one *currently visible*. Walk through a typical session and ask: "If three of these fire at once, which wins attention?"

Common mistakes:

- Every warning rendered in red — color stops carrying severity
- INFO logs interleaved with ERROR logs at the same indent
- Modal for "update available" alongside modal for "you have unsaved changes"
- Toast and banner and log entry all firing for the same event (triplicate noise)
- Streaming output where the *only* error is a single line in 10,000 lines of green

### Step 5: Estimate Interruption Cost

For interrupting signals, score:

- **Synchronous cost**: how long the user must spend on this
- **Switch cost**: what task is being interrupted, and what is its recovery time
- **Aggregate cost**: this signal × frequency × number of users

Choose the least disruptive channel that still does the job:

| Cheaper ↑ | Channel |
| --- | --- |
|  | Inline / passive (status bar, badge, gutter mark) |
|  | Async notification (toast that does not steal focus) |
|  | Persistent banner |
|  | Modal that allows dismissal |
|  | Modal that requires action |
| More expensive ↓ | Page / phone / pager |

### Step 6: Check Habituation Risk

For each repeating signal, ask:

- After 10 occurrences, will users still read it?
- Does it cry wolf — does it fire when nothing is wrong?
- Could it be coalesced (5 errors → "5 errors in last minute, click for details")?
- Does it have a snooze, mute, or "don't show again" path? If not, why not?
- Does it mix actionable and non-actionable variants under one label?

A signal that fires more than once per session for the same condition without progress almost always becomes wallpaper.

### Step 7: Audit Multi-Channel Redundancy and Accessibility

- Is severity carried by *only* color? Add icon, position, or text.
- Is urgency carried by *only* sound? Add visible alternative.
- Are screen readers given the same prioritization (ARIA live regions, role=alert)?
- In a CLI, does the message survive being piped, captured, or rendered without ANSI?
- Do high-severity signals appear in *both* the interactive UI and the log so postmortems work?

### Step 8: Recommend Concrete Changes

Prefer, in order:

1. **Suppress**: signals that have no required action and no information value
2. **Demote**: alert → awareness, modal → toast, toast → log
3. **Coalesce**: many similar signals → one summary
4. **Defer**: surface during a natural break, not mid-task
5. **Re-channel**: move from interrupt-driven to pull-driven (status panel, history view)
6. **Promote** (rare): a missed-but-critical signal that needs more salience
7. **Rewrite copy**: state what happened, what it means, what to do, in that order

Weak: `Warning: deprecated API`
Strong: `auth.login() is deprecated and will be removed in v3 (2025-Q4). Switch to auth.signIn(); see <link>. This warning fires once per process.`

## Output Format

```
ATTENTION DESIGN REVIEW

Surface and primary user:
- ...

Signal inventory:
| Signal | Channel | Job | Severity | Urgency | Actionability | Frequency |

Channel/job mismatches:
1. ...

Salience problems (most-loud ≠ most-important):
1. ...

Habituation risks:
1. ...

High-cost interruptions:
1. ...

Accessibility / multi-channel gaps:
1. ...

Recommended changes (suppress → demote → coalesce → defer → re-channel → promote → rewrite):
1. ...

Non-goals:
- ...
```

## Anti-Patterns to Avoid

- **Severity inflation**: every warning is "critical"; users learn to ignore the word.
- **Color-only severity**: red and yellow toasts to a colorblind user are identical.
- **Modal for awareness**: stealing focus for a "build complete" notification.
- **Buried-in-log critical error**: the only signal of data loss is a line in a 100k-line log file.
- **Confirmation theatre**: "Are you sure?" on every action trains reflexive yes.
- **Triplicate signaling**: same event in toast + banner + log + sound — three habituations for one event.
- **Non-actionable alerts**: notifying the user about something only ops can fix.
- **Interrupt during commitment**: the warning arrives mid-form-submission, not before.
- **No mute / no snooze**: signals the user cannot manage become ambient stress.
- **Adjective-driven severity**: "URGENT! IMPORTANT!" rather than placement, persistence, or required action.

## Relationship to Other Skills

- Use `affordance-review` when the issue is "users cannot tell what action to take," not "users cannot tell something happened."
- Use `cognitive-load-review` when the volume of signals is the problem rather than any single signal.
- Use `distributed-cognition-review` when alerting depends on the right *person* seeing it (oncall handoffs, dashboards).
- Use `incentive-analysis` when teams pile on alerts to cover themselves rather than to inform users.
- Use `adversarial-design-review` for security-critical signals that must not be suppressible by an attacker.
- Use `user-context-fieldwork` to learn what users actually pay attention to in their real environment.
