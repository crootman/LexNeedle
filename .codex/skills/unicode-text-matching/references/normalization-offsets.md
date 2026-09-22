# Normalization and Offset Mapping

This reference describes the failure modes to account for when a matcher
searches a normalized or case-folded representation but reports spans into the
original Python string.

## Coordinate Systems

Keep these coordinate systems distinct:

1. **Source coordinates:** Python code-point indices into the caller's original `str`.
2. **Transformed coordinates:** indices in the normalized and case-folded search buffer.
3. **Boundary coordinates:** policy-specific positions that may need to align with a word or grapheme boundary.

Only source coordinates belong in the public `Match.start` and `Match.end`.

## Alignment Requirements

For every transformed code point or token, retain the source interval that
contributed to it. When a transformed unit combines multiple source units, its
interval must cover all contributing source positions. When one source unit
expands into several transformed units, each transformed unit may point to the
same source interval.

When a match begins or ends inside a transformed expansion, choose and document
the source boundary policy. A safe default is to expand the reported span to
the complete contributing source interval so the slicing invariant remains
true. Reject or defer a match if the selected boundary cannot be represented
without splitting a source grapheme according to the configured policy.

## Avoid the Common Shortcut

Do not do this:

```python
normalized = unicodedata.normalize("NFKC", text).casefold()
# Match in normalized and return normalized offsets against text.
```

The transformed string can have different length and boundaries. A correct
implementation must carry an alignment map or use an equivalent incremental
representation that can recover source intervals.

## Tests

Test both equality and coordinate behavior:

```python
assert text[match.start:match.end] == match.text
assert 0 <= match.start <= match.end <= len(text)
```

Include source strings where:

- one source code point case-folds to multiple code points (`U+00DF`)
- composed and decomposed accents represent equivalent text
- compatibility normalization changes representation or width
- combining marks follow a base character
- multiple source characters compose into one transformed unit
- a match is adjacent to punctuation or a non-breaking space

Use the same mapping tests for `finditer()`, `find()`, and replacement. A
replacement implementation that uses transformed offsets can corrupt unrelated
source text even when extraction tests pass.
