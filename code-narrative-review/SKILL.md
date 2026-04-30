---
name: code-narrative-review
description: Improve readability, conceptual flow, naming, API story, and maintainability of complex code.
user-invocable: true
---

# Code Narrative Review

Act as a literary editor for code. Review how well the code tells its story: what concepts are introduced, in what order, with what names, and whether the reader can predict what comes next.

## When to Use This

- Code works but feels hard to read
- APIs or components have unclear names or responsibilities
- A PR needs maintainability review
- Comments explain symptoms rather than concepts

## Process

1. Identify the main story: what problem does this code solve?
2. List the core concepts and whether names match their roles.
3. Check ordering: are prerequisites introduced before use?
4. Find narrative breaks: surprising side effects, hidden dependencies, abrupt abstraction changes.
5. Distinguish useful comments from comments that compensate for poor structure.
6. Recommend renames, extraction, reordering, or comments that clarify intent.

## Output Format

```
CODE NARRATIVE REVIEW

Core story:
- ...

Confusing moments:
1. ...

Naming issues:
1. ...

Recommended edits:
1. ...
```

## Anti-Patterns

- Polishing style while ignoring conceptual confusion
- Adding comments instead of fixing misleading names
- Hiding the main path among edge cases
- Reviewing formatting rather than readability
