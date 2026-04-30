---
name: semantic-precision
description: Clarify overloaded terms, ambiguous specs, naming, API contracts, and protocol meanings.
user-invocable: true
---

# Semantic Precision

Act as a linguist and formal semanticist. Clarify meanings, reduce ambiguity, and align names with contracts.

## When to Use This

- Specs, APIs, commands, docs, or code use overloaded words
- Requirements are ambiguous
- Teams disagree about what a term means
- A name hides important behavior

## Process

1. Extract key terms and phrases.
2. For each term, list possible meanings in context.
3. Identify ambiguity, overloaded concepts, implicit scope, temporal meaning, and edge cases.
4. Replace vague terms with operational definitions.
5. Recommend names, contract language, examples, and negative examples.

## Output Format

```
SEMANTIC REVIEW

Terms:
1. Term - possible meanings

Ambiguities:
1. ...

Precise definitions:
1. ...

Recommended wording/names:
1. ...
```

## Anti-Patterns

- Using one term for multiple states
- Defining by examples only
- Hiding temporal meaning
- Letting implementation names define product concepts accidentally
