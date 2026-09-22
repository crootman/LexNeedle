---
name: python-docs
description: Write or review LexNeedle public documentation, docstrings, examples, and changelog-facing behavior notes. Use when changing a public API, error behavior, examples, README content, or package documentation.
---

# Python Documentation for LexNeedle

Document the contract a caller needs to use safely: behavior, ordering,
boundaries, errors, complexity caveats, and Unicode semantics. Do not narrate
obvious implementation steps or repeat type annotations in prose.

## Public API documentation

- Give exported modules, classes, functions, and configuration options concise
  docstrings when their behavior is not obvious from name and signature.
- Use a short summary followed by `Args:`, `Returns:`, and `Raises:` sections
  only when they add useful contract information.
- Keep the README’s quick start executable and importable from the built
  package. Use examples to demonstrate the primary public API, not internals.
- Update documentation in the same change as public behavior, matching
  semantics, serialization, or supported-version changes.

## LexNeedle-specific contract

Document case policy, normalization order, boundaries, overlap strategy,
insertion-order guarantees, and that `start` and `end` index the original
Python string. State limitations rather than claiming full Unicode segmentation
conformance without implementing it.

## Review

Verify examples against the actual package. Apply Ruff docstring rules only
after the project chooses a stable convention; do not add a blanket lint rule
that forces low-value prose into every internal helper.
