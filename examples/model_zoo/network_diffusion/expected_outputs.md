# Expected Outputs

A successful baseline run should produce an archive with:

- `manifest.json`
- `dataset_schema.json`
- `run_index.json`
- `data/runs.json`
- `data/model_records.json`
- `data/agent_records.json`
- `reports/diffusion_analysis_summary.csv` after running `analysis/analyze.py`

The main model metrics are `adoption_share`, `adopter_count`,
`new_adoptions`, and `mean_threshold`.
