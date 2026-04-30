# Personal Skills Library

A collection of `/skill-name` slash commands for the Copilot CLI, each translating a mature reasoning discipline from another field into a structured workflow an LLM agent can invoke on demand.

Every skill follows the same shape: a framing paragraph, when-to-use triggers with an escape hatch, a domain vocabulary table, a 6–8-step process with templates and weak-vs-strong examples, an output template, anti-patterns, and cross-references to related skills.

## How to use

```text
/skills reload      # pick up new skills
/skills list        # see what's installed
/<skill-name>       # invoke a skill
```

Skills are also auto-suggested by the agent when their description matches the task at hand. They live in `~/.copilot/skills/<name>/SKILL.md`.

## Skills by theme

### 🐛 Debugging & diagnosis
| Skill | Lens |
|---|---|
| `popperian-debug` | Falsificationism — formulate, rank, and try to disprove hypotheses |
| `differential-diagnosis-debugging` | Medical triage — likelihood × severity × test cost |
| `bayesian-reasoning` | Belief updating with priors, likelihoods, posteriors |
| `statistical-debugging` | Flaky tests, base rates, false positives, confidence |
| `code-forensics` | Reconstruct timelines from logs, commits, artifacts |
| `observer-effect-debugging` | Heisenbugs — when measurement perturbs the system |

### 🧠 Reasoning & epistemology
| Skill | Lens |
|---|---|
| `assumption-audit` | Surface and classify hidden assumptions |
| `bias-audit` | Anchoring, confirmation, availability, sunk cost |
| `proof-tactics` | Induction, contradiction, contrapositive, cases |
| `fermi-estimation` | Order-of-magnitude back-of-envelope reasoning |
| `semantic-precision` | Clarify overloaded terms, ambiguous specs |
| `interpretive-reading` | Hermeneutics — charitable reading, hermeneutic circle |
| `communication-pragmatics` | Grice's maxims and speech act theory for engineering text |
| `mental-model-alignment` | System model vs developer model vs user model |

### 🔢 Mathematics & formal methods
| Skill | Lens |
|---|---|
| `formal-invariants` | Discover invariants and encode them as assertions/contracts |
| `dimensional-analysis` | Track units of measure across boundaries |
| `error-and-approximation-analysis` | Floats, ULP, condition numbers, accumulated error |
| `fixed-point-reasoning` | Iteration, convergence, contraction, lfp/gfp |
| `topological-refactoring` | Behavior-preserving deformation; essential vs accidental structure |
| `order-and-lattice-thinking` | Posets, joins, monotonicity, CRDTs, type lattices |
| `relativistic-causality` | Lamport's logical time for distributed systems |

### 🌐 Systems thinking
| Skill | Lens |
|---|---|
| `emergence-analysis` | Local rules → surprising global behavior |
| `systems-archetypes` | Senge's recurring dynamics — fixes-that-fail, limits-to-growth |
| `system-ecosystem-analysis` | Dependency ecosystems, cascading failures, competition |
| `network-topology-review` | Graph centrality, critical nodes, blast radius |
| `feedback-loop-analysis` | Retries, queues, rate limits, reactive loops |
| `constraint-analysis` | Bottlenecks, throughput, queue theory |
| `information-flow-analysis` | Loss, noise, ambiguity, compression, propagation |
| `entropy-and-code-rot` | Thermodynamic reasoning about decay and tech debt |

### 🛡️ Reliability & operations
| Skill | Lens |
|---|---|
| `failure-mode-effects-analysis` | Enumerate failure modes × severity × detectability |
| `premortem-analysis` | Klein's prospective hindsight — narrate the failure |
| `incident-review` | Blameless analysis of contributing factors |
| `preflight-checklist` | Verification before risky action |
| `mise-en-place` | Stage materials/state/observers before execution |
| `operational-game-day` | Controlled drills of failure handling |
| `resilience-engineering` | Graceful degradation, recovery, absorbing shocks |
| `signal-detection-review` | FP/FN, sensitivity, threshold tuning for alerts |
| `ledger-consistency` | Acquire/release, enqueue/dequeue, balance reconciliation |
| `mistake-proofing` | Toyota poka-yoke — make wrong actions impossible |
| `sequencing-and-temperature` | Cooking-style step ordering for migrations |
| `recipe-rescue` | Live triage during execution failures |
| `pickling-and-preservation` | Snapshots, archives, frozen schemas |
| `pharmacological-dosing` | Dose-response, half-life, titration for rollouts |

