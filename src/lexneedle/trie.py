"""A small mutable trie used by :class:`lexneedle.Matcher`."""

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Term:
    """The data associated with one searchable term."""

    keyword: str
    value: object
    metadata: Mapping[str, object] | None


class Node:
    """One node in the character trie."""

    __slots__ = ("children", "term")

    def __init__(self) -> None:
        self.children: dict[str, Node] = {}
        self.term: Term | None = None


class Trie:
    """Store transformed terms without exposing trie implementation details."""

    __slots__ = ("root",)

    def __init__(self) -> None:
        self.root = Node()

    def get(self, key: str) -> Term | None:
        node = self.root
        for character in key:
            child = node.children.get(character)
            if child is None:
                return None
            node = child
        return node.term

    def set(self, key: str, term: Term) -> None:
        node = self.root
        for character in key:
            node = node.children.setdefault(character, Node())
        node.term = term

    def remove(self, key: str) -> bool:
        node = self.root
        path: list[tuple[Node, str]] = []
        for character in key:
            child = node.children.get(character)
            if child is None:
                return False
            path.append((node, character))
            node = child
        if node.term is None:
            return False
        node.term = None
        for parent, character in reversed(path):
            child = parent.children[character]
            if child.term is not None or child.children:
                break
            del parent.children[character]
        return True
