# Data

Small derived tables only. Raw traces stay on Hugging Face and are fetched by `analysis/fetch_traces.py`.

`results_manifest.csv` has one row per run and links every reported number to the traces that produced it:

| Column | Meaning |
| --- | --- |
| task_id | Benchmark task identifier |
| track | Galaxy or custom code |
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
