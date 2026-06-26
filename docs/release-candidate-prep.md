# Release Candidate Preparation

This page describes how ABMForge should prepare a release candidate without
accidentally publishing to production PyPI.

The current process is conservative:

1. align release metadata;
2. update the changelog;
3. run strict metadata checks;
4. build distributions;
5. validate distributions;
6. run package smoke checks;
7. run the release workflow without publishing;
8. optionally publish to TestPyPI after manual approval.

## Current Policy

Release candidate preparation should not automatically:

- bump the package version;
- create a git tag;
- publish to production PyPI;
- create a GitHub Release;
- upload to Zenodo.

Those actions should be explicit maintainer decisions.

## Metadata Alignment

Before creating a release candidate, check that these files agree where they
declare a version:

- `pyproject.toml`;
- `src/abmforge` runtime version;
- `CITATION.cff`;
- `codemeta.json`;
- `CHANGELOG.md`.

Run:

```bash
python scripts/check_release_metadata.py --strict
```

Strict mode requires the current declared version to appear in `CHANGELOG.md`.

## Changelog Requirements

Each release candidate changelog entry should include:

- version identifier;
- release status or date;
- highlights;
- breaking changes;
- new features;
- documentation changes;
- test and CI changes;
- known limitations.

Development versions may be marked as `Unreleased` until a tag is created.

## Release Candidate Local Checks

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

If packaging or templates changed, also run the installed-wheel smoke workflow.

## GitHub Actions Checks

Before tagging a release candidate, confirm that the following pass on `main`:

- main CI matrix;
- package smoke workflow;
- release workflow build job;
- docs build;
- tests;
- type checks.

## TestPyPI Dry Run

A TestPyPI dry run should use the release workflow:

1. run the workflow without publishing;
2. inspect distribution artifacts;
3. run the workflow manually with `publish_testpypi=true`;
4. approve the `testpypi` environment;
5. install from TestPyPI in a clean environment;
6. run smoke checks.

## Tagging Guidance

Use pre-release tags for candidate work:

```text
v0.3.0a1
v0.3.0rc1
```

Do not tag a production release until:

- changelog is complete;
- strict metadata check passes;
- TestPyPI install works;
- package smoke passes;
- maintainer has reviewed release artifacts.

## Known Alpha Limitations

Before a release candidate, the project should be honest about limitations:

- ABMForge is alpha-stage research software;
- public APIs remain provisional unless explicitly marked stable;
- archive and dataset formats may still evolve;
- untrusted model code is not sandboxed;
- benchmark infrastructure is a scaffold, not a performance claim;
- scientific validity depends on model assumptions and validation evidence.

## Maintainer Checklist

- [ ] Current version is intentional.
- [ ] Changelog entry exists for the current version.
- [ ] `python scripts/check_release_metadata.py --strict` passes.
- [ ] Documentation builds with `mkdocs build --strict`.
- [ ] Tests pass.
- [ ] Type checks pass.
- [ ] Wheel and sdist build.
- [ ] `twine check` passes.
- [ ] Package smoke passes.
- [ ] Release workflow build artifact is inspected.
- [ ] TestPyPI dry run is completed if publishing is planned.
