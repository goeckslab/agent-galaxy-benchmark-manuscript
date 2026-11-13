# Analysis

Code that turns benchmark runs and traces into the numbers and tables used in the paper.

## Brief Communication package

These scripts rebuild the tables, figures and supplementary PDF in `figures/benchmark_results_summary/` from pinned sources, offline.
The [package README](../figures/benchmark_results_summary/README.md) gives the reproduction commands and links the build journal.

- `build_benchmark_summary.py` writes every figure's tables and, unless run with `--tables-only`, draws the nine plates; it stops if its accuracy values differ from `data/accuracy_by_model.csv` (`accuracy.py`).
- `benchmark_records.py` reads `data/site/` through `site_data.py`, the shared loader, and adds the per-run fields the package needs.
- `extract_rerun_report.py` transcribes the authors' rerun report into `s2_reruns/dataset/report_runs.csv` and `report_effects.csv`; the PDF is held by the authors, and without it the build uses the committed transcription.
- `check_workflow_output.py` compares the agent's and the curated workflow's yeast DESeq2 tables for Supplementary Fig. 1.
- `build_results_manifest.py` writes `data/results_manifest.csv`, one row per primary run.
- `assemble_supplement.py` places the seven supplementary vector plates with their canonical legends in `supplementary_figures.pdf`.
- `summary_provenance.py` checks every source checksum and, with `--inventory`, rewrites the output inventory.
- `verify_benchmark_package.py` checks the printed artwork, numerical reconciliations, source data and output inventory; `--with-manuscript` also checks the three rendered manuscript formats.
- `catalog_benchmark_pages.py` recrawls the results website by following links, to refresh the page catalogue for a new edition.
- `fetch_verified50_key.py` is an optional cross-check against the gated Verified-50 deposit (needs `HF_TOKEN`); its outputs are git-ignored.

## Data access and shared analyses

- `fetch_traces.py` downloads traces from the Hugging Face dataset into `traces/` (git-ignored).
- `fetch_site_data.py` copies the results website's machine-readable data (per-run results, scores and token use for every benchmark) into `data/site/`, checks it against the website's published checksums, and records each file in `data/site/MANIFEST.csv`; new analyses should read these copies.
- `fetch_site_token_totals.py` fetches main-run token totals per benchmark, model and condition from the results website into `data/site_token_totals.csv`; all token totals in the paper come from the website.
- `token_usage.py` computes Galaxy ÷ custom-code token ratios for the main runs (from `data/site_token_totals.csv`) and for each BixBench token-optimization round (from `data/token_optimization_rounds.csv`); its outputs feed `figures/sfig_token_*` and `supplement/notes/token_usage.md`.
- `site_data.py` loads `data/site/` as tidy tables, one per benchmark, applying the website's rules (use `status`, drop superseded experiments and held reruns, never treat a missing score as zero) and the paper's model and condition names.
- `accuracy.py` computes accuracy per benchmark, model and condition, plus all models together, into `data/accuracy_by_model.csv`, and a per-benchmark summary across models into `data/accuracy_summary.csv`; it feeds `figures/sfig_accuracy_by_model`.
- `failure_analysis/` holds one write-up per task, named `<task-id>.md`, each ending with trace references.

Rules: every number in the paper traces to a script here or a row in `data/results_manifest.csv`.
Verify agent-reported answers against independent ground truth, not the agent's own conclusion.
