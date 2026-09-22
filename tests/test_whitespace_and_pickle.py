import pickle

from lexneedle import Matcher


def test_whitespace_equivalent_preserves_source_spans_and_replacement() -> None:
    matcher = Matcher(boundary="none", whitespace_equivalent=True)
    matcher.add("New York", "NY")
    text = "New\u00a0\tYork"

    matches = matcher.find(text)

    assert [(match.text, match.start, match.end) for match in matches] == [(text, 0, len(text))]
    assert matcher.replace(text) == "NY"


def test_whitespace_equivalent_is_opt_in_and_round_trips_json(tmp_path) -> None:
    matcher = Matcher(boundary="none", whitespace_equivalent=True)
    matcher.add("a b", "matched")
    path = tmp_path / "matcher.json"

    assert matcher.find("a\n b")
    assert Matcher(boundary="none").find("a\n b") == []
    matcher.save(path)
    loaded = Matcher.load(path)
    assert loaded.whitespace_equivalent
    assert loaded.find("a\n b") == matcher.find("a\n b")


def test_whitespace_equivalent_keeps_leading_and_trailing_separators_distinct() -> None:
    matcher = Matcher(boundary="none", whitespace_equivalent=True)
    matcher.add(" a ")

    assert [match.text for match in matcher.find("\ta\n")] == ["\ta\n"]
    assert matcher.find("a") == []


def test_whitespace_equivalent_preserves_normalized_casefold_expansions() -> None:
    matcher = Matcher(boundary="none", unicode_normalization="NFC", whitespace_equivalent=True)
    matcher.add("STRASSE CAFÉ", "matched")
    source = "Straße\tcafe\u0301"

    [match] = matcher.find(source)

    assert (match.text, match.start, match.end) == (source, 0, len(source))
    assert source[match.start : match.end] == match.text
    assert matcher.replace(source) == "matched"
    matcher = Matcher(boundary="none", unicode_normalization="NFC", whitespace_equivalent=True)
    matcher.add("s CAFÉ")
    assert matcher.find("ß\tcafe\u0301") == []


def test_metadata_bearing_matcher_pickles_through_reconstruction() -> None:
    matcher = Matcher(boundary="none", whitespace_equivalent=True)
    matcher.add("New York", {"city": "New York"}, metadata={"source": "test"})

    restored = pickle.loads(pickle.dumps(matcher))

    assert restored.find("New\tYork") == matcher.find("New\tYork")
