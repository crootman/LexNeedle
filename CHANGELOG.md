# Changelog

This file records notable user-facing changes to LexNeedle.

## [0.1.0] - 2026-09-22

### Added

- Deterministic dictionary matching with original-string offsets and explicit
  overlap strategies.
- Unicode case folding, NFC, NFD, NFKC, and NFKD normalization with aligned
  source spans.
- Unicode-aware word boundaries, custom boundary policies, and optional
  whitespace-equivalent matching.
- Alias registration, replacement helpers, deterministic iteration, and batch
  matching.
- Validated, versioned JSON persistence with atomic replacement and trusted
  local pickle support.
- A compatibility facade for common FlashText extraction, replacement, lookup,
  and mutation workflows.
- Complete type information, including the `py.typed` marker, with no runtime
  dependencies.

[0.1.0]: https://github.com/crootman/LexNeedle/releases/tag/v0.1.0
