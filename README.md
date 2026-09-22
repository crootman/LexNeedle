# LexNeedle

LexNeedle is a deterministic, Unicode-aware dictionary matcher for Python
3.12+, with zero runtime dependencies. Use it when exact terms, trustworthy
original-text offsets, and predictable overlap handling matter.

## Install

```shell
uv add lexneedle
```

For the unreleased `main` branch:

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

This prints `Panadol paracetamol 0 7`. The reported offsets always index the
original Python string:

```python
text = "Panadol 500mg tablets"
[match] = matcher.find(text)
assert text[match.start : match.end] == match.text
```

## Guarantees

- Case-insensitive matching uses locale-independent Unicode `casefold()`;
  optional NFC, NFD, NFKC, and NFKD normalization preserves source offsets.
- Results are deterministic for the same configuration, terms, input, and
  Python Unicode data. They do not depend on term insertion order.
- Explicit boundary and overlap policies make substring and collision behavior
  visible rather than accidental.
- JSON save/load is validated and versioned. New POSIX files are created with
  mode `0o600`, subject to the process umask.

## Documentation

The documentation sources cover [getting started], [redacting known
identifiers], [tagging documents], [Unicode and offsets], [boundaries and
overlap strategies], [replacement], [JSON persistence], [FlashText migration],
[API reference], and [performance limits].

[getting started]: https://github.com/crootman/LexNeedle/blob/main/docs/getting-started.md
[redacting known identifiers]: https://github.com/crootman/LexNeedle/blob/main/docs/tutorials/redact-known-values.md
[tagging documents]: https://github.com/crootman/LexNeedle/blob/main/docs/tutorials/tag-documents.md
[Unicode and offsets]: https://github.com/crootman/LexNeedle/blob/main/docs/explanation/unicode-and-offsets.md
[boundaries and overlap strategies]: https://github.com/crootman/LexNeedle/blob/main/docs/how-to/matching-policies.md
[replacement]: https://github.com/crootman/LexNeedle/blob/main/docs/how-to/replacement.md
[JSON persistence]: https://github.com/crootman/LexNeedle/blob/main/docs/how-to/persistence.md
[FlashText migration]: https://github.com/crootman/LexNeedle/blob/main/docs/how-to/flashtext-migration.md
[API reference]: https://github.com/crootman/LexNeedle/blob/main/docs/reference/api.md
[performance limits]: https://github.com/crootman/LexNeedle/blob/main/docs/explanation/performance-and-limits.md

## Development

Run the library quality gate with `uv sync --all-groups`, then:

```shell
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest
uv run sphinx-build -W --keep-going -b html docs docs/_build/html
uv build
```

See the [contribution guide] for development guidance and the [release
checklist] for the maintainer workflow.

[contribution guide]: https://github.com/crootman/LexNeedle/blob/main/CONTRIBUTING.md
[release checklist]: https://github.com/crootman/LexNeedle/blob/main/docs/releasing.md
