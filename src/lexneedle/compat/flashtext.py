"""A focused FlashText-compatible facade over :class:`lexneedle.Matcher`."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from ..matcher import Matcher


class KeywordProcessor:
    """Support the common FlashText migration API without copying its internals."""

    def __init__(self, case_sensitive: bool = False) -> None:
        self._matcher = Matcher(case_sensitive=case_sensitive)

    def __len__(self) -> int:
        return len(self._matcher)

    def __contains__(self, keyword: object) -> bool:
        return keyword in self._matcher

    def add_keyword(self, keyword: str, clean_name: object | None = None) -> bool:
        existed = keyword in self._matcher
        self._matcher.add(keyword, keyword if clean_name is None else clean_name)
        return not existed

    def add_keywords_from_list(self, keywords: Iterable[str]) -> None:
        for keyword in keywords:
            self.add_keyword(keyword)

    def add_keywords_from_dict(self, keywords: Mapping[object, Iterable[str]]) -> None:
        for clean_name, aliases in keywords.items():
            for alias in aliases:
                self.add_keyword(alias, clean_name)

    def remove_keyword(self, keyword: str) -> bool:
        return self._matcher.remove(keyword)

    def remove_keywords_from_list(self, keywords: Iterable[str]) -> None:
        for keyword in keywords:
            self.remove_keyword(keyword)

    def remove_keywords_from_dict(self, keywords: Mapping[object, Iterable[str]]) -> None:
        for aliases in keywords.values():
            self.remove_keywords_from_list(aliases)

    def extract_keywords(self, sentence: str, span_info: bool = False) -> list[object]:
        matches = self._matcher.find(sentence)
        if span_info:
            return [(match.value, match.start, match.end) for match in matches]
        return [match.value for match in matches]

    def replace_keywords(self, sentence: str) -> str:
        return self._matcher.replace(sentence)

    def get_keyword(self, keyword: str) -> object | None:
        return self._matcher.get(keyword)

    def get_all_keywords(self) -> dict[str, object]:
        return dict(self._matcher.items())
