---
name: unicode-text-matching
description: This skill should be used when implementing or reviewing Unicode-aware matching, case folding, normalization, word boundaries, grapheme boundaries, or original-offset preservation in a text-processing library.
---

# Unicode Text Matching

Design text matching around explicit Unicode semantics instead of ASCII
assumptions. Keep the matching representation separate from the source text so
normalization and case folding cannot silently corrupt public offsets.

## Use This Skill When

- Adding or changing case-sensitive or case-insensitive matching
- Implementing Unicode normalization or boundary policies
- Handling combining marks, emoji, CJK, or right-to-left scripts
- Returning spans after transforming the search representation
- Reviewing a trie or matcher for deterministic Unicode behavior

## Non-Negotiable Invariant

Public offsets refer to the original Python string:

```python
text[match.start:match.end] == match.text
```

Python string offsets count Unicode code points, not UTF-8 bytes and not
user-perceived grapheme clusters. Do not expose offsets from a normalized,
case-folded, encoded, or tokenized buffer as if they were source offsets.

## Transformation Pipeline

Define and document the order of operations. A typical pipeline is:

1. Validate matcher configuration and reject unsupported normalization modes.
2. Transform dictionary terms with the same normalization and case policy as input.
3. Transform the input while retaining an alignment from transformed positions to source intervals.
4. Match only in the transformed representation.
5. Convert every selected transformed span back to the smallest correct source span.
6. Build `Match.text` from the original input slice, never from transformed text.

Normalization can compose, decompose, reorder, or change the number of code
points. Case folding can expand a single source character. Use an explicit
alignment strategy and test expansion, contraction, and combining-mark cases;
do not assume a one-to-one character mapping.

Read `references/normalization-offsets.md` before changing the mapping design.

## Case Handling

- Use exact code-point comparison for case-sensitive mode.
- Prefer `str.casefold()` over `str.lower()` for Unicode-insensitive matching.
- Document locale-independent behavior; do not silently implement Turkish-specific rules.
- Test characters whose folded form changes length, including `U+00DF` (sharp s).

## Boundaries Are Policies

Keep boundary detection outside trie storage. Distinguish:

- **word boundaries:** whether a term is adjacent to word-like text
- **grapheme boundaries:** whether a span splits a user-perceived character
- **script segmentation:** behavior for scripts such as Chinese, Japanese, Thai, or Lao
- **substring mode:** explicit opt-in matching without word boundaries

Unicode Standard Annex #29 defines default grapheme, word, and sentence
segmentation as separate algorithms. Python's standard library exposes useful
Unicode properties but does not by itself provide a complete UAX #29 word
segmenter. If the zero-dependency core implements a deliberate subset or
tailoring, name the policy and test its limits rather than claiming full
Unicode conformance.

Never split a returned match inside a combining sequence or grapheme cluster
unless the public API explicitly documents code-point spans as the desired
behavior.

## Deterministic Matching

Specify tie-breaking independently of dictionary insertion order. Test:

- shared prefixes and one term containing another
- aliases with identical transformed forms
- overlaps beginning at different positions
- duplicate insertion and removal
- `all`, `longest`, and `leftmost_longest` strategies

Keep the algorithm finite and iterative for untrusted input. Avoid building a
large regular expression from user-controlled terms or using recursion that
scales with input length.

## Test Matrix

At minimum, cover:

- accented Latin text, `U+00DF`, Greek, Cyrillic, Arabic, Hebrew, and Devanagari
- Chinese, Japanese, and Korean text without ASCII word separators
- combining marks, non-breaking spaces, punctuation, and emoji sequences
- normalization forms NFC, NFD, NFKC, and NFKD where supported
- case-fold expansion and source-offset preservation
- text beginning or ending at a boundary and text containing adjacent terms

Use explicit regression tests for discovered failures and property tests for
the slicing invariant and deterministic ordering.

## Review Checklist

- [ ] Transformation order is documented and tested.
- [ ] Dictionary and input use compatible policies.
- [ ] Every transformed span maps to an original source interval.
- [ ] `Match.text` is an original slice.
- [ ] Boundary behavior is explicit for non-ASCII scripts.
- [ ] Results do not depend on insertion order.
- [ ] The standard-library-only runtime constraint is preserved.
