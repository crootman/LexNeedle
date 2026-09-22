---
name: python-testing
description: Design or review LexNeedle tests with pytest, pytest-cov, pytest-benchmark, fixtures, parametrization, regression tests, and Hypothesis. Use when changing Python behavior, fixing a bug, or measuring a benchmarked behavior.
---

# Python Testing for LexNeedle

Use pytest to turn public behavior into durable evidence. Tests must be
deterministic, independent, and readable without an implementation tour.

## Workflow

1. Read neighboring tests and the current public contract first.
2. For a behavior change or bug, write a focused test that fails for the
   intended reason.
3. Implement the smallest correct change, run the focused test, then run the
   relevant suite.
4. Assert outcomes, exceptions, spans, and serialized values—not trie layout
   or private helper calls.

Prefer the real collaborator, then a small fake, then a mock at an external
boundary. Use fixtures only for shared setup and `tmp_path` for filesystem
tests. Parametrize a compact, named matrix instead of duplicating equivalent
test functions.

## LexNeedle priorities

Every matcher change should consider empty, duplicate, repeated, and shared
prefix terms; overlap resolution; insertion-order independence; boundaries;
case folding; normalization; aliases; replacement; and serialization.

Every result must satisfy:

```python
text[match.start:match.end] == match.text
```

For Unicode transformations, use the `unicode-text-matching` skill before
choosing the test cases or implementation strategy.

## Property and benchmark tests

Add Hypothesis only as a development dependency and only when it protects a
meaningful invariant. Keep a small named regression test for every discovered
failure. High-value properties include deterministic repeated calls, iterator
and list API agreement, source-span validity, and serialization round trips.

Use pytest-benchmark for benchmark tests. Keep them separate from ordinary
correctness assertions, use fixed or seeded data, and record the matcher
configuration and expected result. See `pytest-benchmark` for methodology.

## Verification

```bash
uv run pytest tests/path/to/focused_test.py
uv run pytest
```

Do not skip a failing test to make CI green. Register any custom markers in
`pyproject.toml`, and do not make normal tests depend on the network, clock, or
machine-local state.
