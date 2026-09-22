"""Import, export, and quick-start smoke tests for the installed package."""

from pathlib import Path

import lexneedle
from lexneedle import Matcher
from lexneedle.compat.flashtext import KeywordProcessor


def test_public_api_exports_are_importable() -> None:
    assert sorted(lexneedle.__all__) == [
        "Boundary",
        "ConfigurationError",
        "Match",
        "Matcher",
        "Normalization",
        "Replacement",
        "SerializationError",
        "Strategy",
    ]
    for name in lexneedle.__all__:
        assert getattr(lexneedle, name) is not None


def test_py_typed_marker_ships_with_the_package() -> None:
    assert (Path(lexneedle.__file__).parent / "py.typed").is_file()


def test_readme_quick_start_example_runs() -> None:
    matcher = Matcher()
    matcher.add("Panadol", value="paracetamol", metadata={"type": "brand"})

    [match] = matcher.find("Panadol 500mg tablets")

    assert (match.text, match.value, match.start, match.end) == ("Panadol", "paracetamol", 0, 7)


def test_flashtext_facade_lists_all_keywords() -> None:
    processor = KeywordProcessor()
    processor.add_keyword("java", "Java")

    assert processor.get_all_keywords() == {"java": "Java"}
