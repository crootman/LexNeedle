import unicodedata
from typing import Literal

import pytest

from lexneedle import Matcher
from lexneedle.normalize import transform


@pytest.mark.parametrize("form", ["NFC", "NFD", "NFKC", "NFKD"])
@pytest.mark.parametrize(
    "text", ["e\u0301", "é", "\uff21\uff22\uff23", "각", "ᄀ\u0300ᅡ", "ে\u0334া"]
)
def test_transform_matches_unicodedata(
    form: Literal["NFC", "NFD", "NFKC", "NFKD"], text: str
) -> None:
    actual = transform(text, normalization=form, case_sensitive=False)

    assert actual.text == unicodedata.normalize(form, text).casefold()
    assert len(actual.text) == len(actual.provenance)


def test_nfc_preserves_original_decomposed_source_offsets() -> None:
    matcher = Matcher(unicode_normalization="NFC")
    matcher.add("café")
    text = "A cafe\u0301 here"

    [match] = matcher.find(text)
    assert (match.start, match.end, match.text) == (2, 7, "cafe\u0301")
    assert text[match.start : match.end] == match.text


def test_nfkc_matches_compatibility_forms_with_source_offsets() -> None:
    matcher = Matcher(unicode_normalization="NFKC")
    matcher.add("ABC")
    text = "\uff21\uff22\uff23"

    [match] = matcher.find(text)
    assert (match.start, match.end, match.text) == (0, 3, text)


def test_match_does_not_split_combining_sequence() -> None:
    matcher = Matcher(unicode_normalization="NFD", boundary="none")
    matcher.add("e")

    assert matcher.find("e\u0301") == []


def test_normalization_reordering_resolves_strategies_in_source_order() -> None:
    source = "\u0323\uff9e"
    matcher = Matcher(unicode_normalization="NFKC", case_sensitive=True, boundary="none")
    matcher.add_many([source, source[1]])

    assert [(match.start, match.end) for match in matcher.find(source)] == [(0, 2)]
    assert matcher.replace(source, lambda match: "X") == "X"


def test_longest_groups_reordered_candidates_by_original_start() -> None:
    source = "\u0323\uff9e\u0300"
    matcher = Matcher(unicode_normalization="NFKC", case_sensitive=True, boundary="none")
    matcher.add_many([source, source[0]])

    assert [(match.start, match.end) for match in matcher.find(source, strategy="longest")] == [
        (0, 3)
    ]
