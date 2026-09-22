"""Reproducible public-API performance evidence for :class:`lexneedle.Matcher`.

Run the fast subset with ``uv run pytest benchmarks/test_matrix.py --benchmark-only``.
Set ``LEXNEEDLE_BENCHMARK_LARGE=1`` for 10,000/100,000-term dictionaries and
1/10 MiB inputs. The matcher benchmarks use only public APIs, so they also run
against a baseline with ``PYTHONPATH=/path/to/baseline/src``.
"""

from __future__ import annotations

import os
import platform
import random
import sys
import tracemalloc
import unicodedata
from collections.abc import Callable
from pathlib import Path
from typing import Literal, cast

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from lexneedle import Match, Matcher
from lexneedle.normalize import transform

type Strategy = Literal["all", "longest", "leftmost_longest"]

_SEED = 24_680
_FAST_SIZES = (10, 100, 1_000)
LONG_TERM = "long-" + "x" * 512
LONG_NEAR_MISS = "long-" + "x" * 511 + "y"


def _large_enabled() -> bool:
    return os.environ.get("LEXNEEDLE_BENCHMARK_LARGE") == "1"


SIZES = _FAST_SIZES + ((10_000, 100_000) if _large_enabled() else ())
INPUT_SIZES = (("one_kib", 1_024), ("one_hundred_kib", 100 * 1_024)) + (
    (("one_mebibyte", 1_024**2), ("ten_mebibytes", 10 * 1_024**2)) if _large_enabled() else ()
)


def _record(
    benchmark: BenchmarkFixture,
    *,
    operation: str,
    dictionary_size: int,
    text: str = "",
    expected_matches: int = 0,
    configuration: str = "default",
) -> None:
    """Attach comparison-relevant facts to the saved benchmark result."""
    benchmark.extra_info.update(
        operation=operation,
        dictionary_size=dictionary_size,
        input_characters=len(text),
        input_utf8_bytes=len(text.encode("utf-8")),
        expected_matches=expected_matches,
        configuration=configuration,
        seed=_SEED,
        python=sys.version.split()[0],
        platform=platform.platform(),
    )


def _seeded_terms(size: int) -> list[str]:
    """Return unique varied terms with a deterministic, recorded seed."""
    generator = random.Random(_SEED)
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return [
        f"term-{index:06d}-{''.join(generator.choice(alphabet) for _ in range(12))}"
        for index in range(size)
    ]


def _build_matcher(terms: list[str]) -> Matcher:
    matcher = Matcher()
    matcher.add_many(terms)
    return matcher


def _matcher(size: int) -> Matcher:
    return _build_matcher(_seeded_terms(size))


def _matches(matcher: Matcher, text: str, strategy: Strategy | None = None) -> list[Match]:
    return matcher.find(text, strategy=strategy)


def _consume_finditer(matcher: Matcher, text: str, strategy: Strategy) -> int:
    return sum(1 for _ in matcher.finditer(text, strategy=strategy))


def _peak_bytes(operation: Callable[[], object]) -> tuple[object, int, int]:
    tracemalloc.start()
    try:
        result = operation()
        retained, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, retained, peak


@pytest.mark.parametrize("size", SIZES)
def test_construction(benchmark: BenchmarkFixture, size: int) -> None:
    terms = _seeded_terms(size)
    _record(benchmark, operation="construction", dictionary_size=size)
    benchmark(_build_matcher, terms)


@pytest.mark.parametrize("size", SIZES)
def test_varied_dictionary_one_hit(benchmark: BenchmarkFixture, size: int) -> None:
    terms = _seeded_terms(size)
    matcher = _build_matcher(terms)
    text = f"before {terms[-1]} after"
    assert len(_matches(matcher, text)) == 1
    _record(benchmark, operation="find", dictionary_size=size, text=text, expected_matches=1)
    benchmark(matcher.find, text)


