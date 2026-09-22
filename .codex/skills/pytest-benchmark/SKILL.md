---
name: pytest-benchmark
description: Measure or compare LexNeedle performance with pytest-benchmark. Use when adding a benchmark, investigating a regression, comparing matcher approaches, or making a performance claim.
---

# Python Benchmarking with pytest-benchmark

Measure correctness first, then measure one clearly named operation with
pytest-benchmark. Never add pyperf or a one-off wall-clock loop.

## Benchmark contract

State the operation, dictionary and input sizes, expected result, Python and
dependency versions, platform, and commit. Separate matcher construction from
matching, iteration, replacement, and memory questions.

For LexNeedle, cover no-match, few-match, many-match, shared-prefix,
long-keyword, Unicode, boundary, and case-policy workloads. Keep each workload
small enough to identify what changed; do not combine a 100,000-term dictionary
and a 10 MB input into every benchmark.

## Pattern

Use fixed or seed-recorded fixtures and assert equivalence before timing:

```python
def test_find_large_dictionary(benchmark: object) -> None:
    matcher = build_matcher()
    text = load_text()
    assert matcher.find(text) == expected_matches

    benchmark(matcher.find, text)
```

Use the actual pytest-benchmark fixture annotation supplied by the installed
version when type checking benchmark tests. Do not fabricate a protocol merely
to annotate a test helper.

Run a focused benchmark with pytest, for example:

```bash
uv run pytest benchmarks/test_find.py --benchmark-only
```

Use pytest-benchmark’s saved-data and comparison options when the repository
adopts a baseline workflow. Do not report a speedup from a single favorable run.

## Interpretation

Compare only equal semantics: the same terms, text, normalization, boundaries,
case policy, result shape, and warm-up behavior. Record instability and rerun
under comparable conditions rather than discarding inconvenient results.

Performance claims need a reproducible command and environment context. Keep
benchmarks out of the ordinary correctness gate unless the project explicitly
sets a stable performance policy.
