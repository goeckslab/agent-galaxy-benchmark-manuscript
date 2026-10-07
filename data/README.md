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

`analysis/export_galaxy_benchmark_tables.py` writes the tables below from the run archive (`paulocilasjr/Galaxy_benchmark`, commit `0dbf3f4`, branch `archive/reruns-token-figures-2026-10-07`).
That commit includes the 53 reviewed CompBioBench Galaxy reruns of 2026-10-05, which replaced the runs they superseded (archive `CompBio/reruns_20261005/`).
It also scores every run as the public results site shows it (https://goeckslab.github.io/galaxy-agent-benchmark/; archive `figures/make_scored_runs.py`):
- BixBench-Verified-50 grades include the site's regrades of bix-53-q2 and bix-43-q2 (27 runs).
- CompBioBench grades are the official-leaderboard grades.
- The IWC host-read removal task is scored from each run's `run_record.json`.
They cover the four primary model configurations and hold identifiers, scores, counts, cause codes and tool identifiers only: no trace text, prompts or answers.

The figures (1-5, and Extended Data Figures 2-7) read `figure_panels/`: the values the archive's figure scripts computed and drew, which `figures/*/make_figure.py` replays with the same drawing code (see [figure_panels/README.md](figure_panels/README.md)).
The tables below support the text and the earlier figure versions kept in `supplement/figures/previous_versions/`, which read them; versions before 2026-10-07 no longer reproduce their stored images, because the tables now include the reruns and the site-matched scores.

`run_scores.csv` has one row per scored run (3,840 runs):

| Column | Meaning |
| --- | --- |
| benchmark | `BixBench-Verified-50`, `CompBioBench` or `IWC` |
| task_id | Benchmark task identifier |
| cluster | Resampling unit for intervals and tests: the BixBench source capsule, otherwise the task |
| model | Display name used in figures |
| track | Execution condition: `Galaxy` or `custom code` |
| replicate | Replicate number |
| score | 1 or 0 for acceptance (BixBench-Verified-50, CompBioBench); output agreement from 0 to 1 (IWC) |

IWC has ten tasks here. The host-read removal task takes each run's `run_record.json` value, which the results site shows.

`galaxy_traced_runs.csv` lists the Galaxy-condition runs with a parsed trace (1,908 runs), the denominators for tool use.
Its columns are `benchmark`, `task_id`, `model` and `replicate`.

`galaxy_tool_use.csv` has one row for each traced Galaxy run and installed tool the run called, whether or not the job succeeded, and one row for each run that called a user-defined tool (UDT).
Its columns are the four run columns, `tool_id` (the Tool Shed identifier without its version, a built-in identifier such as `Cut1`, or `UDT`) and `kind` (`installed` or `udt`).

`run_execution_errors.csv` has one row per run with execution-error records (3,791 of the 3,840 scored runs). It comes from sheet `abc_runs` of `manuscript_material/on_demand/Source_Data_OD_Fig5.xlsx` in the archive, plus the 24 host-read removal runs, which the archive extracts with the same rules (`figures/wf003_abc_runs.csv`):

| Column | Meaning |
| --- | --- |
| benchmark, task_id, model, track, replicate | Run identifiers, as in `run_scores.csv` |
| failed_shell_commands | Shell commands that failed, not counting a silent exit code 1 |
| galaxy_jobs_in_error_state | Galaxy jobs of the run that ended in the error state (0 for custom-code runs) |

`bixbench_failure_causes.csv` has one row per incorrect BixBench-Verified-50 run (151 runs), from the run-level failure audit (`analysis_reports/galaxy_improvement_20260924/v2_trace_friction/ledger.json` in the archive).
The 4 bix-43-q2 runs that only the results site grades incorrect were never audited. They take the task-level audit's cause, `EVALUATOR` (the archive's `individual_error_analysis.md`).
The export checks that every incorrect run in `run_scores.csv` has exactly one row.
Only the cause codes are exported; the audit's answer and note fields are not.

| Column | Meaning |
| --- | --- |
| benchmark, task_id, model, track, replicate | Run identifiers, as in `run_scores.csv` |
| primary_cause | `RIGOR` (no answer validation), `KNOWLEDGE` (wrong biological or statistical concept), `PLATFORM` (a Galaxy tool, wrapper or job gave the wrong result), `HARNESS` (no answer submitted), `SPEC` (under-specified task or reference) or `EVALUATOR` (scorer rejected a valid answer) |
| secondary_cause | A second contributing cause, with the same codes; empty when there is none |
| confidence | The auditor's confidence in the primary cause: `high`, `moderate`, `mixed` or `unresolved`; empty for the task-level rows |
| cause_source | `run-level audit`, or `task-level audit` for runs regraded incorrect after it |

