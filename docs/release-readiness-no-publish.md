# Release Readiness Without Publishing

This page defines the credential-free release-readiness path for ABMForge.

Use this path when TestPyPI or production PyPI access is not available, or when
a maintainer wants to verify release quality before any upload.

## Scope

This process verifies release readiness without publishing to TestPyPI or PyPI.
It requires no package-index credentials, no PyPI token, and no trusted-publisher
approval.

## Local checks

Run from the repository root:

```bash
python scripts/check_version_consistency.py
python scripts/check_release_metadata.py --strict
python -m ruff check src tests examples scripts benchmarks
python -m mypy src
python -m pytest -q
python -m mkdocs build --strict
python -m build
python -m twine check dist/*
```

## Deferred publishing steps

The following actions are intentionally deferred until TestPyPI/PyPI access is
available:

- `twine upload`;
- manual release workflow dispatch with `publish_testpypi=true`;
- TestPyPI environment approval;
- TestPyPI install smoke;
- manual release workflow dispatch with `publish_pypi=true`;
- production PyPI environment approval;
- production PyPI install smoke;
- GitHub release publication;
- DOI or archived-release publication.

## Release workflow safety

The release workflow may build distributions without publishing. Publishing jobs
must remain behind explicit manual inputs and environment approvals:

- TestPyPI publishing requires `publish_testpypi=true`;
- production PyPI publishing requires `publish_pypi=true`;
- production PyPI publishing requires a `refs/tags/v*` ref;
- package uploads should use PyPI Trusted Publishing rather than long-lived
  tokens when package-index access is available.

## Acceptance criteria

A no-publish release-readiness check is successful when version consistency,
strict release metadata, tests, documentation build, `python -m build`, and
`python -m twine check dist/*` all pass, and no upload command has been run.

This process supports release preparation only. It does not imply that ABMForge
has been published to PyPI or that an external user can install it from PyPI.
