# Personal Skills Library

A collection of `/skill-name` slash commands for the Copilot CLI, each translating a mature reasoning discipline from another field into a structured workflow an agent can invoke on demand.

The premise: most engineering reasoning errors aren't novel. They've been studied — and often *named* — by chemists, immunologists, structural engineers, hermeneuts, traders, chefs, and athletic coaches. These skills import that vocabulary so we can recognise the situation, reach for the right framework, and avoid reinventing the analysis.

Each skill follows the same shape: a framing paragraph, when-to-use triggers with an explicit escape hatch, a domain vocabulary table, a 6–8-step process with templates and weak-vs-strong examples, an output template, anti-patterns, and cross-references to related skills.

## How to use

```text
/skills reload      # pick up new skills
/skills list        # see what's installed
/<skill-name>       # invoke a skill
```

Skills are also auto-suggested when their description matches the task. They live at `~/.copilot/skills/<name>/SKILL.md`.

---

## Catalog

The third column tells you, in plain English, *when to reach for it*.

### 🐛 Debugging & diagnosis

| Skill | Lens | Reach for it when… |
|---|---|---|
| `popperian-debug` | Falsificationism — formulate, rank, and try to disprove hypotheses | You're stuck on a bug, the obvious fix didn't work, or you keep finding "the cause" and being wrong |
| `differential-diagnosis-debugging` | Medical triage — likelihood × severity × test cost | You have several plausible causes and need to decide which to investigate first |
| `bayesian-reasoning` | Belief updating with priors, likelihoods, posteriors | New evidence arrived and you need to know how much to update — especially when the evidence is striking but the base rate is low |
| `statistical-debugging` | Flaky tests, base rates, false positives, confidence | A test is intermittent, a metric is noisy, or you're tempted to act on a single observation |
| `code-forensics` | Reconstruct timelines from logs, commits, artifacts | An incident happened and you need a defensible chronology before drawing conclusions |
| `observer-effect-debugging` | Heisenbugs — when measurement perturbs the system | "It only fails when the debugger isn't attached" / "It only works when I add a log line" |

### 🧠 Reasoning & epistemology

| Skill | Lens | Reach for it when… |
|---|---|---|
| `assumption-audit` | Surface and classify hidden assumptions | A design feels off but you can't say why; or you're handed a plan that "obviously" works |
| `bias-audit` | Anchoring, confirmation, availability, sunk cost | You've been deep in a problem and want to check if your reasoning has slid into a known cognitive trap |
| `proof-tactics` | Induction, contradiction, contrapositive, cases | You need to argue that a loop terminates, a recursion is exhaustive, or an edge case can't happen |
| `fermi-estimation` | Order-of-magnitude back-of-envelope reasoning | Before designing for a load, optimising a path, or sizing a machine — sanity-check the numbers |
| `semantic-precision` | Clarify overloaded terms, ambiguous specs | Two people are arguing using the same word for different things; a spec uses "must" without saying who must |
| `interpretive-reading` | Hermeneutics — charitable reading, hermeneutic circle | Reading legacy code, a confusing PR, an opaque error message, or an under-specified RFC |
| `communication-pragmatics` | Grice's maxims and speech act theory | Writing an error message, commit message, log line, agent prompt, or PR description that has to land correctly |
| `mental-model-alignment` | System model vs developer model vs user model | A bug isn't really a bug — it's a mismatch between how the system works and how someone *thinks* it works |

### 🔢 Mathematics & formal methods

| Skill | Lens | Reach for it when… |
|---|---|---|
| `formal-invariants` | Discover invariants and encode as assertions/contracts | A subsystem keeps regressing in subtle ways; you want a property the code can never violate |
| `dimensional-analysis` | Track units of measure across boundaries | You suspect a units bug — bytes vs MB, ms vs s, count vs ratio — or you're crossing a system boundary that strips units |
| `error-and-approximation-analysis` | Floats, ULP, condition numbers, accumulated error | Money in floats, drifting clocks, geo coordinates, ML pipelines that don't add up |
| `fixed-point-reasoning` | Iteration, convergence, contraction, lfp/gfp | Designing a retry loop, type checker, scheduler, autoscaler, or any "iterate to stable" system |
| `topological-refactoring` | Behavior-preserving deformation; essential vs accidental structure | Mid-refactor and asking "is this *still the same shape*?" — what tests must keep passing |
| `order-and-lattice-thinking` | Posets, joins, monotonicity, CRDTs, type lattices | Designing version compatibility, permission models, CRDTs, type subtyping, or dataflow analyses |
| `proof-tactics` | Mathematical proof techniques | (See above — also under reasoning) |
| `relativistic-causality` | Lamport's logical time for distributed systems | Reasoning about event ordering, replicas, "did A happen before B?", consistency models |

