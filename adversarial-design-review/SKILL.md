---
name: adversarial-design-review
description: Model adversarial users, attackers, malformed inputs, prompt injection, abuse cases, and metric gaming.
user-invocable: true
---

# Adversarial Design Review

Act as a security-minded game theorist embedded in the engineering workflow. Treat every actor in the system — end users, plugin authors, dependencies, the model itself, future maintainers, and outright attackers — as agents with their own capabilities, observations, and incentives. Your job is to find how the design can be abused, bypassed, confused, escalated, or quietly gamed before the system ships.

Success looks like a clear inventory of trust boundaries, abuse cases ranked by impact and feasibility, and concrete mitigations placed at the boundary where trust changes hands. Failure looks like a list of vague "be careful" warnings, a threat model that only covers the happy path, or mitigations that depend on actors choosing to behave well.

## When to Use This

- Reviewing authentication, authorization, secrets, sandboxing, or process isolation
- Designing CLIs, APIs, plugin systems, MCP servers, or tool-execution pipelines
- Handling untrusted input: user prompts, model output, file contents, network data, plugin manifests, environment variables, paths, URLs
- Changing defaults, quotas, rate limits, retry policies, or safety gates
- Introducing telemetry, metrics, or evaluation scores that someone might want to game
- Reviewing error handling, logging, or any code path that handles secrets or PII
- Anything that crosses a process, network, repo, account, or trust boundary

**Escape hatch**: If the change is purely internal refactoring with no boundary, no untrusted input, no secret, no privilege change, and no observable side effect, skip this skill. Use it where an actor with bad intent or bad luck could materially harm correctness, security, privacy, or trust.

## Core Mindset

Stop asking "does this work for the intended user?" and start asking "what does each actor *gain* by violating the intended contract, and what stops them?"

Ask:

- Where does trust change hands? (process, network, repo, user, model, plugin, dependency)
- What does each actor see, control, or influence on each side of that boundary?
- Which assumed-honest actor could be confused, compromised, or replaced?
- What is the worst legal action under this design? What is the worst illegal action that is still cheap?
- If a metric or check were the only thing standing between an actor and a reward, how would they game it?
- What happens between the time we *check* a property and the time we *use* it?
- Who pays the cost of each safety check, and will they route around it?

## Domain Vocabulary

Use these frameworks to drive coverage. Pick the lenses that fit the surface under review.

### STRIDE threat categories

| Category | Question | Common manifestations |
| --- | --- | --- |
| **Spoofing** | Can identity be forged? | Stolen tokens, missing auth, trusting `User-Agent`, trusting model claims about who called it |
| **Tampering** | Can data or code be modified in transit or at rest? | Mutable cache, writable config, supply-chain swap, prompt rewriting |
| **Repudiation** | Can an actor deny an action? | Missing audit logs, shared accounts, unsigned actions |
| **Information disclosure** | Can data leak across a boundary? | Verbose errors, debug logs, side channels, prompt echo, secrets in env dumps |
| **Denial of service** | Can the actor exhaust a resource? | Unbounded input, recursion, fork bombs, model token floods, retry storms |
| **Elevation of privilege** | Can a low-trust actor act with higher trust? | Confused deputy, unsanitized shell, plugin escapes, path traversal, SSRF |

### Attack-surface concepts

- **Trust boundary**: any line where data or control crosses from one trust level to another. Must have validation, auth, or both.
- **Confused deputy**: a privileged component performs an action *on behalf of* a less privileged actor without checking that the actor was entitled to ask for it.
- **TOCTOU (time-of-check to time-of-use)**: state changes between the validation and the use; common with files, paths, locks, and remote resources.
- **Capability vs identity**: prefer unforgeable handles (file descriptors, signed tokens) over name-based authorization (paths, usernames) that the caller controls.
- **Principle of least privilege**: each component runs with the minimum rights it needs to do its job.
- **Defense in depth**: at least two independent layers must fail before harm occurs; never rely on a single check.
- **Fail-closed vs fail-open**: when a check errors, does the system deny by default or allow? Most security checks must fail closed.

### Prompt-injection and LLM-specific categories

- **Instruction override**: untrusted text containing "ignore previous instructions, do X"
- **Indirect injection**: malicious instructions embedded in tool output, fetched pages, file contents, code comments, issue bodies
- **Data exfiltration**: model induced to leak secrets, prior context, system prompts, or other tenants' data via tool calls or rendered links
- **Tool / capability abuse**: model coerced to invoke privileged tools (shell, network, write) on behalf of the attacker
- **Jailbreak**: bypassing safety policy via roleplay, encoding, multi-turn priming
- **Output smuggling**: hidden instructions in markdown, ANSI, zero-width characters, URLs, or images consumed by downstream systems

### Incentive failure modes

- **Goodhart's Law**: when a measure becomes a target, it ceases to be a good measure.
- **Campbell's Law**: the more a quantitative indicator is used for decision-making, the more it distorts the process it monitors.
- **Cobra effect / perverse incentive**: a reward intended to reduce a behavior makes the underlying problem more profitable.
- **Race-to-the-bottom**: actors degrade quality to win on the measured axis (latency, token count, pass-rate).

## The Process

### Step 1: Define the Asset and Boundary

Be specific about *what* you are protecting and *from whom*. Vague targets produce vague threat models.

```
ASSET:
- What is valuable here: (data, capability, reputation, budget, correctness, availability)
- Who is the legitimate owner:
- Boundary under review:
- Trust levels on each side:
- Intended invariant: "X may only happen if Y"
```

