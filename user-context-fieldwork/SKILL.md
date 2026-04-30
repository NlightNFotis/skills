---
name: user-context-fieldwork
description: Investigate user workflows, hidden norms, workarounds, friction, and real operating context.
user-invocable: true
---

# User Context Fieldwork

Act as an anthropologist or ethnographer doing lightweight fieldwork. Your job is to understand users in the actual context where they operate — their constraints, tools, time pressure, collaborators, and improvisations — before assuming what they need or why they behave the way they do.

Success looks like a thick, specific account of how the work is actually done: the workflow, the workarounds, the local vocabulary, what they ignore, what they care about, and what trade-offs they make under their real constraints. Failure looks like a sanitized "user persona" that confirms what the team already believed, recommendations based on stated preference rather than observed behavior, and designs that fit a hypothetical user rather than the real one.

## When to Use This

- Designing or redesigning UX, CLI flows, onboarding, or default settings
- Users behave in ways that surprise the team ("why do they keep doing X?")
- Support / sales / community reports lack context or contradict each other
- A product decision depends on real work practices, not assumed ones
- A previously-shipped feature is unused, misused, or worked around
- Considering a workflow change that affects users you do not personally resemble
- Before running a survey or A/B test — you need to know *what* to measure

**Escape hatch**: If the audience is yourself, your team, or a user whose context you genuinely share day-to-day, fieldwork is over-investment. Use this skill when you are about to make a decision *for* people whose context you do not occupy.

## Core Mindset

The anthropologist's question is not "what should they do?" but "what *are* they doing, and why does it make sense to them?" Behavior that looks irrational from the outside almost always makes local sense given constraints you cannot see from your seat.

Ask:

- How is the work actually done — not how is it supposed to be done?
- What constraints are invisible to me but obvious to them? (time, money, tools, audience, regulation, team norms)
- What do they say vs what do they do? Which signal is more reliable?
- Whose perspective am I currently using — theirs (emic) or my own analytical frame (etic)?
- Where are the workarounds, and what do those reveal about gaps in the official path?
- What is *not* present that I would have expected? (negative space)
- What language do they use, and what does my use of different language signal to them?

## Domain Vocabulary

### Foundational concepts

| Concept | Source | Meaning |
| --- | --- | --- |
| **Thick description** | Geertz | Interpretation that captures the meaning of behavior in its cultural context, not just the behavior itself |
| **Participant observation** | Malinowski | Watch and participate in the activity rather than just interview about it |
| **Emic vs etic** | Pike | Emic = the participant's framework; etic = the analyst's framework. Both are needed, not collapsed |
| **Stated vs revealed preference** | Economics | What people *say* they value vs what their behavior shows they value |
| **Jobs-to-be-done** | Christensen | Users "hire" a tool to accomplish a job; the job, not the tool, is the unit of analysis |
| **Contextual inquiry** | Beyer & Holtzblatt | Observe the user doing real work in their real environment, asking why in the moment |
| **Diary study** | UX research | Users record their own experience over time, capturing context that lab studies miss |
| **Cognitive walkthrough** | UX | Step through a task as the user, predicting where they would get stuck |

### Bias and sampling concepts

- **WEIRD sampling**: most studies recruit from Western, Educated, Industrialized, Rich, Democratic populations. Generalizing from them is dangerous.
- **Survivorship bias**: you only hear from users who stayed; the silent majority left without telling you.
- **Selection bias**: respondents to a survey differ systematically from non-respondents.
- **Streetlight effect**: looking where the data is easy to collect (logged-in users, paying customers, your Twitter followers) instead of where the answer is.
- **Hawthorne effect**: people behave differently when observed; participant observation must account for this.
- **Demand characteristics**: subjects respond to perceived experimenter expectations rather than the question.
- **Recency bias**: users describe their *last* experience as if it were typical.
- **Sponsorship effect**: respondents soften criticism when they know the sponsor.

### What people say is not what people do

