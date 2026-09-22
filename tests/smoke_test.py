"""Smoke test for installed distributions: exercise the public API only."""

import tempfile
from pathlib import Path

from lexneedle import Matcher


def main() -> None:
    matcher = Matcher(unicode_normalization="NFC")
    matcher.add("caf\u00e9", value="coffee")
    text = "A cafe\u0301 break"

    [match] = matcher.find(text)
    assert text[match.start : match.end] == match.text
    assert match.value == "coffee"

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "terms.json"
        matcher.save(path)
        assert Matcher.load(path).get("caf\u00e9") == "coffee"

    print("smoke test passed")


if __name__ == "__main__":
    main()
