# JSON matcher definition format

`Matcher.save()` currently writes format version 2. `Matcher.load()` also
accepts an unpublished version 1 compatibility schema. No published LexNeedle
release wrote version 1; the reader treats its missing `whitespace_equivalent`
setting as `false`.

```json
{
  "format_version": 2,
  "configuration": {
    "case_sensitive": false,
    "unicode_normalization": null,
    "boundary": "word",
    "strategy": "leftmost_longest",
    "whitespace_equivalent": false
  },
  "terms": [
    {
      "keyword": "Panadol",
      "value": "paracetamol",
      "metadata": {"type": "brand"}
    }
  ]
}
```

The top-level object and each nested configuration or term object must have
exactly the shown keys. `keyword` must be a non-empty string; `metadata` is
either `null` or a JSON object with string keys. Values and metadata must be
representable losslessly by JSON: `null`, booleans, finite numbers, strings,
lists, and objects with string keys. Duplicate JSON keys, non-finite numbers,
cycles, malformed UTF-8, and configuration or term collisions are rejected with
`SerializationError`.

Only the built-in `word` and `none` boundaries are serializable. Matchers with
custom boundary policies cannot be saved, because executing behavior must not
be embedded in a JSON definition.
