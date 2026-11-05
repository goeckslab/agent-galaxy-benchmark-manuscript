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

## Website data copy (`data/site/`)

`data/site/` is a verbatim copy of the machine-readable results the benchmark results website publishes (https://goeckslab.github.io/galaxy-agent-benchmark/data/index.json), written by `analysis/fetch_site_data.py`.
Analyses must read these copies, never the live URLs, because the website regenerates its files on every deployment.
Refresh the copy in a pull request of its own, so the diff shows which results changed.

Files keep their paths on the website, so the index's relative URLs still resolve:

| File | Contents |
| --- | --- |
| `data/index.json`, `data/README.md` | The website's index of results files and its documentation of their fields |
| `bixbench/data/results.json` | BixBench-Verified-50: per-item runs and per-experiment accuracy |
| `compbiobench/data/paper_results.json` | CompBioBench: per-item runs and per-replicate official scores |
| `compbiobench/data/public_token_usage.tsv`, `compbiobench/data/public_udt_usage.tsv` | CompBioBench token use and user-defined-tool use, per replicate |
| `iwc/data/results.json`, `iwc/data/token_usage.tsv` | IWC workflow generation (ten items): per-item runs and token use |
| `iwc/long-chain/data/results.json` | IWC multi-step tasks: per-run scores |

`data/site/MANIFEST.csv` records each file's URL, size, SHA-256, fetch date and the server's Last-Modified time.
Its `checksum_source` column says whether the SHA-256 was checked against `index.json`: the four results files were; the index, its README and the usage tables are not listed in it.
`source_commit` is the commit of `goeckslab/galaxy-agent-benchmark` (private) the website was deployed from; the website does not publish it, so it is recorded only after a check (see below).
Run `python analysis/fetch_site_data.py --check` to confirm the local copies still match the manifest.

The committed copy was fetched on 2026-11-05 from a deployment last modified at 2026-10-28 01:15:59 GMT.
Its `source_commit` is `804299a`: the six files that are committed under `site/` in the benchmark repository are byte-identical to that commit, and the CompBioBench results differ from its parent `df07b3e`.
The other three (`bixbench/data/results.json`, `iwc/data/results.json` and `data/index.json`) are generated at deployment and are not committed there.

Rules from the website's `data/README.md` that every analysis of these files must follow:

- BixBench: use `status`, not the historical `raw_status`; exclude experiments with `superseded` metadata from the main comparison.
- CompBioBench: use per-replicate `official_score` (out of 100) for accuracy; `predicted_score` is a prediction, not a score; select main or supplementary model configurations to match the intended figure rather than pooling them.
- IWC: accuracy is `acc`; keep `acc_status` and nulls; `step_score` is a separate metric.
- IWC multi-step tasks: leave runs in `held_reruns` out of every average until rescored; average `acc` over scored runs per task, then over tasks.
- In every benchmark, never treat a missing score as zero.

The files include reference answers.
They are for reporting and plotting, and must not be given to agents taking the benchmark.

### License

`data/site/` is copied from `goeckslab/galaxy-agent-benchmark` under its MIT license, reproduced in `data/site/LICENSE` from commit `804299a`.
That file is copied from the repository, not from the website, so `fetch_site_data.py` does not fetch it and `MANIFEST.csv` does not list it.
The copy also contains questions and answers from the original benchmarks, which keep their own licenses:

- BixBench-Verified-50: Apache 2.0 (Hugging Face dataset `phylobio/BixBench-Verified-50`).
- CompBioBench v1: CC BY 4.0 (Zenodo record 19443186, DOI 10.5281/zenodo.19443186).
- IWC: the workflows are from the Intergalactic Workflow Commission (https://iwc.galaxyproject.org/), where each workflow states its own license; the copy names and links to them.

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
