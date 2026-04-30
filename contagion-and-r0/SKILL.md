---
name: contagion-and-r0
description: Apply epidemiological reasoning — R0, generation time, susceptibility, contact tracing, herd immunity — to vulnerability propagation, dependency CVEs, credential leaks, bug spread, and incident blast radius.
user-invocable: true
---

# Contagion and R0

Act as an epidemiologist confronting a new outbreak. Public health does not ask "is this dangerous?" — it asks *how fast does it spread, who is susceptible, what is the generation time, and where do we cut transmission?* The mathematics is simple and brutal: anything with R > 1 grows exponentially until it runs out of susceptibles or you intervene. Software has identical dynamics for CVEs propagating through dependency graphs, credential leaks across reused systems, viral bug reproductions across forks, and contagious misconfigurations spreading by copy-paste.

`immune-system-design` is about the *defences*: innate vs adaptive, what's "self." This skill is about *spread dynamics* once something is loose: how fast it propagates, who is susceptible, where to cut transmission, and when to stop.

Success looks like a quantified blast-radius assessment with an estimated R, a contact-trace of exposed surfaces, and a containment plan ranked by transmission-cut effectiveness. Failure looks like "we patched the affected service" without asking how the contagion got there or where else it travelled.

## When to Use This

- A CVE drops in a popular dependency and you must decide who to notify, what to patch first, and how wide the blast radius is
- A credential or token leaks and you need to enumerate everywhere it could have been reused
- A bug found in one service is suspected to have been copy-pasted into others
- A misconfiguration (insecure default, broken IAM template) was templated and may have proliferated
- An incident's root cause is shared infrastructure or a shared library — assess co-affected systems
- Pre-incident: identify "super-spreader" components whose compromise would propagate widely
- Designing a security advisory: who to notify, in what order, with what urgency

**Escape hatch**: For non-propagating issues (a one-off bug in a single non-shared component, a vulnerability in a system with no callers), epidemiological framing is overkill. Use this when something *can spread*, not for isolated faults.

## Core Questions

- What is the pathogen? (CVE, leaked secret, copy-pasted bug, misconfig)
- What is the route of transmission? (dependency, copy-paste, shared infra, shared identity)
- Who is susceptible? (services using the version, systems trusting the credential, callers of the pattern)
- What is R0 in this graph? (mean expected secondary infections from one infected node)
- What is the generation time? (latency between infection and onward transmission)
- Where are the super-spreaders? (highly-connected nodes with weak isolation)
- What intervention has the highest transmission-cut per cost?
- What does herd immunity look like — what coverage stops sustained spread?

## Domain Vocabulary

| Term | Definition | Software analogue |
| --- | --- | --- |
| **Pathogen** | The transmissible agent | The CVE, leaked credential, viral bug, bad pattern |
| **Host** | The infected entity | An affected service, repo, account, image |
| **Vector** | The transmission medium | npm/pip dependency, container base image, shared module, copy-paste, IaC template, shared identity provider |
| **Susceptible (S)** | Could be infected if exposed | Uses the vulnerable version; trusts the credential |
| **Infected (I)** | Currently affected | Confirmed running the bad version / using the leaked secret |
| **Recovered / Removed (R)** | No longer infectious | Patched, rotated, redesigned away |
| **R0 (basic reproduction number)** | Mean secondary cases per index case in a fully-susceptible population | Mean downstream affected nodes per affected node, no mitigation |
| **Rt (effective)** | Same, given current immunity/intervention | After patches and partial rotations |
| **Generation time** | Time from infection to onward transmission | Time from a service being compromised to it infecting another (e.g., next deploy, next image rebuild) |
| **Serial interval** | Observed time between successive cases | Empirical lag between detected infections |
| **Super-spreader** | High-degree, high-contact node | Base image used by 80% of services; identity used by 50 systems; "utils" repo copy-pasted across the org |
| **Contact tracing** | Identify who an infected case was exposed to | Where else has this version been deployed, this credential been used, this code been copied? |
| **Herd immunity threshold** | 1 − 1/R0 coverage stops sustained spread | Patch coverage required to drop Rt below 1 |
| **Reservoir** | A population that sustains the pathogen even when removed elsewhere | Old container images, frozen forks, ungated CI environments |
| **Index case** | First identified infection | First detected affected service / first known compromised account |
| **Outbreak vs endemic** | Acute spike vs persistent low-level | A CVE-driven mass exposure vs a pattern that re-emerges in every new project |
| **Quarantine** | Isolate suspected/exposed before confirmed | Block deploys, revoke trust, freeze environments while assessing |
| **Containment** | Stop spread but allow current cases to resolve | Patch new builds; cordon old |
| **Eradication** | Remove the pathogen entirely | Roll out fix; verify zero remaining instances |