`run_tokens_actions.csv` has one row per scored run (3,840 runs), joining two archive tables: `manuscript_narrative/original_layout/analysis/token_run_observations.csv` for tokens and sheet `abf_runs` of `manuscript_material/on_demand/Source_Data_OD_Fig6.xlsx` for actions.
Some counts are empty, mostly for runs without a parsed trace: 14 runs have no token count, 15 no cached count and 12 no action count.

| Column | Meaning |
| --- | --- |
| benchmark, task_id, model, track, replicate | Run identifiers, as in `run_scores.csv` |
| input_tokens | Input tokens over the run, including cached context |
| cached_input_tokens | The part of `input_tokens` read from the prompt cache |
| actions | Tool calls by the agent: shell commands, Galaxy interface calls, web searches or fetches, file reads, writes and edits |

`galaxy_interface_calls.csv` has one row per traced Galaxy run and Galaxy interface function the run called (9,045 rows), summed from the archive's call records.
It covers 1,812 of the 1,908 runs in `galaxy_traced_runs.csv`; the other 96 (95 DeepSeek V4 Pro, 1 GPT-5.6 Luna) made no Galaxy interface call.

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

`compbiobench_task_domains.csv` gives the domain of each of the 100 CompBioBench tasks, as labelled by the benchmark (`CompBio/compBio_overview_audit.json` in the archive); its columns are `task_id` and `domain`.

`galaxy_run_steps.csv` lists the analysis steps that ran as Galaxy jobs in each traced Galaxy run (5,489 rows), from the archive's call records: one row per installed tool the run executed and one row named `UDT` when the run executed any user-defined tool.
Its columns are the four run columns of `galaxy_traced_runs.csv` and `step` (a Tool Shed identifier without version, a built-in identifier such as `Cut1`, or `UDT`).
Only requests whose job was created count, unlike `galaxy_tool_use.csv`, which counts every request.

`execution_error_types.csv` counts execution errors by type and by where they occurred, per run (6,238 rows, 11,878 errors), from sheet `abc_every_error` of `manuscript_material/on_demand/Source_Data_OD_Fig5.xlsx`, plus the host-read removal runs (`figures/wf003_abc_every_error.csv`).

| Column | Meaning |
| --- | --- |
| benchmark, task_id, model, track, replicate | Run identifiers, as in `run_scores.csv` |
| channel | `shell command`, `Galaxy job, installed tool` or `Galaxy job, UDT` (a Galaxy job whose tool identifier the run submitted as a UDT) |
| error_type | The error class assigned from the error message, exit code and command (seven classes) |
| errors | Number of errors |

`galaxy_parameter_checks.csv` counts the parameter-check results of the 16,757 installed-tool requests, per benchmark and model.
Its columns are `benchmark`, `model`, `prov_status` (`matched`, `mismatch`, `no_explicit_non_dataset_parameters`, `not_comparable` or `none` when no check was returned), `prov_stage` (`validation`, before the job ran, or `post_run`) and `requests`.

`galaxy_failure_classes.csv` counts the 7,141 failed Galaxy requests of the four primary configurations by failure class and benchmark, from `manuscript_narrative/original_layout/analysis/token_failure_classes.csv`.
Its columns are `benchmark`, `failure_stage` (request rejected before a job ran, job failed during execution, or other), `failure_class` (codes A1–A8, B1–B5, X and Z with a description), `subclass` and `requests`.

`replicate_answer_agreement.csv` has one row per BixBench-Verified-50 and CompBioBench replicate set (1,200 sets: one task × model × condition).
The export compares the submitted answers of the three runs in memory, as text after trimming and lower-casing and with numbers rounded to three significant digits; the answers themselves are not written.

| Column | Meaning |
| --- | --- |
| benchmark, task_id, model, track | Replicate-set identifiers |
| runs | Scored runs in the set (3) |
| distinct_answers | Number of distinct answers among the runs; a missing answer counts as its own value |
| missing_answers | Runs without a recorded answer |

`inspectability_counts.csv` counts what each analysis step leaves for inspection after the run, by condition, from the run-level evidence files (`<benchmark>/analysis/<task>/history_analysis_evidence.json`).
Galaxy steps are Galaxy jobs; custom-code steps are the agent's shell commands that the evidence labels as analysis.
Its columns are `track`, `element` (`command`, `tool_version`, `parameters`, `outputs`, or `history_retrieved` for runs), `unit`, `with_record` and `total`.
Tool Shed identifiers carry the tool version; built-in Galaxy tools take the version of the recorded Galaxy release.
