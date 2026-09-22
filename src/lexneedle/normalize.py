"""Unicode transformation with source-coordinate provenance."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Literal, cast

from .exceptions import ConfigurationError

type NormalizationForm = Literal["NFC", "NFD", "NFKC", "NFKD"]
Normalization = str | None
_NORMALIZATIONS = frozenset({"NFC", "NFD", "NFKC", "NFKD"})


@dataclass(frozen=True, slots=True)
class Provenance:
    """The source interval and indivisible contribution group of one output scalar."""

    start: int
    end: int
    group: int


@dataclass(frozen=True, slots=True)
class TransformedText:
    """A transformed string and a same-length provenance vector."""

    text: str
    provenance: tuple[Provenance, ...]


@dataclass(slots=True)
class _Unit:
    character: str
    start: int
    end: int
    group: int


def validate_normalization(value: Normalization) -> None:
    """Reject unsupported normalization settings."""
    if value is not None and value not in _NORMALIZATIONS:
        message = "unicode_normalization must be None, 'NFC', 'NFD', 'NFKC', or 'NFKD'"
        raise ConfigurationError(message)


def transform(text: str, *, normalization: Normalization, case_sensitive: bool) -> TransformedText:
    """Transform *text* using the matcher pipeline and retain source provenance."""
    validate_normalization(normalization)
    if normalization is None:
        return _transform_without_normalization(text, case_sensitive=case_sensitive)
    compatibility = normalization in {"NFKC", "NFKD"}
    units = _decompose(text, compatibility=compatibility)
    units = _canonical_order(units)
    if normalization in {"NFC", "NFKC"}:
        units = _compose(units)
    output: list[str] = []
    provenance: list[Provenance] = []
    for unit in units:
        folded = unit.character if case_sensitive else unit.character.casefold()
        for character in folded:
            output.append(character)
            provenance.append(Provenance(unit.start, unit.end, unit.group))
    result = "".join(output)
    expected = text if normalization is None else unicodedata.normalize(_form(normalization), text)
    if not case_sensitive:
        expected = expected.casefold()
    if result != expected:
        raise RuntimeError("internal Unicode transformation did not match unicodedata")
    return TransformedText(result, tuple(provenance))


def transform_key(text: str, *, normalization: Normalization, case_sensitive: bool) -> str:
    """Transform dictionary and lookup text when source provenance is unnecessary."""
    validate_normalization(normalization)
    result = text if normalization is None else unicodedata.normalize(_form(normalization), text)
    return result if case_sensitive else result.casefold()


def _transform_without_normalization(text: str, *, case_sensitive: bool) -> TransformedText:
    """Transform text with its one-code-point-per-source provenance mapping."""
    if case_sensitive or text.isascii():
        provenance = tuple(Provenance(index, index + 1, index) for index in range(len(text)))
        if case_sensitive:
            return TransformedText(text, provenance)
        return TransformedText(text.casefold(), provenance)
    output: list[str] = []
    expanded_provenance: list[Provenance] = []
    for index, character in enumerate(text):
        folded = character.casefold()
        for output_character in folded:
            output.append(output_character)
            expanded_provenance.append(Provenance(index, index + 1, index))
    return TransformedText("".join(output), tuple(expanded_provenance))


def _decompose(text: str, *, compatibility: bool) -> list[_Unit]:
    form = "NFKD" if compatibility else "NFD"
    units: list[_Unit] = []
    for index, character in enumerate(text):
        decomposed = unicodedata.normalize(form, character)
        units.extend(_Unit(part, index, index + 1, index) for part in decomposed)
    return units


def _canonical_order(units: list[_Unit]) -> list[_Unit]:
    ordered: list[_Unit] = []
    run: list[_Unit] = []
    for unit in units:
        if unicodedata.combining(unit.character) == 0:
            ordered.extend(_sort_nonstarters(run))
            run = [unit]
        else:
            run.append(unit)
    ordered.extend(_sort_nonstarters(run))
    return ordered


def _sort_nonstarters(run: list[_Unit]) -> list[_Unit]:
    if not run:
        return []
    if unicodedata.combining(run[0].character) == 0:
        return [run[0], *sorted(run[1:], key=lambda unit: unicodedata.combining(unit.character))]
    return sorted(run, key=lambda unit: unicodedata.combining(unit.character))


def _compose(units: list[_Unit]) -> list[_Unit]:
    """Apply canonical composition, including ccc-zero Hangul composition."""
    if not units:
        return []
    composed: list[_Unit] = []
    starter_index: int | None = None
    last_ccc = 0
    for unit in units:
        ccc = unicodedata.combining(unit.character)
        if starter_index is not None:
            starter = composed[starter_index]
            combined = unicodedata.normalize("NFC", starter.character + unit.character)
            can_compose = len(combined) == 1 and combined != starter.character + unit.character
            unblocked = last_ccc < ccc or last_ccc == 0
            if can_compose and unblocked:
                starter.character = combined
                starter.start = min(starter.start, unit.start)
                starter.end = max(starter.end, unit.end)
                starter.group = min(starter.group, unit.group)
                if ccc == 0:
                    last_ccc = 0
                continue
        composed.append(unit)
        if ccc == 0:
            starter_index = len(composed) - 1
            last_ccc = 0
        else:
            last_ccc = ccc
    return composed


def _form(value: str) -> NormalizationForm:
    return cast(NormalizationForm, value)
