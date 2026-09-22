# Redact known identifiers

Use LexNeedle to locate and redact identifiers already present in a curated
dictionary: known customer names, email addresses, account identifiers, or
internal project names. It is an exact matcher, not a detector for unknown
email addresses, phone numbers, or other patterns. Use regular expressions or
a dedicated PII system when the value is not known in advance.

Unicode case folding makes `Straße` and `STRASSE` equivalent for the default
case-insensitive policy. The source span still points to the original text.

```{doctest}
>>> matcher = Matcher(boundary="none")
>>> matcher.add("Straße", value="[customer]")
>>> text = "Send STRASSE to the review queue"
>>> matcher.replace(text)
'Send [customer] to the review queue'
>>> match = matcher.find(text)[0]
>>> text[match.start : match.end]
'STRASSE'
```

For auditable logs, retain the returned matches with the redacted text:

```{doctest}
>>> redacted, matches = matcher.replace_with_matches(text)
>>> (redacted, [(m.start, m.end, m.text) for m in matches])
('Send [customer] to the review queue', [(5, 12, 'STRASSE')])
```

See {doc}`../explanation/unicode-and-offsets` for normalization and the limits of
case folding.
