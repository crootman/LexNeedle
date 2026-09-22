# Replace matches

`replace()` uses the matcher's default strategy unless an explicit strategy is
given. Replacement needs a non-overlapping strategy, so `all` and `longest`
are rejected. A string value is used directly; for structured values, provide a
callable that returns a string.

```{doctest}
>>> matcher = Matcher()
>>> matcher.add("ID-7", {"replacement": "[account]"})
>>> matcher.replace("ID-7", lambda match: match.value["replacement"])
'[account]'
```

Use `replace_with_matches()` when a pipeline needs both the replacement text
and the exact matches selected for replacement:

```{doctest}
>>> matcher = Matcher()
>>> matcher.add("Panadol", "paracetamol")
>>> matcher.replace_with_matches("Panadol")
('paracetamol', [Match(keyword='Panadol', text='Panadol', value='paracetamol', start=0, end=7, metadata=None)])
```
