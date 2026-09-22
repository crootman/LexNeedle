# Unicode matching and source offsets

LexNeedle applies the configured Unicode normalization first, then
locale-independent `str.casefold()` unless `case_sensitive=True`. It supports
`None`, `NFC`, `NFD`, `NFKC`, and `NFKD` normalization.

The searchable transformed text retains provenance to the original Python
string. Every `Match.start` and `Match.end` therefore indexes the source, not a
case-folded or normalized buffer:

```{doctest}
>>> matcher = Matcher(unicode_normalization="NFC")
>>> matcher.add("café")
>>> text = "cafe\u0301"
>>> match = matcher.find(text)[0]
>>> (match.start, match.end, text[match.start : match.end])
(0, 5, 'café')
```

A reported match must cover whole normalization contribution groups and the
matched source slice must transform back to the exact searchable term. This
deliberately rejects candidates that would split a case-fold expansion or a
normalization group. It also protects common combining, spacing-mark,
variation-selector, and ZWJ edges; LexNeedle does not claim full Unicode
grapheme segmentation.

Case folding is locale-independent. It is useful for Unicode caseless matching,
but it is not a locale-sensitive Turkish equivalence policy and it does not
remove accents: `Müller` does not become `Muller` merely by case folding or the
normalization forms LexNeedle exposes.
