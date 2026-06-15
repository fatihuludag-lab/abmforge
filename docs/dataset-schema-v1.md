# Dataset Schema v1

**Status:** Draft
**Version:** 1.0
**Applies to:** ABMForge ≥ 0.2.x

## Overview

ABMForge uses a dataset-first approach for simulation outputs.

The Dataset Schema defines a standardized tabular representation for:
- Agent-level observations
- Model-level observations
- Event logs
- Experiment metadata
- Reproducibility information

## Core Dataset Types

- agent_state
- model_state
- event_log
- experiment_run

## Agent State Dataset

Required columns:

| Column | Type |
|----------|----------|
| run_id | string |
| step | int |
| agent_id | string |
| agent_type | string |
| alive | bool |

## Model State Dataset

Required columns:

| Column | Type |
|----------|----------|
| run_id | string |
| step | int |

## Event Log Dataset

Required columns:

| Column | Type |
|----------|----------|
| run_id | string |
| step | int |
| event_id | string |
| event_type | string |

## Experiment Run Dataset

Required columns:

| Column | Type |
|----------|----------|
| run_id | string |
| scenario_name | string |
| seed | int |
| started_at | datetime |
| ended_at | datetime |

## Export Formats

Current support:
- CSV

Planned support:
- Parquet
- Arrow
- Feather

## Versioning Policy

Major schema changes require a new schema version.

Example:

schema_version=v1
