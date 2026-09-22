import unicodedata
from random import Random
from typing import Literal

import pytest

from lexneedle import Matcher
from lexneedle.normalize import Provenance, transform, transform_key


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


def test_composition_across_an_intervening_mark_is_not_reported() -> None:
    source = "a\u0334\u0301"
    matcher = Matcher(unicode_normalization="NFC", case_sensitive=True, boundary="none")
    matcher.add("\u00e1", value="value")

    assert "\u00e1" in transform(source, normalization="NFC", case_sensitive=True).text
    assert matcher.find(source) == []
    assert matcher.find(source, strategy="all") == []
    assert matcher.replace(source, lambda match: "X") == source


@pytest.mark.parametrize("case_sensitive", [False, True])
def test_transform_without_normalization_keeps_exact_provenance(
    case_sensitive: bool,
) -> None:
    alphabet = "AaZzßİΣςé\u0301👩\u200d"
    generator = Random(731)
    for _ in range(100):
        text = "".join(generator.choice(alphabet) for _ in range(40))
        actual = transform(text, normalization=None, case_sensitive=case_sensitive)
        expected = text if case_sensitive else text.casefold()
        expected_provenance = tuple(
            Provenance(index, index + 1, index)
            for index, character in enumerate(text)
            for _ in (character if case_sensitive else character.casefold())
        )

        assert actual.text == expected
        assert actual.provenance == expected_provenance


@pytest.mark.parametrize("normalization", [None, "NFC", "NFD", "NFKC", "NFKD"])
@pytest.mark.parametrize("case_sensitive", [False, True])
def test_transform_key_matches_the_unicode_pipeline(
    normalization: Literal["NFC", "NFD", "NFKC", "NFKD"] | None,
    case_sensitive: bool,
) -> None:
    generator = Random(919)
    alphabet = "AaZzßİΣςé\u0301\uff21가"
    for _ in range(100):
        text = "".join(generator.choice(alphabet) for _ in range(40))
        expected = text if normalization is None else unicodedata.normalize(normalization, text)
        if not case_sensitive:
            expected = expected.casefold()

        assert (
            transform_key(text, normalization=normalization, case_sensitive=case_sensitive)
            == expected
        )


@pytest.mark.parametrize("normalization", [None, "NFC", "NFD", "NFKC", "NFKD"])
@pytest.mark.parametrize("case_sensitive", [False, True])
def test_seeded_terms_match_their_original_source_across_transformations(
    normalization: Literal["NFC", "NFD", "NFKC", "NFKD"] | None,
    case_sensitive: bool,
) -> None:
    generator = Random(457)
    alphabet = "AaZzßİΣςé\u0301\uff21가"
    for _ in range(50):
        source = "".join(generator.choice(alphabet) for _ in range(20))
        matcher = Matcher(
            case_sensitive=case_sensitive,
            unicode_normalization=normalization,
            boundary="none",
        )
        matcher.add(source, value="value")

        for strategy in ("all", "longest", "leftmost_longest"):
            assert [
                (match.keyword, match.text, match.value, match.start, match.end)
                for match in matcher.find(source, strategy=strategy)
            ] == [(source, source, "value", 0, len(source))]
