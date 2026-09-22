# Getting started

Install LexNeedle into a Python 3.12+ project:

```shell
uv add lexneedle
```

Create a matcher, register a term, and search text. A `Match` carries both the
registered `keyword` and the exact source `text` it matched.

```{doctest}
>>> matcher = Matcher()
>>> matcher.add("Panadol", value="paracetamol")
>>> match = matcher.find("Panadol 500mg tablets")[0]
>>> (match.text, match.value, match.start, match.end)
('Panadol', 'paracetamol', 0, 7)
>>> "Panadol 500mg tablets"[match.start : match.end] == match.text
True
```

`Matcher` uses Unicode case folding by default. Use `case_sensitive=True` if
the dictionary must distinguish spelling case. The default word boundary avoids
matching a registered word inside another word; see {doc}`how-to/matching-policies`
for substring matching and overlap choices.

Register aliases together when they share one canonical value and metadata:

```{doctest}
>>> matcher = Matcher()
>>> matcher.add(["Panadol", "Panadol Osteo"], value="paracetamol")
>>> [match.value for match in matcher.find("Panadol Osteo")]
['paracetamol']
```
