# Analysis

Code that turns benchmark runs and traces into the numbers and tables used in the paper.

- `fetch_traces.py` downloads traces from the Hugging Face dataset into `traces/` (git-ignored).
- `token_usage.py` computes Galaxy ÷ custom-code token ratios for the main runs (from `data/run_tokens_actions.csv`) and for each BixBench token-optimization round (from `data/token_optimization_rounds.csv`); its outputs feed `figures/sfig_token_*` and `supplement/notes/token_usage.md`.
- `failure_analysis/` holds one write-up per task, named `<task-id>.md`, each ending with trace references.

Rules: every number in the paper traces to a script here or a row in `data/results_manifest.csv`.
Verify agent-reported answers against independent ground truth, not the agent's own conclusion.
