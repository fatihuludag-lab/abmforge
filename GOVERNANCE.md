# Governance

ABMForge is currently maintained by Fatih Uludağ as a small open research
software project.

The governance model may evolve if the project gains external users and
contributors.

## Project Goals

ABMForge aims to be:

- lightweight and Python-first;
- reproducibility-oriented;
- experiment-native;
- dataset-first;
- useful for research and teaching;
- suitable for auditable agent-based modelling workflows.

## Decision Making

Project decisions are currently made by the maintainer.

Design decisions should consider:

- research usefulness;
- API clarity;
- reproducibility;
- testability;
- documentation burden;
- backward compatibility;
- packaging and release impact.

For large changes, prefer an issue or RFC-style discussion before opening a
large implementation pull request.

## Contribution Principles

Contributions should:

- include tests;
- update documentation when user-facing behavior changes;
- avoid unnecessary dependencies in the core package;
- preserve deterministic and reproducibility-oriented behavior;
- keep public APIs clear and typed where practical;
- avoid overstating scientific or production guarantees.

## API Stability

ABMForge is alpha software. Public APIs may still change.

Breaking changes should be:

- documented in the changelog;
- justified by a clear design or research workflow benefit;
- accompanied by migration notes when possible.

## Maintainer Responsibilities

The maintainer is responsible for:

- reviewing issues and pull requests;
- maintaining release quality;
- keeping documentation accurate;
- preserving project scope;
- triaging security reports;
- deciding when APIs are stable enough for beta or 1.0.

## Future Governance

If ABMForge gains active external contributors, the project should add:

- contributor roles;
- review expectations;
- release manager responsibilities;
- decision records;
- a formal RFC process.
