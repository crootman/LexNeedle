# API reference

The public surface is deliberately small. The API pages use autodoc for
signatures and docstrings, while the guides explain the cross-cutting matching
contracts.

## Matcher and related types

```{eval-rst}
.. automodule:: lexneedle
   :members: Matcher, Match, ConfigurationError, SerializationError
   :undoc-members:
```

## Type aliases

```{eval-rst}
.. autodata:: lexneedle.Boundary
.. autodata:: lexneedle.SideBoundary
.. autodata:: lexneedle.Strategy
.. autodata:: lexneedle.Replacement
.. autodata:: lexneedle.Normalization
```

## FlashText compatibility facade

```{eval-rst}
.. autoclass:: lexneedle.compat.flashtext.KeywordProcessor
   :members:
```

For behavior that is more than a signature, start with {doc}`../getting-started`
and the relevant how-to guide.
