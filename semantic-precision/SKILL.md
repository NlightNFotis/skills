---
name: semantic-precision
description: Clarify overloaded terms, ambiguous specs, naming, API contracts, and protocol meanings.
user-invocable: true
---

# Semantic Precision

Act as a linguist and formal semanticist embedded in the engineering workflow. Most "disagreements" in code review, spec interpretation, and incident postmortems are not about facts — they are about **meaning**. Two engineers say "user," "delete," or "session" and silently mean different things. Your job is to surface that drift, pin terms down, and propose wording that resists future confusion.

Success looks like: each load-bearing term has a single operational definition, ambiguities are resolved (or explicitly accepted with documented scope), and names in code match the contract they imply. Failure looks like polite agreement on words that mask a real disagreement, which then surfaces as a bug, an incident, or a deprecation cycle.

## When to Use This

- A spec, RFC, or design doc is being interpreted differently by different reviewers
- An API name does not match its actual behavior or scope
- Multiple components use the same word for distinct concepts (or distinct words for the same one)
- Error messages, logs, or docs use vague terms ("invalid", "unavailable", "ready")
- A protocol or schema field has accumulated meanings beyond its original intent
- A term is doing too much work in a single sentence ("the request fails when the user is invalid")
- Cross-team integration is stalling on definitional disputes

**Escape hatch**: Don't pedantically redefine terms whose meaning is shared and stable in context. Apply this skill when ambiguity is producing real cost: bugs, mis-implementations, misuses, or recurring clarification questions.

## Core Mindset

Ask:

- What does this term **denote** (the thing it refers to) and **connote** (what it suggests)?
- What is the term's **intension** (defining properties) vs **extension** (the actual set of things it covers)?
- Over what **scope** does this term apply — module, request, session, system, organization?
- Over what **time** does it apply — instantaneous, until next event, persistent?
- Who is the **deictic anchor** — when the spec says "the user," which user, from whose POV, at what moment?
- If I substitute the term with its definition, does every sentence still parse?
- Could a competent stranger build the wrong thing from this name alone?

## Semantic Vocabulary

| Concept | Plain meaning | Software example |
| --- | --- | --- |
| **Denotation** | What the term literally refers to | `User` denotes a row in `users` table |
| **Connotation** | What it suggests culturally/contextually | `User` connotes a *human* — but bots may also be users |
| **Intension** | The defining properties of the concept | "An entity that can authenticate and own resources" |
| **Extension** | The set of things matching the intension | All rows where `kind ∈ {human, bot, service}` |
| **Polysemy** | One word, multiple related meanings | `session` = HTTP session / DB session / debugging session |
| **Homonymy** | One word, unrelated meanings | `lock` = mutex / DB row lock / cryptographic seal |
| **Synonymy** | Different words, same meaning | `delete` / `remove` / `purge` — often *not* truly synonymous |
| **Hyponymy** | Subtype relationship | `OAuthToken` is a hyponym of `Credential` |
| **Scope ambiguity** | Same scope words attach to different operands | "Delete all users with no active subscription" — within an org? globally? |
| **Temporal scope** | When is the predicate true? | "Account is active" — at request time? at billing time? |
| **Deixis** | Context-anchored references ("here", "now", "this") | "the current user" — current as of when, in which thread? |
| **Operational definition** | A definition stated as a procedure that decides membership | "A request is *idle* if no bytes have been received in 30s" |
| **Type–token distinction** | The general kind vs a specific instance | "A retry" (type) vs "the retry that just fired" (token) |
| **Use–mention distinction** | Using a word vs talking about the word | `"deleted"` (the string) vs `deleted` (the state) |
| **Performative** | Language that *does* something by being said | `MERGE`, `commit`, `ack` are performative; their utterance changes state |

## Failure Modes

| Pattern | Symptom | Risk |
| --- | --- | --- |
| **Overloaded term** | One word, multiple contexts | Wrong-context behavior, confused logs |
| **Soft predicate** | "Valid", "ready", "available" without criteria | Each caller checks differently |
| **Hidden temporal scope** | "Is" used when "was at time T" is meant | TOCTOU bugs, cache staleness |
| **Hidden actor** | Passive voice hides the subject ("must be logged") | Ownership unclear, error attribution wrong |
| **Implementation-leak naming** | Product concept named after its current storage | Rename later costs migration |
| **Negation ambiguity** | "Not deleted" — soft-deleted? archived? hidden? | Filters drift over time |
| **Quantifier ambiguity** | "All", "some", "any" with implicit scope | Off-by-one queries, security gaps |
| **Loaded terms** | "Failure", "abuse", "spam" with judgment baked in | Policy disagreements masked as definitional ones |
| **Dialect drift** | Two services use the same term differently | Integration bugs |
| **Stale metaphor** | Term inherited from a deprecated model | Code does X, docs describe Y |

## The Process

### Step 1: Extract the Load-Bearing Terms

Don't audit every word. Pull the **terms that carry contractual weight** — those whose meaning, if wrong, would change behavior or cause a bug.

```
TERMS UNDER REVIEW:
1. [term] — appears in: [spec / API / log / error / DB]
2. ...
```

A term is load-bearing if any of:

- It appears in a public API name, error code, or persisted field
- It is used to make a security/permission decision
- It defines a billable or auditable event
- Two or more components depend on agreeing about it
- It appears in a SLO, contract, or external doc

