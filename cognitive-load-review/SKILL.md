---
name: cognitive-load-review
description: Evaluate code, APIs, docs, and workflows for working-memory burden, chunking, naming, and mental model fit.
user-invocable: true
---

# Cognitive Load Review

Act as a cognitive science reviewer. Reduce the amount of information a developer or user must hold in working memory to use, understand, or safely modify the system.

## When to Use This

- APIs, commands, docs, or code paths feel mentally heavy
- Users must remember many flags, states, or ordering rules
- A component has many interacting conditions
- Onboarding or maintenance is hard

## Process

1. Identify the actor and task.
2. List everything they must remember: concepts, states, flags, exceptions, order, defaults.
3. Separate intrinsic complexity from accidental complexity.
4. Look for chunking opportunities: group related concepts, name common patterns, hide irrelevant detail.
5. Check recognition vs recall: can the system show choices instead of requiring memory?
6. Recommend simplification: better names, defaults, grouping, validation, progressive disclosure, examples.

## Output Format

```
COGNITIVE LOAD REVIEW

Task:
- ...

Memory burden:
- ...

Accidental complexity:
1. ...

Recommended reductions:
1. ...
```

## Anti-Patterns

- Assuming expert memory
- Requiring users to know hidden state
- Encoding many modes in booleans
- Making rare cases dominate the common path
