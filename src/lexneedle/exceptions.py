"""Exceptions raised by LexNeedle."""


class ConfigurationError(ValueError):
    """Raised when a matcher configuration or term is invalid."""


class SerializationError(ValueError):
    """Raised when a serialized matcher is malformed or unsupported."""
