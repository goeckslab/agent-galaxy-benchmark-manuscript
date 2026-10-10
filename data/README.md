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

## Token usage tables

`token_optimization_rounds.csv` lists the BixBench-Verified-50 token totals at each Galaxy token-optimization stage, transcribed by hand from the benchmark results site (`goeckslab/galaxy-agent-benchmark`) and Junhao Qiu's notes; its `source` column names where each row comes from.

| Column | Meaning |
| --- | --- |
| order, slug, stage, change | Stage order, identifier, name and a short description of what changed |
| model, runs_per_task | Model, and runs per task in each condition |
| galaxy_tokens_m, custom_code_tokens_m | Total tokens (input plus output, cached input counted once), in millions; empty when only an approximate ratio is known |
| token_unit | `total over 150 runs` or `mean per 50-task run` |
| ratio_reported | Approximate Galaxy ÷ custom-code ratio, for stages without totals |
| galaxy_correct, galaxy_runs | Correct Galaxy runs and runs, where reported |
| source | Where the row's numbers come from |

`token_optimization_ratios.csv` is that table plus `ratio` (computed from the totals, or the reported ratio) and `approximate`, written by `analysis/token_usage.py`.

`token_ratios_main_runs.csv` is written by `analysis/token_usage.py` from `run_tokens_actions.csv` (added in PR #12; the committed version was generated from PR #12 commit `9c8593f`).
It has one row per benchmark and model, plus `All models`, with Galaxy and custom-code run counts, runs without a token count, summed input tokens, and their `ratio`.
