# LexNeedle agent guide

LexNeedle is a pure-Python, deterministic, Unicode-aware dictionary matching
library intended for publication on PyPI. Favour simple, readable code that is
easy to review and maintain.

## Non-negotiable constraints

- Support Python 3.14 and later. Use Python 3.14 features only when they make
  the public code clearer; do not add compatibility shims for older Python.
- Keep production dependencies in the standard library unless a maintainer
  explicitly approves a user-facing dependency.
- Use `uv` for interpreters, environments, dependencies, locking, commands,
  builds, and publishing. Use `uv add` or `uv remove`; never hand-edit
  `uv.lock`.
- Use Ruff for formatting and linting, `ty` for static type checking, pytest
  for tests, pytest-cov for coverage, and pytest-benchmark for benchmarks.
- Do not add mypy, Pyright, Black, Flake8, isort, Poetry, Pipenv, or pyperf.

## Project workflow

Before changing behaviour, read the relevant public contract, neighboring
tests, and the focused skill. Plan only when a change is ambiguous, public,
or substantial; otherwise make the smallest complete change and verify it.

Use the repository configuration rather than guessing commands. The normal
quality gate is:

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest
uv build
```

Run focused tests while iterating, then the relevant final checks. Do not
claim a command passed unless it was run. Inspect wheel and source-distribution
contents before a release.

## Library contracts

- Public APIs must be fully typed and documented where callers need behavior,
  errors, ordering, or performance guarantees.
- Matching must be deterministic and must not depend on term insertion order
  unless the public API explicitly documents that rule.
- Public offsets always index the original Python string:

  ```python
  text[match.start : match.end] == match.text
  ```

- Keep transformed matching text separate from source text. Case folding and
  normalization need explicit alignment back to original offsets.
- Keep boundary, normalization, matching, replacement, and serialization
  policies explicit. Prefer a small function or dataclass over a framework,
  registry, or premature class hierarchy.
- Treat serialized content and user-provided metadata as untrusted. Do not use
  pickle as the default serialization format.

## Ask before

Ask before changing public matching semantics, the Python support range,
runtime dependencies, serialized formats, CI/release publishing, or benchmark
claims and thresholds. Preserve unrelated working-tree changes.

## Focused skills

- `python-library-foundations`: project configuration, package structure, and Python style.
- `python-typing`: `ty`-checked public typing.
- `python-testing`: pytest, regression tests, and Hypothesis.
- `unicode-text-matching`: normalization, boundaries, and source offsets.
- `pytest-benchmark`: pytest-benchmark methodology.
- `python-docs` and `python-release`: public documentation and PyPI releases.
- `lexneedle-workflow`: lightweight planning and incremental implementation.
- `lexneedle-quality-review`: final review and AI-specific failure-mode checks.
