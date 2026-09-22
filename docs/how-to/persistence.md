# Save and load matcher definitions

`Matcher.save()` writes a validated, versioned JSON definition and
`Matcher.load()` validates it before constructing a matcher. JSON is the safe
format for untrusted matcher definitions; standard-library pickle is supported
only for trusted local process transfer.

```{doctest}
>>> from pathlib import Path
>>> path = Path("terms.json")
>>> matcher = Matcher()
>>> matcher.add("Panadol", "paracetamol")
>>> matcher.save(path)
>>> Matcher.load(path).find("panadol")[0].value
'paracetamol'
>>> path.unlink()
```

Saving encodes and writes a temporary file beside the resolved destination,
then atomically replaces the destination. Invalid values and ordinary writing
failures therefore do not truncate an existing file. A new file is created
with POSIX mode `0o600`, subject to the process umask. Saving an existing file
preserves its POSIX mode bits, including when saving through a symlink to an
existing target. It does not promise ownership or ACL preservation, power-loss
durability, or protection from a symlink retargeted during the operation. A
crash before replacement can leave a `.lexneedle-*.tmp` file beside the target.

See {doc}`../reference/json-format` for the versioned schema and validation
rules.
