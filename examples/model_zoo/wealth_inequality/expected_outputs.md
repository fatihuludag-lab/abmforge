# Expected Outputs

A successful baseline run should produce an archive with:

- `manifest.json`
- `dataset_schema.json`
- `run_index.json`
- `data/runs.json`
- `data/model_records.json`
- `data/agent_records.json`
- `reports/wealth_analysis_summary.csv` after running `analysis/analyze.py`

The main model metrics are `gini`, `mean_wealth`, `max_wealth`, and
`total_wealth`.
