# Figure 1: benchmark overview

Study design (a) and the isolated execution pipeline applied to every run (b), drawn as pictograms with minimal text.
Definitions live in the legend draft, [legend.md](legend.md).

## Files

- `make_figure.py`: draws the figure and writes every file below.
- `fig1_benchmark_overview.pdf`: vector, with Arial embedded as TrueType.
- `fig1_benchmark_overview.png`: 600 dpi, RGB.
- `fig1_benchmark_overview.svg`: editable text, for composing panels in Inkscape.
- `source_data.csv`: every plotted value with its kind (`data`, `design`, `derived` or `illustrative`) and source.
- `legend.md`: figure legend draft.

## Regenerate

```bash
python figures/fig1_benchmark_overview/make_figure.py
```

## Where the numbers come from

The figure plots study-design constants, not results: tasks per benchmark, four model configurations, two execution conditions and three replicate runs.
`data/results_manifest.csv` has no rows yet, so these values are set in `make_figure.py` and were checked against the benchmark repository at `paulocilasjr/Galaxy_benchmark@b66d91a`.
`source_data.csv` names the file behind each value.
The accuracy gauge, the interface-calls bars and the failure-cause bar are glyphs, not results, and are labelled `illustrative`.

## Style

The figure is 180 mm wide, with Arial at 5–7 pt and 8 pt bold panel letters.
Colours come from the Okabe-Ito palette: vermillion is custom code and blue is Galaxy, repeated by marker shape (square and circle) for greyscale.
Where Arial is not installed, the script uses Liberation Sans, which has the same metrics.

## Open items

- The Fig. 1 legend in `manuscript/results.qmd` still describes the earlier three-panel draft and should be replaced by `legend.md`.
- Panel a's title uses "GalaxyBench", one of the naming questions listed in `manuscript/outline.md`.
- GPT-5.6 Luna's max reasoning effort is confirmed by runtime records, except in 900 CompBioBench custom-code runs (GPT-5.5, GPT-5.6 Sol and GPT-5.6 Luna) that have no runtime record.
