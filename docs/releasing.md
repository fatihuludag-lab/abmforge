# Releasing ABMForge

ABMForge release automation is intentionally conservative. Distribution
artifacts are built, validated, smoke-tested, checksummed, and stored before
either package index can receive them.

The release workflow supports:

- manual release validation and artifact generation;
- builds triggered by valid version tags;
- full quality gates before package construction;
- wheel and source distribution validation;
- clean-environment installed-wheel smoke testing;
- SHA-256 checksum generation;
- optional TestPyPI publishing through a protected environment;
- optional production PyPI publishing from a valid version tag;
- OpenID Connect trusted publishing without long-lived package-index tokens.

A tag push does not automatically publish to TestPyPI or production PyPI.
Publishing remains an explicit manual action.

## Release workflow

The workflow file is:

```text
.github/workflows/release.yml
```

It can be triggered:

1. manually through `workflow_dispatch`;
2. by pushing a tag matching `v*`.

The workflow serializes runs for the same Git ref and does not cancel an
in-progress release operation.

## Quality gates

Before building distributions, the workflow runs:

```bash
python scripts/check_version_consistency.py
python scripts/check_release_metadata.py --strict
python scripts/check_release_tag.py --tag "$GITHUB_REF_NAME"
ruff format --check src tests examples scripts
ruff check src tests examples scripts
mypy src
pytest --cov=abmforge --cov-report=term-missing --cov-fail-under=70
mkdocs build --strict
```

The release-tag check runs for tag references. A valid version tag must match
the package version declared by both `pyproject.toml` and the runtime version
module.

Examples of valid version tags include:

```text
v0.3.0a1
v0.3.0rc1
v0.3.0
```

A broad tag such as `vnext`, or a tag whose version differs from the package
metadata, fails before package construction.

## Build and artifact validation

After the quality gates pass, the build job:

```bash
python -m build
python -m twine check dist/*
```

The generated wheel is installed into a clean virtual environment and tested
with `scripts/smoke_installed_package.py`.

The workflow then generates:

```text
SHA256SUMS
```

The validated distributions and `SHA256SUMS` are uploaded as separate GitHub
Actions artifacts. Publishing jobs download these exact artifacts and verify
their checksums before uploading packages. Packages are therefore not rebuilt
inside a publishing job.

## Publication target selection

Manual runs provide two independent inputs:

- `publish_testpypi`;
- `publish_pypi`.

Only one publication target may be selected for a workflow run. Selecting both
causes validation to fail.

A run with both inputs set to `false` performs a complete no-publish release
validation and artifact build.

## TestPyPI publishing

TestPyPI publishing runs only when:

- the workflow is manually triggered;
- `publish_testpypi` is `true`;
- `publish_pypi` is `false`;
- the `testpypi` GitHub environment allows deployment;
- a TestPyPI trusted publisher is configured for the repository.

The `testpypi` environment should require manual approval and restrict who may
approve deployments.

## Production PyPI publishing

Production publishing runs only when:

- the workflow is manually dispatched from a valid version tag;
- `publish_pypi` is `true`;
- `publish_testpypi` is `false`;
- the tag matches the package version;
- all quality, build, smoke, metadata, and checksum gates pass;
- the protected `pypi` environment allows deployment;
- a PyPI trusted publisher is configured for the repository.

The production workflow uses OpenID Connect through
`pypa/gh-action-pypi-publish`. Long-lived PyPI tokens should not be stored in
the repository.

## Recommended protected environments

Configure two GitHub environments:

```text
testpypi
pypi
```

Recommended settings include:

- required manual approval;
- restricted deployment approvers;
- production deployment limited to version tags;
- no long-lived package-index passwords when trusted publishing is available.

## Before creating a release

Run locally:

```bash
python scripts/check_version_consistency.py
python scripts/check_release_metadata.py --strict
python -m ruff format --check src tests examples scripts
python -m ruff check src tests examples scripts
python -m mypy src
python -m pytest -q
python -m mkdocs build --strict
python -m build
python -m twine check dist/*
```

For a planned tag, also run:

```bash
python scripts/check_release_tag.py --tag v0.3.0a1
```

Replace the example tag with the intended release version.

## First Safe Release Path

Use this sequence for the first production release:

1. merge all release-readiness changes;
2. update package, citation, codemeta, and changelog versions;
3. run all local release checks;
4. create and push a valid release-candidate tag;
5. allow the tag-triggered workflow to build and validate artifacts;
6. inspect the distributions and `SHA256SUMS`;
7. manually run the workflow from the same tag with
   `publish_testpypi=true`;
8. approve the protected TestPyPI deployment;
9. install the exact version from TestPyPI in a clean environment;
10. run the installed-package smoke test;
11. manually run the workflow from the same tag with `publish_pypi=true`;
12. approve the protected production PyPI deployment;
13. run the production PyPI install-smoke workflow for the released version.

## Non-goals

The release workflow does not currently:

- create GitHub Releases automatically;
- generate signed provenance attestations;
- update Zenodo metadata;
- bump package versions automatically;
- generate release notes automatically.

Those capabilities should be added through separate reviewed changes.
