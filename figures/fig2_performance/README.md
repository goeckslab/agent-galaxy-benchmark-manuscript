# Figure 2: Agents maintain bioinformatics accuracy when operating through Galaxy

Four panels that answer the questions of Results section 1 of `manuscript/outline.md`.
The legend draft is in [legend.md](legend.md).

- **a**: accuracy in each benchmark, by model and condition, with each replicate as a dot; no model differs between Galaxy and custom code on any benchmark.
- **b**: Galaxy minus custom code by benchmark, for runs correct and for replicate sets with all three runs correct; the largest gain is in consistency on the Galaxy-derived IWC tasks, but no difference is significant.
- **c**: correct runs of three for each task and model, custom code against Galaxy; the same tasks succeed or fail in both conditions (509 of 636 pairs on the diagonal).
- **d**: the primary cause of each incorrect BixBench-Verified-50 run, by how many runs of its set failed; single failures are mostly unchecked answers, failures in all three runs mostly benchmark specification or scoring.

## Files

- `make_figure.py`: computes the statistics, draws the figure and writes every file below.
- `fig2_performance.pdf`: vector, with Arial embedded as TrueType.
- `fig2_performance.png`: 600 dpi, RGB.
- `fig2_performance.svg`: editable text.
- `source_data.csv`: every plotted value, interval and *P* value, one row each.
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the data/ tables change
python figures/fig2_performance/make_figure.py
```

The figure reads `data/run_scores.csv` and `data/bixbench_failure_causes.csv`, which `data/README.md` describes.
The statistics take about four seconds and are reproducible: the random seed is fixed (20261002).

## Statistics

- A run is correct when accepted (BixBench-Verified-50, CompBioBench) or, for IWC, at ≥ 0.99 output agreement; panel a shows IWC as mean agreement.
- Error bars and intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples), resampling BixBench source capsules or tasks within each benchmark.
- *P* values come from two-sided paired randomization tests that flip the sign of cluster-level differences (200,000 draws; exact enumeration for IWC), Holm-adjusted within each panel (12 comparisons in a, 6 in b).

## Style

The figure is 180 × 166 mm, with Arial at 5–7 pt and 8 pt bold panel letters.
Vermillion is custom code and blue is Galaxy, as in every figure; custom code is always shown first.
Panel c shades counts on a logarithmic grey scale and outlines the cells where both conditions had the same count.
Where Arial is not installed, the script uses Liberation Sans, which has the same metrics.
