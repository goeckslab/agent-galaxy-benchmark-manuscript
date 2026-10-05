# Figure 5: Galaxy increases analysis inspectability at higher token cost

Four panels that answer the questions of Results section 4 of `manuscript/outline.md`.
The legend draft is in [legend.md](legend.md).

- **a**: accuracy against median input tokens per run, one point per replicate, model and condition; at the same accuracy, Galaxy used 3.4–6.6 times more input tokens on the same task, 3.0 times counting only uncached input.
- **b**: incorrect runs used no more input tokens than correct runs of the same task and model, in either condition, so the cost is not spent on failed attempts.
- **c**: input tokens follow the number of actions; Galaxy runs took 2.5 times more actions and used 1.9 times more input tokens per action.
- **d**: finding tools makes up about half of the requests to Galaxy and of the text Galaxy sends back.

What the extra tokens buy, a record of every analysis step, is described in the text; its counts are in `source_data.csv` as `text` rows.

## Files

- `make_figure.py`: computes the statistics, draws the figure and writes every file below.
- `fig5_token_cost.pdf` (run-level dots rasterized at 600 dpi), `.png` (600 dpi, RGB) and `.svg` (editable text).
- `source_data.csv`: every plotted summary value, ratio, interval and *P* value, one row each.
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the data/ tables change
python figures/fig5_token_cost/make_figure.py
```

The figure reads `data/run_scores.csv`, `run_tokens_actions.csv`, `galaxy_interface_calls.csv`, `galaxy_tool_lookup.csv` and `inspectability_counts.csv`, which `data/README.md` describes.
The statistics take about seven seconds and are reproducible: the random seed is fixed (20261002).

## Statistics

- Input tokens include cached context; uncached input is input tokens minus cached tokens.
- Ratios are geometric means over paired cells (task × model, medians over replicate runs) or over replicate sets (panel b), with 95% percentile cluster-bootstrap intervals and paired cluster sign-flip tests (200,000 draws), Holm-adjusted within each panel.
- The uncached ratio uses its own random stream, so the draws of the other panels are unchanged.

## Style

The figure is 180 × 128 mm, with Arial at 5–7 pt and 8 pt bold panel letters.
Panel a colours the models (Paul Tol muted green, purple, sand and indigo) and keeps the condition in the marker shape; the other panels use vermillion for custom code and blue for Galaxy.
