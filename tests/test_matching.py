import pytest

from lexneedle import ConfigurationError, Matcher


def _matcher() -> Matcher:
    matcher = Matcher()
    matcher.add_many(["Machine", "Learning", "Machine Learning"])
    return matcher


def test_leftmost_longest_is_default_and_insertion_independent() -> None:
    matcher = _matcher()

    assert [match.text for match in matcher.find("I like Machine Learning")] == ["Machine Learning"]

    reversed_matcher = Matcher()
    reversed_matcher.add_many(["Machine Learning", "Learning", "Machine"])
    assert reversed_matcher.find("I like Machine Learning") == matcher.find(
        "I like Machine Learning"
    )


def test_all_includes_overlaps_and_longest_keeps_one_per_start() -> None:
    matcher = _matcher()

    assert [match.text for match in matcher.find("Machine Learning", strategy="all")] == [
        "Machine Learning",
        "Machine",
        "Learning",
    ]
    assert [match.text for match in matcher.find("Machine Learning", strategy="longest")] == [
        "Machine Learning",
        "Learning",
    ]


def test_leftmost_longest_skips_overlapping_later_matches() -> None:
    matcher = Matcher(boundary="none")
    matcher.add_many(["aba", "bab"])

    assert [match.text for match in matcher.find("ababa")] == ["aba"]
    assert [match.text for match in matcher.find("ababa", strategy="all")] == ["aba", "bab", "aba"]


def test_word_boundary_blocks_substrings_and_recognises_punctuation() -> None:
    matcher = Matcher()
    matcher.add("he")

    assert matcher.find("theory") == []
    assert [match.text for match in matcher.find("(he), he!")] == ["he", "he"]


def test_none_boundary_allows_substrings() -> None:
    matcher = Matcher(boundary="none")
    matcher.add("he")

    assert [match.start for match in matcher.find("theory")] == [1]


def test_custom_boundary_receives_original_source_positions() -> None:
    seen: list[int] = []

    def boundary(text: str, position: int) -> bool:
        seen.append(position)
        return position in {0, len(text)}

    matcher = Matcher(boundary=boundary)
    matcher.add("term")

    assert [match.text for match in matcher.find("term")] == ["term"]
    assert seen == [0, 4]


def test_invalid_configuration_is_rejected() -> None:
    invalid_strategy = "shortest"
    with pytest.raises(ConfigurationError):
        Matcher(strategy=invalid_strategy)  # ty: ignore[invalid-argument-type]
    invalid_boundary = "letters"
    with pytest.raises(ConfigurationError):
        Matcher(boundary=invalid_boundary)  # ty: ignore[invalid-argument-type]


def test_default_finditer_does_not_inspect_later_boundary_candidates() -> None:
    def boundary(text: str, position: int) -> bool:
        if position > 4:
            raise AssertionError("late candidate inspected")
        return position in {0, 4}

    matcher = Matcher(boundary=boundary)
    matcher.add("term")

    assert next(matcher.finditer("term later term")).text == "term"
