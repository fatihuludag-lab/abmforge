# Vision

ABMForge aims to be a modern, installable, extensible framework for agent-based simulation in Python.

## Core principles

- Easy start: users can write a small model with `Model`, `Agent`, and `Scenario`.
- Reproducible by default: seed, parameters, run metadata, status, and records are preserved.
- Dataset-first: recording and analysis are not an afterthought.
- Experiment-native: scenarios and experiments are part of the core model of the framework.
- Observable simulation: future releases will support snapshots, replay, and debugging.
- Extensible: heavy features should be optional packages or plugins.

## Differentiators

- Event ownership and tag-based cancellation.
- Recorder/Dataset instead of a legacy collector pattern.
- Scenario/Experiment as first-class concepts.
- Optional dependency groups for data, visualization, geo, and distributed execution.
- Future object-mode and columnar-mode agent backends.
