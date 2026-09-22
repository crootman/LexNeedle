# Determinism

For the same matcher configuration, registered terms, input string, and Python
Unicode data, LexNeedle produces deterministic matches. Results do not depend
on term insertion order: transformed key collisions are rejected rather than
silently selecting the first registration.

`items()` and iteration are sorted by the registered keyword. Match results are
in source order; `all` puts longer candidates before shorter ones at the same
source offset. The selected behavior for the other overlap strategies is
documented in {doc}`../how-to/matching-policies`.

Python releases can bundle different Unicode database versions. A newly added
Unicode character or property can therefore behave differently across supported
Python versions. Pin a Python version or test the locales and scripts relevant
to a compliance requirement when cross-version stability matters.
