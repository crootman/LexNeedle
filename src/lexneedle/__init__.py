"""LexNeedle provides deterministic, Unicode-aware dictionary matching."""

from .exceptions import ConfigurationError, SerializationError
from .match import Match
from .matcher import Boundary, Matcher, Replacement

__all__ = [
    "Boundary",
    "ConfigurationError",
    "Match",
    "Matcher",
    "Replacement",
    "SerializationError",
]
