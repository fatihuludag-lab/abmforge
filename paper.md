---
title: "ABMForge: An experiment-native Python framework for reproducible agent-based modeling research"
tags:
  - Python
  - agent-based modeling
  - computational social science
  - reproducibility
  - simulation
  - research software
authors:
  - name: Fatih Uludağ
    affiliation: 1
affiliations:
  - name: Department of Econometrics, Van Yüzüncü Yıl University, Türkiye
    index: 1
date: 2026-06-28
bibliography: paper.bib
---

# Summary

ABMForge is a lightweight, Python-first framework for agent-based modeling
research. It is designed for researchers, educators, and model developers who
need simulations that are easy to write, inspect, archive, and reproduce. The
framework provides a compact modeling core with agents, models, schedulers,
spaces, event queues, datasets, scenario definitions, multi-run experiments,
archive validation, reproducibility manifests, and ODD-style model
documentation.

The project is intentionally not a clone of established agent-based modeling
platforms such as Mesa [@mesa], NetLogo [@netlogo], Repast [@repast], MASON
[@mason], or Agents.jl [@agentsjl]. Instead, ABMForge focuses on the research
workflow surrounding computational experiments: scenario-based execution,
dataset-oriented outputs, reproducibility metadata, archive integrity checks,
and publication-facing artifacts.

# Statement of need

Agent-based modeling is widely used in economics, computational social science,
epidemiology, urban systems, environmental modeling, and education. In many
projects, however, the model code is easier to preserve than the research
workflow that produced the results. A published simulation study often requires
more than a runnable model: it needs controlled seeds, explicit scenarios,
parameter grids, replication metadata, structured output tables, provenance
records, documentation of model assumptions, and inspectable archives that can
be validated after the experiment has been run.

Existing platforms address important parts of this ecosystem. NetLogo provides a
highly accessible modeling environment for teaching and exploratory modeling
[@netlogo]. Mesa offers a flexible Python framework for agent-based modeling and
analysis [@mesa]. Repast and MASON provide mature Java-based simulation toolkits
[@repast; @mason], while Agents.jl integrates agent-based modeling with the Julia
scientific computing ecosystem [@agentsjl]. ABMForge complements these tools by
emphasizing a small Python API and an experiment-native workflow for producing
research artifacts.

The target users are researchers and students who want to build ABM studies in
Python while preserving the structure of the experiment. ABMForge is especially
suited for early-stage computational research, teaching reproducible simulation
practice, and preparing small to medium-sized ABM studies where the audit trail
is as important as the model implementation.

# Design and functionality

ABMForge separates the modeling core from the research workflow. The core
includes `Agent`, `Model`, collections, schedulers, spaces, and event queues.
The workflow layer includes `Scenario`, `Experiment`, parameter grids, seed
sequences, datasets, experiment archives, and command-line tools. Model outputs
are recorded as structured tables covering runs, model-level records,
agent-level records, event records, lifecycle records, and errors.

Scenario and experiment configuration files allow researchers to describe runs
outside Python source code. This encourages reuse, review, and replication of
experiment settings. Validation errors are field-oriented and designed for both
Python and CLI use, so invalid scenario files can be fixed without reading a
long traceback.

ABMForge archives are directory-based research artifacts. An archive can include
configuration files, structured datasets, a dataset schema, a run index,
reproducibility metadata, reports, logs, snapshots, and additional artifacts.
The archive validator checks the minimum archive contract, dataset schema
hashes, record counts, record hashes, and manifest artifact checksums. The
machine-readable `archive_v1_contract()` helper exposes the current public-alpha
storage contract for tests, documentation, and downstream tooling.

# Reproducibility workflow

The reproducibility workflow combines deterministic seeds, dataset schemas,
manifest metadata, and archive validation. A manifest records information about
the software version, Python runtime, platform, package environment, Git state,
dataset schema hash, table record counts, table hashes, and archive artifact
checksums. These records help detect changes to archived configuration files,
datasets, schema files, reports, and other registered artifacts after creation.

ABMForge also supports ODD-style model documentation [@odd]. The current ODD
helper produces Markdown and JSON artifacts that describe purpose, entities,
scales, processes, design concepts, initialization, input data, and submodels.
The generated documentation is marked for manual review because ODD remains a
scientific model specification task rather than a purely automatic export.

# Example use case

The repository includes a reference reproducible study based on a synthetic
threshold-adoption model. The example runs a parameterized, multi-seed
experiment from YAML, writes an archive, validates the archive, summarizes the
results, exports analysis artifacts, and generates reviewer-facing files such as
ODD Markdown, ODD JSON, a research protocol, and an artifact manifest. This
example is deliberately small. Its purpose is to demonstrate the complete
ABMForge workflow rather than to make an empirical claim about adoption
behavior.

# Limitations and future work

ABMForge is alpha-stage software. The public API is being stabilized, and some
modules remain provisional or experimental. The current reproducibility workflow
supports auditability through seeds, structured archives, manifests, and
checksums, but full reconstruction of every simulation state still depends on
preserving source code, input files, dependencies, and execution environments.
Full state replay across worlds, schedulers, event queues, and external data is
a future goal rather than a completed guarantee.

Future work includes release hardening, PyPI publication, fuller archive schema
validation, stronger replay contracts, additional research examples, calibration
and validation workflows, parallel experiment execution, and improved
documentation for downstream extension.

# Acknowledgements

The development of ABMForge has been guided by reproducible computational
research practice, agent-based modeling methodology, and scientific software
review criteria.