### 🌐 Systems thinking

| Skill | Lens | Reach for it when… |
|---|---|---|
| `emergence-analysis` | Local rules → surprising global behavior | A system is doing something nobody designed; small local changes have large global effects |
| `systems-archetypes` | Senge's recurring dynamics — fixes-that-fail, limits-to-growth | A team keeps fixing the same problem, or growth has stalled, or quick fixes are creating new problems |
| `system-ecosystem-analysis` | Dependency ecosystems, cascading failures, competition | Looking at the wider environment of your system — vendors, dependencies, alternatives, cascades |
| `network-topology-review` | Graph centrality, critical nodes, blast radius | Mapping which services/files/people would do the most damage if they fail |
| `feedback-loop-analysis` | Retries, queues, rate limits, reactive loops | Anywhere one component reacts to another and the loop can resonate, oscillate, or amplify |
| `constraint-analysis` | Bottlenecks, throughput, queue theory | "Where is the bottleneck *really*?" — before optimising the wrong thing |
| `information-flow-analysis` | Loss, noise, ambiguity, compression, propagation | Tracking how information degrades as it moves through layers, logs, dashboards, and people |
| `entropy-and-code-rot` | Thermodynamics — entropy, free energy, reversibility | Reasoning about decay, drift, why "we'll fix it later" is asymmetric, the cost of not maintaining |

### 🛡️ Reliability & operations

| Skill | Lens | Reach for it when… |
|---|---|---|
| `failure-mode-effects-analysis` | Enumerate failure modes × severity × detectability | Before a risky change — produce a structured list of what could go wrong and what catches it |
| `premortem-analysis` | Klein's prospective hindsight — narrate the failure | Before committing to a plan — imagine it has already failed, work backwards |
| `incident-review` | Blameless analysis of contributing factors | After an incident — produce contributing factors, safeguards, recurrence prevention |
| `preflight-checklist` | Verification before risky action | A checklist of things to *verify* immediately before action |
| `mise-en-place` | Stage materials/state/observers before execution | Before a migration/debug session — set up rollback scripts, terminals, queries, monitoring |
| `operational-game-day` | Controlled drills of failure handling | Designing a chaos exercise — what assumptions are we testing, what counts as pass |
| `resilience-engineering` | Graceful degradation, recovery, absorbing shocks | Designing how the system behaves under stress — degrade modes, recovery paths, safety boundaries |
| `signal-detection-review` | FP/FN, sensitivity, threshold tuning | Tuning alerts/tests/classifiers — too noisy, too quiet, or wrongly thresholded |
| `ledger-consistency` | Acquire/release, enqueue/dequeue, balance reconciliation | Tracking state transitions — every acquire matches a release, every event has a source |
| `mistake-proofing` | Toyota poka-yoke — make wrong actions impossible | Designing APIs, configs, or flows where wrong calls should be *structurally impossible*, not just detected |
| `sequencing-and-temperature` | Cooking-style step ordering for migrations | Ordering migration/deploy steps — what's irreversible, what's reversible, what has carryover |
| `recipe-rescue` | Live triage during execution failures | Mid-incident — decide whether to keep going, patch in place, or roll back |
| `pickling-and-preservation` | Snapshots, archives, frozen schemas | Designing snapshots, audit logs, frozen schemas, archival formats — what's preserved vs lost |
| `pharmacological-dosing` | Dose-response, half-life, titration | Tuning rate limits, retry budgets, feature flag rollouts — start low, go slow, watch for steady state |

### 🎨 Design & human factors

| Skill | Lens | Reach for it when… |
|---|---|---|
| `adversarial-design-review` | Attackers, malformed inputs, prompt injection, abuse | Reviewing a design for misuse, abuse, prompt injection, or metric gaming |
| `affordance-review` | Make right actions obvious, wrong actions hard | Reviewing an API/CLI/UI for whether the right thing is the easy thing |
| `attention-design-review` | Notification/log salience and interruption cost | Tuning alerts, prompts, errors, and UI signals — what deserves to interrupt |
| `cognitive-load-review` | Working memory, chunking, mental model fit | Code/API/doc that *feels* hard — measure why and reduce the load |
| `distributed-cognition-review` | Knowledge across code, docs, tools, tests, rituals | Asking where knowledge lives — and whether it survives if a person, doc, or tool disappears |
| `incentive-analysis` | How users/maintainers/attackers respond to rules | Before launching a metric, default, rule, or reward — predict how people game it |
| `user-context-fieldwork` | Real workflows, hidden norms, workarounds, friction | Before redesigning a workflow — investigate what users actually do, not what they say they do |
| `code-narrative-review` | Readability, conceptual flow, naming, API story | Reviewing complex code for whether it tells a coherent story to the next reader |