@pytest.mark.parametrize("workload", ["no_match", "few_match", "many_match"])
def test_match_density_workloads(benchmark: BenchmarkFixture, workload: str) -> None:
    terms = _seeded_terms(500)
    matcher = Matcher()
    matcher.add_many(terms)
    texts = {
        "no_match": "absent-token " * 200,
        "few_match": "absent-token " * 80 + terms[12] + " absent-token " * 80 + terms[345],
        "many_match": (terms[3] + " ") * 200,
    }
    expected = {
        "no_match": [],
        "few_match": [terms[12], terms[345]],
        "many_match": [terms[3]] * 200,
    }
    text = texts[workload]
    assert [match.text for match in _matches(matcher, text)] == expected[workload]
    _record(
        benchmark,
        operation=f"find_{workload}",
        dictionary_size=len(terms),
        text=text,
        expected_matches=len(expected[workload]),
    )
    benchmark(matcher.find, text)


@pytest.mark.parametrize("workload", ["shared_prefix_hit", "shared_prefix_near_miss"])
def test_shared_prefix_workloads(benchmark: BenchmarkFixture, workload: str) -> None:
    matcher = Matcher(boundary="none")
    matcher.add_many(
        [
            "machine",
            "machine learning",
            "machine learning model",
            "machine learning model training",
        ]
    )
    texts = {
        "shared_prefix_hit": "machine learning model training " * 80,
        "shared_prefix_near_miss": "machine learning model traininx " * 80,
    }
    expected = {
        "shared_prefix_hit": ["machine learning model training"] * 80,
        "shared_prefix_near_miss": ["machine learning model"] * 80,
    }
    text = texts[workload]
    assert [match.text for match in _matches(matcher, text)] == expected[workload]
    _record(
        benchmark,
        operation=f"find_{workload}",
        dictionary_size=len(matcher),
        text=text,
        expected_matches=len(expected[workload]),
        configuration="boundary=none,strategy=leftmost_longest",
    )
    benchmark(matcher.find, text)


@pytest.mark.parametrize("workload", ["long_hit", "long_near_miss"])
def test_hundreds_character_keyword(benchmark: BenchmarkFixture, workload: str) -> None:
    matcher = Matcher(boundary="none")
    matcher.add(LONG_TERM)
    texts = {"long_hit": (LONG_TERM + " ") * 24, "long_near_miss": (LONG_NEAR_MISS + " ") * 24}
    expected = {"long_hit": [LONG_TERM] * 24, "long_near_miss": []}
    text = texts[workload]
    assert [match.text for match in _matches(matcher, text)] == expected[workload]
    _record(
        benchmark,
        operation=f"find_{workload}",
        dictionary_size=1,
        text=text,
        expected_matches=len(expected[workload]),
        configuration="boundary=none,keyword_characters=517",
    )
    benchmark(matcher.find, text)


@pytest.mark.parametrize("strategy", ["all", "longest", "leftmost_longest"])
def test_overlap_strategies(benchmark: BenchmarkFixture, strategy: Strategy) -> None:
    matcher = Matcher(boundary="none")
    matcher.add_many(["a", "ab", "aba", "bab"])
    text = "ababa " * 100
    expected = {"all": 800, "longest": 400, "leftmost_longest": 200}
    assert len(_matches(matcher, text, strategy)) == expected[strategy]
    _record(
        benchmark,
        operation="find_overlap",
        dictionary_size=len(matcher),
        text=text,
        expected_matches=expected[strategy],
        configuration=f"boundary=none,strategy={strategy}",
    )
    benchmark(matcher.find, text, strategy=strategy)


@pytest.mark.parametrize("strategy", ["all", "longest", "leftmost_longest"])
def test_finditer_strategies(benchmark: BenchmarkFixture, strategy: Strategy) -> None:
    matcher = Matcher(boundary="none")
    matcher.add_many(["a", "ab", "aba", "bab"])
    text = "ababa " * 100
    expected = {"all": 800, "longest": 400, "leftmost_longest": 200}
    assert _consume_finditer(matcher, text, strategy) == expected[strategy]
    _record(
        benchmark,
        operation="finditer_consume",
        dictionary_size=len(matcher),
        text=text,
        expected_matches=expected[strategy],
        configuration=f"boundary=none,strategy={strategy}",
    )
    benchmark(_consume_finditer, matcher, text, strategy)