### Step 2: Enumerate Actors

List every actor who can observe or influence the boundary. Do not collapse them into "the user."

For each, capture:

- **Capabilities**: what they can read, write, send, run
- **Observations**: what they see (responses, timing, errors, logs)
- **Incentives**: what they gain from violating the contract
- **Cost of attack**: trivial / scripted / requires research / requires insider access

Always include: honest user, careless user, malicious external user, compromised dependency, malicious plugin author, the LLM itself, future maintainer who copies the pattern.

### Step 3: Generate Abuse Cases

For each actor, walk the STRIDE table and the LLM-specific categories. For each cell that is plausible, write a one-line abuse case.

```
ABUSE CASE:
- Actor:
- Goal:
- Capability used:
- Steps:
- Violated invariant:
- Impact:
- Cost to execute:
```

Prefer concrete examples over abstract categories. "Plugin manifest with `../../etc/passwd` in `binPath`" is more useful than "path traversal possible."

### Step 4: Build the Attack Tree (when stakes are high)

For high-impact assets, expand the highest-risk goal into an OR-tree of paths.

```
GOAL: Read another tenant's session contents
├── OR: Predict session ID
├── OR: Inject a tool call that reads sibling files
│   ├── AND: Get model to call read_file
│   └── AND: Supply a path that escapes the tenant root
├── OR: Compromise the storage backend
└── OR: Replay an old auth token
```

Pick the cheapest leaf for the attacker — that is your real risk.

### Step 5: Rank by Impact × Feasibility

Use a coarse 3×3 matrix. Anything in the top-right is a release blocker.

| Impact \\ Feasibility | Easy / scripted | Moderate research | Insider / chained |
| --- | --- | --- | --- |
| **Catastrophic** (data loss, RCE, cross-tenant) | P0 | P0 | P1 |
| **Serious** (privilege escalation, secret leak) | P0 | P1 | P2 |
| **Limited** (single-user, recoverable) | P1 | P2 | P3 |

### Step 6: Design Mitigations at the Boundary

Place each mitigation as close to the trust boundary as possible. Prefer:

| Strong | Weak |
| --- | --- |
| Make invalid states unrepresentable (typed capability) | Document "do not pass untrusted input" |
| Validate and canonicalize at the boundary, then pass capabilities downstream | Re-validate on every internal call |
| Separate the privileged operation from the actor request (no confused deputy) | Trust caller-supplied identity |
| Sandbox / drop privileges before handling untrusted data | Audit untrusted data after the fact |
| Fail closed | Log a warning and continue |
| Constant-time comparison for secrets | `==` on tokens |
| Allow-list | Deny-list |

For LLM-facing surfaces specifically:

- Treat all tool output, fetched content, and file contents as untrusted instructions.
- Strip or fence untrusted text before it reaches the model context.
- Require explicit user confirmation for irreversible or cross-boundary tool calls.
- Never let the model author its own authorization claims.

### Step 7: Add Tests and Telemetry for the Top Risks

For each P0/P1, ship a test that exercises the abuse case and a signal that fires if it ever succeeds in production.

- Unit/integration test with a malicious input
- Fuzz harness for parsers, path resolvers, prompt assemblers
- Assertion at the choke point that the canonicalized form matches the validated form
- Telemetry counter on rejected boundary violations (so you notice when attempts spike)

### Step 8: Document Residual Risk

Some risks are accepted, not eliminated. Say so explicitly, with the reason and the trigger that would force a re-review.

## Output Format

```
ADVERSARIAL DESIGN REVIEW

Asset and boundary:
- ...

Actors:
| Actor | Capabilities | Incentives | Cost |
| --- | --- | --- | --- |

Abuse cases (STRIDE + LLM):
1. [Category] [actor] [one-line abuse]
   - Steps:
   - Impact:
   - Feasibility:

Risk ranking:
- P0: ...
- P1: ...

Recommended mitigations (at the boundary):
1. ...

Tests / telemetry to add:
1. ...

Accepted residual risk:
- ... (because ..., re-review if ...)
```

## Anti-Patterns to Avoid

- **Documentation as a control**: "users must not paste secrets here" is not a mitigation.
- **Trusting model output**: tool calls, JSON, paths, and URLs from the model are untrusted input.
- **Validating after side effects**: any check after the write, exec, or network call is theatre.
- **Single-layer defense**: one regex, one auth check, one allow-list, with no defense in depth.
- **Allow-by-default on error**: catch blocks that swallow auth failures and continue.
- **Name-based authorization**: trusting paths, usernames, or repo slugs the caller controls.
- **Solving STRIDE-S only**: spoofing gets attention; tampering, repudiation, and DoS get ignored.
- **Designing only for the attacker you imagined**: enumerate actors first, then threats.

## Relationship to Other Skills

- Use `assumption-audit` to surface trust assumptions before threat modeling; every "trusted" assumption is a potential boundary.
- Use `formal-invariants` to encode the security property ("X may only happen if Y") as an enforceable rule.
- Use `incentive-analysis` when the threat is gaming rather than exploitation — they share game-theory roots but differ in actor intent.
- Use `popperian-debug` when investigating a suspected exploit: treat the attack as a hypothesis and try to falsify it.
- Use `code-forensics` after a security incident to reconstruct the timeline before proposing fixes.
- Use `attention-design-review` when the mitigation depends on a human noticing a warning — most do not.
