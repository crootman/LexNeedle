---
name: python-typing
description: Write, review, or configure typed Python 3.14+ for LexNeedle with ty. Use when changing annotations, generics, protocols, public API contracts, or type-checker configuration.
---

# Python Typing with ty

Use `ty` as LexNeedle's only static type checker. Public types are part of the
library contract, not decoration.

## Rules

- Annotate every public function, method, class attribute, and exported
  constant. Keep internal locals inferred unless an annotation adds clarity.
- Prefer built-in generics, `X | None`, `typing.Self`, and `typing.Protocol`
  where they express the real contract. Avoid `Any`; use `object`, a type
  parameter, or a protocol instead.
- Python 3.14 permits PEP 695 syntax. Use it only when a generic abstraction is
  already justified; a one-use type variable or class hierarchy is not an
  improvement.
- Keep runtime imports and annotation imports deliberate. Use
  `typing.TYPE_CHECKING` to avoid imports needed solely for static analysis.
- Suppress a ty diagnostic only with the narrowest available rule and a comment
  explaining why the exception is safe. Never hide a file’s diagnostics.

## Configuration and verification

`ty` reads `[tool.ty]` from `pyproject.toml` and infers Python 3.14 from
`project.requires-python`. Add configuration only for a demonstrated rule,
environment root, or exclusion; do not copy a strictness template blindly.

```bash
uv run ty check
```

Treat a reported type error as an API or control-flow question first. Fix the
types and behavior together rather than adding casts until diagnostics disappear.
