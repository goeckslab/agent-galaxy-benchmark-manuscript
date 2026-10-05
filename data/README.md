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

`analysis/export_galaxy_benchmark_tables.py` writes the tables below from the run archive (`paulocilasjr/Galaxy_benchmark`, commit `b66d91a`).
They cover the four primary model configurations and hold identifiers, scores, counts, cause codes and tool identifiers only: no trace text, prompts or answers.
Figure 2 reads `run_scores.csv`, `galaxy_traced_runs.csv` and `galaxy_tool_use.csv`; Figure 3 reads `run_scores.csv`, `run_execution_errors.csv` and `bixbench_failure_causes.csv`; Figure 4 reads `run_scores.csv`, `run_tokens_actions.csv`, `galaxy_interface_calls.csv` and `galaxy_tool_lookup.csv`.

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

`run_execution_errors.csv` has one row per run with execution-error records (3,767 of the 3,816 scored runs), from sheet `abc_runs` of `manuscript_material/on_demand/Source_Data_OD_Fig5.xlsx` in the archive:

| Column | Meaning |
| --- | --- |
| benchmark, task_id, model, track, replicate | Run identifiers, as in `run_scores.csv` |
| failed_shell_commands | Shell commands that failed, not counting a silent exit code 1 |
| galaxy_jobs_in_error_state | Galaxy jobs of the run that ended in the error state (0 for custom-code runs) |

`bixbench_failure_causes.csv` has one row per incorrect BixBench-Verified-50 run (170 runs), from the run-level failure audit (`analysis_reports/galaxy_improvement_20260924/v2_trace_friction/ledger.json` in the archive).
The export checks that every incorrect run in `run_scores.csv` has exactly one row.
Only the cause codes are exported; the audit's answer and note fields are not.

| Column | Meaning |
| --- | --- |
| benchmark, task_id, model, track, replicate | Run identifiers, as in `run_scores.csv` |
| primary_cause | `RIGOR` (no answer validation), `KNOWLEDGE` (wrong biological or statistical concept), `PLATFORM` (a Galaxy tool, wrapper or job gave the wrong result), `HARNESS` (no answer submitted), `SPEC` (under-specified task or reference) or `EVALUATOR` (scorer rejected a valid answer) |
| secondary_cause | A second contributing cause, with the same codes; empty when there is none |
| confidence | The auditor's confidence in the primary cause: `high`, `moderate`, `mixed` or `unresolved` |

`run_tokens_actions.csv` has one row per scored run (3,816 runs), joining two archive tables: `manuscript_narrative/original_layout/analysis/token_run_observations.csv` for tokens and sheet `abf_runs` of `manuscript_material/on_demand/Source_Data_OD_Fig6.xlsx` for actions.
Some counts are empty, mostly for runs without a parsed trace: 14 runs have no token count, 15 no cached count and 12 no action count.

| Column | Meaning |
| --- | --- |
| benchmark, task_id, model, track, replicate | Run identifiers, as in `run_scores.csv` |
| input_tokens | Input tokens over the run, including cached context |
| cached_input_tokens | The part of `input_tokens` read from the prompt cache |
| actions | Tool calls by the agent: shell commands, Galaxy interface calls, web searches or fetches, file reads, writes and edits |

`galaxy_interface_calls.csv` has one row per traced Galaxy run and Galaxy interface function the run called (9,147 rows), summed from the archive's call records.
It covers 1,808 of the 1,908 runs in `galaxy_traced_runs.csv`; the other 100 (99 DeepSeek V4 Pro, 1 GPT-5.6 Luna) made no Galaxy interface call.

| Column | Meaning |
| --- | --- |
| benchmark, task_id, model, replicate | Run identifiers, as in `galaxy_traced_runs.csv` |
| interface_function | The Galaxy interface function, for example `search_galaxy_tools`, `inspect_galaxy_tool` or `run_galaxy_tool_and_wait` |
| requests | Number of calls to that function in the run |
| chars_returned | Characters of text the function returned to the agent over those calls |

`galaxy_tool_lookup.csv` has one row per benchmark, copied from the archive's interface-friction table (`manuscript_narrative/original_layout/analysis/token_interface_friction.csv`):

| Column | Meaning |
| --- | --- |
| benchmark | `BixBench-Verified-50`, `CompBioBench` or `IWC` |
| tools_inspected | Distinct tools whose description an agent read, counted once per traced Galaxy run |
| never_run | How many of those tools the same run never ran |
| percent | `never_run` as a percentage of `tools_inspected` |
