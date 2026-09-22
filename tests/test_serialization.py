import json
import os
from errno import ENAMETOOLONG
from pathlib import Path

import pytest

from lexneedle import Matcher, SerializationError, serialization


def test_json_round_trip_preserves_configuration_and_terms(tmp_path) -> None:
    matcher = Matcher(unicode_normalization="NFC", boundary="none", strategy="all")
    matcher.add("café", None, metadata={"labels": ["coffee"]})
    path = tmp_path / "terms.json"

    matcher.save(path)
    loaded = Matcher.load(path)

    assert loaded.find("cafe\u0301", strategy="all") == matcher.find("cafe\u0301", strategy="all")


def test_v1_json_loads_with_exact_whitespace_matching(tmp_path) -> None:
    path = tmp_path / "v1.json"
    path.write_text(
        json.dumps(
            {
                "format_version": 1,
                "configuration": {
                    "case_sensitive": False,
                    "unicode_normalization": None,
                    "boundary": "none",
                    "strategy": "leftmost_longest",
                },
                "terms": [{"keyword": "New York", "value": "NY", "metadata": None}],
            }
        ),
        encoding="utf-8",
    )

    loaded = Matcher.load(path)

    assert not loaded.whitespace_equivalent
    assert loaded.find("New York")
    assert loaded.find("New\tYork") == []


def test_save_rejects_side_boundary_without_overwriting_existing_file(tmp_path) -> None:
    path = tmp_path / "terms.json"
    path.write_text("original", encoding="utf-8")

    def side_boundary(_: str, __: int, ___: str) -> bool:
        return True

    matcher = Matcher(side_boundary=side_boundary)
    matcher.add("term")

    with pytest.raises(SerializationError, match="callable boundary"):
        matcher.save(path)
    assert path.read_text(encoding="utf-8") == "original"


def test_save_does_not_truncate_existing_file_when_value_is_not_json(tmp_path) -> None:
    path = tmp_path / "terms.json"
    path.write_text("keep me", encoding="utf-8")
    matcher = Matcher()
    matcher.add("term", {"bad": {1, 2}})

    with pytest.raises(SerializationError, match="losslessly"):
        matcher.save(path)
    assert path.read_text(encoding="utf-8") == "keep me"


def test_save_replaces_existing_file_after_writing_temporary_file(tmp_path) -> None:
    path = tmp_path / "terms.json"
    path.write_text("old", encoding="utf-8")
    matcher = Matcher()
    matcher.add("term", {"value": 1})

    matcher.save(path)

    assert json.loads(path.read_text(encoding="utf-8"))["terms"] == [
        {"keyword": "term", "metadata": None, "value": {"value": 1}}
    ]
    assert list(tmp_path.iterdir()) == [path]


def test_save_supports_a_relative_destination_path(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    matcher = Matcher()
    matcher.add("term", "value")

    matcher.save("terms.json")

    assert Matcher.load("terms.json").find("term")[0].value == "value"


@pytest.mark.skipif(os.name != "posix", reason="POSIX name-length behavior")
def test_save_and_load_supports_a_near_name_max_filename(tmp_path) -> None:
    path = tmp_path / ("x" * 240 + ".json")
    matcher = Matcher()
    matcher.add("term", "value")

    try:
        matcher.save(path)
    except OSError as error:
        if error.errno == ENAMETOOLONG:
            pytest.skip("filesystem does not support a 245-byte filename")
        raise

    assert Matcher.load(path).find("term")[0].value == "value"


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits are unavailable")
def test_save_preserves_existing_permissions(tmp_path) -> None:
    target = tmp_path / "terms.json"
    target.write_text("old", encoding="utf-8")
    target.chmod(0o640)
    matcher = Matcher()
    matcher.add("term", "value")

    matcher.save(target)

    assert json.loads(target.read_text(encoding="utf-8"))["terms"][0]["keyword"] == "term"
    assert target.stat().st_mode & 0o777 == 0o640


def test_save_follows_existing_symlink(tmp_path) -> None:
    target = tmp_path / "terms.json"
    target.write_text("old", encoding="utf-8")
    link = tmp_path / "terms-link.json"
    try:
        link.symlink_to(target)
    except (NotImplementedError, OSError) as error:
        pytest.skip(f"symlinks are unavailable: {error}")
    matcher = Matcher()
    matcher.add("term", "value")

    matcher.save(link)

    assert link.is_symlink()
    assert json.loads(target.read_text(encoding="utf-8"))["terms"][0]["keyword"] == "term"


@pytest.mark.parametrize("error", [OSError("injected write failure"), KeyboardInterrupt()])
def test_save_preserves_existing_file_when_temporary_write_fails(
    tmp_path, monkeypatch, error
) -> None:
    path = tmp_path / "terms.json"
    path.write_text("original", encoding="utf-8")
    matcher = Matcher()
    matcher.add("term", "value")

    class FailingTemporaryFile:
        name = str(tmp_path / ".lexneedle-write-failure.tmp")

        def __enter__(self) -> FailingTemporaryFile:
            Path(self.name).touch()
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def write(self, value: str) -> int:
            raise error

    monkeypatch.setattr(
        serialization.tempfile, "NamedTemporaryFile", lambda **_kwargs: FailingTemporaryFile()
    )

    with pytest.raises(type(error)):
        matcher.save(path)

    assert path.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.iterdir()) == [path]


def test_save_preserves_existing_file_when_replacement_fails(tmp_path, monkeypatch) -> None:
    path = tmp_path / "terms.json"
    path.write_text("original", encoding="utf-8")
    matcher = Matcher()
    matcher.add("term", "value")

    def fail_replace(source: Path, destination: Path) -> None:
        assert destination == path
        assert source.parent == path.parent
        raise OSError("injected replacement failure")

    monkeypatch.setattr(serialization.Path, "replace", fail_replace)

    with pytest.raises(OSError, match="injected replacement failure"):
        matcher.save(path)

    assert path.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.iterdir()) == [path]


def test_save_preserves_existing_file_when_temporary_close_fails(tmp_path, monkeypatch) -> None:
    path = tmp_path / "terms.json"
    path.write_text("original", encoding="utf-8")
    matcher = Matcher()
    matcher.add("term", "value")

    class CloseFailingTemporaryFile:
        name = str(tmp_path / ".lexneedle-close-failure.tmp")

        def __enter__(self) -> CloseFailingTemporaryFile:
            Path(self.name).touch()
            return self

        def __exit__(self, *args: object) -> None:
            raise OSError("injected close failure")

        def write(self, value: str) -> int:
            return len(value)

    monkeypatch.setattr(
        serialization.tempfile, "NamedTemporaryFile", lambda **_kwargs: CloseFailingTemporaryFile()
    )

    with pytest.raises(OSError, match="injected close failure"):
        matcher.save(path)

    assert path.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.iterdir()) == [path]


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


def test_load_rejects_invalid_utf8(tmp_path) -> None:
    path = tmp_path / "terms.json"
    path.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(SerializationError, match="valid JSON"):
        Matcher.load(path)


def test_load_propagates_missing_file_errors(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        Matcher.load(tmp_path / "missing.json")


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
    [
        ("boundary", []),
        ("strategy", []),
        ("unicode_normalization", "bad"),
        ("unicode_normalization", "nfc"),
        ("case_sensitive", 1),
        ("whitespace_equivalent", 1),
    ],
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
