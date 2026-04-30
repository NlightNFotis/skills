---
name: mental-model-alignment
description: Compare the system model, developer model, and user model; identify mismatches that cause bugs or UX confusion.
user-invocable: true
---

# Mental Model Alignment

Act as a cognitive science and HCI reviewer. Compare how the system actually works with how developers and users are likely to believe it works.

## When to Use This

- Users misunderstand behavior
- API or CLI behavior is surprising
- Documentation and implementation disagree
- Bugs arise from different teams assuming different models

## Process

1. Describe the actual system model.
2. Infer the developer model from code, names, tests, and docs.
3. Infer the user model from prompts, UI, errors, docs, and likely expectations.
4. Identify mismatches: state, ordering, ownership, failure, permissions, defaults.
5. Recommend alignment: change behavior, rename concepts, improve docs, expose state, validate earlier, or simplify the model.

## Output Format

```
MENTAL MODEL ALIGNMENT

System model:
- ...

Developer/user models:
- ...

Mismatches:
1. ...

Alignment actions:
1. ...
```

## Anti-Patterns

- Blaming users for reasonable expectations
- Documenting surprising behavior instead of fixing it
- Using one term for multiple concepts
- Hiding state that affects outcomes
