# Analysis

Code that turns benchmark runs and traces into the numbers and tables used in the paper.

- `fetch_traces.py` downloads traces from the Hugging Face dataset into `traces/` (git-ignored).
- `fetch_site_token_totals.py` fetches main-run token totals per benchmark, model and condition from the results website into `data/site_token_totals.csv`; all token totals in the paper come from the website.
- `token_usage.py` computes Galaxy ÷ custom-code token ratios for the main runs (from `data/site_token_totals.csv`) and for each BixBench token-optimization round (from `data/token_optimization_rounds.csv`); its outputs feed `figures/sfig_token_*` and `supplement/notes/token_usage.md`.
- `replicate_consensus.py` estimates how much a majority vote across replicate runs, or a step that picks a correct replicate, would change accuracy on BixBench-Verified-50 and CompBioBench; it writes `data/replicate_consensus.csv` and `data/bixbench_causes_by_agreement.csv`.
- `failure_analysis/` holds one write-up per task, named `<task-id>.md`, each ending with trace references.

Rules: every number in the paper traces to a script here or a row in `data/results_manifest.csv`.
Verify agent-reported answers against independent ground truth, not the agent's own conclusion.
