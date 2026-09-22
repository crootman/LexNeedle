---
name: lexneedle-quality-review
description: Review a LexNeedle implementation, fix, refactor, or dependency update before declaring it complete. Use for prioritized findings across correctness, Unicode semantics, failure modes, design, security, performance, tests, and packaging.
---

# Code Review and Quality

Review behavior and risk, not personal style. Report findings first, ordered as
`Critical`, `Required`, or `Optional`, with a file/line, concrete impact, and
the smallest practical remedy. A clean review is valid.

## Review sequence

1. Read the task, public contract, changed tests, and enough surrounding code
   to understand the intended boundary.
2. Check that each new behavior has a focused test and each bug has a test that
   would have failed before the fix.
3. Inspect correctness, types, failure paths, dependencies, performance, and
   package contents. Do not expand the review into unrelated cleanup.

## LexNeedle checks

- Every match preserves the original source slice:

  ```python
  text[match.start:match.end] == match.text
  ```

- Empty, duplicate, shared-prefix, overlapping, Unicode, and repeated-call
  cases are deterministic and do not depend on term insertion order.
- Case folding or normalization never exposes transformed-buffer offsets.
- Boundary, replacement, alias, metadata, and serialization behavior are
  explicit and covered at the public boundary.
- The implementation remains Python 3.14+, standard-library-only at runtime,
  and free of needless registries, frameworks, or deep inheritance.

## AI-change failure-mode scan

Check the paths plausible implementations often omit: malformed input,
invalid configuration, huge terms or inputs, resource cleanup, recursion depth,
serialization failures, type escapes, and imports not present in the locked
environment. Do not swallow broad exceptions or convert failures to empty
results. Never use pickle as the default parser for untrusted data.

Review every new dependency for a standard-library alternative, Python 3.14
support, license, maintenance, provenance, and the generated lockfile diff.
Runtime dependencies require maintainer approval.

## Final evidence

Run the focused test first, then the relevant quality gate:

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest
uv build
```

For packaging or release work, inspect the wheel and source distribution and
test a clean installation. State exactly what was run and what remains
unverified.
