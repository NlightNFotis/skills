---
name: reverse-engineering
description: Disciplined understanding of opaque systems through black/gray/white-box analysis, behavioral characterization, golden references, and differential analysis — separating observed behavior from inferred contract.
user-invocable: true
---

# Reverse Engineering

Act as a reverse engineer staring at a system whose internals are unavailable, unreliable, or untrustworthy. Your job is to derive a workable model of how the system behaves from the outside, distinguishing what you have *observed* from what you have *inferred*, and resisting the urge to assume intent where you have only seen output.

The goal is to produce a behavioral characterization solid enough to build, debug, integrate, or replace against — without conflating "I saw it do this once" with "this is the contract." A successful reverse-engineering pass yields a golden reference, a documented boundary, and a decision about whether to keep extending the analysis or to rewrite from spec.

## When to Use This

- Working with legacy code whose author is gone and whose tests are absent
- Integrating against a third-party API whose docs lie, lag, or omit edge cases
- Debugging a closed-source binary, vendored library, or compiled tool you cannot read
- Characterizing an internal service that has no spec, only a running instance
- Planning a clean-room reimplementation of a component for license, compliance, or replatform reasons
- Validating that a refactor preserved behavior when no behavioral spec exists
- Investigating a system you inherited where docs and code disagree

**Escape hatch**: If you have a clear spec and source access, do not reverse-engineer — just read it. Use this skill when you must derive understanding from outside, or where existing documentation cannot be trusted.

## Core Questions

Ask:

- What is the boundary of the system I am studying — where do inputs go in and outputs come out?
- What can I observe directly, and what am I inferring?
- What is *contract* (guaranteed by the producer) versus what is *coincidence* (true today but not promised)?
- What is the cheapest probe that distinguishes between two competing models?
- Do I have a golden reference (known-good input/output) I can compare against?
- Am I assuming intent? Strip the assumption and re-examine the evidence.
- When do I stop? At what point is rewriting cheaper than continuing to characterize?
- Are there legal constraints (license, terms of service, clean-room obligations) on how I do this?

## Levels of Access

| Level | What you can see | Typical methods |
| --- | --- | --- |
| **Black-box** | Inputs and outputs only | Probing, fuzzing, behavioral characterization, latency timing |
| **Gray-box** | Some internals: logs, metrics, error messages, version strings | Log analysis, error-message taxonomy, telemetry inspection |
| **White-box** | Full source, symbols, or decompilation | Code reading, static analysis, instrumentation |
| **Translucent** | Encrypted/obfuscated but you control the runtime | Tracing syscalls, network capture, debugger attach |

Match your method to your access level. Black-box claims should not depend on assumed internals.

## Domain Vocabulary

| Term | Meaning |
| --- | --- |
| **Tear-down** | Disassembling a system to inspect its parts |
| **Bill of Materials (BoM)** | Enumerated list of components/dependencies the system is built from |
| **Signal tracing** | Following an input through the system to where it appears as output |
| **Boundary identification** | Determining where one component ends and the next begins |
| **Interface inference** | Deriving the API/protocol from observed traffic or calls |
| **Behavioral characterization** | Mapping inputs to outputs across the relevant input space |
| **Golden reference** | A known-good input/output pair (or set) used as the truth oracle |
| **Differential analysis** | Comparing two implementations or two versions to isolate behavior |
| **Provenance** | Where a piece of behavior or data originated |
| **Clean-room reimplementation** | Two-team pattern: one team specifies behavior; a second team implements from spec only, without seeing the original — for license/compliance defensibility |
| **Observed behavior vs contract** | What it does today vs what it promises to keep doing |

## The Process

### Step 1: Define the Target and Access Level

```
TARGET:
- System under study:
- Why I need to understand it:
- Access level (black/gray/white/translucent):
- Inputs I can control:
- Outputs I can observe:
- What I am NOT trying to learn (out of scope):
- Legal/license constraints:
```

A reverse-engineering effort without a stop condition expands forever. Constrain it.

### Step 2: Establish a Golden Reference

Before characterizing, capture at least one input/output pair you trust as correct.

- Production traffic samples with known-good responses
- Test fixtures from the existing system (if any)
- Vendor-provided examples
- The system's own behavior on canonical inputs in a controlled environment

Without a golden reference, you cannot tell whether an observed behavior is correct, buggy, or environmental.

### Step 3: Identify Boundaries and BoM

Map the system's external surface and known parts.

- What processes, files, sockets, env vars, secrets, data stores does it touch?
- What dependencies does it ship with (BoM): libraries, binaries, models, configs, fonts, certificates?
- What versions? What hashes? Provenance of each?

For black-box systems, even network capture (`tcpdump`, proxy, eBPF) and process inspection (`lsof`, `strace`, `ltrace`) reveal a partial BoM.

### Step 4: Probe Behaviorally

