# Analysis

ABMForge includes basic analysis helpers for experiment outputs.

## SensitivityAnalysis

`SensitivityAnalysis` estimates simple parameter effects using final model-level metric values.

```python
from abmforge import SensitivityAnalysis

analysis = SensitivityAnalysis(
    experiment_result,
    metric="total_wealth",
)

summary = analysis.summary()
print(summary)
```

## SALib Integration

SALib support is optional.

Install analysis dependencies:

```bash
pip install -e ".[analysis]"
```

## Sobol Sampling

```python
from abmforge import SALibProblem, sample_sobol

problem = SALibProblem(
    bounds={
        "density": (0.4, 0.9),
        "homophily": (0.1, 0.8),
    }
)

samples = sample_sobol(problem, n=128, seed=42)
```

## Morris Sampling

```python
from abmforge import SALibProblem, sample_morris

problem = SALibProblem(
    bounds={
        "density": (0.4, 0.9),
        "homophily": (0.1, 0.8),
    }
)

samples = sample_morris(problem, n=32, seed=42)
```

## Recommended Workflow

1. Define parameter ranges.
2. Generate samples.
3. Run model scenarios.
4. Collect final metrics.
5. Analyze sensitivity.