def test_replacement(benchmark: BenchmarkFixture) -> None:
    matcher = Matcher()
    matcher.add("Big Apple", "New York")
    text = "Big Apple and " * 200
    expected = "New York and " * 200
    assert matcher.replace(text) == expected
    _record(benchmark, operation="replace", dictionary_size=1, text=text, expected_matches=200)
    benchmark(matcher.replace, text)


@pytest.mark.parametrize(("name", "size"), INPUT_SIZES)
def test_no_match_input_sizes(benchmark: BenchmarkFixture, name: str, size: int) -> None:
    matcher = Matcher()
    matcher.add("needle")
    text = "x" * size
    assert _matches(matcher, text) == []
    _record(
        benchmark,
        operation=f"find_no_match_{name}",
        dictionary_size=1,
        text=text,
        expected_matches=0,
    )
    benchmark(matcher.find, text)


@pytest.mark.parametrize("case_sensitive", [False, True])
def test_case_policy_same_input(benchmark: BenchmarkFixture, case_sensitive: bool) -> None:
    terms = ["Straße", "cafe\u0301", "Μάιος", "Москва"]
    text = "Straße cafe\u0301 Μάιος Москва"
    matcher = Matcher(case_sensitive=case_sensitive, unicode_normalization="NFC", boundary="none")
    matcher.add_many(terms)
    assert len(_matches(matcher, text)) == 4
    _record(
        benchmark,
        operation="find_case_policy",
        dictionary_size=len(terms),
        text=text,
        expected_matches=4,
        configuration=f"case_sensitive={case_sensitive},normalization=NFC,boundary=none",
    )
    benchmark(matcher.find, text)


@pytest.mark.parametrize(
    ("normalization", "expected"),
    [(None, 1), ("NFC", 2), ("NFD", 2), ("NFKC", 3), ("NFKD", 3)],
)
def test_normalization_matrix(
    benchmark: BenchmarkFixture, normalization: str | None, expected: int
) -> None:
    text = "cafe\u0301 \uff21\uff22\uff23 \ufb01"
    matcher = Matcher(unicode_normalization=normalization, boundary="none")
    matcher.add_many(["CAFÉ", "ABC", "fi"])
    assert len(_matches(matcher, text)) == expected
    _record(
        benchmark,
        operation="find_normalization",
        dictionary_size=len(matcher),
        text=text,
        expected_matches=expected,
        configuration=f"case_sensitive=False,normalization={normalization},boundary=none",
    )
    benchmark(matcher.find, text)


def test_unicode_script_workload(benchmark: BenchmarkFixture) -> None:
    terms = [
        "CAFÉ",
        "ΜΆΙΟΣ",
        "\u041c\u041e\u0421\u041a\u0412\u0410",
        "مرحبا",
        "שלום",
        "नमस्ते",
        "北京",
        "東京",
        "서울",
        "👩‍💻",
    ]
    text = "cafe\u0301 Μάιος Москва مرحبا שלום नमस्ते 北京 東京 서울 👩‍💻 " * 60
    matcher = Matcher(unicode_normalization="NFC", boundary="none")
    matcher.add_many(terms)
    assert len(_matches(matcher, text)) == 600
    _record(
        benchmark,
        operation="find_unicode_scripts",
        dictionary_size=len(terms),
        text=text,
        expected_matches=600,
        configuration="case_sensitive=False,normalization=NFC,boundary=none",
    )
    benchmark(matcher.find, text)


