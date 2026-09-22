# Migrate common FlashText calls

`lexneedle.compat.flashtext.KeywordProcessor` supports the common FlashText
keyword add, extract, replace, remove, and lookup calls while using LexNeedle's
Unicode matching behavior.

```{doctest}
>>> from lexneedle.compat.flashtext import KeywordProcessor
>>> processor = KeywordProcessor()
>>> processor.add_keyword("java", "Java")
True
>>> processor.extract_keywords("Java and java")
['Java', 'Java']
```

This facade is not a byte-for-byte FlashText implementation. Its default word
boundary is Unicode-aware rather than ASCII-only; case-insensitive matching
uses `casefold()` rather than `lower()`; transformed collisions are rejected;
and values and metadata remain structured internally. It intentionally omits
FlashText fuzzy search, mapping operators, and mutable non-word-boundary sets.

Pass `boundary="none"` for CJK or intentional substring matching,
`strategy="all"` to retain overlaps, and `whitespace_equivalent=True` to treat
Unicode whitespace runs as one separator.
