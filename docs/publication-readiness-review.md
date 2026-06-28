# Publication Readiness Review

This page is an internal reviewer-style readiness assessment for ABMForge as a
scientific software project. It is not a submission letter and it does not claim
that the project is already accepted or release-complete.

## Current maturity classification

Current status:

```text
publication-oriented research-workflow alpha
```

ABMForge is beyond a toy prototype because it has a tested Python package
structure, command-line workflows, scenario configuration, experiment archives,
dataset schemas, reproducibility manifests, archive checksums, ODD-style model
documentation, a reference reproducible study, issue templates, and a software
paper scaffold.

ABMForge is not yet production-ready because the public package release,
TestPyPI/PyPI install smoke, DOI/archive release, full replay guarantees, and
final paper review are not complete.

## Evidence already in the repository

The following repository components support a future JOSS, SoftwareX, or Journal
of Open Research Software submission:

- modern Python package layout;
- typed package marker;
- CI across supported Python versions;
- package smoke workflows;
- CLI workflow;
- scenario YAML workflow;
- experiment configuration workflow;
- structured dataset tables;
- experiment archive writer and validator;
- archive v1 storage contract;
- manifest artifact checksums;
- research-grade reproducible study;
- ODD Markdown and JSON artifacts;
- software paper scaffold;
- release-readiness without publishing;
- community issue templates and reproducibility report template;
- citation metadata and project metadata files.

## Submission blockers

These items should be resolved before a formal software paper submission:

1. **Public alpha release**  
   Create a release tag and publish the package to TestPyPI/PyPI or clearly
   document an accepted install route for the target venue.

2. **Install smoke from published artifact**  
   Verify that a clean environment can install the released package and run the
   installed-package smoke test.

3. **Release artifact and DOI**  
   Create a citable release artifact, for example through GitHub Releases and
   Zenodo.

4. **Final paper review**  
   Review `paper.md` for claim accuracy, word count, citations, author metadata,
   affiliation metadata, and limitations.

5. **Manual ODD review**  
   Review generated ODD files in the reference study. ODD artifacts are
   publication-supporting documents, not automatically validated scientific
   truth.

6. **Repository issue settings**  
   Confirm that GitHub Issues and Discussions are enabled for public alpha
   support, or document the alternative reporting channel.

## Non-blockers for an alpha software paper

The following items are useful future work but should not block an alpha-stage
software paper if limitations are stated clearly:

- full deterministic state replay for every world, scheduler, and event-queue
  combination;
- high-performance or HPC execution;
- a large model zoo;
- empirical calibration workflows;
- stable 1.0 API guarantees;
- rich dashboard interfaces;
- AI-enabled agent provenance.

## Claims that are currently defensible

The paper and README can defensibly claim that ABMForge provides:

- a lightweight Python-first ABM framework;
- scenario-driven model execution;
- structured dataset outputs;
- experiment-native workflows;
- reproducibility-oriented manifests;
- archive validation;
- archive artifact checksum checks;
- ODD-style documentation helpers;
- a research-grade reproducible study example;
- public-alpha API categorization.

## Claims to avoid or qualify

The project should not currently claim that it:

- replaces Mesa, NetLogo, Repast, MASON, or Agents.jl in general;
- provides full deterministic replay for all model states;
- is production-ready;
- is API-stable at 1.0 level;
- has been empirically validated across domains;
- supports large-scale HPC workflows;
- is already available from PyPI unless the release has actually happened.

Preferred wording:

```text
ABMForge complements existing ABM tools by emphasizing experiment-native,
dataset-first, and reproducibility-oriented research workflows in Python.
```

Avoid wording:

```text
ABMForge is a complete replacement for existing ABM platforms.
```

## Reviewer risk register

| Risk | Likely reviewer concern | Mitigation |
|---|---|---|
| Alpha API | Public API may change before 1.0 | API stability policy and public-alpha surface tests |
| Release status | Package may not be installable from PyPI | No-publish readiness now; TestPyPI/PyPI release before submission |
| Reproducibility scope | Archive metadata is not full state replay | State limitations explicitly in paper and docs |
| Model documentation | Generated ODD may be incomplete | Mark ODD as manual-review-required |
| Differentiation | Another Python ABM framework | Emphasize archive, manifest, dataset, and research workflow contribution |
| Community support | Users may not know where to report issues | Issue templates, reproducibility report template, Discussions |

## Pre-submission checklist

Before submission, complete the following:

- [ ] merge all release-readiness PRs;
- [ ] run full CI on the release commit;
- [ ] run `python scripts/check_version_consistency.py`;
- [ ] run `python scripts/check_release_metadata.py --strict`;
- [ ] build documentation with `python -m mkdocs build --strict`;
- [ ] build distributions with `python -m build`;
- [ ] run `python -m twine check dist/*`;
- [ ] publish or dry-run via TestPyPI according to release policy;
- [ ] verify clean install smoke from the released artifact;
- [ ] create GitHub release notes;
- [ ] create or reserve DOI/archive release;
- [ ] review `paper.md` manually;
- [ ] review `paper.bib` manually;
- [ ] confirm issue templates are visible on GitHub;
- [ ] confirm Discussions are enabled or support alternatives are documented;
- [ ] ensure the reference reproducible study runs from a clean checkout.

## Recommended next PRs

Recommended next work after this readiness review:

1. `docs/paper-refinement`
2. `release/changelog-notes-cleanup`
3. `docs/readme-positioning-final`
4. `release/testpypi-publish-smoke` after credentials are available
5. `release/pypi-alpha-v0.3.0a1` after TestPyPI validation

## Current decision

ABMForge should be described as:

```text
publication-oriented research-workflow alpha
```

It is not yet production-ready, but it has a credible path toward a software
paper submission once release, DOI, and final paper review tasks are completed.
