# Choose boundaries and overlap strategies

The default `boundary="word"` requires a boundary on each exterior side of a
candidate. Word characters include Unicode letters, marks, numbers, connector
punctuation, and joiners. This is intentionally not a full UAX #29 word
segmenter.

Use `boundary="none"` when substring matching is intentional:

```{doctest}
>>> matcher = Matcher(boundary="none")
>>> matcher.add("needle")
>>> [match.start for match in matcher.find("hayneedle")]
[3]
```

A legacy boundary callable receives `(text, position)`. A side-aware policy
can receive `(text, position, "left" | "right")`; it is only available with the
built-in word boundary.

## Overlaps

`leftmost_longest` is the default: choose the earliest valid match, choose the
longest match at that position, then skip overlaps. `all` keeps every candidate
in source order, with longer candidates first at the same start. `longest`
keeps one longest candidate per start, including overlaps. `global_longest`
selects globally longest non-overlapping candidates, breaking equal lengths by
source position then keyword, and returns source order.

```{doctest}
>>> matcher = Matcher(boundary="none")
>>> matcher.add_many(["aba", "ba"])
>>> [(m.keyword, m.start) for m in matcher.find("ababa", strategy="all")]
[('aba', 0), ('ba', 1), ('aba', 2), ('ba', 3)]
>>> [(m.keyword, m.start) for m in matcher.find("ababa")]
[('aba', 0), ('ba', 3)]
```

Terms that collide after the configured normalization and case policy are
rejected, so registration order cannot decide a result.

## Whitespace equivalence

Set `whitespace_equivalent=True` to make each non-empty run of Unicode
whitespace match one searchable separator. It is opt-in and returns the
original input slice and offsets:

```{doctest}
>>> matcher = Matcher(whitespace_equivalent=True)
>>> matcher.add("New York")
>>> match = matcher.find("New\u00a0\tYork")[0]
>>> match.text
'New\xa0\tYork'
```

Leading and trailing whitespace in a term remain significant. See
{doc}`../explanation/performance-and-limits` before trying to chunk input with
whitespace equivalence enabled.
