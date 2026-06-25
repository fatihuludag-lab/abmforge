# ODD Export Specification

**Status:** Draft  
**Version:** 1.0  
**Applies to:** ABMForge >= 0.2.x

## Overview

ABMForge provides a lightweight ODD-style documentation helper through
`ODDDocument`.

ODD stands for **Overview, Design Concepts, and Details**. It is commonly used
to describe agent-based models in a structured and publication-friendly way.

The current ABMForge ODD support is intentionally conservative:

- it creates a structured ODD skeleton;
- it can inspect public model methods;
- it exports Markdown and JSON;
- it marks the document as requiring manual review;
- it does not claim that the model is automatically complete, validated, or publication-ready.

## Public API

Use `ODDDocument` from the public ABMForge API:

<!-- abmforge:execute-python -->
```python
from abmforge import Model, ODDDocument


class WealthModel(Model):
    def setup(self) -> None:
        self.population = 100

    def step(self) -> None:
        pass


odd = ODDDocument.from_model(
    WealthModel,
    purpose="Document a simple wealth model.",
    authors=["Fatih Uludağ"],
    entities=["Household"],
    scales={
        "time": "discrete simulation step",
        "space": "abstract population",
    },
    process_overview=[
        "The model advances one discrete step at a time.",
    ],
    design_concepts={
        "stochasticity": "The model may use controlled random number generation.",
        "observation": "Model-level and agent-level outputs can be recorded.",
    },
    initialization=[
        "The model initializes a fixed-size population.",
    ],
)

odd.add_state_variable(
    "Household",
    "wealth",
    description="Household wealth level.",
    kind="float",
    unit="abstract units",
)

odd.write_markdown("outputs/ODD.md")
odd.write_json("outputs/ODD.json")
```

## ODD Structure

ABMForge's ODD skeleton includes:

1. Purpose
2. Entities, state variables, and scales
3. Process overview and scheduling
4. Design concepts
5. Initialization
6. Input data
7. Submodels
8. Decision processes
9. ABMForge model introspection
10. Completeness checklist

## Manual Review Requirement

Generated ODD files are skeleton documents. Authors should review and complete
every section before using them in a thesis, article, technical report, or
supplementary material.

The ODD helper supports documentation. It does not replace scientific validation,
calibration, sensitivity analysis, or methodological review.

## Output Formats

Currently supported:

- Markdown
- JSON

Planned or future formats may include:

- HTML
- PDF
- journal-specific templates

## Recommended Workflow

```text
model class
    ↓
ODDDocument.from_model(...)
    ↓
manual review and completion
    ↓
ODD.md / ODD.json
    ↓
experiment archive or publication supplement
```

## Versioning

Current schema version:

```text
abmforge.odd.v1
```
