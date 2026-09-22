"""Opt-in, equal-semantics extraction benchmarks."""

from __future__ import annotations

import re

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from lexneedle import Matcher

TERMS = ["alpha", "beta", "gamma", "delta", "epsilon"]
TEXT = "alpha x beta y gamma z delta epsilon " * 200


def _lexneedle_extract(matcher: Matcher, text: str) -> list[object]:
    return [match.value for match in matcher.find(text)]


def test_lexneedle_extract(benchmark: BenchmarkFixture) -> None:
    matcher = Matcher()
    matcher.add_many(TERMS)
    assert _lexneedle_extract(matcher, TEXT) == [term for _ in range(200) for term in TERMS]
    benchmark(_lexneedle_extract, matcher, TEXT)


def test_regex_extract(benchmark: BenchmarkFixture) -> None:
    pattern = re.compile(r"(?<!\w)(?:alpha|beta|gamma|delta|epsilon)(?!\w)", re.IGNORECASE)
    assert pattern.findall(TEXT) == [term for _ in range(200) for term in TERMS]
    benchmark(pattern.findall, TEXT)


def test_flashtext_extract(benchmark: BenchmarkFixture) -> None:
    flashtext = pytest.importorskip("flashtext")
    processor = flashtext.KeywordProcessor(case_sensitive=False)
    processor.add_keywords_from_list(TERMS)
    assert processor.extract_keywords(TEXT) == [term for _ in range(200) for term in TERMS]
    benchmark(processor.extract_keywords, TEXT)


def test_regex_replacement(benchmark: BenchmarkFixture) -> None:
    pattern = re.compile(r"(?<!\w)Big Apple(?!\w)", re.IGNORECASE)
    text = "Big Apple and " * 200
    assert pattern.sub("New York", text).count("New York") == 200
    benchmark(pattern.sub, "New York", text)


def test_flashtext_replacement(benchmark: BenchmarkFixture) -> None:
    flashtext = pytest.importorskip("flashtext")
    processor = flashtext.KeywordProcessor(case_sensitive=False)
    processor.add_keyword("Big Apple", "New York")
    text = "Big Apple and " * 200
    assert processor.replace_keywords(text).count("New York") == 200
    benchmark(processor.replace_keywords, text)
