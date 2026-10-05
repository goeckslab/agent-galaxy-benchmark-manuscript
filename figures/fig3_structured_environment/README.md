# Figure 3: Galaxy provides a structured environment for agent analyses

Six panels that answer the questions of Results section 2 of `manuscript/outline.md`, read left to right and top to bottom.
The legend draft is in [legend.md](legend.md).

- **a**: runs correct by task domain in both conditions; no domain differs.
- **b**: how each Galaxy run used Galaxy (installed tools, UDTs, both or neither), by benchmark and model.
- **c**: execution errors by type and by where they occurred: installed-tool jobs, UDT jobs, and shell commands in Galaxy and custom-code runs.
- **d**: runs ending correct by the number of execution errors in the run; at equal error counts Galaxy runs recover more often.
- **e**: parameter checks on installed-tool requests; 20% of requests had a mismatch caught before the job ran.
- **f**: failed Galaxy requests grouped by the change that would most likely prevent them.

## Files

- `make_figure.py`: computes the statistics, draws the figure and writes every file below.
- `fig3_structured_environment.pdf`, `.png` (600 dpi, RGB) and `.svg` (editable text).
- `source_data.csv`: every plotted value, interval, *P* value, fitted coefficient and count, one row each.
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the data/ tables change
python figures/fig3_structured_environment/make_figure.py
```

The figure reads `data/run_scores.csv`, `run_execution_errors.csv`, `execution_error_types.csv`, `compbiobench_task_domains.csv`, `galaxy_run_steps.csv`, `galaxy_traced_runs.csv`, `galaxy_parameter_checks.csv` and `galaxy_failure_classes.csv`, which `data/README.md` describes.
The statistics take about six seconds and are reproducible: the random seed is fixed (20261002).

## Definitions and statistics

- Execution errors are failed shell commands, not counting a silent exit code 1, plus Galaxy jobs that ended in the error state; error types follow each error's message, exit code and command.
- A Galaxy job error is a UDT error when its tool identifier is one the run submitted as a user-defined tool.
- Panel d fits a binomial logistic regression of ending correct on ln(1 + errors) per condition with 2,000-resample cluster-bootstrap bands; its annotated comparison averages the Galaxy minus custom-code difference over four error bins, weighted by their share of runs with errors, and was chosen after inspecting the bins (unadjusted, +2.3 points, *P* = 0.07).
- Panel f groups the failure classes of the request and job records (A1–A8, B1–B5, X, Z) by the change that would most likely prevent them; the grouping is ours and is listed in `source_data.csv`.
- Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples); *P* values come from paired cluster randomization tests (200,000 draws), Holm-adjusted within each panel.

## Style

The figure is 180 × 170 mm, with Arial at 5–7 pt and 8 pt bold panel letters.
Every bar segment in panels b, c and e carries its share: inside the segment when it fits, otherwise outside with a short leader line.
Vermillion is custom code and blue is Galaxy; error types take Paul Tol's light scheme, which avoids both.
