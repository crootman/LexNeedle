# Releasing LexNeedle

This is the maintainer checklist for preparing and publishing a LexNeedle
release. The release workflow in `.github/workflows/release.yml` is the source
of truth for automation.

## Safety rules

- Release from a reviewed commit on `main` with a passing CI run.
- Keep the project version, changelog entry, annotated Git tag, and published
  version identical.
- Treat published files and release tags as immutable. Never overwrite a PyPI
  file or move a tag that identifies a published release.
- Publish only through GitHub Actions and PyPI Trusted Publishing. Do not store
  or use a long-lived PyPI token.
- Require explicit maintainer confirmation before creating or pushing a release
  tag or creating a GitHub Release.
- Do not put credentials, private account details, or copied CI secrets in
  commits, issues, release notes, or agent prompts.

## 1. Prepare the release

1. Choose the release version and review the complete diff since the previous
   tag.
2. Update `project.version` in `pyproject.toml`.
3. Move the relevant `Unreleased` notes in `CHANGELOG.md` into a dated release
   section. Describe user-visible changes under headings such as `Added`,
   `Changed`, `Fixed`, `Removed`, or `Security`; leave an empty `Unreleased`
   section for future work and update its comparison link.
4. Update the README, public docstrings, examples, and architecture notes for
   any changed behavior, errors, compatibility, or limitations.
5. Confirm that no generated files, local configuration, credentials, or
   unrelated changes are included.
6. Verify every documentation URL advertised by the README and package metadata
   resolves to the intended content. For separately hosted documentation,
   confirm the release's `stable` and development `latest` builds before
   publishing. Do not publish a release whose documentation links are dead.

Run the locked quality gate:

```shell
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest --cov=lexneedle --cov-report=term-missing --cov-fail-under=90
uv run sphinx-build -W --keep-going -b html docs docs/_build/html
uv run sphinx-build -W --keep-going -b doctest docs docs/_build/doctest
uv build --clear
```

Validate the distributions and install each one in isolation:

```shell
uvx --from twine twine check dist/*
uv run --isolated --no-project --python 3.12 \
  --with dist/lexneedle-X.Y.Z-py3-none-any.whl tests/smoke_test.py
uv run --isolated --no-project --python 3.12 \
  --with dist/lexneedle-X.Y.Z.tar.gz tests/smoke_test.py
```

Replace `X.Y.Z` with the version being prepared. `uv build --clear` prevents
artifacts from an older release remaining in `dist/` and being inspected by
mistake.

Inspect both archives. At minimum, confirm their names and versions, metadata,
README rendering, license files, package modules, and `lexneedle/py.typed`.
Before continuing, `git status --short` should show only the intended release
changes.

## 2. Review and merge

Commit the version, changelog, and associated documentation together. Push the
commit and wait for all required GitHub CI jobs to pass. Recheck advertised
documentation URLs from the pushed commit. Confirm that `main` points to the
exact commit intended for release and that the release tag does not already
exist.

The PyPI Trusted Publisher must remain constrained to these public identifiers:

- Owner: `crootman`
- Repository: `LexNeedle`
- Workflow: `release.yml`
- GitHub environment: `pypi`

The GitHub `pypi` environment should restrict deployment to release tags and,
where practical, require maintainer approval.

## 3. Publish

After explicit confirmation, create and push an annotated tag matching the
project version:

```shell
git tag -a vX.Y.Z -m "LexNeedle X.Y.Z"
git push origin vX.Y.Z
```

The tag starts the `Release` GitHub Actions workflow. It verifies the tag and
version, reruns the quality gate, builds and inspects fresh distributions,
smoke-tests both artifacts, and publishes them to PyPI. Approve the `pypi`
environment deployment if its protection rules require approval.

Do not perform a second upload from a workstation. If the workflow fails,
inspect the failed step and rerun it only when no source change is required. If
published artifacts are wrong, do not replace them; prepare a new corrective
version.

## 4. Verify and announce

1. Confirm that the workflow completed successfully and that PyPI lists the
   expected version, wheel, source distribution, metadata, and provenance.
2. Install the published version from PyPI in an isolated environment and run
   a minimal public-API check.
3. In GitHub, open **Releases**, choose **Draft a new release**, select the
   existing tag, and use `LexNeedle X.Y.Z` as the title. Use the matching
   changelog section as concise release notes, link to the PyPI project, and
   publish the GitHub Release.
4. Confirm that the GitHub Release, PyPI project, changelog, and documentation
   all show the same version.
5. Leave the Trusted Publisher constrained to the `pypi` environment.

For example, replace `X.Y.Z` and run this published-package check:

```shell
uv run --isolated --no-project --with "lexneedle==X.Y.Z" python - <<'PY'
from lexneedle import Matcher

matcher = Matcher()
matcher.add("needle")
assert matcher.find("needle")[0].text == "needle"
PY
```

## Read-only agent preflight

The following prompt can be given to a coding agent before each release:

> Perform a read-only release-readiness review for LexNeedle version X.Y.Z.
> Read `AGENTS.md`, `docs/releasing.md`, the public documentation, tests, and
> release workflow. Do not change files, create or push a tag, create a GitHub
> Release, or publish anything. Verify the working tree and release commit,
> version and changelog agreement, locked quality gate, coverage threshold,
> distribution contents, metadata rendering, isolated smoke tests, and release
> workflow security. Report findings as Critical, Required, or Optional, list
> every command actually run, and identify any external settings that cannot be
> verified from the repository.

After the preflight is clean, ask the agent separately to prepare any approved
version and documentation changes. Tagging and publication still require a
final explicit confirmation.
