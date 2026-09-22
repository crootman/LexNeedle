"""Boundary policies for matching source text."""

import unicodedata
from collections.abc import Callable
from typing import Literal

Boundary = Callable[[str, int], bool]
SideBoundary = Callable[[str, int, Literal["left", "right"]], bool]


def is_word_character(character: str) -> bool:
    """Return whether *character* participates in LexNeedle's word policy."""
    if character in {"\u200c", "\u200d"}:
        return True
    category = unicodedata.category(character)
    return category[0] in {"L", "M", "N"} or category == "Pc"


def word_boundary(text: str, position: int) -> bool:
    """Return the legacy position-only word-boundary predicate.

    :class:`~lexneedle.Matcher` evaluates its built-in ``"word"`` policy
    against the exterior source character on each side of a candidate.  This
    helper remains available for legacy two-argument custom policies, where a
    position has no knowledge of which side of a candidate is being checked.
    """
    return (
        position == 0
        or position == len(text)
        or not is_word_character(text[position - 1])
        or not is_word_character(text[position])
    )


def no_boundary(_: str, __: int) -> bool:
    """Accept every position as a boundary."""
    return True
