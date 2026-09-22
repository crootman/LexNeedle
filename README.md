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
represent losslessly. Saving writes a temporary file beside the resolved target
and then atomically replaces it, so a write failure does not truncate an
existing file. Saving through a symlink updates its target and preserves an
existing target's POSIX mode bits; a new file uses mode `0o600` on POSIX,
subject to the process umask. Saving does not promise ownership or ACL
preservation, and it is not a power-loss durability guarantee. Metadata is
copied shallowly and exposed as a read-only outer mapping.

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
input first, then streams leftmost-longest candidates; it does not provide
full-input streaming or a bounded-memory guarantee. Offsets count Python code
points. The matcher protects common combining, spacing-mark, variation-selector,
and ZWJ edges, but it does not claim full Unicode grapheme segmentation.

## Benchmarks

Run `uv run pytest benchmarks/test_extract.py --benchmark-only` for the
controlled extraction comparison, or `uv run pytest benchmarks/test_matrix.py
--benchmark-only` for the full matrix. The fast matrix includes 1 KiB and
100 KiB input texts and 10-, 100-, and 1,000-term dictionaries. Set
`LEXNEEDLE_BENCHMARK_LARGE=1` to add 10,000- and 100,000-term dictionaries and
1 MiB and 10 MiB inputs.

The matrix separately measures construction, varied dictionaries, no/few/many
match density, shared prefixes, hundreds-character hits and near misses,
overlap strategies, `finditer()` consumption, replacement, case policy,
normalization, isolated alignment transforms, Unicode scripts, serialization,
and retained/peak memory. It records configuration and input details in
pytest-benchmark `extra_info`. Memory is measured in a separate traced pass,
so timed benchmark calls remain untraced. Use pytest-benchmark's
`--benchmark-json results.json` to save the results.

Use `uv run --with flashtext pytest benchmarks/test_extract.py
--benchmark-only` to include FlashText. The regex and FlashText tests use a
controlled ASCII workload with equivalent case-insensitive word-boundary
results; they do not establish general Unicode equivalence. No speed claim is
made. See [architecture notes](docs/architecture.md) and
[performance review](docs/performance-review.md).

## Limits

The first release intentionally does not implement full-input streaming,
frozen concurrent matchers, Aho-Corasick failure links, or memory-optimized
compiled dictionaries. Benchmarks are supplied as pytest-benchmark workloads;
they make no speed claim.
