# Architecture and research notes

LexNeedle uses a mutable character trie. It scans candidate starts iteratively;
it does not use recursion, user-built regular expressions, or Aho-Corasick
failure links. Shared prefixes share trie nodes.

The design was informed by [FlashText](https://github.com/vi3k6i5/flashtext),
Vikash Singh's [2017 paper](https://arxiv.org/abs/1711.00046),
[flashtext-i18n](https://github.com/termdock/flashtext-i18n),
[flashtext2](https://github.com/shner-elmo/flashtext2), and
[pyahocorasick](https://pyahocorasick.readthedocs.io/). No source code from
these projects is included.

Input transformation retains source provenance for each output scalar. A match
must cover whole contribution groups and transform back to its source slice;
this rejects partial `ß` case-fold expansions. Mutation is unsynchronized: do
not mutate a matcher while another thread uses it. Streaming, freezing, and
compact compiled dictionaries remain future work.
