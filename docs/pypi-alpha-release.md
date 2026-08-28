# PyPI Alpha Release Preparation - Historical v0.3.0a1

This page records ABMForge's first production PyPI alpha release. Version `0.3.0a1` has already been published and must not be reused.

The first public release was:

```text
v0.3.0a1
```

The released package version was:

```text
0.3.0a1
```

The published release can be installed with:

```bash
python -m pip install abmforge
```

This page is a historical release record. Commands that create or push `v0.3.0a1` must not be rerun.

## Release Policy

The first production PyPI release was intentionally an alpha release.

Alpha release expectations:

- APIs are still provisional unless explicitly documented as stable.
- Archive and dataset contracts may still evolve.
- Users should pin versions for research artifacts.
- The project is suitable for early research use, testing, teaching, and
  feedback.
- The project is not yet a stable 1.0 production framework.

Historical public version:

```text
0.3.0a1
```

Historical tag:

```text
v0.3.0a1
```

## Trusted Publishing

ABMForge should publish to PyPI through Trusted Publishing from GitHub Actions.

Do not store long-lived PyPI tokens unless Trusted Publishing is unavailable.

Production PyPI trusted publisher settings should be separate from TestPyPI.

Recommended production PyPI trusted publisher fields:

```text
Repository owner: fatihuludag-lab
Repository name: abmforge
Workflow filename: release.yml
Environment name: pypi
```

The GitHub environment should be named:

```text
pypi
```

Recommended environment protections:

- require manual approval;
- restrict who can approve deployments;
- do not allow unreviewed production publishing;
- keep production PyPI separate from TestPyPI.

## Production Publish Gate

Production PyPI publishing must require all of the following:

- manual workflow dispatch;
- `publish_pypi=true`;
- workflow selected on a `v*` tag ref;
- `pypi` environment approval;
- trusted publisher configured on PyPI;
- build job completed;
- artifact inspection completed;
- TestPyPI dry run completed;
- release metadata strict check passed;
- maintainer approval.

The release workflow should build on tag pushes but should not publish to PyPI
automatically on tag push.

## Credential-Free Readiness Path

If TestPyPI or production PyPI access is unavailable, do not run the publishing
steps on this page. Use the no-publish release-readiness path instead:

```text
docs/release-readiness-no-publish.md
```

That path validates metadata, tests, documentation, build artifacts, and
`twine check` without uploading distributions.

## Historical v0.3.0a1 Release Sequence

Historical sequence for `v0.3.0a1`:

1. merge release preparation PR;
2. confirm `main` is green;
3. confirm strict metadata check passes;
4. created and pushed tag `v0.3.0a1`;
5. let the release workflow build artifacts from the tag;
6. inspect artifacts;
7. run TestPyPI dry run;
8. run TestPyPI install smoke;
9. manually ran the release workflow on tag `v0.3.0a1` with `publish_pypi=true`;
10. approve the `pypi` environment;
11. run production PyPI install smoke;
12. create GitHub Release notes.

## Historical Local Checks Before Tagging

Run:

```bash
python scripts/check_release_metadata.py --strict
python -m ruff format --check src tests examples scripts benchmarks
python -m ruff check src tests examples scripts benchmarks
python -m mkdocs build --strict
python -m pytest -q
python -m mypy src
python -m build
python -m twine check dist/*
```

## Historical Alpha Tag Command

For the historical `v0.3.0a1` release, the tag commands were:

> **Historical record:** Do not run these commands again for `v0.3.0a1`.

```text
git switch main
git pull --ff-only origin main
git status --short
git tag v0.3.0a1
git push origin v0.3.0a1
```

The tag was created only after the release metadata and changelog were verified. The existing `v0.3.0a1` tag must never be recreated, moved, or force-updated.

## Production Install Verification

After publishing:

```bash
python -m venv /tmp/abmforge-pypi-smoke
/tmp/abmforge-pypi-smoke/bin/python -m pip install --upgrade pip
/tmp/abmforge-pypi-smoke/bin/python -m pip install abmforge
/tmp/abmforge-pypi-smoke/bin/python -m abmforge.cli.main --version
```

Then verify CLI behavior:

```bash
abmforge --version
abmforge info
abmforge cite
abmforge templates --json
abmforge new abmforge-smoke-study --template research
cd abmforge-smoke-study
abmforge run configs/baseline.yaml --archive outputs/archive --overwrite
abmforge validate outputs/archive
abmforge summarize outputs/archive --json
```

## Manual PyPI Install Smoke Workflow

ABMForge provides a manual workflow:

```text
.github/workflows/pypi-install-smoke.yml
```

It installs ABMForge from production PyPI and runs the installed-package smoke
script.

It is intentionally manual and does not publish anything.

## Failure Handling

If production publishing fails:

- confirm the PyPI project trusted publisher is configured;
- confirm the workflow filename is `release.yml`;
- confirm the environment name is `pypi`;
- confirm the workflow was run on a `v*` tag ref;
- confirm the version has not already been uploaded;
- inspect the release workflow logs.

If install smoke fails:

- inspect package metadata;
- inspect package data inclusion;
- verify CLI entry points;
- verify template files;
- compare with TestPyPI install smoke.

## Rollback and Yanking

PyPI releases cannot be overwritten.

If a broken release is published:

- do not try to upload a file with the same version;
- publish a new fixed version;
- consider yanking the broken release if appropriate;
- document the issue in release notes.

## Non-Goals

This preparation does not:

- publish to PyPI automatically;
- create a GitHub Release automatically;
- create a Zenodo DOI;
- submit a JOSS or SoftwareX paper;
- make ABMForge stable 1.0 software.

Those are separate release and publication steps.
