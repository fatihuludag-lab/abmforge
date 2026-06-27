# TestPyPI Dry Run

This guide describes how to verify an ABMForge release candidate on TestPyPI
before publishing to production PyPI.

The goal is to confirm that users can install the package from an index and run
the installed CLI in a clean environment.

This page does not publish to production PyPI.

## Why TestPyPI First?

TestPyPI is a package index for release rehearsal. It helps verify package
metadata, wheel upload, dependency resolution, installed imports, CLI entry
points, package data such as templates, and basic scenario/archive workflows.

Production PyPI publishing should happen only after a successful TestPyPI
installation smoke test.

## Trusted Publishing

ABMForge should use PyPI Trusted Publishing through GitHub Actions rather than
long-lived API tokens.

The release workflow should publish to TestPyPI only when:

- the workflow is triggered manually;
- `publish_testpypi=true`;
- the GitHub environment named `testpypi` is approved;
- a TestPyPI trusted publisher exists for the repository and workflow.

## Required TestPyPI Project Settings

Create or configure the ABMForge project on TestPyPI.

Recommended trusted publisher fields:

```text
Repository owner: fatihuludag-lab
Repository name: abmforge
Workflow filename: release.yml
Environment name: testpypi
```

Use a pending trusted publisher if the project does not exist on TestPyPI yet.

## Dry-Run Sequence

Recommended sequence:

1. confirm `main` is green;
2. run the Release workflow without publishing;
3. inspect uploaded distribution artifacts;
4. run the Release workflow manually with `publish_testpypi=true`;
5. approve the `testpypi` GitHub environment deployment;
6. wait for TestPyPI upload to complete;
7. run the manual TestPyPI install smoke workflow;
8. verify CLI, templates, scenario execution, and archive validation;
9. only then consider production PyPI preparation.

## Manual TestPyPI Install

Install from TestPyPI in a clean environment.

Linux/macOS:

```bash
python -m venv /tmp/abmforge-testpypi-smoke
/tmp/abmforge-testpypi-smoke/bin/python -m pip install --upgrade pip
/tmp/abmforge-testpypi-smoke/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  abmforge
```

Windows PowerShell:

```powershell
$SmokeVenv = "$env:TEMP\abmforge-testpypi-smoke"
Remove-Item $SmokeVenv -Recurse -Force -ErrorAction SilentlyContinue
python -m venv $SmokeVenv

& "$SmokeVenv\Scripts\python.exe" -m pip install --upgrade pip
& "$SmokeVenv\Scripts\python.exe" -m pip install `
  --index-url https://test.pypi.org/simple/ `
  --extra-index-url https://pypi.org/simple/ `
  abmforge
```

For a specific version:

```bash
python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  "abmforge==0.3.0a1"
```

## Installed-Package Verification

After installation, verify:

```bash
abmforge --version
abmforge info
abmforge cite
abmforge templates --json
```

Then create and run a template project:

```bash
abmforge new abmforge-smoke-study --template grid
cd abmforge-smoke-study
abmforge run configs/baseline.yaml --archive outputs/archive --overwrite
abmforge validate outputs/archive
abmforge summarize outputs/archive --json
```

The archive should validate successfully.

## Manual GitHub Workflow

ABMForge also provides a manual TestPyPI install smoke workflow:

```text
.github/workflows/testpypi-install-smoke.yml
```

It is intentionally `workflow_dispatch` only.

It does not publish anything.

It installs ABMForge from TestPyPI and runs the installed-package smoke script.

## Expected Success Criteria

A TestPyPI dry run is successful when:

- the TestPyPI upload succeeds;
- clean-environment install succeeds;
- `abmforge --version` works;
- `abmforge info` works;
- `abmforge templates --json` works;
- a generated template scenario runs;
- the generated archive validates;
- summary output is produced.

## Failure Handling

If the upload fails:

- check Trusted Publisher settings;
- confirm the workflow filename is `release.yml`;
- confirm the environment name is `testpypi`;
- confirm the version has not already been uploaded.

If installation fails:

- inspect package metadata;
- inspect dependency availability;
- check whether dependencies must be pulled from production PyPI with
  `--extra-index-url`;
- try installing a pinned version.

If runtime smoke fails:

- check package data inclusion;
- check entry points;
- check template files;
- check archive validation output.

## Production PyPI Gate

Do not publish to production PyPI until:

- TestPyPI dry run succeeds;
- package smoke workflow succeeds;
- release metadata strict check succeeds;
- changelog entry is complete;
- maintainer reviews artifacts;
- release notes are ready.

## Non-Goals

This dry-run process does not create a production PyPI release, create a GitHub
Release, create a DOI, guarantee scientific validity of example models, or make
performance claims.