### 💰 Decision-making (financial reasoning)

| Skill | Lens | Reach for it when… |
|---|---|---|
| `portfolio-theory` | Markowitz — diversify across uncorrelated bets | Choosing dependencies, vendors, experiments — are you diversified or just stacked? |
| `time-value-of-money` | DCF/NPV applied to refactor-vs-ship decisions | "Should we ship now or polish?" — make the discounting explicit |
| `optionality-as-value` | Real options, one-way vs two-way doors | Before an irreversible commit — what's the value of *keeping the door open*? |
| `hedging-and-insurance` | Risk transfer — redundancy, error budgets, multi-region | Designing redundancy/backups/multi-cloud as deliberate insurance with explicit premiums |
| `capital-allocation` | Where to spend effort, hurdle rates, sunk-cost discipline | Roadmap decisions, tech-debt vs feature split, deciding what *not* to do |
| `market-microstructure` | Order-book mechanics for schedulers and matchers | Designing schedulers, load balancers, ad bidding, GPU job queues, matching systems |
| `bubble-dynamics` | Behavioral finance for tech adoption and hype cycles | Before adopting/migrating to the next hot framework or paradigm — where are we in the cycle? |

### ⚡ Adaptive execution

| Skill | Lens | Reach for it when… |
|---|---|---|
| `ooda-adaptive-execution` | Observe-orient-decide-act loops under uncertainty | Doing exploratory or adaptive work where each step depends on what the last revealed |
| `taste-as-you-go` | Continuous mid-step verification | Long-running operations where verifying intermediate state is cheap and end-state is unrecoverable |

### 🧬 Biology & life-sciences thinking

| Skill | Lens | Reach for it when… |
|---|---|---|
| `evolutionary-pressure` | Selection, drift, vestigial features, Red Queen | Reasoning about why an API/codebase has the shape it does — what survived, what's vestigial |
| `immune-system-design` | Innate vs adaptive, autoimmunity, vaccination | Designing layered defense — security architecture, anomaly detection, what's "self" vs "non-self" |
| `apoptosis-and-cell-death` | Programmed cell death as a *health function* | Sunset planning, deprecation hygiene — when *not dying* is the pathology |
| `symbiosis-and-mutualism` | Mutualism / commensalism / parasitism, obligate vs facultative | Characterising a specific dependency or vendor relationship — who benefits, who pays, who's stuck |

### ⚗️ Chemistry

| Skill | Lens | Reach for it when… |
|---|---|---|
| `reaction-kinetics-and-catalysis` | Rate laws, activation energy, catalysts, Le Chatelier | Adoption is stalling at activation energy; or you need a catalyst (docs, examples, evangelists) to unblock it |
| `solubility-and-miscibility` | "Like dissolves like", emulsifiers, partition coefficient | Integrating two systems/stacks/teams that don't naturally mix — and asking whether you need an emulsifier or accept separation |
| `crystallization-and-nucleation` | Seed crystals, supersaturation, ordered growth | Driving standards/pattern adoption — when the system is supersaturated and ready for a seed |

### 🏃 Fitness & sports performance

| Skill | Lens | Reach for it when… |
|---|---|---|
| `progressive-overload` | SAID, load-recovery-supercompensation, deloads | Stress-testing capacity — ramp progressively rather than step-load; recognise the exhaustion phase |
| `periodization-and-recovery` | Macro/meso/micro cycles, taper, supercompensation | Planning release cadence — building in deliberate recovery, off-seasons, and tapers |
| `pacing-and-energy-budget` | Aerobic/anaerobic, lactate threshold, negative split | Reasoning about *sustainable rate* — recognising you've gone above threshold before you blow up |
| `form-under-load` | Technique degrades before strength; injuries from bad form | Code quality under deadline — why corners cut under pressure cause the next incident |

### 🔧 Engineering disciplines (mechanical / civil / control / reliability)

