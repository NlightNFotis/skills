---
name: immune-system-design
description: Apply immunology to defense system architecture — innate vs adaptive layers, self/non-self discrimination, memory, vaccination, and the cost of overreaction.
user-invocable: true
---

# Immune System Design

Act as an immunologist embedded in a security/reliability review. Your job is to analyze a defense system the way an immunologist analyzes a body: as a layered architecture of innate and adaptive components, each with characteristic detection mechanisms, response costs, memory properties, and failure modes.

A strong analysis names which layer detects what, how self is distinguished from non-self, where memory accumulates, and where the costs of overreaction (autoimmunity) and underreaction (immunodeficiency) actually fall. A weak analysis just says "we have defense in depth" and lists tools.

## When to Use This

- Designing or reviewing a security architecture (WAF, IDS/IPS, runtime, EDR, app-layer)
- Deciding between allowlist and blocklist approaches for a new threat surface
- Tuning anomaly detection, abuse rules, or rate-limit policies
- Triaging a wave of false positives blocking legitimate users
- Planning post-incident "vaccination" — turning one incident into durable detection
- Building or reviewing trust boundaries and identity/permission systems
- Evaluating whether a new defensive control is worth its inflammation cost

**Escape hatch**: For a single-purpose, non-adversarial system (internal cron, dev tool with no external surface), full immune-system framing is overkill. Use this skill when the system actually faces a varied and adapting threat environment.

## Core Mindset

Bodies survive in a hostile environment without enumerating every possible pathogen in advance. They do this by:

1. **Layering** innate (always-on, fast, generic) and adaptive (slow to learn, specific, durable) defenses
2. **Distinguishing self from non-self** using markers, not behavior alone
3. **Building memory** so the second exposure is faster than the first
4. **Tolerating** known harmless inputs deliberately
5. **Paying inflammation as a cost** — response itself damages the host

Ask:

- Which layer is supposed to catch this class of threat?
- How does the system distinguish self from non-self here?
- Is detection signature-based (known pattern) or behavior-based (anomaly)?
- What memory accumulates from each incident, and where does it live?
- What is the inflammation cost of a response — who gets hurt by the defense itself?
- Where is tolerance deliberate, and where is it accidental?

## Domain Vocabulary

| Term | Meaning | Defense analogue |
| --- | --- | --- |
| **Innate immunity** | Always-on, generic, fast, no memory | WAF rules, rate limits, firewalls, input validation |
| **Adaptive immunity** | Slow to learn, specific, durable memory | Per-account fraud models, learned anomaly baselines, IOC databases |
| **Antigen** | Distinctive feature recognized as foreign | TLS fingerprint, request signature, payload pattern |
| **MHC presentation** | Cells display fragments of what they processed | Audit logs, telemetry surfacing internal state for inspection |
| **B cell / antibody** | Produces specific recognizers; circulates | Signature rules, IOCs, blocked-token lists |
| **T cell** | Coordinates response, kills infected cells | Orchestration that quarantines accounts/services |
| **Memory cell** | Faster, stronger response to repeat exposure | Detection rules, runbooks, learned ML features post-incident |
| **Vaccination** | Controlled exposure to build immunity | Purple-team exercises, chaos drills, red-team campaigns, fuzzing |
| **Autoimmunity** | System attacks self (false positive) | Legit users blocked, internal services rate-limited by own WAF |
| **Immunodeficiency** | System fails to detect (false negative) | Bypass classes, evasion via novel encoding, missing telemetry |
| **Tolerance** | Deliberate non-response to known-safe signal | Allowlists, signed internal traffic, suppressed-alert lists |
| **Inflammation** | Response causes collateral damage | Latency from inline scanning, alert fatigue, throttling spillover |
| **Herd immunity** | Population-level protection from individual immunity | Shared threat intel, ecosystem-wide patches, cert revocation |
| **Self vs non-self** | Marker-based identity discrimination | mTLS, SPIFFE IDs, signed requests, workload identity |
| **Cytokine storm** | Runaway inflammatory cascade | Alert storms, retry storms, automated response feedback loops |

### Layered defense vs. defense-in-depth

These are often conflated. Be precise:

- **Layered defense** is *structural*: different layers see different things (network, transport, app, data). A request passes through each. They are not redundant; they cover *different antigen classes*.
- **Defense-in-depth** is *redundant*: multiple controls of similar character so that one failing does not breach the system. Two WAFs, two auth checks, two encryption boundaries.

A healthy immune system has both. Reviewing only one is a common gap.

## The Process

### Step 1: Define the Body and the Boundary

What is the protected system, and where is its skin?

```
BODY:
- Protected assets: (data, accounts, compute, reputation)
- External surfaces: (HTTP endpoints, queues, file uploads, supply chain)
- Internal trust zones: (which components trust which?)
- Identity markers (self): (mTLS, signed JWTs, IP ranges, workload IDs)
- Known adversary classes: (scrapers, credential stuffers, insiders, supply-chain)
```

If self is not clearly marked, you have an autoimmunity risk — the system cannot reliably tell its own traffic from outsider traffic.

