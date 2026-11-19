# Error taxonomy tables

Tables behind `manuscript/error_taxonomy.md`, which maps the errors agents made into two categories, knowledge and execution environment, and two groups, recorded in successful runs and prevented the correct answer.

| File | One row per | Written by |
|---|---|---|
| `execution_errors.csv` | benchmark × condition × outcome × source (shell or Galaxy call) × error type: events and runs with at least one event, with category, subcategory and, for Galaxy calls, stage | `analysis/error_taxonomy.py` |
| `execution_subcategories.csv` | benchmark (and `All`) × condition × outcome × subcategory: events, runs with at least one event (each run counted once), runs with a log | `analysis/error_taxonomy.py` |
| `run_summary.csv` | benchmark × condition × outcome: runs, runs with a log, shell commands, Galaxy calls, runs with an execution error and errors, with and without the interface's pre-submission parameter check | `analysis/error_taxonomy.py` |
| `iwc_multistep_reasons.csv` | failed IWC multi-step result (573): scorer reasons and the primary reason | `analysis/iwc_failed_results.py` |
| `iwc_multistep_reason_counts.csv` | the same, as long-format count tables | `analysis/iwc_failed_results.py` |
| `bixbench_agent_failures_traced.csv` | BixBench incorrect run not attributed to the benchmark by the audit (49): category, subcategory, a paraphrase of the evidence, whether the mistake is visible in the Galaxy history, confidence and correct sibling runs | classified by reading each run's event log |
| `iwc_multistep_page_causes.csv` | cause statement in the error analyses of the ten IWC multi-step task pages (92): group, category, subcategory, runs named | classified from the archived task pages |
| `iwc_workflow_explanations.csv` | published explanation of the IWC workflow-task scores below 1 (24 labels): category, subcategory, runs per condition | classified from the archived explanation page |

`error_taxonomy.py` reads the private run event logs from the git-ignored cache `traces/codex_events/`; its outputs hold counts only.
The three classified tables were prepared with Claude Code and await author review; their evidence columns paraphrase the logs or pages and quote no trace text.
