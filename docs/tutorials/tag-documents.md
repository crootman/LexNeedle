# Tag documents from a term list

Attach structured values to dictionary entries so content classification remains
data-driven. The matching code stays unchanged when a domain expert updates the
versioned JSON matcher definition.

```{doctest}
>>> matcher = Matcher()
>>> matcher.add("card", {"category": "payment", "priority": 2})
>>> matcher.add("invoice", {"category": "billing", "priority": 1})
>>> [(match.text, match.value["category"]) for match in matcher.find("Card invoice")]
[('Card', 'payment'), ('invoice', 'billing')]
```

Persist a reviewed dictionary with `matcher.save("terms.json")`; the format and
its security properties are documented in {doc}`../how-to/persistence`.
