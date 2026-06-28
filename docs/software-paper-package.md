# Software Paper Package

This page tracks the publication package for ABMForge as a scientific software
project.

## Target venues

The current package is primarily shaped around a JOSS-style short software
paper. The same material can later be expanded for SoftwareX or Journal of Open
Research Software.

## Current package

- `paper.md`: software paper scaffold.
- `paper.bib`: bibliography for the paper.
- `examples/reproducible_study/`: reference reproducible study.
- `docs/reproducibility-manifest-v1.md`: manifest contract.
- `docs/experiment-archive-v1.md`: archive contract.
- `docs/api-stability.md`: public alpha API policy.

## Submission blockers

Before submission, the following should be completed:

- public alpha release tag;
- PyPI or TestPyPI install smoke;
- DOI or archived release artifact;
- final author metadata and ORCID, if available;
- final review of citations and comparison claims;
- full clean CI run on the release commit;
- manual review of the generated ODD example;
- confirmation that the paper remains within the target venue word limit.

## Statement of need focus

ABMForge should be positioned as an experiment-native, dataset-first, and
reproducibility-oriented Python ABM framework. The paper should not claim that
ABMForge is a complete replacement for Mesa, NetLogo, Repast, MASON, or Agents.jl.
Its strongest contribution is the research workflow around ABM experiments.

## Current limitations to disclose

- alpha-stage API;
- no full deterministic state replay guarantee for all model/world/scheduler
  combinations;
- PyPI release status should match the actual release state at submission time;
- generated ODD artifacts require manual scientific review;
- examples are workflow demonstrations, not empirical validation studies.

## Readiness review

The publication readiness review is tracked separately in:

```text
docs/publication-readiness-review.md
```

That page separates submission blockers, non-blockers, defensible claims,
claims to avoid, and pre-submission checks.