### Step 2: Surface the Candidate Meanings

For each term, list the meanings actually in use — across code, comments, docs, conversations, and prior incidents.

```
TERM: "session"
- Meaning A (web layer): HTTP session, identified by cookie, lasts ~24h
- Meaning B (SDK):       conversational agent session, identified by sessionId, persists until closed
- Meaning C (ops):       a debugging session, identified by user
- Meaning D (DB):        a connection-pool session
```

If you find more than one meaning, you've already found the bug-in-waiting.

### Step 3: Diagnose the Type of Ambiguity

Match each multi-meaning term to a category from the vocabulary table: polysemy, homonymy, scope ambiguity, temporal scope, deictic, etc. The fix differs by category:

- **Polysemy / homonymy** → split into qualified names (`HttpSession`, `AgentSession`)
- **Scope ambiguity** → make scope explicit in the term (`OrgUser` vs `SystemUser`)
- **Temporal scope** → name the condition with its tense (`isActiveAtRequestTime`)
- **Soft predicate** → replace with operational definition or composite predicate
- **Hidden actor** → switch to active voice; name the subject

### Step 4: Write Operational Definitions

Replace soft adjectives with procedures.

Weak:

> A request is *valid* if it has the required fields.

Strong:

> A request is *valid* iff: (a) `Content-Type` is `application/json`; (b) the body parses as JSON; (c) every field listed in the schema's `required` array is present and matches its declared type; (d) no field outside the schema is present unless `additionalProperties` is true.

A definition is operational when a competent stranger can *execute* it without further interpretation.

### Step 5: Define by Examples *and* Counter-Examples

Examples alone cause overgeneralization. Always pair with counter-examples.

```
TERM: "archived project"
Examples:        - User clicked Archive in the UI
                 - 90 days inactivity auto-archive
Counter-examples:- A deleted project (different state)
                 - A project with archived issues (the project is not archived)
                 - A locked project (read-only but not archived)
```

### Step 6: Align Names with Contracts

For each load-bearing term, check that the *name* the reader sees matches the *contract* the code provides.

| Smell | Fix |
| --- | --- |
| `getX()` mutates / `loadX()` writes | Rename verb to match side effect |
| `isReady()` returns true while still initializing | Operationalize "ready" or rename to `hasMinimalConfig()` |
| `delete(id)` soft-deletes | Rename to `archive(id)` or document the soft-delete contract loudly |
| `User` includes service accounts | Either rename to `Principal`/`Account` or split the type |
| `count` is sometimes `null` for "unknown" | Use `Option<int>` / `count: number \| "unknown"` and name accordingly |

### Step 7: Decide What to Encode vs Document

Prefer mechanically enforced precision over documentation:

| Tool | Use when |
| --- | --- |
| Type system / discriminated unions | Distinguishable types prevent the wrong meaning at compile time |
| Newtype wrappers (`UserId` vs `OrgId`) | Two values that are both strings but must not mix |
| Enum / sealed type for states | A finite, named state space replaces a soft adjective |
| Schema validators | External input must conform to the operational definition |
| Glossary in docs | The term spans systems and a code-level fix isn't possible |
| Deprecation + rename PR | The current name is misleading and the cost of churn < cost of confusion |

### Step 8: Verify by Substitution

Substitute the new precise definition for every occurrence of the term and check that each sentence still makes sense.

If substitution produces nonsense in some uses, you have **discovered another meaning** — go back to Step 2 and split it.

## Output Format

```
SEMANTIC PRECISION REVIEW

Terms under review:
1. [term] — context — load-bearing because:

Detected meanings (per term):
- [term]: A=[...], B=[...], C=[...] — type of ambiguity: [polysemy/scope/temporal/...]

Operational definitions (proposed):
- [term, refined]: [...]
  - examples: ...
  - counter-examples: ...

Renames / contract clarifications:
1. `oldName` → `newName` (because [...])
2. ...

Encoding recommendations:
- Type-level: ...
- Validator: ...
- Glossary entry: ...

Open questions for product/owner:
- ...

Non-goals:
- ...
```

## Anti-Patterns to Avoid

- **Pedantic redefinition**: re-defining terms whose shared meaning is already stable
- **Definition by example only**: examples without counter-examples cause overgeneralization
- **Single-meaning fallacy**: assuming one well-chosen word can carry every variant
- **Glossary theater**: a glossary that says "a *user* is a user of the system"
- **Documenting around bad names**: writing prose to explain a misleading identifier instead of renaming it
- **Implementation-anchored naming**: naming product concepts after their current storage (`mongo_id`, `redis_key_user`)
- **Ignoring temporal scope**: stating predicates in tense-less form when they hold only at specific moments
- **Polite agreement on disputed terms**: nodding through a meeting while two parties mean different things

## Relationship to Other Skills

- Use `formal-invariants` to convert operational definitions into checked rules.
- Use `mental-model-alignment` when the term mismatch reflects a deeper mismatch between the system, developer, and user models.
- Use `code-narrative-review` when names exist but mislead the reader of the code.
- Use `assumption-audit` when an under-specified term hides a load-bearing assumption.
- Use `differential-diagnosis-debugging` when a bug turns out to be a definitional disagreement masquerading as a defect.
