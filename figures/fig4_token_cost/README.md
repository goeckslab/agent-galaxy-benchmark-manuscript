# Figure 4: Galaxy trades input tokens for analysis provenance

Four panels that follow the argument of Results section 3: what Galaxy costs, what does not explain the cost, and what does.
The legend draft is in [legend.md](legend.md).

- **a**: at the same accuracy, Galaxy runs used 3.4–6.6 times more input tokens than custom-code runs of the same task.
- **b**: incorrect runs used no more input tokens than correct runs of the same task and model, in either condition.
- **c**: input tokens follow the number of actions; Galaxy runs took more actions, and each action carried more input tokens.
- **d**: finding tools (searching and reading tool descriptions) makes up about half of the requests to Galaxy and of the text Galaxy sends back.

## Files

- `make_figure.py`: computes the statistics, draws the figure and writes every file below.
- `fig4_token_cost.pdf`: vector, with Arial embedded as TrueType; the run-level dots of panels b and c are rasterized at 600 dpi to keep the file small.
- `fig4_token_cost.png`: 600 dpi, RGB.
- `fig4_token_cost.svg`: editable text.
- `source_data.csv`: every plotted summary value, interval, ratio and *P* value, one row each; run-level values are in `data/run_tokens_actions.csv`.
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the data/ tables change
python figures/fig4_token_cost/make_figure.py
```

The figure reads `data/run_scores.csv`, `data/run_tokens_actions.csv`, `data/galaxy_interface_calls.csv` and `data/galaxy_tool_lookup.csv`, which `data/README.md` describes.
The statistics take about six seconds and are reproducible: the random seed is fixed (20261002).

## Definitions

- Input tokens include cached context: everything the model read, counted at every step.
- Actions are the agent's tool calls: shell commands, Galaxy interface calls, web searches or fetches, and file reads, writes and edits.
- A run is correct when accepted or, for IWC, at ≥ 0.99 output agreement, as in Figures 2b and 3.
- A paired cell is one task × model, with the median over its replicate runs in each condition.

## Statistics

- Ratios are geometric means of Galaxy over custom-code values (panels a and c) or of incorrect over correct runs within a replicate set (panel b), over paired cells.
- Intervals are 95% percentile cluster-bootstrap intervals, resampling BixBench source capsules or tasks within each benchmark (20,000 resamples; 2,000 for the accuracy and median intervals of panel a).
- *P* values come from two-sided paired randomization tests that flip the sign of cluster-level log ratios (200,000 draws).
  Holm adjustment runs across the four models in panels a and c, whose pooled rows are single tests, and in panel b across the eight model × condition ratios and, separately, the two pooled ratios.
- Panel a pools only BixBench-Verified-50 and CompBioBench, as Figure 2a does, so accuracy and tokens describe the same runs.
- Panel c joins medians within bins of actions (bins with at least ten runs) instead of fitting lines, because the relation curves on log axes.

## Style

The figure is 180 × 128 mm, with Arial at 5–7 pt and 8 pt bold panel letters.
Vermillion squares are custom code and blue circles are Galaxy, as in every figure; custom code is always shown first.
In panel b, light boxes are correct runs and solid boxes incorrect runs.
In panel d, finding tools is the only coloured segment, because it is the part of the cost an interface change could reduce.
Where Arial is not installed, the script uses Liberation Sans, which has the same metrics.
