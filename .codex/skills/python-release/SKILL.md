---
name: python-release
description: Prepare, validate, or publish a LexNeedle PyPI release with uv, uv_build, GitHub Actions, and PyPI Trusted Publishing. Use when changing release metadata, CI publishing, versions, artifacts, tags, or release notes.
---

# LexNeedle Release Engineering

Release immutable, inspectable artifacts built from the reviewed source tree.
Use `uv_build`, static PEP 621 project metadata, and `uv build`; do not add a
second build backend, versioning framework, or upload tool without approval.

## Before a release

1. Update the project version and release notes according to the agreed
   versioning policy.
2. Run Ruff, `ty`, the full pytest suite, and `uv build`.
3. Inspect both `dist/*.whl` and `dist/*.tar.gz`; verify metadata, README
   rendering, source files, and `py.typed`.
4. Install the wheel into a clean environment and run a minimal import and
   public-API smoke test.

## Publishing and CI

Use tag-triggered GitHub Actions with least-privilege permissions and PyPI
Trusted Publishing (OIDC). The publish job needs `id-token: write`; ordinary
CI needs only the permissions it uses. Pin actions to reviewed full commit SHAs
and keep `uv sync --locked --all-groups` in CI.

Never publish from an unreviewed workstation command or store a long-lived PyPI
token when Trusted Publishing is available. A release tag, project version, and
published artifact version must agree.
