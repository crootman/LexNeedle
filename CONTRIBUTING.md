# Contributing

LexNeedle is a pure-Python, deterministic, Unicode-aware dictionary matcher for
Python 3.14 and later. Contributions should stay small, readable, and
reviewable; production code uses only the standard library.

## Setup

Install [uv](https://docs.astral.sh/uv/) and sync the environment:

```shell
uv sync --all-groups
```

Use `uv add` and `uv remove` for dependencies; never edit `uv.lock` by hand.

## Before you open a pull request

Run the same gate as CI:

```shell
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest
uv build
```

Run focused tests while iterating (`uv run pytest tests/test_matching.py`), then
the full gate. Linux CI also enforces
`uv run pytest --cov=lexneedle --cov-report=term-missing --cov-fail-under=90`.
The benchmark suite in `benchmarks/` is opt-in and separate from correctness
tests; see the README for commands.

## What we look for

- Behavior changes come with focused tests; a bug fix includes a test that
  fails before the fix.
- Every match keeps `text[match.start : match.end] == match.text` for the
  original input string.
- Matching stays deterministic and independent of term insertion order.
- Public behavior, errors, ordering, complexity caveats, and Unicode semantics
  are documented in the same change.
- Normalization, boundary, overlap, replacement, and serialization policies
  stay explicit and local. Prefer a small function or dataclass over a
  registry, framework, or deep hierarchy.

## Ask first

Open an issue before changing:

- public matching semantics;
- the supported Python range or runtime dependencies;
- serialized formats or format versions;
- CI or release publishing;
- benchmark claims or thresholds.

## Commits

Use short conventional-style messages (`fix:`, `feat:`, `docs:`, `perf:`,
`test:`), and keep unrelated changes out of the commit. Do not commit
`.codex/`, `tmp/`, `dist/`, or generated caches.

## Releasing

Releases are tag-driven. The maintainer:

1. updates the version in `pyproject.toml` and prepares release notes;
2. runs the full gate above and inspects `dist/`;
3. pushes a `vX.Y.Z` tag.

`.github/workflows/release.yml` then verifies the tag against the project
version, reruns the gate, smoke-tests both distributions in isolated
environments, and publishes with PyPI Trusted Publishing. The repository needs
a `pypi` environment and a matching Trusted Publisher configured on PyPI before
the first release; no long-lived token is stored.