@pytest.mark.parametrize("normalization", [None, "NFC", "NFKC"])
@pytest.mark.parametrize("case_sensitive", [False, True])
def test_isolated_alignment_transform(
    benchmark: BenchmarkFixture, normalization: str | None, case_sensitive: bool
) -> None:
    text = "cafe\u0301 \uff21\uff22\uff23 Straße Μάιος " * 200

    transformed = transform(text, normalization=normalization, case_sensitive=case_sensitive)
    expected = (
        text
        if normalization is None
        else unicodedata.normalize(cast(Literal["NFC", "NFD", "NFKC", "NFKD"], normalization), text)
    )
    if not case_sensitive:
        expected = expected.casefold()
    assert transformed.text == expected
    _record(
        benchmark,
        operation="alignment_transform",
        dictionary_size=0,
        text=text,
        configuration=f"normalization={normalization},case_sensitive={case_sensitive}",
    )
    benchmark(transform, text, normalization=normalization, case_sensitive=case_sensitive)


@pytest.mark.parametrize("normalization", [None, "NFC", "NFKC"])
@pytest.mark.parametrize("case_sensitive", [False, True])
def test_normalized_no_match(
    benchmark: BenchmarkFixture, normalization: str | None, case_sensitive: bool
) -> None:
    text = "cafe\u0301 \uff21\uff22\uff23 Straße Μάιος مرحبا 北京 👩‍💻 " * 200
    matcher = Matcher(
        case_sensitive=case_sensitive,
        unicode_normalization=normalization,
        boundary="none",
    )
    matcher.add("absent-match-token")
    assert _matches(matcher, text) == []
    _record(
        benchmark,
        operation="find_normalized_no_match",
        dictionary_size=len(matcher),
        text=text,
        expected_matches=0,
        configuration=f"normalization={normalization},case_sensitive={case_sensitive},boundary=none",
    )
    benchmark(matcher.find, text)


@pytest.mark.parametrize("size", SIZES)
def test_retained_dictionary_memory(benchmark: BenchmarkFixture, size: int) -> None:
    terms = _seeded_terms(size)
    matcher, retained, peak = _peak_bytes(lambda: _build_matcher(terms))
    assert isinstance(matcher, Matcher)
    assert len(matcher) == size
    assert peak >= retained > 0
    _record(benchmark, operation="retained_dictionary_memory", dictionary_size=size)
    benchmark.extra_info.update(retained_bytes=retained, peak_bytes=peak)
    benchmark(_build_matcher, terms)


def test_matching_peak_memory(benchmark: BenchmarkFixture) -> None:
    matcher = Matcher(boundary="none")
    matcher.add("needle")
    text = "needle " * 500

    def find() -> list[Match]:
        return _matches(matcher, text)

    matches, retained, peak = _peak_bytes(find)
    assert isinstance(matches, list)
    assert len(matches) == 500
    assert peak >= retained > 0
    _record(
        benchmark,
        operation="matching_peak_memory",
        dictionary_size=len(matcher),
        text=text,
        expected_matches=500,
        configuration="boundary=none,strategy=leftmost_longest",
    )
    benchmark.extra_info.update(retained_bytes=retained, peak_bytes=peak)
    benchmark(find)


def _serialization_matcher() -> Matcher:
    matcher = Matcher(unicode_normalization="NFC", boundary="none")
    matcher.add_many({term: {"rank": index} for index, term in enumerate(_seeded_terms(100))})
    return matcher


def test_save(benchmark: BenchmarkFixture, tmp_path: Path) -> None:
    matcher = _serialization_matcher()
    path = tmp_path / "matcher.json"
    matcher.save(path)
    assert Matcher.load(path).find(_seeded_terms(100)[0])
    _record(
        benchmark, operation="save", dictionary_size=len(matcher), configuration="NFC,boundary=none"
    )
    benchmark(matcher.save, path)


def test_load(benchmark: BenchmarkFixture, tmp_path: Path) -> None:
    matcher = _serialization_matcher()
    path = tmp_path / "matcher.json"
    matcher.save(path)
    loaded = Matcher.load(path)
    assert len(loaded) == len(matcher)
    _record(
        benchmark, operation="load", dictionary_size=len(matcher), configuration="NFC,boundary=none"
    )
    benchmark(Matcher.load, path)
