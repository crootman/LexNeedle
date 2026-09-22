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

The full documentation covers [getting started], [redacting known identifiers],
[tagging documents], [Unicode and offsets], [boundaries and overlap strategies],
[replacement], [JSON persistence], [FlashText migration], [API reference], and
[performance limits].

[getting started]: https://lexneedle.readthedocs.io/en/stable/getting-started.html
[redacting known identifiers]: https://lexneedle.readthedocs.io/en/stable/tutorials/redact-known-values.html
[tagging documents]: https://lexneedle.readthedocs.io/en/stable/tutorials/tag-documents.html
[Unicode and offsets]: https://lexneedle.readthedocs.io/en/stable/explanation/unicode-and-offsets.html
[boundaries and overlap strategies]: https://lexneedle.readthedocs.io/en/stable/how-to/matching-policies.html
[replacement]: https://lexneedle.readthedocs.io/en/stable/how-to/replacement.html
[JSON persistence]: https://lexneedle.readthedocs.io/en/stable/how-to/persistence.html
[FlashText migration]: https://lexneedle.readthedocs.io/en/stable/how-to/flashtext-migration.html
[API reference]: https://lexneedle.readthedocs.io/en/stable/reference/api.html
[performance limits]: https://lexneedle.readthedocs.io/en/stable/explanation/performance-and-limits.html

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

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance and
[docs/releasing.md](docs/releasing.md) for the release checklist.
