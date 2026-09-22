# Performance and limits

LexNeedle uses a mutable character trie and scans candidate starts iteratively.
It does not use regular-expression construction or Aho-Corasick failure links.
Matching work is proportional to scanned candidate paths rather than a strict
complexity promise.

`finditer()` first constructs aligned transformed input, then streams selected
leftmost-longest candidates. It is not full-input streaming and does not provide
a bounded-memory guarantee. Matchers are unsynchronized: concurrent reads of an
unchanged matcher are safe, but do not mutate one while another thread uses it.

`global_longest` materializes candidates and compares each candidate with the
already selected matches. Selection can be quadratic on candidate-dense input;
use `leftmost_longest` for high-density workloads when its local greedy policy
fits the result you need.

## Chunking

Independently matching arbitrary chunks can miss a term that crosses a chunk
boundary. There is no generally safe fixed overlap when normalization or
whitespace equivalence is enabled: a normalized term may cover a longer source
sequence, and a collapsed whitespace run has unbounded source length. A caller
that chunks input must retain sufficient original context for its own terms and
deduplicate reported spans.

LexNeedle does not currently offer frozen concurrent matchers, Aho-Corasick
failure links, or compact compiled dictionaries. The benchmark suite provides
repeatable workloads, not a general speed or memory claim. Run it with:

```shell
uv run pytest benchmarks/test_extract.py --benchmark-only
uv run pytest benchmarks/test_matrix.py --benchmark-only
```

Set `LEXNEEDLE_BENCHMARK_LARGE=1` to include larger dictionary and input sizes.
The benchmark configuration and measured data are described in
{doc}`../architecture`.