## The Process

### Step 1: Identify the Pathogen and Its Route

Be specific. "CVE-2025-XYZ" is not the pathogen for purposes of containment — `lib@<2.4.1` *via* the npm dependency tree is the pathogen + route. The route determines the susceptible population.

| Pathogen | Likely routes |
| --- | --- |
| Library CVE | Direct dep; transitive dep; vendored copy; container base image |
| Leaked credential | Reuse across systems; embedded in images, IaC, CI logs, browser storage |
| Copy-pasted bug | Same author across repos; templated scaffolding; "stack-overflow shape" |
| Bad IaC pattern | Module reuse, internal Backstage template, copy-modify across teams |
| Compromised identity | All systems federated through the same IdP; cached tokens |

Weak:

> CVE in `lodash`. Patch everywhere.

Strong:

> CVE in `lodash@<4.17.21` exploitable when input X reaches sink Y. Routes: 12 services pin it directly; 41 pull it transitively via `framework-foo`; 6 base images bake it in; 3 desktop apps ship it. Susceptibility differs per route — only services calling sink Y are exploitable, but all need the bump for hygiene.

### Step 2: Enumerate the Susceptible Population

For each route, list every entity that *could* be infected. Distinguish:

- **Susceptible & exposed**: uses the route and meets exposure conditions
- **Susceptible, not exposed**: uses the route but conditions don't apply (e.g., doesn't call the sink)
- **Not susceptible**: doesn't use the route
- **Unknown**: insufficient inventory; treat as susceptible for triage

The "Unknown" bucket is where outbreaks hide. If it's large, your *first* intervention is to shrink it (inventory, SBOM, secret scanning), not to patch.

### Step 3: Estimate R0 in This Graph

For each infected node, count how many downstream nodes will become infected if no intervention occurs and the natural process (next deploy, next image rebuild, next credential reuse) plays out.

```
R0 estimation:
- Index case downstream nodes via route 1: ...
- Index case downstream nodes via route 2: ...
- Mean secondary infections (weighted by route prevalence):
- Variance: high if super-spreaders exist (R0 alone is misleading)
```

Important: the *distribution* matters as much as the mean. A pathogen with R0 = 2 where most nodes infect 0 and a few infect 100 (super-spreader-driven) needs different containment from one where every node infects exactly 2.

### Step 4: Identify Super-Spreaders

Find high-degree, high-trust nodes whose compromise would dominate spread:

- Base container images / golden AMIs (one infected image → all derived services)
- Shared internal libraries used across many services
- The org's CI/CD identity, root account, shared deploy key
- Internal "platform" templates (Backstage, scaffolders)
- Any system trusted by many others (IdP, secrets manager, package registry)

Containment effort focused on super-spreaders has dramatically more transmission-cut per unit work than treating individual cases.

### Step 5: Estimate Generation Time and Choose Urgency

Spread speed is set by generation time (time from infection to onward transmission). For software:

| Vector | Typical generation time |
| --- | --- |
| Active CI rebuilds and deploys | Hours |
| Weekly base-image rebuilds | Days |
| Long-running services with no rebuild | Months (reservoir!) |
| Code copy-paste during feature development | Weeks |
| Credential reuse on next login | Minutes |

If generation time is shorter than your detection-to-mitigation time, exponential spread will outrun you. Either shorten the response loop or extend the generation time (freeze deploys, rotate credentials immediately, block builds).

### Step 6: Choose Interventions by Transmission-Cut per Cost

Rank interventions, not by completeness, but by R-reduction per unit effort.

| Intervention | Effect on R | Cost | When to use |
| --- | --- | --- | --- |
| Patch the super-spreader | Large drop | Moderate | Always first if a super-spreader exists |
| Quarantine (block deploys, revoke trust) | Drops Rt to ~0 temporarily | High operational cost | Outbreak phase; buy time |
| Fix at the route (lockfile pin, base-image bump) | Cuts new infections | Low | Always do alongside case-by-case patching |
| Patch each affected case | Cuts that branch | Linear in case count | Background task |
| Rebuild reservoirs (re-bake old images) | Empties the reservoir | High | After containment to prevent re-emergence |
| Rotate widely-used credential | Drops Rt to ~0 | High user-visible cost | Confirmed leak with reuse risk |
| Education / pattern guidance | Reduces R for endemic copy-paste | Slow | For patterns that recur in new code |