| Skill | Lens | Reach for it when… |
|---|---|---|
| `factor-of-safety` | Designed margin against load (FoS, MoS, partial safety factors) | Sizing capacity, retry budgets, rate limits — make the safety factor explicit, not vibes |
| `tolerance-stack-up` | Variances combine across an assembly (worst-case vs RSS) | Distributing an end-to-end SLO/budget across stages — and asking whether the sum still fits |
| `fatigue-and-stress-cycling` | Cyclic loading failure below yield (S-N curves, Miner's rule) | Reasoning about systems that work fine for years, then suddenly don't — or chronic on-call load on humans |
| `control-systems-pid` | PID controllers, gain tuning, integral windup | Tuning autoscalers, congestion control, retry timers — anywhere you regulate to a setpoint |
| `commissioning-and-decommissioning` | FAT/SAT, punchlists, lockout-tagout, mothballing | Launching a service properly (acceptance + handover) or sunsetting one properly (drain + archive + remove) |
| `maintenance-philosophy` | Reactive / preventive / predictive / RCM | Choosing the maintenance posture per subsystem — not every service deserves the same strategy |
| `reverse-engineering` | Black-box / gray-box, behavioral characterization, golden references | Understanding legacy or third-party systems with no spec — disciplined inference from observation |
| `materials-selection` | Property matrix, Ashby charts, performance index, lifecycle cost | Choosing a tech stack, library, or tool — write the required-vs-desirable properties *before* shopping |

---

## Skill provenance

Skills are intentionally drawn from outside CS to import frameworks the field has already paid for in blood:

| Source field | Skills |
|---|---|
| Philosophy of science | `popperian-debug`, `assumption-audit`, `bias-audit` |
| Mathematics / logic | `formal-invariants`, `proof-tactics`, `dimensional-analysis`, `fixed-point-reasoning`, `topological-refactoring`, `order-and-lattice-thinking`, `error-and-approximation-analysis`, `bayesian-reasoning` |
| Physics | `entropy-and-code-rot`, `relativistic-causality`, `observer-effect-debugging`, `fermi-estimation` |
| Chemistry | `reaction-kinetics-and-catalysis`, `solubility-and-miscibility`, `crystallization-and-nucleation` |
| Biology / medicine | `evolutionary-pressure`, `immune-system-design`, `apoptosis-and-cell-death`, `symbiosis-and-mutualism`, `differential-diagnosis-debugging`, `pharmacological-dosing` |
| Engineering / reliability | `failure-mode-effects-analysis`, `feedback-loop-analysis`, `resilience-engineering`, `signal-detection-review`, `mistake-proofing`, `operational-game-day`, `preflight-checklist`, `factor-of-safety`, `tolerance-stack-up`, `fatigue-and-stress-cycling`, `control-systems-pid`, `commissioning-and-decommissioning`, `maintenance-philosophy`, `reverse-engineering`, `materials-selection` |
| Systems theory / cybernetics | `emergence-analysis`, `systems-archetypes`, `system-ecosystem-analysis`, `network-topology-review`, `constraint-analysis`, `information-flow-analysis` |
| Cognitive science / HCI | `cognitive-load-review`, `mental-model-alignment`, `distributed-cognition-review`, `attention-design-review`, `affordance-review` |
| Anthropology / sociology | `user-context-fieldwork`, `incentive-analysis` |
| Finance / economics | `portfolio-theory`, `time-value-of-money`, `optionality-as-value`, `hedging-and-insurance`, `capital-allocation`, `market-microstructure`, `bubble-dynamics` |
| Sports / fitness | `progressive-overload`, `periodization-and-recovery`, `pacing-and-energy-budget`, `form-under-load` |
| Culinary | `mise-en-place`, `sequencing-and-temperature`, `taste-as-you-go`, `recipe-rescue`, `pickling-and-preservation` |
| Hermeneutics / linguistics | `interpretive-reading`, `communication-pragmatics`, `semantic-precision` |
| Military strategy | `ooda-adaptive-execution`, `premortem-analysis`, `adversarial-design-review` |
| Forensics | `code-forensics`, `incident-review` |

---

## Authoring conventions

Each `SKILL.md` should:

1. Have YAML frontmatter with `name`, `description`, `user-invocable: true`.
2. Open with a framing paragraph that names *who the agent is acting as*.
3. State what success/failure looks like.
4. Include **When to Use This** with 5–7 triggers and an explicit escape hatch.
5. Surface **Core Mindset / Core Questions** — the lens this discipline brings.
6. Provide a **domain vocabulary table** or classification scheme — this is what makes the skill substantive.
7. Lay out **The Process** — 6–8 numbered steps with sub-questions, techniques, structured templates, and weak-vs-strong examples.
8. Provide an **Output Format** the agent fills in.
9. List **Anti-Patterns to Avoid** — 5–8 specific failure modes.
10. Cross-reference **Relationship to Other Skills**.

Target length: **180–280 lines**. Generic process language is the failure mode — every step should be recognisably from the originating discipline.
