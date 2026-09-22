# LexNeedle

Deterministic Unicode-aware dictionary matching for Python 3.14+, with zero
runtime dependencies.

## Installation

Install the latest published release from PyPI:

```shell
uv add lexneedle
```

To try the unreleased `main` branch instead:

```shell
uv add "git+https://github.com/crootman/LexNeedle"
```

## Quick start

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
offsets. A reported match must cover whole normalization contribution groups and
its source slice must re-transform to the exact transformed match. For example,
NFC composes `á` in `"a\u0334\u0301"`, but the composed character covers all
three source code points, so that candidate is intentionally not reported. This
keeps offsets and re-matching self-consistent. The default `boundary="word"`
treats Unicode letters, marks, numbers, connector punctuation, and joiners as
word characters. It checks the exterior character before and after a candidate
independently, so punctuation inside a registered term cannot make an adjacent
word character look like a boundary. It is not a full UAX #29 word segmenter.
Use `boundary="none"` for substring matching, a legacy callable receiving
`(text, position)`, or `side_boundary=` with `(text, position, "left" | "right")`
for a side-aware word policy.

The default `leftmost_longest` strategy chooses the earliest match, then the
longest at that position, and skips overlaps. `all` returns all candidates in
source order (longer before shorter at the same offset); `longest` keeps the
longest candidate at each start, including overlaps. Terms that collide after
normalization/case folding are rejected, ensuring results never depend on
insertion order. `global_longest` greedily selects longest candidates across
the complete input, resolving equal lengths by source position and keyword,
then returns the non-overlapping selection in source order.
Its selection pass compares each candidate with every already selected match,
so it can have quadratic selection work on inputs with many candidates; use
`leftmost_longest` for high-density workloads because it avoids materializing
every candidate.

Set `whitespace_equivalent=True` to make every non-empty run of Unicode
whitespace in a term or input match one separator. It is opt-in and preserves
the original input slice and offsets; for example, `"New York"` can match
`"New\u00a0\tYork"`. `replace_with_matches()` returns the replacement result
and the selected `Match` objects without a second scan.

Aliases can share canonical data:

```python
matcher.add(["Panadol", "Panadol Osteo"], value="paracetamol")
```

`replace()` uses leftmost-longest matching by default (or `global_longest` if
configured). Values must be strings unless a
replacement callable explicitly converts a structured value. `save()` and
`Matcher.load()` use validated, versioned JSON and reject values JSON cannot
represent losslessly. Saving writes a temporary file beside the resolved target
and then atomically replaces it, so a write failure does not truncate an
existing file. Saving through a symlink updates its target and preserves an
existing target's POSIX mode bits; a new file uses mode `0o600` on POSIX,
subject to the process umask. Saving does not promise ownership or ACL
preservation, and it is not a power-loss durability guarantee; a crash between
writing the temporary file and replacing the destination can leave a
`.lexneedle-*.tmp` file beside it. Metadata is copied shallowly and exposed as a
read-only outer mapping.

For FlashText migrations, `lexneedle.compat.flashtext.KeywordProcessor`
supports the common keyword add, extract, replace, remove, and lookup methods.
Its `boundary="none"` option enables CJK/substring matching; pass
`strategy="all"` (or per-call `extract_keywords(..., strategy="all")`) to
retain overlaps; pass `whitespace_equivalent=True` to match Unicode whitespace
runs as one separator.

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
`items()` yields `(keyword, value)` pairs and iteration yields keywords, both in
sorted order, so enumeration never depends on insertion order. The
compatibility facade intentionally omits FlashText fuzzy search, mapping
operators, and mutable non-word-boundary sets. It uses LexNeedle's casefolding,
Unicode boundaries, transformed-collision rejection, and structured internals;
these differ from FlashText's ASCII boundary and `lower()` behavior.

Matching work is proportional to scanned candidate paths, rather than a promise
of a strict complexity bound. `finditer()` constructs the aligned transformed
input first, then streams leftmost-longest candidates; it does not provide
full-input streaming or a bounded-memory guarantee. Offsets count Python code
points. The matcher protects common combining, spacing-mark, variation-selector,
and ZWJ edges by not reporting candidates that would split them, but it does not
claim full Unicode grapheme segmentation.

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
made. See the
[architecture notes](https://github.com/crootman/LexNeedle/blob/main/docs/architecture.md).

## Limits

Version 0.1.0 intentionally does not implement full-input streaming,
frozen concurrent matchers, Aho-Corasick failure links, or memory-optimized
compiled dictionaries. Matchers are not synchronized: do not mutate one while
another thread reads it; concurrent reads of an unchanged matcher are safe.
Benchmarks are supplied as pytest-benchmark workloads; they make no speed claim.
For large inputs, process the complete text when possible. Independently
matching arbitrary chunks can miss terms crossing a chunk boundary. There is
no generally safe fixed overlap when normalization or whitespace equivalence is
enabled: a normalized term can cover a longer source sequence and a collapsed
whitespace run has unbounded source length. Callers that chunk input must retain
enough original text for their own constraints and deduplicate reported spans;
true streaming remains unsupported. JSON is the safe, versioned persistence
format.
Standard-library pickle is supported only for trusted local process transfer;
all values, metadata, and custom policies must themselves be pickleable.
