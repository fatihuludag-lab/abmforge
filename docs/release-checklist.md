# Release Checklist

ABMForge releases should be prepared conservatively.

This checklist is intended for release candidates, TestPyPI publishing, and
controlled production PyPI releases.

## Release Goals

A release should provide:

- a consistent version across project metadata;
- a clean changelog entry;
- buildable wheel and source distributions;
- validated distribution metadata;
- installed-wheel smoke tests;
- a reproducible release workflow log;
- clear citation metadata;
- clear release notes.

## Version Metadata

Before tagging a release, check version consistency across:

- `pyproject.toml`;
- `src/abmforge/__init__.py`;
- `CITATION.cff`, when it declares a version;
- `codemeta.json`, when it declares a software version;
- `CHANGELOG.md`.

Use:

```bash
python scripts/check_release_metadata.py
```

The script is intentionally conservative. It fails on conflicting version values
among fields that are present, while allowing optional metadata fields to be
filled closer to a formal release.

## Local Release Readiness Checks

Run:

```bash
python -m ruff format --check src tests examples scripts
python -m ruff check src tests examples scripts
python -m mkdocs build --strict
python -m pytest -q
python -m mypy src
python -m build
python -m twine check dist/*
python scripts/check_release_metadata.py --strict
python scripts/check_release_tag.py --tag v0.3.0a1
```

Replace the example tag with the intended release version. The tag must match
the versions declared in `pyproject.toml` and the runtime version module.

## Release Tag Validation

Release tags must use a supported version form and match the package metadata.

Run:

```bash
python scripts/check_release_tag.py --tag v0.3.0a1
```

The release workflow rejects:

- malformed tags such as `vnext`;
- tags that do not begin with `v`;
- tags whose version differs from the package version;
- production publishing dispatched from a non-tag reference.

## Built-Wheel Smoke Test

The release candidate should be installable from the built wheel in a clean
environment.

On Windows PowerShell:

```powershell
$SmokeVenv = "$env:TEMP\abmforge-wheel-smoke"
Remove-Item $SmokeVenv -Recurse -Force -ErrorAction SilentlyContinue
python -m venv $SmokeVenv

$Wheel = Get-ChildItem dist\*.whl | Select-Object -First 1
& "$SmokeVenv\Scripts\python.exe" -m pip install --upgrade pip
& "$SmokeVenv\Scripts\python.exe" -m pip install $Wheel.FullName

Push-Location $env:TEMP
& "$SmokeVenv\Scripts\python.exe" "$PWD\scripts\smoke_installed_package.py"
Pop-Location
```

On Linux/macOS:

```bash
python -m venv /tmp/abmforge-wheel-smoke
/tmp/abmforge-wheel-smoke/bin/python -m pip install --upgrade pip
/tmp/abmforge-wheel-smoke/bin/python -m pip install dist/*.whl
cd /tmp
/tmp/abmforge-wheel-smoke/bin/python /path/to/abmforge/scripts/smoke_installed_package.py
```

## Distribution Checksums

After building and validating the distributions, generate:

```bash
sha256sum dist/* > SHA256SUMS
```

The release workflow uploads `SHA256SUMS` separately from the wheel and source
distribution. TestPyPI and production PyPI jobs download the validated
artifacts and verify their checksums before publishing.

Packages are not rebuilt inside publication jobs.

## No-Publish Release Readiness

When TestPyPI or production PyPI access is unavailable, maintainers should run
the no-publish release-readiness path instead of attempting package uploads.

See:

```text
docs/release-readiness-no-publish.md
```

This path verifies version metadata, strict release metadata, tests,
documentation, package build artifacts, and `twine check` without running
`twine upload`, `publish_testpypi=true`, or `publish_pypi=true`.

## TestPyPI Dry Run

The safe release path is:

1. run the Release workflow without publishing;
2. inspect uploaded distribution artifacts;
3. manually run the Release workflow from the same valid version tag with `publish_testpypi=true`;
4. approve the `testpypi` environment deployment;
5. install from TestPyPI in a clean environment;
6. run an installed-package smoke test.

## Controlled Production PyPI Publishing

Production PyPI publishing is manual and requires:

- dispatching the Release workflow from a valid version tag;
- setting `publish_pypi=true`;
- keeping `publish_testpypi=false`;
- successful quality, metadata, package, smoke, and checksum checks;
- approval through the protected `pypi` environment;
- PyPI trusted publishing through OpenID Connect.

Only one publication target may be selected in a workflow run. Selecting both
`publish_testpypi` and `publish_pypi` causes the validation job to fail.

## Tagging Policy

Use release candidate tags before production releases.

Examples:

```text
v0.3.0a1
v0.3.0rc1
v0.3.0
```

Do not create a production tag until:

- the changelog entry is complete;
- CI is green;
- package smoke is green;
- release workflow artifact build is green;
- TestPyPI install has been tested.

## Changelog Policy

Each release entry should include:

- release date;
- highlights;
- breaking changes;
- new features;
- bug fixes;
- documentation changes;
- test and CI changes;
- known limitations.

## Citation Metadata

Before a formal release, update citation metadata so that users can cite the
software accurately.

Check:

- author names;
- title;
- version;
- release date;
- repository URL;
- DOI when available;
- preferred citation.

## Non-Goals

This checklist does not replace:

- GitHub Release notes;
- Zenodo archive metadata;
- production PyPI publishing;
- publication paper preparation;
- long-term support policy.

Those should be handled by separate release and publication tasks.
