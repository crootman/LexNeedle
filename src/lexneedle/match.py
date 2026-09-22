"""Public match result types."""

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Match:
    """A term occurrence whose offsets index the original input string."""

    keyword: str
    text: str
    value: object
    start: int
    end: int
    metadata: Mapping[str, object] | None = None
