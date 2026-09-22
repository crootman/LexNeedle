"""Boundary policies for matching source text."""

import unicodedata
from collections.abc import Callable

Boundary = Callable[[str, int], bool]


def is_word_character(character: str) -> bool:
    """Return whether *character* participates in LexNeedle's word policy."""
    if character in {"\u200c", "\u200d"}:
        return True
    category = unicodedata.category(character)
    return category[0] in {"L", "M", "N"} or category == "Pc"


def word_boundary(text: str, position: int) -> bool:
    """Return whether *position* is next to a non-word character or an edge."""
    return (
        position == 0
        or position == len(text)
        or not is_word_character(text[position - 1])
        or not is_word_character(text[position])
    )


def no_boundary(_: str, __: int) -> bool:
    """Accept every position as a boundary."""
    return True
