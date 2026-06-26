# Releasing ABMForge

ABMForge release automation is intentionally conservative.

The current release workflow supports:

- manual release preparation;
- tag-triggered distribution builds;
- wheel and sdist validation;
- artifact upload from GitHub Actions;
- optional TestPyPI publishing through a protected environment.

It does not automatically publish to production PyPI.

## Release Workflow

The workflow file is:

```text
.github/workflows/release.yml
```

It can be triggered in two ways:

1. manually through `workflow_dispatch`;
2. by pushing a version tag matching `v*`.

The build job always:

```bash
python -m build
python -m twine check dist/*
```

and uploads the generated distributions as workflow artifacts.

## TestPyPI Publishing

TestPyPI publishing is manual and opt-in.

It only runs when:

- the workflow is manually triggered;
- `publish_testpypi` is set to `true`;
- the GitHub environment named `testpypi` allows the deployment;
- a TestPyPI trusted publisher has been configured for the repository.

No long-lived PyPI token should be committed to the repository.

## Recommended TestPyPI Environment

Create a GitHub environment named:

```text
testpypi
```

Recommended settings:

- require manual approval;
- restrict who can approve deployments;
- do not store long-lived PyPI passwords unless trusted publishing is unavailable.

## Before Creating a Release

Run locally:

```bash
python -m ruff format --check src tests examples scripts
python -m ruff check src tests examples scripts
python -m mkdocs build --strict
python -m pytest -q
python -m mypy src
python -m build
```

Then inspect:

```bash
python -m twine check dist/*
```

## First Safe Release Path

Suggested sequence:

1. merge all release-readiness PRs;
2. update version metadata;
3. update changelog;
4. create a release candidate tag;
5. run the Release workflow without TestPyPI publishing;
6. inspect workflow artifacts;
7. run the workflow manually with `publish_testpypi=true`;
8. install from TestPyPI in a clean environment;
9. only then consider production PyPI publishing in a later PR.

## Non-Goals

The current workflow does not yet:

- publish to production PyPI;
- create GitHub Releases automatically;
- sign artifacts;
- generate provenance attestations;
- update Zenodo metadata;
- bump versions automatically.

Those should be added in later, separate PRs.
