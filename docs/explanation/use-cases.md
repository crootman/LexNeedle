# Use cases and alternatives

LexNeedle's sweet spot is exact-match, dictionary-driven, Unicode-aware
matching with deterministic results and source offsets that remain usable in
the original text.

## Known-identifier redaction

When sensitive values come from a curated list—customer names, known email
addresses, account identifiers, or internal project names—LexNeedle can locate
and redact those exact entries. Unicode case folding allows `Straße` to match
`STRASSE`, and optional normalization handles canonically or compatibly
equivalent text. The returned offsets make a redaction auditable. It does not
discover unknown identifiers from a pattern; use regular expressions or a
dedicated PII detector for that job.

## Content filtering and terminology audits

Attach a structured value such as `{"term": "card", "category": "payment"}`
to a term list. Support tickets, scraped pages, localization strings, and
preprocessing inputs can then be tagged from a reviewed configuration instead
of a chain of application conditionals. Sorted iteration and deterministic
matching make forbidden-term and terminology audits repeatable.

## Offset-sensitive processing

Pipelines that extract a span, process it, and insert it back into the source
need `text[match.start : match.end] == match.text`. LexNeedle guarantees that
invariant for each reported match, including when matching applies case folding
or normalization.

## Choose another tool when

- You need to recognize an unknown structured pattern once or from arbitrary
  text: use `re` or the third-party `regex` module.
- You need typo tolerance or fuzzy search: use a dedicated fuzzy-search tool
  such as RapidFuzz or an edit-distance index.
- You need true grapheme or word segmentation: use ICU or another implementation
  verified for the relevant UAX #29 requirements.
- You need very large dictionaries or a streaming-oriented architecture:
  benchmark an Aho-Corasick implementation such as `pyahocorasick` against
  your workload.

See {doc}`performance-and-limits` for LexNeedle's own limits.
