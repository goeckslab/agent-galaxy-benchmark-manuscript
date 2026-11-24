# Revised-outline verification

Derived evidence for [the project evaluation](../../supplement/notes/project_verification_2026-11-17.md).
These tables supplement the existing package; they do not change its manuscript, figures, or run manifest.

Recompute the offline tables from the repository root:

```powershell
.venv/Scripts/python.exe analysis/verify_outline_claims.py
```

The script checks frozen-source hashes through the shared loader, reconstructs the revised three-benchmark cohort, reconciles audit denominators, recomputes paired intervals and repeatability diagnostics, and checks archived genomic and RNA-seq data.
It writes `inputs.csv` with normalized source fingerprints and `verification.json` with check metadata.
When the local `iwc-multistep-snapshots` branch exists, its results and pooled intervals are also compared without checking out the branch.

| Tables | Content |
|---|---|
| `performance.csv` | Benchmark-specific endpoints and paired intervals; reconstructed CompBioBench matches are separate from official points |
| `multistep_runs.csv`, `multistep_by_task.csv` | The multi-step cohort and equal-task summaries |
| `multistep_leave_one_out.csv`, `multistep_leave_one_out_by_model.csv`, `trial_run_descriptive.csv` | Explicitly exploratory sensitivity (pooled and per model; `none` reproduces `data/accuracy_by_model.csv`) and trial-run descriptions; not recommendations to exclude runs |
| `error_denominators.csv`, `error_totals.csv`, `error_subcategories.csv` | Main-cohort counts restricted to the three paper benchmarks, with logged-run denominators |
| `audit_labels.csv`, `trace_crosswalk.csv`, `history_visibility.csv` | Counts of existing classifications; no independent adjudication of cause labels |
| `history_lookup_errors.csv` | Missing or unusable history context, including supplied histories the interface could not use |
| `replicate_diagnostics.csv` | Separate correctness-based diagnostics and answer-string voting; explicit weighting for multi-step outputs |
| `token_costs.csv`, `bixbench_tokens_by_outcome.csv`, `bixbench_tokens_by_model.csv` | Recorded token totals, coverage, elapsed time, outcome-conditioned means, and BixBench Galaxy-to-custom-code ratios per model from the frozen release |

The public header example has a separate, network-dependent check:

```powershell
.venv/Scripts/python.exe analysis/check_bixbench_header.py
```

It reads the original measurements in three public Galaxy histories and the filtered tables and line-count outputs in the two incorrect runs, then writes `header_history_check.csv` and `header_history_sources.json`.
The correct comparison run used a different analysis route; its input measurements independently reproduce its accepted answer.
Public responses are cached in the ignored `.venv/qa/header-history-public-cache/`; use `--refresh` for a fresh retrieval.
The source fingerprints identify what was read; they do not substitute for a durable public archive.

For the evaluation, the original execution classifier was also rerun from the private cached event logs into an ignored temporary directory, and its three output tables were compared with `data/error_taxonomy/`.
That reproduction confirms deterministic counts, not the scientific validity of the category definitions.
No private trace content is included here.