Reach herd immunity (Rt < 1) before pursuing eradication. The last 5% of cases takes 50% of the effort and is rarely the next priority during an active outbreak.

### Step 7: Contact Trace from Each Confirmed Case

For every confirmed infection, ask: *what did this entity touch while infectious?*

```
CONTACT TRACE (per infected node):
- During the infectious window [t_infect, t_remediate]:
  - Outbound deploys / artifacts produced:
  - Credentials used → systems accessed:
  - Secrets read or written:
  - Code/templates copied from this repo:
  - Tokens issued or cached:
- Each contact: classify exposed / not exposed; treat per Step 2.
```

This is how you find the cases you didn't know about. Most "the breach was bigger than we thought" reports are missing-contact-trace stories.

### Step 8: Declare Containment Then Eradication

Don't conflate them.

- **Containment achieved**: Rt < 1 sustainably. New infections trending down. Acute response can wind down.
- **Eradication achieved**: Zero infectious entities remain *and* the reservoir is empty. No risk of resurgence.

Many incidents declare victory at containment and stop, leaving a reservoir (an old image, a pinned-old-version internal tool, a frozen fork). Months later the same pathogen re-emerges. Eradication requires explicit reservoir hunting.

## Output Format

```
CONTAGION ASSESSMENT

Pathogen:
Route(s) of transmission:

Susceptible population:
- Susceptible & exposed: count, list
- Susceptible, not exposed: count, list
- Not susceptible: count, list
- Unknown (treat as susceptible): count, list, plan to shrink

R0 estimate:
- Mean secondary infections per case:
- Distribution shape (homogeneous / super-spreader-driven):
- Generation time:

Super-spreaders identified:
- Node, fan-out, current state

Index case(s):
Contact trace summary:
- Exposed contacts identified:
- Newly-confirmed cases from trace:

Intervention plan (ranked by R-cut per cost):
1. [intervention] — expected ΔR — cost — owner
2. ...

Containment criteria:
- Metric, threshold, current value

Eradication plan:
- Reservoir inventory:
- Reservoir-clearing tasks:
- Verification (zero remaining):

Communications:
- Internal advisory:
- External advisory (if applicable):
- Notification ordering (super-spreaders first):
```

## Anti-Patterns to Avoid

- **Patching cases without cutting the route**: closing each detected instance while the lockfile/base image keeps re-introducing the pathogen.
- **Ignoring the Unknown bucket**: triaging only the inventory you have; the outbreak grows in the unobserved population.
- **Treating R0 as a single number**: super-spreader dynamics need the *distribution*; mean alone misallocates effort.
- **Skipping contact tracing**: the breach was bigger than you thought because nobody enumerated what the index case touched while infectious.
- **Stopping at containment**: the reservoir reignites the outbreak weeks later; eradication needs explicit reservoir hunting.
- **Wide rotation without priority**: rotating every credential at once causes more outage than the breach; rotate by exposure × privilege.
- **Confusing immunity with absence**: a service that doesn't run the vulnerable code path *today* may tomorrow if a feature flag flips — don't mark it immune.
- **Quarantine without a plan to lift**: blocking all deploys indefinitely is a self-inflicted outage; declare the criteria for ending quarantine when you start it.

## Relationship to Other Skills

- Use `immune-system-design` for the *defensive architecture* (innate vs adaptive, what's self) — this skill is about an active outbreak's spread dynamics.
- Use `network-topology-review` to identify super-spreaders — high-centrality nodes in the dependency / trust graph.
- Use `incident-review` after containment to capture contributing factors and prevent recurrence.
- Use `code-forensics` to date the index case and reconstruct the timeline of exposure.
- Use `signal-detection-review` for the inventory side: are your detectors finding the susceptible population, and at what FP/FN?
- Use `apoptosis-and-cell-death` for the reservoir problem: services and forks that should have been retired are now harbouring the pathogen.
- Use `pharmacological-dosing` for the rollout of fixes and credential rotations — staged, monitored, with stopping criteria.
