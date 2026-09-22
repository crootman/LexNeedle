"""Safe, versioned JSON persistence for matcher definitions."""

from __future__ import annotations

import json
import math
import stat
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

from .exceptions import SerializationError

if TYPE_CHECKING:
    from .matcher import Matcher

FORMAT_VERSION = 1


def save(matcher: Matcher, path: str | Path) -> None:
    """Serialize *matcher* by atomically replacing the destination file.

    Encoding and writing occur before replacement, so invalid values and write
    failures cannot truncate an existing destination. Symlink destinations are
    resolved before replacement, preserving write-through behavior and existing
    target's POSIX mode bits. This does not make the save durable against power
    loss or preserve ownership or ACLs.
    """
    if callable(matcher.boundary):
        raise SerializationError("matchers with callable boundaries cannot be serialized")
    payload = {
        "format_version": FORMAT_VERSION,
        "configuration": {
            "case_sensitive": matcher.case_sensitive,
            "unicode_normalization": matcher.unicode_normalization,
            "boundary": matcher.boundary,
            "strategy": matcher.strategy,
        },
        "terms": [
            {
                "keyword": term.keyword,
                "value": term.value,
                "metadata": None if term.metadata is None else dict(term.metadata),
            }
            for term in sorted(matcher._keys.values(), key=lambda item: item.keyword)
        ],
    }
    try:
        _validate_json_value(payload)
    except RecursionError as error:
        raise SerializationError("matcher contains values nested too deeply for JSON") from error
    try:
        encoded = json.dumps(payload, ensure_ascii=True, indent=2, allow_nan=False) + "\n"
    except (RecursionError, TypeError, ValueError) as error:
        raise SerializationError(
            "matcher contains a value that JSON cannot represent losslessly"
        ) from error
    destination = Path(path)
    if destination.is_symlink():
        destination = destination.resolve()
    try:
        mode = stat.S_IMODE(destination.stat().st_mode)
    except FileNotFoundError:
        mode = None
    temporary_path: Path | None = None
    replaced = False
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=".lexneedle-",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            if mode is not None:
                temporary_path.chmod(mode)
            temporary.write(encoded)
        temporary_path.replace(destination)
        replaced = True
    finally:
        if not replaced and temporary_path is not None:
            with suppress(OSError):
                temporary_path.unlink()


def load(path: str | Path) -> Matcher:
    """Load and validate a matcher definition without executing input content."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
        payload = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except OSError:
        raise
    except (
        UnicodeDecodeError,
        ValueError,
        json.JSONDecodeError,
        RecursionError,
        SerializationError,
    ) as error:
        raise SerializationError("matcher file is not valid JSON") from error
    try:
        _validate_json_value(payload)
    except (RecursionError, SerializationError) as error:
        raise SerializationError("matcher file contains unsupported JSON values") from error
    if not isinstance(payload, dict):
        raise SerializationError("matcher file must contain a JSON object")
    _require_keys(payload, {"format_version", "configuration", "terms"}, "matcher file")
    version = payload["format_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != FORMAT_VERSION:
        raise SerializationError("unsupported matcher format version")
    config = payload["configuration"]
    if not isinstance(config, dict):
        raise SerializationError("configuration must be an object")
    _require_keys(
        config, {"case_sensitive", "unicode_normalization", "boundary", "strategy"}, "configuration"
    )
    case_sensitive = config["case_sensitive"]
    normalization = config["unicode_normalization"]
    boundary = config["boundary"]
    strategy = config["strategy"]
    if not isinstance(case_sensitive, bool):
        raise SerializationError("configuration.case_sensitive must be a boolean")
    if normalization is not None and not isinstance(normalization, str):
        raise SerializationError("configuration.unicode_normalization must be a string or null")
    if not isinstance(boundary, str) or boundary not in {"word", "none"}:
        raise SerializationError("configuration.boundary must be 'word' or 'none'")
    if not isinstance(strategy, str) or strategy not in {"all", "longest", "leftmost_longest"}:
        raise SerializationError("configuration.strategy is invalid")
    terms = payload["terms"]
    if not isinstance(terms, list):
        raise SerializationError("terms must be an array")
    from .matcher import Matcher

    try:
        matcher = Matcher(
            case_sensitive=case_sensitive,
            unicode_normalization=normalization,
            boundary=boundary,
            strategy=strategy,
        )
    except (TypeError, ValueError) as error:
        raise SerializationError("configuration is invalid") from error
    seen_keywords: set[str] = set()
    for entry in terms:
        if not isinstance(entry, dict):
            raise SerializationError("each term must be an object")
        _require_keys(entry, {"keyword", "value", "metadata"}, "term")
        keyword = entry["keyword"]
        metadata = entry["metadata"]
        if not isinstance(keyword, str) or not keyword:
            raise SerializationError("term keyword must be a non-empty string")
        if keyword in seen_keywords:
            raise SerializationError("term keyword is duplicated")
        seen_keywords.add(keyword)
        if metadata is not None and (
            not isinstance(metadata, dict) or not all(isinstance(key, str) for key in metadata)
        ):
            raise SerializationError("term metadata must be an object with string keys or null")
        try:
            matcher.add(keyword, entry["value"], metadata=metadata)
        except (TypeError, ValueError) as error:
            raise SerializationError("term is incompatible with matcher configuration") from error
    return matcher


def _validate_json_value(value: object, ancestors: set[int] | None = None) -> None:
    ancestors = set() if ancestors is None else ancestors
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if math.isfinite(value):
            return
        raise SerializationError("JSON does not represent non-finite floats losslessly")
    if isinstance(value, list):
        _validate_container(value, ancestors)
        for item in value:
            _validate_json_value(item, ancestors)
        ancestors.remove(id(value))
        return
    if isinstance(value, dict):
        _validate_container(value, ancestors)
        for key, item in value.items():
            if not isinstance(key, str):
                raise SerializationError("JSON object keys must be strings")
            _validate_json_value(item, ancestors)
        ancestors.remove(id(value))
        return
    raise SerializationError(f"JSON cannot represent {type(value).__name__} losslessly")


def _validate_container(value: object, ancestors: set[int]) -> None:
    value_id = id(value)
    if value_id in ancestors:
        raise SerializationError("JSON cannot represent cyclic values")
    ancestors.add(value_id)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SerializationError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> object:
    raise SerializationError(f"invalid JSON constant: {value}")


def _require_keys(value: dict[str, object], expected: set[str], name: str) -> None:
    if set(value) != expected:
        raise SerializationError(f"{name} has missing or unknown fields")
