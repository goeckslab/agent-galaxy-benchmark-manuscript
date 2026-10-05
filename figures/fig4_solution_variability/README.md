# Figure 4: Task solution variability is model-dependent

Four panels that answer the questions of Results section 3 of `manuscript/outline.md`.
The legend draft is in [legend.md](legend.md).

- **a**: the 15 installed Galaxy tools used in the most Galaxy runs, with each model's share and its use of user-defined tools (UDTs).
- **b**: share of replicate sets whose three runs gave the same answer, by model, in both conditions, per benchmark and pooled; models differ in both environments, so variability is a property of the model rather than of Galaxy.
- **c**: similarity of each task's run trajectories (the Galaxy tools of the three replicate runs) against the share of its runs that were correct; no relation across tasks, and none when models are compared on the same task, so trajectory diversity is neutral for accuracy.
- **d**: in replicate sets with a wrong answer, whether the error was random (answers differ between replicates) or systematic (the same wrong answer in all three), by task difficulty; systematic errors dominate on the hardest tasks.

## Files

- `make_figure.py`: computes the statistics, draws the figure and writes every file below.
- `fig4_solution_variability.pdf`, `.png` (600 dpi, RGB) and `.svg` (editable text).
- `source_data.csv`: every plotted value, interval, *P* value and count, one row each; rows marked `text` hold results cited in the Results but not plotted (trajectory similarity by model and benchmark, and accuracy by trajectory-similarity bin).
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the data/ tables change
python figures/fig4_solution_variability/make_figure.py
```

The figure reads `data/run_scores.csv`, `galaxy_tool_use.csv`, `galaxy_run_steps.csv`, `galaxy_traced_runs.csv` and `replicate_answer_agreement.csv`, which `data/README.md` describes.
The permutation tests take about a minute; the random seed is fixed (20261002).

## Definitions and statistics

- A run trajectory is the set of analysis steps that ran as Galaxy jobs: the installed tools plus one step for any UDT, because agents name each UDT anew.
  Trajectories are measured in the Galaxy condition only: custom-code commands are free text with no structured record of tools, so answers are the measure common to both conditions.
- Trajectory similarity is the mean pairwise Jaccard index of the three replicate trajectories of a task and model.
- Answers are compared as text after trimming and lower-casing, with numbers rounded to three significant digits; the export writes only the number of distinct answers per set.
- *P* values in panel b test a model effect within each condition by permuting model labels within tasks (20,000 permutations); Spearman correlations in panel c use permutation tests within benchmarks across tasks and within tasks when models are compared.
- Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples).

## Style

The figure is 180 × 131 mm, with Arial at 5–7 pt and 8 pt bold panel letters.
Models take Paul Tol's muted green, purple, sand and indigo; in panel b, squares are custom code and circles Galaxy.
Benchmarks in panel c take Okabe–Ito orange and sky blue and a light pink for IWC; errors in panel d are bluish green (random) and reddish purple (systematic).