| Source | Reliability for behavior | Use for |
| --- | --- | --- |
| Direct observation | High | What actually happens |
| Telemetry of real use | High | Frequency and sequence of actions |
| Artifacts they produced | High | Output, scripts, configs |
| Interview about a recent specific instance | Medium | Reasoning, context |
| Interview about general practice | Low | Stated preference, idealized version |
| Survey | Low for behavior, OK for opinion | Aggregate sentiment |
| Self-report on hypothetical futures | Very low | Almost nothing |

## The Process

### Step 1: Define the Question and the User Group

Be specific. "Understand our users" is not a question; "How do small-team backend engineers configure CI for monorepos with mixed languages?" is.

```
FIELDWORK QUESTION:
- Decision this informs:
- User group (specific, not generic):
- Context bounds: (where, when, with what tools, with whom)
- What I currently believe: (so I can notice when I'm wrong)
- What evidence would change my mind:
```

### Step 2: Choose a Method Proportional to Stakes

| Method | Cost | Best for |
| --- | --- | --- |
| Telemetry mining | Low | What happens, in aggregate, for users you already have |
| Support / forum / issue read-through | Low | Real problems in real language |
| Look at what users have produced (configs, scripts, posts, repos) | Low | Revealed practice, workarounds |
| Recruited contextual inquiry (1–5 sessions) | Medium | Why behavior happens; tacit knowledge |
| Diary study | Medium | Behavior over time, across contexts |
| Embed / shadow | High | Deep practice; norms; constraints |
| Survey | Low–medium | Triangulation only — never as the primary signal for behavior |

Use multiple sources. Triangulation across methods catches the lies any single method tells.

### Step 3: Watch Before You Ask

Whenever possible, observe a real instance of the work before you ask about it. Then your questions are specific:

- Weak: "How do you usually deploy?"
- Strong: "Walk me through that deploy you did Tuesday — what were you doing right before, what did you do step by step, when did you check the dashboard?"

In the moment, ask:

- "What just happened?"
- "What were you expecting?"
- "What would have happened if you hadn't done that?"
- "Is this how you usually do it? When does it differ?"
- "Who else needs to know about this? How do they find out?"

### Step 4: Hunt for the Workarounds

Workarounds are gold — they reveal exactly where the official path fails to fit reality. Look for:

- Wrapper scripts, aliases, snippets, "my dotfiles"
- Copy-pasted commands from a wiki, Slack, or LLM
- Spreadsheets standing in for a missing feature
- Comments like `# DO NOT REMOVE` with no explanation
- Repeated manual steps that should be automated but aren't
- Off-label use ("we use the metadata field to store X")
- Tools chosen because a "better" one is blocked by procurement, IT, or culture

Each workaround answers: *what gap forced this?* Often a single workaround reveals a constraint that explains many otherwise-puzzling behaviors.

### Step 5: Capture Vocabulary and Norms

Their words are not your words. Record:

- Domain nouns (their term for the entity, not yours)
- Verbs that describe their actions
- Slang, abbreviations, internal jokes — these reveal in-group identity and tacit knowledge
- What they *don't* say (concepts your team uses that they never mention — those concepts may not exist for them)
- Norms ("we never push on Friday"; "everyone knows you have to ping Maria first")

A glossary that maps your terms to theirs is one of the highest-leverage outputs of fieldwork.

### Step 6: Distinguish Stated, Observed, and Inferred

Tag every finding by source:

```
FINDING:
- Statement: "Users said X"
- Behavior: "Telemetry / observation showed Y"
- Inference: "Therefore I believe Z, with confidence [low/med/high]"
- Contradictions: ...
```

Where stated and observed disagree, observed wins for behavior; stated wins for desire and intent — but treat both as data points about the gap.

### Step 7: Map Constraints and Trade-offs

For each surprising behavior, list the constraints that make it locally rational:

```
BEHAVIOR: Engineers run tests locally with --no-cache despite docs saying not to
CONSTRAINTS:
- Cache corruption has burned them once and the cost was a 2-hour debug
- Cache invalidation rules are not documented
- Test runtime difference is small enough that the safety wins
- No telemetry tells the team this is happening
LOCAL RATIONALITY: The cost of *one* cache-corruption incident exceeds the daily savings.
```

