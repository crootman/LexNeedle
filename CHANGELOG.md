# Changelog

This file records notable user-facing changes to LexNeedle.

## [Unreleased]

## [0.1.1] - 2026-09-22

### Changed

- Lowered the supported Python version to Python 3.12 and expanded CI coverage
  across Python 3.12, 3.13, and 3.14.

### Added

- Versioned Sphinx documentation with executable examples, practical tutorials,
  API reference, Unicode matching guidance, persistence details, and limits.

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

[Unreleased]: https://github.com/crootman/LexNeedle/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/crootman/LexNeedle/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/crootman/LexNeedle/releases/tag/v0.1.0