Design probes to characterize behavior across the input space. Be systematic:

- **Identity probes**: send canonical inputs, confirm canonical outputs (verifies environment)
- **Boundary probes**: empty, null, max-size, max-int, negative, unicode, malformed
- **Ordering probes**: same inputs in different orders, concurrently, with delays
- **State probes**: does the same input twice produce the same output? After restart? After idle time?
- **Error probes**: deliberately invalid inputs — error message taxonomy is highly informative
- **Differential probes**: same input to two versions, two implementations, two configurations

Record probes in a table:

```
| Probe | Input | Expected (hypothesis) | Observed | Match? | Inference |
```

### Step 5: Distinguish Observation from Inference

This is the discipline that separates reverse engineering from speculation.

- **Observed**: I sent X and got Y, here is the recording.
- **Inferred**: from N observations, I generalize that behavior B holds.
- **Assumed**: I have not tested it, but I believe behavior C holds because of D.

Tag every claim. When you write a model of the system, mark each statement with its evidentiary basis.

Weak:

> The API returns the user object on success.

Strong:

> Observed (12 calls, 3 environments): on HTTP 200, response body contains a JSON object with at least the fields `id`, `email`, `created_at`. Inferred: these fields are stable. Assumed: ordering of fields is not significant.

### Step 6: Differential Analysis

When two implementations or versions exist, diff their behavior, not their code.

- Replay the same input set against both
- Diff the outputs structurally (not as text — semantic diff)
- For each divergence: is it a bug in one, a deliberate change, or an undocumented degree of freedom?

Differential analysis is how you discover that "the contract" is actually three subtly different behaviors across versions, regions, or accounts.

### Step 7: Build the Model and Mark Confidence

Produce a written model of the system's behavior with confidence levels.

```
BEHAVIORAL MODEL
- Component: ...
- Inputs: ...
- Outputs: ...
- State: ...
- Behavior rules:
  1. [statement] — confidence: high / medium / low — basis: observed N times / inferred / assumed
- Known unknowns:
  - ...
- Known divergences from documentation:
  - ...
```

Low-confidence rules are *hypotheses to test next*, not facts to build on.

### Step 8: Decide — Continue, Replace, or Clean-Room

At each iteration, ask whether continuing reverse engineering is the right next step.

| Situation | Action |
| --- | --- |
| Model is good enough for the integration/debug task | Stop. Document. Move on. |
| Behavior is too inconsistent to characterize cheaply | Reconsider whether to depend on it at all |
| Cost of further probing > cost of rewriting | Rewrite from the model you have |
| Need legal defensibility (license, IP) | Switch to clean-room: spec team writes the model, separate impl team builds from the spec only |
| Behavior keeps surprising you with each probe | Your model is wrong — restart Step 5, do not patch |

The discipline of stopping is as important as the discipline of probing. Reverse engineering can become a hobby that displaces shipping.

## Output Format

```
REVERSE ENGINEERING REPORT

Target and access level:
- ...

Golden reference:
- ...

Bill of materials (observed):
- ...

Behavioral model:
- Rules with confidence and basis:
  1. ...

Differential findings (if applicable):
- ...

Known unknowns / risks:
- ...

Decision:
- Continue probing / Sufficient for task / Rewrite / Clean-room reimplement
- Rationale:

Next probes (if continuing):
1. ...
```

## Anti-Patterns to Avoid

- **Conflating observation with contract**: "it does this today" is not the same as "it promises to do this"
- **Assuming intent**: explanations about *why* the system behaves this way are speculation unless sourced
- **Single-sample generalization**: one observation is a data point, not a rule
- **Patching the model when probes surprise you**: surprise means the model is wrong; rebuild it instead of bolting on exceptions
- **Reading the code and calling it reverse engineering**: white-box reading is fine, but mark which claims are observed vs inferred from reading
- **Ignoring environment**: same binary behaves differently across OS, locale, time zone, version, network — characterize the environment too
- **Skipping the golden reference**: without a truth oracle, every observation is unanchored
- **Reverse engineering forever**: not deciding when to stop is a failure mode; budget the effort
- **Ignoring legal constraints**: clean-room exists for a reason; understand license and ToS before probing third-party systems

## Relationship to Other Skills

- Use `code-forensics` for *post-incident timeline reconstruction* from logs, commits, and traces — that is about *what happened*. This skill is about *how the system works* in steady state.
- Use `assumption-audit` to classify which parts of your reverse-engineered model are observed, inferred, or assumed, and to surface unsafe assumptions.
- Use `formal-invariants` to turn high-confidence behavioral rules into checkable invariants once the model stabilizes.
- Use `differential-diagnosis-debugging` when probing has produced multiple competing models and you need to choose among them.
- Use `semantic-precision` to nail down terminology when the system uses words ambiguously (and reverse-engineered systems almost always do).
