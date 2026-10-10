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

All token totals in the paper come from the results website (https://goeckslab.github.io/galaxy-agent-benchmark/).

`site_token_totals.csv` is written by `analysis/fetch_site_token_totals.py` from the website: summed from its per-replicate tables for CompBioBench and IWC, and read from the per-model table on its BixBench tokens page (rounded to 0.01M) for BixBench-Verified-50.
The committed version was fetched on 2026-10-12, when the deployed files matched commit `ff9c4f5` of `goeckslab/galaxy-agent-benchmark`.

| Column | Meaning |
| --- | --- |
| benchmark, model, track | Benchmark, model configuration and execution condition |
| runs_with_usage | Runs with a usage record (empty for BixBench-Verified-50, whose page does not give it) |
| input_tokens, total_tokens | Input tokens (cached input included) and total tokens (input plus output) |
| precision | `exact`, or `rounded to 0.01M` |
| source | Website page or table, and fetch date |

`token_ratios_main_runs.csv` is written by `analysis/token_usage.py` from `site_token_totals.csv`: one row per benchmark and model, plus `All models`, with Galaxy and custom-code total tokens and their `ratio`.

`replicate_consensus.csv` and `bixbench_causes_by_agreement.csv` are written by `analysis/replicate_consensus.py` from `run_scores.csv` and `bixbench_failure_causes.csv`.
The committed versions were generated from those two inputs at PR #12 commit `9c8593f`, before they were merged to `main`; rerun the script after they merge and check that nothing changed.
Votes are computed from correctness, assuming correct answers agree; see the script's docstring.

`replicate_consensus.csv` has one row per benchmark (BixBench-Verified-50 and CompBioBench) and condition.
A replicate group is the 3 replicate runs of one task, model and condition.

| Column | Meaning |
| --- | --- |
| benchmark, track | Benchmark and execution condition |
| runs, replicate_groups, tasks | Counts the rates are computed over |
| single_run_accuracy | Share of runs correct |
| majority_of_3_accuracy | Share of replicate groups with at least 2 of 3 runs correct |
| any_of_3_accuracy | Share of replicate groups with at least 1 run correct: the ceiling for a step that picks a correct replicate |
| majority_of_12_accuracy | Share of tasks with more than 6 of their 12 runs (4 models × 3 replicates) correct |
| groups_3_of_3 … groups_0_of_3 | Share of replicate groups with 3, 2, 1 or 0 runs correct |
| incorrect_runs | Incorrect runs |
| incorrect_in_all_wrong_groups | Incorrect runs whose replicate group had no correct run |
| incorrect_in_majority_correct_groups | Incorrect runs whose other 2 replicates were correct, which a majority vote would fix |

`bixbench_causes_by_agreement.csv` counts incorrect BixBench-Verified-50 runs by `track`, `primary_cause` (codes as in `bixbench_failure_causes.csv`) and `correct_replicates_in_group` (0, 1 or 2 of the run's other replicates correct), in `incorrect_runs`.
