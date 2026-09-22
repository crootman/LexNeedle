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