### 🎨 Design & human factors
| Skill | Lens |
|---|---|
| `adversarial-design-review` | Attackers, malformed inputs, prompt injection, abuse |
| `affordance-review` | Make right actions obvious, wrong actions hard |
| `attention-design-review` | Notification/log salience and interruption cost |
| `cognitive-load-review` | Working memory, chunking, mental model fit |
| `distributed-cognition-review` | Knowledge sharing across code, docs, tools, rituals |
| `incentive-analysis` | How users/maintainers/attackers respond to rules |
| `user-context-fieldwork` | Real workflows, hidden norms, workarounds, friction |
| `code-narrative-review` | Readability, conceptual flow, naming, API story |

### 💰 Decision-making (financial reasoning)
| Skill | Lens |
|---|---|
| `portfolio-theory` | Markowitz — diversify across uncorrelated bets |
| `time-value-of-money` | DCF/NPV applied to refactor-vs-ship and tech debt |
| `optionality-as-value` | Real options, one-way vs two-way doors |
| `hedging-and-insurance` | Risk transfer — redundancy, error budgets, multi-region |
| `capital-allocation` | Where to spend effort, hurdle rates, ignore sunk cost |
| `market-microstructure` | Order-book mechanics for schedulers and matchers |
| `bubble-dynamics` | Behavioral finance for tech adoption and hype cycles |

### ⚡ Adaptive execution
| Skill | Lens |
|---|---|
| `ooda-adaptive-execution` | Observe-orient-decide-act loops under uncertainty |
| `taste-as-you-go` | Continuous mid-step verification |

## Skill provenance

Skills are intentionally drawn from outside CS to import frameworks the field has already paid for in blood:

| Source field | Skills |
|---|---|
| Philosophy of science | `popperian-debug`, `assumption-audit`, `bias-audit` |
| Mathematics / logic | `formal-invariants`, `proof-tactics`, `dimensional-analysis`, `fixed-point-reasoning`, `topological-refactoring`, `order-and-lattice-thinking`, `error-and-approximation-analysis`, `bayesian-reasoning` |
| Physics | `entropy-and-code-rot`, `relativistic-causality`, `observer-effect-debugging`, `fermi-estimation` |
| Medicine / pharmacology | `differential-diagnosis-debugging`, `pharmacological-dosing` |
| Engineering / systems | `failure-mode-effects-analysis`, `feedback-loop-analysis`, `resilience-engineering`, `signal-detection-review`, `mistake-proofing`, `operational-game-day`, `preflight-checklist` |
| Systems theory / cybernetics | `emergence-analysis`, `systems-archetypes`, `system-ecosystem-analysis`, `network-topology-review`, `constraint-analysis`, `information-flow-analysis`, `feedback-loop-analysis` |
| Cognitive science / HCI | `cognitive-load-review`, `mental-model-alignment`, `distributed-cognition-review`, `attention-design-review`, `affordance-review` |
| Anthropology / sociology | `user-context-fieldwork`, `incentive-analysis` |
| Finance / economics | `portfolio-theory`, `time-value-of-money`, `optionality-as-value`, `hedging-and-insurance`, `capital-allocation`, `market-microstructure`, `bubble-dynamics` |
| Culinary | `mise-en-place`, `sequencing-and-temperature`, `taste-as-you-go`, `recipe-rescue`, `pickling-and-preservation` |
| Hermeneutics / linguistics | `interpretive-reading`, `communication-pragmatics`, `semantic-precision` |
| Military strategy | `ooda-adaptive-execution`, `premortem-analysis`, `adversarial-design-review` |
| Forensics | `code-forensics`, `incident-review` |

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

Target length: 180–280 lines. Generic process language is the failure mode — every step should be recognisably from the originating discipline.
