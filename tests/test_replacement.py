import pytest

from lexneedle import ConfigurationError, Matcher


def test_replacement_uses_canonical_string_values() -> None:
    matcher = Matcher()
    matcher.add("Big Apple", "New York")

    assert matcher.replace("I love the Big Apple.") == "I love the New York."


def test_replacement_rejects_implicit_conversion_of_structured_values() -> None:
    matcher = Matcher()
    matcher.add("Big Apple", {"city": "New York"})

    with pytest.raises(TypeError, match="strings"):
        matcher.replace("Big Apple")

    def city(match: object) -> str:
        from lexneedle import Match

        assert isinstance(match, Match)
        assert isinstance(match.value, dict)
        value = match.value["city"]
        assert isinstance(value, str)
        return value

    assert matcher.replace("Big Apple", city) == "New York"


def test_constant_and_callable_replacements() -> None:
    matcher = Matcher()
    matcher.add("a", "x")

    assert matcher.replace("a a", "z") == "z z"
    assert matcher.replace("a a", lambda match: match.text.upper()) == "A A"


def test_replacement_requires_non_overlapping_strategy() -> None:
    matcher = Matcher(strategy="all")
    matcher.add("word", "term")

    with pytest.raises(ConfigurationError, match="leftmost_longest"):
        matcher.replace("word")


def test_replacement_diagnostics_and_flashtext_adjacent_regressions() -> None:
    matcher = Matcher(boundary="none")
    matcher.add("a", "")

    result, matches = matcher.replace_with_matches("aaa")

    assert result == ""
    assert [(match.start, match.end) for match in matches] == [(0, 1), (1, 2), (2, 3)]


def test_flashtext_partial_path_does_not_skip_following_replacement() -> None:
    matcher = Matcher(boundary="none")
    matcher.add_many({"on case": "case", "J2EE": "Java"})

    assert matcher.replace("on J2EE") == "on Java"


def test_flashtext_distinct_and_repeated_adjacent_replacements() -> None:
    matcher = Matcher(boundary="none")
    matcher.add_many({"one": "1", "two": "2", "word": "X"})

    assert matcher.replace("onetwo") == "12"
    assert matcher.replace("wordword") == "XX"


def test_flashtext_empty_replacement_for_a_multi_character_term() -> None:
    matcher = Matcher(boundary="none")
    matcher.add("remove", "")

    assert matcher.replace("removeremove") == ""


def test_global_longest_replacement_is_supported() -> None:
    matcher = Matcher(boundary="none", strategy="global_longest")
    matcher.add_many({"abc": "X", "cde": "Y", "ab": "Z"})

    assert matcher.replace("abcde") == "Xde"


def test_replacement_rejects_unsupported_types_with_a_clear_error() -> None:
    matcher = Matcher()
    matcher.add("word", "term")

    with pytest.raises(TypeError, match="string, a callable, or None"):
        matcher.replace("word", 5)  # ty: ignore[invalid-argument-type]
