# Analysis

Code that turns benchmark runs and traces into the numbers and tables used in the paper.

- `fetch_traces.py` downloads traces from the Hugging Face dataset into `traces/` (git-ignored).
- `fetch_site_data.py` copies the results website's machine-readable data (per-run results, scores and token use for every benchmark) into `data/site/`, checks it against the website's published checksums, and records each file in `data/site/MANIFEST.csv`; new analyses should read these copies.
- `fetch_site_token_totals.py` fetches main-run token totals per benchmark, model and condition from the results website into `data/site_token_totals.csv`; all token totals in the paper come from the website.
- `token_usage.py` computes Galaxy ÷ custom-code token ratios for the main runs (from `data/site_token_totals.csv`) and for each BixBench token-optimization round (from `data/token_optimization_rounds.csv`); its outputs feed `figures/sfig_token_*` and `supplement/notes/token_usage.md`.
- `site_data.py` loads `data/site/` as tidy tables, one per benchmark, applying the website's rules (use `status`, drop superseded experiments and held reruns, never treat a missing score as zero) and the paper's model and condition names.
- `accuracy.py` computes accuracy per benchmark, model and condition, plus all models together, into `data/accuracy_by_model.csv`, and a per-benchmark summary across models into `data/accuracy_summary.csv`; it feeds `figures/sfig_accuracy_by_model`.
- `failure_analysis/` holds one write-up per task, named `<task-id>.md`, each ending with trace references.

Rules: every number in the paper traces to a script here or a row in `data/results_manifest.csv`.
Verify agent-reported answers against independent ground truth, not the agent's own conclusion.
