# LexNeedle

Fast, deterministic dictionary matching for Python 3.14+, with zero runtime dependencies.

Install with `uv add lexneedle`.

```python
from lexneedle import Matcher

matcher = Matcher()
matcher.add("Panadol", value="paracetamol", metadata={"type": "brand"})

for match in matcher.find("Panadol 500mg tablets"):
    print(match.text, match.value, match.start, match.end)
```

`Match.start` and `Match.end` always index the original Python string, so
`text[match.start:match.end] == match.text`.

`Matcher` is case-insensitive by default using locale-independent Unicode
`casefold()`. It supports `None`, `NFC`, `NFD`, `NFKC`, and `NFKD`
normalization; normalization occurs before case folding and preserves source
offsets. The default `boundary="word"` treats Unicode letters, marks, numbers,
connector punctuation, and joiners as word characters. It is not a full UAX #29
word segmenter. Use `boundary="none"` for substring matching or pass a callable
receiving `(text, position)`.

The default `leftmost_longest` strategy chooses the earliest match, then the
longest at that position, and skips overlaps. `all` returns all candidates in
source order (longer before shorter at the same offset); `longest` keeps the
longest candidate at each start, including overlaps. Terms that collide after
normalization/case folding are rejected, ensuring results never depend on
insertion order.

Aliases can share canonical data:

```python
matcher.add(["Panadol", "Panadol Osteo"], value="paracetamol")
```

`replace()` uses leftmost-longest matching. Values must be strings unless a
replacement callable explicitly converts a structured value. `save()` and
`Matcher.load()` use validated, versioned JSON and reject values JSON cannot
represent losslessly. Metadata is copied shallowly and exposed as a read-only
outer mapping.

For FlashText migrations, `lexneedle.compat.flashtext.KeywordProcessor`
supports the common keyword add, extract, replace, remove, and lookup methods.

```python
matches_by_document = list(matcher.find_many(["Panadol", "none"]))
matcher = Matcher(boundary=lambda text, position: position in {0, len(text)})
matcher.add("ID-7", value={"id": 7})
assert matcher.replace("ID-7", lambda match: str(match.value["id"])) == "7"
persistent = Matcher()
persistent.add("Panadol", value="paracetamol")
persistent.save("terms.json")
restored = Matcher.load("terms.json")
```

Empty terms and transformed collisions raise `ConfigurationError`. Malformed
JSON, unsupported values, duplicate fields, and non-finite numbers raise
`SerializationError`. Membership, lookup, and removal use normalized identity.
The compatibility facade intentionally omits FlashText fuzzy search, mapping
operators, and mutable non-word-boundary sets. It uses LexNeedle's casefolding,
Unicode boundaries, transformed-collision rejection, and structured internals;
these differ from FlashText's ASCII boundary and `lower()` behavior.

Matching work is proportional to scanned candidate paths, rather than a promise
of a strict complexity bound. `finditer()` constructs the aligned transformed
input first, then streams leftmost-longest candidates. Offsets count Python code
points. The matcher protects common combining, spacing-mark, variation-selector,
and ZWJ edges, but it does not claim full Unicode grapheme segmentation.

## Benchmarks

Run `uv run pytest benchmarks/test_extract.py --benchmark-only` for extraction,
or `uv run pytest benchmarks/test_matrix.py --benchmark-only` for construction,
replacement, memory, Unicode, dictionary-size, and workload dimensions. Use
`uv run --with flashtext pytest benchmarks/test_extract.py --benchmark-only` to
include FlashText; set `LEXNEEDLE_BENCHMARK_LARGE=1` for 10k/100k dictionaries
and a 10 MB text. The default input matrix is small (70 bytes), paragraph
(3.5 KB), and 1.05 MB; large mode adds 10.5 MB. Use pytest-benchmark's
`--benchmark-json results.json` to save timing plus `peak_bytes` and
`input_bytes` metrics. The extraction comparison projects canonical values under
equal case-insensitive word-boundary semantics. No speed claim is made. See
[architecture notes](docs/architecture.md).

## Limits

The first release intentionally does not implement streaming, frozen concurrent
matchers, Aho-Corasick failure links, or memory-optimized compiled dictionaries.
Benchmarks are supplied as pytest-benchmark workloads; they make no speed claim.
