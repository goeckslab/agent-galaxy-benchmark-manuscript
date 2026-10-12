# Figure 2: Galaxy matches agent performance with custom code

Four panels that follow the argument of Results section 1.
The legend draft is in [legend.md](legend.md).

- **a**: the four model configurations reach the same accuracy in both conditions.
- **b**: Galaxy solves at least as many replicate sets in all three runs.
- **c**: accuracy by benchmark and model in the Galaxy condition, with each replicate shown as a dot.
- **d**: the installed Galaxy tools behind that accuracy, per model.

## Files

- `make_figure.py`: computes the statistics, draws the figure and writes every file below.
- `fig2_performance.pdf`: vector, with Arial embedded as TrueType.
- `fig2_performance.png`: 600 dpi, RGB.
- `fig2_performance.svg`: editable text.
- `source_data.csv`: every plotted value, interval, *P* value and test statistic, one row each.
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the data/ tables change
python figures/fig2_performance/make_figure.py
```

The figure reads `data/run_scores.csv`, `data/galaxy_traced_runs.csv` and `data/galaxy_tool_use.csv`, which `data/README.md` describes.
The statistics take about five seconds and are reproducible: the random seed is fixed (20261002).

## Statistics

- Error bars are 95% percentile cluster-bootstrap intervals (20,000 resamples), resampling BixBench source capsules or tasks, so the three replicate runs of a task are never treated as independent.
- *P* values come from two-sided paired randomization tests that flip the sign of cluster-level differences (200,000 draws; exact enumeration for IWC, which has nine clusters), with Holm adjustment within each panel.
- The model × benchmark test in panel c ranks the four models within each task and permutes whole clusters between benchmarks (100,000 permutations).
- An IWC run counts as correct at ≥ 0.99 output agreement; `source_data.csv` repeats panel b at 0.95 and 1.0.

## Style

The figure is 180 mm wide, with Arial at 5–7 pt and 8 pt bold panel letters.
Vermillion is custom code and blue is Galaxy, as in every figure; custom code is always shown first.
Models take Paul Tol's muted hues (green, purple, olive, wine), which avoid the condition colours and pass a colour-vision-deficiency check.
Where Arial is not installed, the script uses Liberation Sans, which has the same metrics.
