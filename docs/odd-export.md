# ODD Export Specification

**Status:** Draft
**Version:** 1.0
**Applies to:** ABMForge >= 0.2.x

## Overview

ABMForge supports exporting simulation models using the ODD (Overview, Design Concepts, Details) protocol.

The ODD protocol improves:

- Reproducibility
- Transparency
- Scientific communication
- Model comparison
- Publication readiness

## Export Command

```python
from abmforge.export import export_odd

export_odd(model, "model_odd.md")
```

## ODD Structure

### 1. Purpose

Describes the goal of the model.

### 2. Entities, State Variables, and Scales

Documents:

- Agent types
- State variables
- Environment
- Temporal scale
- Spatial scale

### 3. Process Overview and Scheduling

Describes:

- Agent activation
- Scheduling strategy
- Event execution
- Simulation lifecycle

## Design Concepts

- Basic principles
- Emergence
- Adaptation
- Objectives
- Learning
- Prediction
- Sensing
- Interaction
- Stochasticity
- Collectives
- Observation

## Details

### Initialization

Initial model state.

### Input Data

External datasets used by the model.

### Submodels

Agent decision logic and sub-processes.

## Metadata

| Field | Description |
|---------|-------------|
| model_name | Model name |
| model_version | Version |
| abmforge_version | Framework version |
| author | Author |
| created_at | Creation timestamp |

## Output Formats

Current:
- Markdown (.md)

Planned:
- PDF
- HTML
- JATS XML

## Example

```python
odd_text = model.to_odd()

with open("model_odd.md", "w") as f:
    f.write(odd_text)
```

## Future Extensions

- Automatic diagram generation
- UML export
- Network visualization export
- Publication-ready templates
- Journal-specific ODD templates

## Versioning

odd_version=1.0
