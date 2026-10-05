# Data

Small derived tables only. Raw traces stay on Hugging Face and are fetched by `analysis/fetch_traces.py`.

`results_manifest.csv` has one row per run and links every reported number to the traces that produced it:

| Column | Meaning |
| --- | --- |
| task_id | Benchmark task identifier |
| track | Execution condition: `Galaxy` or `custom code` |
| model | Display name used in figures |
| model_string | Exact model identifier as run |
| replicate | Replicate number |
| run_date | Date of the run |
| trace_path | Path of the trace inside the Hugging Face dataset |
| trace_dataset_revision | Dataset revision (commit hash) the trace was read at |
| final_answer | Answer the agent returned |
| expected_answer | Ground-truth answer |
| correct | true or false |
| notes | Anything a reader of the manifest needs to know |

Each derived table needs a note on which script produced it.

## Tables exported from the run archive

`analysis/export_galaxy_benchmark_tables.py` writes the three tables below from the run archive (`paulocilasjr/Galaxy_benchmark`, commit `b66d91a`).
They cover the four primary model configurations and hold identifiers, scores and tool identifiers only: no trace text, prompts or answers.
Figure 2 reads them.

`run_scores.csv` has one row per scored run (3,816 runs):

| Column | Meaning |
| --- | --- |
| benchmark | `BixBench-Verified-50`, `CompBioBench` or `IWC` |
| task_id | Benchmark task identifier |
| cluster | Resampling unit for intervals and tests: the BixBench source capsule, otherwise the task |
| model | Display name used in figures |
| track | Execution condition: `Galaxy` or `custom code` |
| replicate | Replicate number |
| score | 1 or 0 for acceptance (BixBench-Verified-50, CompBioBench); output agreement from 0 to 1 (IWC) |

IWC has nine tasks here: the host-read removal task has no comparable scores between conditions and is not scored.

`galaxy_traced_runs.csv` lists the Galaxy-condition runs with a parsed trace (1,908 runs), the denominators for tool use.
Its columns are `benchmark`, `task_id`, `model` and `replicate`.

`galaxy_tool_use.csv` has one row for each traced Galaxy run and installed tool the run called, whether or not the job succeeded, and one row for each run that called a user-defined tool (UDT).
Its columns are the four run columns, `tool_id` (the Tool Shed identifier without its version, a built-in identifier such as `Cut1`, or `UDT`) and `kind` (`installed` or `udt`).