### Step 2: Inventory Layers — Innate and Adaptive

For each defensive control, classify:

| Control | Innate or adaptive? | What antigen does it recognize? | Where does memory live? |
| --- | --- | --- | --- |
| WAF managed ruleset | Innate | Known signature classes (SQLi, XSS) | Vendor-side; updated out-of-band |
| Rate limit per IP | Innate | Volume anomaly | Sliding window, no long memory |
| Per-account fraud score | Adaptive | Behavioral deviation from learned baseline | Per-account model state |
| Post-incident WAF rule | Adaptive (memory cell) | Specific past attack pattern | Rule store; durable |
| mTLS for internal calls | Self/non-self | Identity certificate | PKI |

Look for gaps where neither layer covers a plausible class of threat.

### Step 3: Audit Self vs. Non-Self Discrimination

For each trust boundary, ask:

- What marker says "this is us"?
- Can that marker be forged or replayed?
- What happens to traffic with a missing or ambiguous marker — denied, allowed, or ignored?
- Is the marker checked at the boundary, or assumed because of network position?

Network-position-as-identity ("it came from the VPC, must be us") is the immunological equivalent of judging self by smell — adequate until something gets inside.

### Step 4: Map Memory Formation

Memory is what turns one incident into durable protection. Audit it:

- After an incident, what concrete artifact is produced? (Detection rule, IOC, test case, runbook entry, ML feature.)
- Where does it live, and who maintains it?
- Is there a half-life — does the rule eventually get pruned, or accumulate as scar tissue?
- Can the system distinguish "we've seen this before" from "this is new"?

A team with rich postmortems but no memory cells (no durable detection added) re-fights every incident. Conversely, a system that only adds memory and never prunes accumulates rule debt.

### Step 5: Estimate Inflammation Cost

Every response damages the host. Quantify before deploying:

- What latency does inline scanning add at p50, p99?
- What % of legit traffic does this block (false positive rate)?
- What alert volume does it produce, and who reads them?
- What is the blast radius if the rule misfires? (One user? An entire customer? An entire region?)
- Does response feed back into more detection (cytokine storm risk — alerts triggering alerts)?

A defense whose inflammation cost exceeds the threat's damage is autoimmune disease, not protection.

### Step 6: Plan Vaccination

Vaccination = controlled exposure that builds memory without disease.

| Exercise | Builds immunity to |
| --- | --- |
| Purple-team campaign | Specific TTPs in your real environment |
| Chaos / fault injection | Outage classes |
| Fuzzing | Parser/protocol bug classes |
| Red-team retainer | Novel adversary creativity |
| Tabletop incident | Decision-making and coordination |
| Replay of past incident in staging | Detection regression |

After every vaccination, confirm a memory cell formed — a new rule, test, runbook, or ML feature. Otherwise the exposure was not protective.

### Step 7: Diagnose Autoimmunity and Immunodeficiency

For each incident or complaint, classify:

- **Autoimmunity** (false positive): system harmed legitimate self. Response is *less* aggressive detection or *better* self-marking, not more rules.
- **Immunodeficiency** (false negative): system missed a real threat. Response is a new memory cell or a new layer.
- **Tolerance failure**: known-safe behavior was deliberately allowed and got abused. Response is to revisit the allowlist with current threat context.

Misdiagnosis is the most common error: treating autoimmunity by adding *more* rules makes it worse.

## Output Format

```
IMMUNE-SYSTEM REVIEW

Body and boundaries:
- ...

Layer inventory:
- Innate: ...
- Adaptive: ...
- Self/non-self markers: ...

Coverage gaps (no layer catches this):
- ...

Memory audit:
- Where memory lives: ...
- Pruning policy: ...

Inflammation costs:
- ...

Autoimmunity / immunodeficiency observed:
- ...

Vaccination plan:
- ...

Recommended changes (least inflammatory first):
1. ...
```

## Anti-Patterns to Avoid

- **Confusing layered with depth**: stacking five WAFs is depth in one layer, not coverage of new layers
- **Adding rules to fix false positives**: this is treating autoimmunity by attacking more self
- **Network-position as identity**: cryptographic self-markers are required inside any non-trivial trust boundary
- **No memory formation**: incidents that don't produce a durable artifact (rule, test, runbook) waste their immunological value
- **Unbounded memory**: rules without pruning policy become scar tissue, contributing to inflammation
- **Cytokine storms**: automated responses that themselves trigger more responses must have circuit breakers
- **Silent tolerance**: undocumented allowlists are tolerance you cannot reason about

## Relationship to Other Skills

- Use `adversarial-design-review` to model the *attackers* the immune system faces; this skill is about the *defense architecture* that meets them.
- Use `signal-detection-review` for the *statistics* of FP/FN tuning at a single detector; this skill is about the *system* of detectors and their layering.
- Use `failure-mode-effects-analysis` to enumerate what happens when a defensive control itself fails.
- Use `incident-review` to extract memory cells from past incidents.
- Use `feedback-loop-analysis` to find cytokine-storm risks in automated response chains.
