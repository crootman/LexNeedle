import json

import pytest

from lexneedle import Matcher, SerializationError


def test_json_round_trip_preserves_configuration_and_terms(tmp_path) -> None:
    matcher = Matcher(unicode_normalization="NFC", boundary="none", strategy="all")
    matcher.add("café", None, metadata={"labels": ["coffee"]})
    path = tmp_path / "terms.json"

    matcher.save(path)
    loaded = Matcher.load(path)

    assert loaded.find("cafe\u0301", strategy="all") == matcher.find("cafe\u0301", strategy="all")


def test_save_does_not_truncate_existing_file_when_value_is_not_json(tmp_path) -> None:
    path = tmp_path / "terms.json"
    path.write_text("keep me", encoding="utf-8")
    matcher = Matcher()
    matcher.add("term", {"bad": {1, 2}})

    with pytest.raises(SerializationError, match="losslessly"):
        matcher.save(path)
    assert path.read_text(encoding="utf-8") == "keep me"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"format_version": True, "configuration": {}, "terms": []},
        {"format_version": 1, "configuration": {}, "terms": []},
    ],
)
def test_load_rejects_malformed_payloads(tmp_path, payload) -> None:
    path = tmp_path / "terms.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SerializationError):
        Matcher.load(path)


def test_load_rejects_duplicate_json_keys(tmp_path) -> None:
    path = tmp_path / "terms.json"
    path.write_text('{"format_version": 1, "format_version": 1}', encoding="utf-8")

    with pytest.raises(SerializationError, match="valid JSON"):
        Matcher.load(path)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), {1: "bad"}, ("tuple",), {"set"}])
def test_save_rejects_lossy_values_without_overwriting_file(tmp_path, value) -> None:
    path = tmp_path / "terms.json"
    path.write_text("original", encoding="utf-8")
    matcher = Matcher()
    matcher.add("term", value)

    with pytest.raises(SerializationError):
        matcher.save(path)
    assert path.read_text(encoding="utf-8") == "original"


def test_serialization_rejects_cycles_and_deep_invalid_input(tmp_path) -> None:
    cycle: list[object] = []
    cycle.append(cycle)
    matcher = Matcher()
    matcher.add("term", cycle)
    path = tmp_path / "terms.json"
    path.write_text("original", encoding="utf-8")

    with pytest.raises(SerializationError):
        matcher.save(path)
    path.write_text("[" * 2_000 + "]" * 2_000, encoding="utf-8")
    with pytest.raises(SerializationError):
        Matcher.load(path)


def test_json_surrogates_round_trip_without_encoding_the_output_file(tmp_path) -> None:
    path = tmp_path / "terms.json"
    matcher = Matcher(boundary="none")
    matcher.add("\ud800", "\udfff")

    matcher.save(path)
    assert Matcher.load(path).find("\ud800")[0].value == "\udfff"


@pytest.mark.parametrize(
    ("field", "value"),
    [("boundary", []), ("strategy", []), ("unicode_normalization", "bad"), ("case_sensitive", 1)],
)
def test_load_rejects_wrong_configuration_types(tmp_path, field, value) -> None:
    path = tmp_path / "terms.json"
    matcher = Matcher()
    matcher.add("term", 1.5)
    matcher.save(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["configuration"][field] = value
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SerializationError):
        Matcher.load(path)


def test_load_rejects_duplicate_terms_and_numeric_overflow(tmp_path) -> None:
    path = tmp_path / "terms.json"
    matcher = Matcher()
    matcher.add("term", 1.5)
    matcher.save(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["terms"] *= 2
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SerializationError):
        Matcher.load(path)
    matcher.save(path)
    path.write_text(path.read_text(encoding="utf-8").replace("1.5", "1e400"), encoding="utf-8")
    with pytest.raises(SerializationError):
        Matcher.load(path)
