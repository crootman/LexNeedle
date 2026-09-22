"""Configurable construction, matching, replacement, and memory workloads.

Run this file explicitly. The default matrix is intentionally small; set
``LEXNEEDLE_BENCHMARK_LARGE=1`` to include 10,000 and 100,000-term dictionaries
and a 10 MB input. The default input matrix includes small, paragraph, and 1 MB
texts. Each test isolates one operation rather than a cartesian product.
"""

from __future__ import annotations

import os
import tracemalloc

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from lexneedle import Matcher

SIZES = [10, 100, 1_000]
if os.environ.get("LEXNEEDLE_BENCHMARK_LARGE") == "1":
    SIZES.extend([10_000, 100_000])


def _terms(size: int) -> list[str]:
    return [f"keyword{index:06d}" for index in range(size)]


def _matcher(size: int) -> Matcher:
    matcher = Matcher()
    matcher.add_many(_terms(size))
    return matcher


@pytest.mark.parametrize("size", SIZES)
def test_construction(benchmark: BenchmarkFixture, size: int) -> None:
    benchmark(_matcher, size)


@pytest.mark.parametrize("size", SIZES)
def test_dictionary_size_matching(benchmark: BenchmarkFixture, size: int) -> None:
    matcher = _matcher(size)
    text = f"keyword{size - 1:06d} "
    assert [match.text for match in matcher.find(text)] == [text[:-1]]
    benchmark(matcher.find, text)


@pytest.mark.parametrize(
    "workload", ["no_match", "few_match", "many_match", "shared_prefix", "long"]
)
def test_extraction_workloads(benchmark: BenchmarkFixture, workload: str) -> None:
    matcher = Matcher(boundary="none")
    matcher.add_many(["needle", "need", "prefix-a", "prefix-ab", "very-long-keyword-value"])
    texts = {
        "no_match": "haystack " * 200,
        "few_match": "haystack " * 100 + "needle" + " haystack " * 100,
        "many_match": "needle " * 200,
        "shared_prefix": "prefix-ab " * 200,
        "long": "very-long-keyword-value " * 100,
    }
    expected = {
        "no_match": [],
        "few_match": ["needle"],
        "many_match": ["needle"] * 200,
        "shared_prefix": ["prefix-ab"] * 200,
        "long": ["very-long-keyword-value"] * 100,
    }
    assert [match.text for match in matcher.find(texts[workload])] == expected[workload]
    benchmark(matcher.find, texts[workload])


def test_replacement(benchmark: BenchmarkFixture) -> None:
    matcher = Matcher()
    matcher.add("Big Apple", "New York")
    text = "Big Apple and " * 200
    assert matcher.replace(text) == "New York and " * 200
    benchmark(matcher.replace, text)


def _peak_bytes(size: int) -> int:
    tracemalloc.start()
    _matcher(size)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


@pytest.mark.parametrize("size", SIZES)
def test_dictionary_memory(benchmark: BenchmarkFixture, size: int) -> None:
    peak = _peak_bytes(size)
    assert peak > 0
    benchmark.extra_info["peak_bytes"] = peak
    benchmark(_peak_bytes, size)


INPUT_SIZES = [("small", 10), ("paragraph", 500), ("one_megabyte", 150_000)]
if os.environ.get("LEXNEEDLE_BENCHMARK_LARGE") == "1":
    INPUT_SIZES.append(("ten_megabytes", 1_500_000))


@pytest.mark.parametrize(("name", "repeats"), INPUT_SIZES)
def test_input_sizes(benchmark: BenchmarkFixture, name: str, repeats: int) -> None:
    matcher = Matcher()
    matcher.add("needle")
    text = "needle " * repeats
    assert [match.text for match in matcher.find(text)] == ["needle"] * repeats
    benchmark.extra_info["input_bytes"] = len(text.encode())
    benchmark(matcher.find, text)


@pytest.mark.parametrize("case_sensitive", [False, True])
def test_unicode_case_policy(benchmark: BenchmarkFixture, case_sensitive: bool) -> None:
    matcher = Matcher(case_sensitive=case_sensitive, unicode_normalization="NFC")
    matcher.add("CAFÉ")
    text = "cafe\u0301 " * 500 if not case_sensitive else "CAFÉ " * 500
    assert len(matcher.find(text)) == 500
    benchmark(matcher.find, text)