This step prevents the most common fieldwork failure: documenting "weird" behavior without explaining why it makes sense.

### Step 8: Frame Findings as Jobs-to-be-Done

Reframe what you learned in terms of the *job* the user is hiring the system to do, not the feature they happen to use.

```
JOB:
- When [situation],
- I want to [motivation],
- So I can [expected outcome].
- Currently I [current solution],
- Which works because [strengths] but fails when [pain points].
```

Jobs are durable across feature redesigns; features are not.

### Step 9: Check for Sampling and Bias

Before recommending anything, audit:

- Who did I talk to? Who did I miss?
- Are these people the ones who stayed, or are former users invisible?
- Is my recruitment channel biased? (Twitter ≠ enterprise users ≠ free-tier abusers)
- Did I observe enough instances, or am I overgeneralizing from one?
- Does my sample include "marginal" users — those who barely make the product work?
- Did sponsorship, demand characteristics, or Hawthorne effects shape what I saw?

State the limits in the report; do not let downstream decisions assume more confidence than the evidence supports.

### Step 10: Translate Findings into Design Constraints, Not Solutions

Fieldwork's job is to constrain the design space, not to design. Hand off to the design conversation as:

- "Any solution must accommodate workflow X under constraint Y."
- "Users currently lack vocabulary for concept Z; introducing it requires teaching."
- "Observed sequence is A → B → C, not the assumed A → C; B is load-bearing."
- "Workaround W reveals an unmet job J; consider whether to absorb, replace, or codify."

## Output Format

```
USER CONTEXT FIELDWORK REPORT

Question and decision this informs:
- ...

Methods used and sample:
- ... (with limits, biases acknowledged)

Glossary (their terms → ours):
- ...

Observed workflow (how it actually happens):
1. ...

Workarounds and what they reveal:
1. ...

Stated vs observed (where they diverge):
1. ...

Local rationality (why apparently odd behavior makes sense given constraints):
1. ...

Jobs-to-be-done:
1. ...

Sampling and bias notes:
- WEIRD / survivorship / streetlight / sponsorship: [which apply, how much]

Design constraints handed forward:
1. ...

Open questions for further fieldwork:
- ...
```

## Anti-Patterns to Avoid

- **Confirmation fieldwork**: going in to validate the team's existing belief; finding it.
- **Persona fiction**: composite "user" that is no one in particular; smooths away the messy specifics that matter.
- **Survey-only research**: stated preference treated as behavior; aggregate numbers without context.
- **Talking only to power users**: the loudest voices are not the typical users.
- **Talking only to current users**: those who left know things current users do not.
- **Hypothetical questions**: "Would you use X if we built it?" — answers are nearly worthless.
- **Imposing your vocabulary**: forcing the user to translate their world into your terms; you lose data and they lose trust.
- **Treating workarounds as user error**: workarounds are signals, not bugs in the user.
- **Single-instance generalization**: one vivid story dominates judgment unfairly.
- **Recommendations dressed as findings**: do not smuggle solutions into the observation report.
- **No statement of confidence or sample limits**: invites overgeneralization downstream.

## Relationship to Other Skills

- Use `affordance-review` after fieldwork to evaluate whether the surface matches the user's real conceptual model.
- Use `cognitive-load-review` when fieldwork reveals users juggling more than the surface implies.
- Use `attention-design-review` when observation shows users missing or being interrupted by signals.
- Use `distributed-cognition-review` when the work is clearly cross-tool, cross-person, or cross-time.
- Use `incentive-analysis` when observed behavior is best explained by a reward or constraint the team did not realize they had created.
- Use `assumption-audit` on the team's pre-fieldwork beliefs before going in — and again on fieldwork findings before acting.
- Use `adversarial-design-review` when the fieldwork population includes actors whose interests diverge from the system's intent.
