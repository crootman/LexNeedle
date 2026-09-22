"""Property tests for the Unicode pipeline and the public matching contract."""

import unicodedata
from typing import Literal

from hypothesis import given, settings
from hypothesis import strategies as st

from lexneedle import ConfigurationError, Matcher
from lexneedle.normalize import transform, transform_key

type Strategy = Literal["all", "longest", "leftmost_longest"]

NORMALIZATIONS: tuple[Literal["NFC", "NFD", "NFKC", "NFKD"] | None, ...] = (
    None,
    "NFC",
    "NFD",
    "NFKC",
    "NFKD",
)
STRATEGIES: tuple[Strategy, ...] = ("all", "longest", "leftmost_longest")
ALPHABET = "aAe\u00e9\u0301\u0323\u0334\u00df\u0130\u03a3\u03c2\u200d\u200c\ufb01\uff21北京👩"


@settings(max_examples=200, deadline=None, derandomize=True)
@given(st.text(max_size=32))
def test_transform_matches_unicodedata_with_aligned_provenance(text: str) -> None:
    for normalization in NORMALIZATIONS:
        for case_sensitive in (False, True):
            actual = transform(text, normalization=normalization, case_sensitive=case_sensitive)
            expected = text if normalization is None else unicodedata.normalize(normalization, text)
            if not case_sensitive:
                expected = expected.casefold()

            assert actual.text == expected
            assert len(actual.provenance) == len(actual.text)


@settings(max_examples=200, deadline=None, derandomize=True)
@given(st.text(max_size=32), st.sampled_from(NORMALIZATIONS), st.booleans())
def test_transform_key_matches_the_unicode_pipeline(
    text: str, normalization: Literal["NFC", "NFD", "NFKC", "NFKD"] | None, case_sensitive: bool
) -> None:
    expected = text if normalization is None else unicodedata.normalize(normalization, text)
    if not case_sensitive:
        expected = expected.casefold()

    assert (
        transform_key(text, normalization=normalization, case_sensitive=case_sensitive) == expected
    )


@settings(max_examples=150, deadline=None, derandomize=True)
@given(
    st.text(alphabet=ALPHABET, max_size=24),
    st.text(alphabet=ALPHABET, min_size=1, max_size=6),
    st.sampled_from(STRATEGIES),
)
def test_matches_preserve_source_slices_and_find_agrees_with_finditer(
    text: str, term: str, strategy: Strategy
) -> None:
    matcher = Matcher(unicode_normalization="NFC", boundary="none")
    try:
        matcher.add(term, value="value")
    except ConfigurationError:
        return

    matches = matcher.find(text, strategy=strategy)
    assert matches == list(matcher.finditer(text, strategy=strategy))
    assert matches == matcher.find(text, strategy=strategy)

    previous_end = 0
    for match in matches:
        assert text[match.start : match.end] == match.text
        assert 0 <= match.start < match.end <= len(text)
        if strategy == "leftmost_longest":
            assert match.start >= previous_end
            previous_end = match.end
