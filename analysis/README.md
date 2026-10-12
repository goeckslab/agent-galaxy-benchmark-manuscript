# Analysis

Code that turns benchmark runs and traces into the numbers and tables used in the paper.

- `fetch_traces.py` downloads traces from the Hugging Face dataset into `traces/` (git-ignored).
- `fetch_site_token_totals.py` fetches main-run token totals per benchmark, model and condition from the results website into `data/site_token_totals.csv`; all token totals in the paper come from the website.
- `token_usage.py` computes Galaxy ÷ custom-code token ratios for the main runs (from `data/site_token_totals.csv`) and for each BixBench token-optimization round (from `data/token_optimization_rounds.csv`); its outputs feed `figures/sfig_token_*` and `supplement/notes/token_usage.md`.
- `replicate_consensus.py` analyses errors across replicate runs on all three benchmarks: how much a majority vote, or a step that picks a correct replicate, would change accuracy; whether errors repeat across replicates; and how incorrect runs relate to failure causes (BixBench-Verified-50), execution errors and task domains (CompBioBench). It writes four tables to `data/`, described in `data/README.md`.
- `failure_analysis/` holds one write-up per task, named `<task-id>.md`, each ending with trace references.

Rules: every number in the paper traces to a script here or a row in `data/results_manifest.csv`.
Verify agent-reported answers against independent ground truth, not the agent's own conclusion.
