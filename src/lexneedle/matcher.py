"""The public deterministic dictionary matcher."""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable, Iterator, Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Literal

from .boundaries import Boundary, no_boundary, word_boundary
from .exceptions import ConfigurationError
from .match import Match
from .normalize import (
    Normalization,
    Provenance,
    TransformedText,
    transform,
    transform_key,
    validate_normalization,
)
from .trie import Term, Trie

type Strategy = Literal["all", "longest", "leftmost_longest"]
type Replacement = str | Callable[[Match], str]
_STRATEGIES = frozenset({"all", "longest", "leftmost_longest"})
_DEFAULT_VALUE = object()


class Matcher:
    """Find registered terms in text with explicit Unicode and overlap semantics.

    Case-insensitive matching uses locale-independent :meth:`str.casefold` after
    optional Unicode normalization. ``boundary='word'`` treats Unicode letters,
    marks, numbers, connector punctuation, and joiners as word characters; it is
    deliberately not a full UAX #29 word segmenter. Source offsets always index
    the original Python string.
    """

    def __init__(
        self,
        *,
        case_sensitive: bool = False,
        unicode_normalization: Normalization = None,
        boundary: Literal["word", "none"] | Boundary = "word",
        strategy: Strategy = "leftmost_longest",
    ) -> None:
        validate_normalization(unicode_normalization)
        self._validate_strategy(strategy)
        if not isinstance(case_sensitive, bool):
            raise ConfigurationError("case_sensitive must be a boolean")
        self._case_sensitive = case_sensitive
        self._unicode_normalization = unicode_normalization
        self._strategy = strategy
        self._boundary_spec = boundary
        self._boundary = self._resolve_boundary(boundary)
        self._trie = Trie()
        self._keys: dict[str, Term] = {}

    def __len__(self) -> int:
        """Return the number of registered searchable terms."""
        return len(self._keys)

    @property
    def case_sensitive(self) -> bool:
        """Whether matching compares case-sensitive transformed text."""
        return self._case_sensitive

    @property
    def unicode_normalization(self) -> Normalization:
        """The Unicode normalization performed before optional case folding."""
        return self._unicode_normalization

    @property
    def strategy(self) -> Strategy:
        """The default overlap strategy."""
        return self._strategy

    @property
    def boundary(self) -> Literal["word", "none"] | Boundary:
        """The configured boundary policy."""
        return self._boundary_spec

    def __contains__(self, keyword: object) -> bool:
        """Return whether *keyword* is registered under this matcher's policy."""
        return isinstance(keyword, str) and self._key(keyword) in self._keys

    def add(
        self,
        keyword: str | Iterable[str],
        value: object = _DEFAULT_VALUE,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        """Register one term or aliases sharing one value and metadata.

        A repeated identical keyword updates its associated value. Two different
        spellings that normalize and case-fold to the same searchable key are
        rejected so results do not depend on insertion order.
        """
        keywords = (keyword,) if isinstance(keyword, str) else tuple(keyword)
        if not keywords:
            raise ConfigurationError("at least one keyword is required")
        snapshot = self._metadata_snapshot(metadata)
        additions: list[tuple[str, Term]] = []
        seen: dict[str, str] = {}
        for item in keywords:
            if not isinstance(item, str):
                raise TypeError("keywords must be strings")
            if not item:
                raise ConfigurationError("keywords must not be empty")
            key = self._key(item)
            if not key:
                raise ConfigurationError("keywords must not normalize to an empty string")
            previous = seen.setdefault(key, item)
            if previous != item:
                raise ConfigurationError("aliases collide after normalization or case folding")
            existing = self._keys.get(key)
            if existing is not None and existing.keyword != item:
                raise ConfigurationError("keyword collides with an existing normalized term")
            additions.append(
                (key, Term(item, item if value is _DEFAULT_VALUE else value, snapshot))
            )
        for key, term in additions:
            self._trie.set(key, term)
            self._keys[key] = term

    def add_many(self, keywords: Iterable[str] | Mapping[str, object]) -> None:
        """Register an iterable of terms or a mapping of terms to canonical values."""
        if isinstance(keywords, Mapping):
            for keyword, value in keywords.items():
                self.add(keyword, value)
            return
        for keyword in keywords:
            self.add(keyword)

    def remove(self, keyword: str) -> bool:
        """Remove *keyword*, returning whether it was registered."""
        if not isinstance(keyword, str):
            raise TypeError("keyword must be a string")
        key = self._key(keyword)
        term = self._keys.get(key)
        if term is None:
            return False
        removed = self._trie.remove(key)
        if removed:
            del self._keys[key]
        return removed

    def clear(self) -> None:
        """Remove every registered term."""
        self._trie = Trie()
        self._keys.clear()

    def get(self, keyword: str, default: object | None = None) -> object | None:
        """Return a keyword's canonical value, or *default* when absent."""
        if not isinstance(keyword, str):
            raise TypeError("keyword must be a string")
        term = self._keys.get(self._key(keyword))
        return default if term is None else term.value

    def find(self, text: str, *, strategy: Strategy | None = None) -> list[Match]:
        """Return matching terms in deterministic source-order."""
        return list(self.finditer(text, strategy=strategy))

    def finditer(self, text: str, *, strategy: Strategy | None = None) -> Iterator[Match]:
        """Yield matching terms in deterministic source-order.

        ``all`` yields every valid candidate. ``longest`` retains the longest
        candidate at each starting offset, even where candidates overlap.
        ``leftmost_longest`` greedily emits the earliest start and longest span,
        then skips every overlap; it is the default and replacement strategy.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        selected_strategy = self.strategy if strategy is None else strategy
        self._validate_strategy(selected_strategy)
        transformed = transform(
            text, normalization=self.unicode_normalization, case_sensitive=self.case_sensitive
        )
        if selected_strategy == "all":
            yield from sorted(
                self._iter_candidates(text, transformed),
                key=lambda match: (match.start, -match.end, match.keyword),
            )
        elif selected_strategy == "longest":
            # Canonical reordering can make distinct transformed starts map to
            # the same source start. Resolve this strategy in source space.
            yield from self._longest_per_start(list(self._iter_candidates(text, transformed)))
        else:
            yield from self._leftmost_longest_source_order(text, transformed)

    def find_many(
        self, texts: Iterable[str], *, strategy: Strategy | None = None
    ) -> Iterator[list[Match]]:
        """Yield :meth:`find` results for every input text without implicit concurrency."""
        for text in texts:
            yield self.find(text, strategy=strategy)

    def replace(
        self,
        text: str,
        replacement: Replacement | None = None,
        *,
        strategy: Strategy | None = None,
    ) -> str:
        """Replace non-overlapping leftmost-longest matches in *text*.

        Without a callable replacement each canonical value must already be a
        string. This prevents accidental conversion of structured values.
        """
        selected_strategy = self.strategy if strategy is None else strategy
        if selected_strategy != "leftmost_longest":
            raise ConfigurationError("replacement requires strategy='leftmost_longest'")
        matches = self.find(text, strategy=selected_strategy)
        parts: list[str] = []
        previous_end = 0
        for match in matches:
            parts.append(text[previous_end : match.start])
            if replacement is None:
                if not isinstance(match.value, str):
                    raise TypeError(
                        "replacement values must be strings; use a replacement callable"
                    )
                parts.append(match.value)
            elif isinstance(replacement, str):
                parts.append(replacement)
            else:
                value = replacement(match)
                if not isinstance(value, str):
                    raise TypeError("replacement callable must return a string")
                parts.append(value)
            previous_end = match.end
        parts.append(text[previous_end:])
        return "".join(parts)

    def save(self, path: str | Path) -> None:
        """Save as versioned, lossless JSON using same-directory atomic replacement.

        Saving through a symlink replaces its target and preserves an existing
        target's POSIX mode bits. A new file uses mode ``0o600`` on POSIX,
        subject to the process umask. Atomic replacement does not guarantee
        durability if the system loses power.
        """
        from .serialization import save

        save(self, path)

    @classmethod
    def load(cls, path: str | Path) -> Matcher:
        """Load a matcher written by :meth:`save`."""
        from .serialization import load

        return load(path)

    def _key(self, keyword: str) -> str:
        return transform_key(
            keyword, normalization=self.unicode_normalization, case_sensitive=self.case_sensitive
        )

    def _iter_candidates(self, source: str, transformed: TransformedText) -> Iterator[Match]:
        extents = self._group_extents(transformed)
        for start in range(len(transformed.text)):
            yield from self._candidates_at_start(source, transformed, extents, start)

    def _candidates_at_start(
        self,
        source: str,
        transformed: TransformedText,
        extents: dict[int, tuple[int, int]],
        start: int,
    ) -> Iterator[Match]:
        node = self._trie.root
        for end in range(start, len(transformed.text)):
            child = node.children.get(transformed.text[end])
            if child is None:
                return
            node = child
            if node.term is not None:
                match = self._make_match(source, transformed, extents, start, end + 1, node.term)
                if match is not None:
                    yield match

    def _make_match(
        self,
        source: str,
        transformed: TransformedText,
        extents: dict[int, tuple[int, int]],
        start: int,
        end: int,
        term: Term,
    ) -> Match | None:
        provenance = transformed.provenance[start:end]
        if not provenance or not self._whole_groups(provenance, extents, start, end):
            return None
        source_start = min(item.start for item in provenance)
        source_end = max(item.end for item in provenance)
        if not self._safe_span(source, source_start, source_end):
            return None
        if not self._boundary(source, source_start) or not self._boundary(source, source_end):
            return None
        source_text = source[source_start:source_end]
        transformed_slice = transformed.text[start:end]
        if self._key(source_text) != transformed_slice:
            return None
        return Match(term.keyword, source_text, term.value, source_start, source_end, term.metadata)

    @staticmethod
    def _group_extents(transformed: TransformedText) -> dict[int, tuple[int, int]]:
        extents: dict[int, tuple[int, int]] = {}
        for index, item in enumerate(transformed.provenance):
            previous = extents.get(item.group)
            extents[item.group] = (index, index) if previous is None else (previous[0], index)
        return extents

    @staticmethod
    def _whole_groups(
        provenance: tuple[Provenance, ...],
        extents: dict[int, tuple[int, int]],
        start: int,
        end: int,
    ) -> bool:
        return all(
            start <= extents[item.group][0] and extents[item.group][1] < end for item in provenance
        )

    @staticmethod
    def _safe_span(source: str, start: int, end: int) -> bool:
        return (
            start == 0
            or (
                not _is_grapheme_extend(source[start])
                and source[start] != "\u200d"
                and source[start - 1] != "\u200d"
            )
        ) and (
            end == len(source)
            or (
                not _is_grapheme_extend(source[end])
                and source[end] != "\u200d"
                and source[end - 1] != "\u200d"
            )
        )

    @staticmethod
    def _longest_per_start(candidates: list[Match]) -> Iterator[Match]:
        by_start: dict[int, Match] = {}
        for match in candidates:
            current = by_start.get(match.start)
            if current is None or (match.end, match.keyword) > (current.end, current.keyword):
                by_start[match.start] = match
        yield from sorted(
            by_start.values(), key=lambda match: (match.start, -match.end, match.keyword)
        )

    def _leftmost_longest_source_order(
        self, source: str, transformed: TransformedText
    ) -> Iterator[Match]:
        """Stream source-ordered results while buffering only reordered starts."""
        extents = self._group_extents(transformed)
        suffix_min = [len(source)] * (len(transformed.text) + 1)
        for index in range(len(transformed.text) - 1, -1, -1):
            suffix_min[index] = min(suffix_min[index + 1], transformed.provenance[index].start)
        pending: dict[int, Match] = {}
        occupied_until = 0
        for index in range(len(transformed.text)):
            for match in self._candidates_at_start(source, transformed, extents, index):
                current = pending.get(match.start)
                if current is None or (match.end, match.keyword) > (current.end, current.keyword):
                    pending[match.start] = match
            threshold = suffix_min[index + 1]
            for start in sorted(key for key in pending if key < threshold):
                match = pending.pop(start)
                if match.start >= occupied_until:
                    yield match
                    occupied_until = match.end
        for start in sorted(pending):
            match = pending[start]
            if match.start >= occupied_until:
                yield match
                occupied_until = match.end

    @staticmethod
    def _metadata_snapshot(metadata: Mapping[str, object] | None) -> Mapping[str, object] | None:
        if metadata is None:
            return None
        if not isinstance(metadata, Mapping) or not all(isinstance(key, str) for key in metadata):
            raise TypeError("metadata must be a mapping with string keys")
        return MappingProxyType(dict(metadata))

    @staticmethod
    def _resolve_boundary(boundary: Literal["word", "none"] | Boundary) -> Boundary:
        if boundary == "word":
            return word_boundary
        if boundary == "none":
            return no_boundary
        if callable(boundary):
            return boundary
        raise ConfigurationError("boundary must be 'word', 'none', or a callable")

    @staticmethod
    def _validate_strategy(strategy: str) -> None:
        if strategy not in _STRATEGIES:
            raise ConfigurationError("strategy must be 'all', 'longest', or 'leftmost_longest'")


def _is_grapheme_extend(character: str) -> bool:
    return unicodedata.combining(character) != 0 or unicodedata.category(character) in {
        "Mc",
        "Me",
        "Mn",
    }
