from types import MappingProxyType

import pytest

from lexneedle import ConfigurationError, Matcher


def test_find_structured_match_and_source_offsets() -> None:
    matcher = Matcher()
    matcher.add("Panadol", "paracetamol", metadata={"type": "brand"})

    [match] = matcher.find("Panadol 500mg tablets")

    assert (match.keyword, match.text, match.value, match.start, match.end) == (
        "Panadol",
        "Panadol",
        "paracetamol",
        0,
        7,
    )
    assert match.metadata == {"type": "brand"}
    assert isinstance(match.metadata, MappingProxyType)


def test_aliases_share_value_and_metadata() -> None:
    matcher = Matcher()
    matcher.add(["Panadol", "Panadol Osteo"], "paracetamol", metadata={"kind": "medicine"})

    assert [match.text for match in matcher.find("Panadol Osteo and Panadol")] == [
        "Panadol Osteo",
        "Panadol",
    ]
    assert {match.value for match in matcher.find("Panadol Osteo and Panadol")} == {"paracetamol"}


def test_duplicate_updates_and_transformed_collision_is_rejected() -> None:
    matcher = Matcher()
    matcher.add("Straße", "old")
    matcher.add("Straße", "new")

    assert matcher.get("Straße") == "new"
    with pytest.raises(ConfigurationError, match="collides"):
        matcher.add("STRASSE", "other")


def test_dictionary_operations_and_bulk_addition() -> None:
    matcher = Matcher()
    matcher.add_many({"one": 1, "two": 2})

    assert len(matcher) == 2
    assert "one" in matcher
    assert matcher.get("missing", "fallback") == "fallback"
    assert matcher.remove("one")
    assert not matcher.remove("one")
    matcher.clear()
    assert len(matcher) == 0


def test_invalid_terms_are_rejected() -> None:
    matcher = Matcher()

    with pytest.raises(ConfigurationError, match="empty"):
        matcher.add("")
    with pytest.raises(ConfigurationError, match="at least"):
        matcher.add([])
    invalid_keyword: object = 1
    with pytest.raises(TypeError, match="strings"):
        matcher.add(["ok", invalid_keyword])  # ty: ignore[invalid-argument-type]


def test_find_many_is_lazy() -> None:
    matcher = Matcher()
    matcher.add("needle")

    assert [
        [match.text for match in matches] for matches in matcher.find_many(["needle", "none"])
    ] == [
        ["needle"],
        [],
    ]


def test_metadata_is_a_shallow_snapshot() -> None:
    metadata = {"labels": ["first"]}
    matcher = Matcher()
    matcher.add("term", metadata=metadata)
    metadata["new"] = "outside"

    [match] = matcher.find("term")
    assert match.metadata == {"labels": ["first"]}
    assert match.metadata["labels"] is metadata["labels"]  # type: ignore[index]


def test_very_long_keyword_removal_is_iterative() -> None:
    keyword = "x" * 5_000
    matcher = Matcher(boundary="none")
    matcher.add(keyword)

    assert matcher.remove(keyword)
    assert matcher.find(keyword) == []


def test_iteration_and_items_are_sorted_and_insertion_order_independent() -> None:
    matcher = Matcher()
    matcher.add_many({"zebra": 1, "apple": 2, "mango": 3})

    other = Matcher()
    other.add_many({"mango": 3, "apple": 2, "zebra": 1})

    assert list(matcher) == ["apple", "mango", "zebra"]
    assert list(matcher.items()) == [("apple", 2), ("mango", 3), ("zebra", 1)]
    assert list(other.items()) == list(matcher.items())


def test_finditer_validates_arguments_before_iteration() -> None:
    matcher = Matcher()
    matcher.add("term")

    invalid_text: object = 1
    with pytest.raises(TypeError, match="text must be a string"):
        matcher.finditer(invalid_text)  # ty: ignore[invalid-argument-type]

    invalid_strategy = "shortest"
    with pytest.raises(ConfigurationError, match="strategy"):
        matcher.finditer("term", strategy=invalid_strategy)  # ty: ignore[invalid-argument-type]
