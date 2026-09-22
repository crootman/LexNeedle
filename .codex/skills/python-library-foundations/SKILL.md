---
name: python-library-foundations
description: Configure, package, or modernize LexNeedle as a pure-Python library with Python 3.14+, uv, Ruff, ty, pytest, and uv_build. Use when changing project tooling, pyproject.toml, package layout, dependencies, or CI quality gates.
---

# Python Library Foundations

Use the smallest conventional Python setup that produces a maintainable,
distributable library. LexNeedle targets Python 3.14 and later.

## Project contract

- Use a `src/lexneedle/` layout and ship `src/lexneedle/py.typed`.
- Keep `[project].dependencies` empty unless a maintainer approves a runtime
  dependency. Development tools belong in `[dependency-groups]`.
- Use `uv_build`, `uv`, Ruff, `ty`, pytest, pytest-cov, and pytest-benchmark.
  Do not add mypy, Pyright, Black, Flake8, isort, Poetry, Pipenv, or pyperf.
- Use `uv add` and `uv remove` for dependencies. Commit the generated
  `uv.lock`; never edit it by hand.

## Configuration baseline

Keep configuration in `pyproject.toml` and make its target explicit:

```toml
[project]
requires-python = ">=3.14"
dependencies = []

[build-system]
requires = ["uv_build>=0.12.17,<0.13.0"]
build-backend = "uv_build"

[tool.ruff]
target-version = "py314"
line-length = 100
src = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-ra", "--strict-markers", "--strict-config"]
```

Use `uv add --dev ruff ty pytest pytest-cov pytest-benchmark` for the standard
development toolchain. Add Hypothesis only when a property test protects a
real invariant.

`ty` infers its target Python version from `project.requires-python`; configure
`[tool.ty]` only for real project-specific paths, exclusions, or rule levels.

## Python style and design

- Let Ruff format code and sort imports. Select rules deliberately; never use
  `ALL` or formatter-disabling comments to win an aesthetic argument.
- Prefer direct functions, immutable dataclasses, and shallow composition.
  Introduce a protocol or abstraction only when it removes a demonstrated
  boundary or repeated complexity.
- Use `pathlib`, context managers, module loggers, and narrow chained
  exceptions at actual I/O or failure boundaries. Library code must not
  configure logging or print diagnostic output.
- Use Python 3.14 syntax when it improves clarity, but do not introduce PEP
  695 generics or a hierarchy when ordinary annotations or a function suffice.

## Verification

Run commands through uv from the repository root:

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest
uv build
```

Before a release, inspect both artifacts, confirm `py.typed` is packaged, and
perform a minimal import from the wheel in a clean environment. Use
`uv sync --locked --all-groups` in CI.
