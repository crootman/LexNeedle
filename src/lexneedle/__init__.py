"""LexNeedle provides deterministic, Unicode-aware dictionary matching."""

from .exceptions import ConfigurationError, SerializationError
from .match import Match
from .matcher import Boundary, Matcher, Replacement, SideBoundary, Strategy
from .normalize import Normalization

__all__ = [
    "Boundary",
    "ConfigurationError",
    "Match",
    "Matcher",
    "Normalization",
    "Replacement",
    "SerializationError",
    "SideBoundary",
    "Strategy",
]
