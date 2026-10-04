# Analysis

Code that turns benchmark runs and traces into the numbers and tables used in the paper.

- `fetch_traces.py` downloads traces from the Hugging Face dataset into `traces/` (git-ignored).
- `failure_analysis/` holds one write-up per task, named `<task-id>.md`, each ending with trace references.

Rules: every number in the paper traces to a script here or a row in `data/results_manifest.csv`.
Verify agent-reported answers against independent ground truth, not the agent's own conclusion.
