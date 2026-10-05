# Figure 3: Galaxy records trace most failures beyond the workbench

Four panels that follow the argument of Results section 2: where runs fail, how often they recover, and why.
The legend draft is in [legend.md](legend.md).

- **a**: Galaxy has fewer replicate sets that fail in only one of three runs; sets that fail in all three runs are equally common.
- **b**: runs with execution errors end correct more often in Galaxy, at equal error counts.
- **c**: in BixBench-Verified-50, single failures mostly lack answer validation, and failures in all three runs mostly trace to the benchmark's specification or scoring; Galaxy itself caused 3 of 170 incorrect runs.
- **d**: with a majority vote, the advantage of panel a disappears, because it came from sets with one incorrect run.

## Files

- `make_figure.py`: computes the statistics, draws the figure and writes every file below.
- `fig3_failure_sources.pdf`: vector, with Arial embedded as TrueType.
- `fig3_failure_sources.png`: 600 dpi, RGB.
- `fig3_failure_sources.svg`: editable text.
- `source_data.csv`: every plotted value, interval, *P* value and fitted coefficient, one row each.
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the data/ tables change
python figures/fig3_failure_sources/make_figure.py
```

The figure reads `data/run_scores.csv`, `data/run_execution_errors.csv` and `data/bixbench_failure_causes.csv`, which `data/README.md` describes.
The statistics take about eight seconds and are reproducible: the random seed is fixed (20261002).

## Definitions

- A replicate set is one task × model × condition: three runs.
- A run is incorrect when it is not accepted (BixBench-Verified-50, CompBioBench) or, for IWC, below 0.99 output agreement, as in Figure 2b.
- Execution errors are failed shell commands, not counting a silent exit code 1, plus Galaxy jobs that ended in the error state.
- Panel c maps each primary cause code of the run-level failure audit to one category: `RIGOR` to no answer validation, `KNOWLEDGE` to lacking biological knowledge, `PLATFORM` to not able to use Galaxy, `HARNESS` to no answer submitted, and `SPEC`, `EVALUATOR` and `CONTRACT` to benchmark specification or scoring.

## Statistics

- Error bars and bands are 95% percentile cluster-bootstrap intervals, resampling BixBench source capsules or tasks within each benchmark (20,000 resamples; 2,000 for the fitted curves of panel b).
- Panels a and d use two-sided paired randomization tests that flip the sign of cluster-level differences (200,000 draws), Holm-adjusted within the panel.
- Panel b fits a binomial logistic regression of ending correct on ln(1 + errors) per condition.
  Its annotated comparison averages the Galaxy minus custom-code difference over four error bins (1–2, 3–5, 6–10, >10), weighted by each bin's share of runs with errors, and tests it by swapping the condition labels of whole clusters (200,000 draws).
  This adjustment was chosen after inspecting the bins; the unadjusted difference (+2.3 points, *P* = 0.07) is in the legend and `source_data.csv`.
- Error counts are outcomes of each run, so panel b shows an association, not a causal effect of recovery.

## Style

The figure is 180 × 128 mm, with Arial at 5–7 pt and 8 pt bold panel letters.
Vermillion is custom code and blue is Galaxy, as in every figure; custom code is always shown first.
Models keep the Paul Tol muted hues of Figure 2.
Cause colours avoid the condition colours: dark grey for no answer validation, yellow for biological knowledge, reddish purple for Galaxy, light grey for no answer, and bluish green for the benchmark.
Where Arial is not installed, the script uses Liberation Sans, which has the same metrics.
