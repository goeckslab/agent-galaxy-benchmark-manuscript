# Figure 1: Study design and isolated execution pipeline

Supports the study design (Results section 1 of `manuscript/outline.md`).
The legend draft is in [legend.md](legend.md).

## Files

- `make_figure.py`: the drawing code of the run archive's `figures/make_fig1_a.py`, copied unchanged; it replays the values that script computed and writes every file below.
- `fig1_benchmark_overview.pdf`, `.png` (600 dpi, RGB) and `.svg` (editable text).
- `source_data.csv`: every plotted value, interval, *P* value and count, one row each (the archive's `fig1_a_source_data.csv`).
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the archive changes
python figures/fig1_benchmark_overview/make_figure.py
```

## Provenance

Every estimate, interval and *P* value was computed by `figures/make_fig1_a.py` in the run archive, [paulocilasjr/Galaxy_benchmark@0dbf3f4](https://github.com/paulocilasjr/Galaxy_benchmark/tree/0dbf3f443b83a91322098c9918d86a5846129215).
While drawing, that script recorded the arguments of each drawing call in `figures/panel_data/fig1_a.json` (`figures/panel_io.py`); `analysis/export_galaxy_benchmark_tables.py` copies the file to `data/figure_panels/`.
`make_figure.py` replays those calls with the same drawing code, so this figure is the archive's figure: the two PNGs were compared pixel for pixel and the source data byte for byte.
Nothing is recomputed in this repository; the recorded tables hold identifiers, scores, counts and estimates only (no trace text, prompts or answers).

## Panels and methods (from the archive script)

```text
Fig. 1a,b schematic: study design (a) and the isolated per-run execution pipeline (b).

Pictogram version: text is reduced to names, counts and short labels; definitions live in the legend
(figures/fig1_a_legend.md). Writes figures/fig1_a.svg (editable text, for Inkscape), fig1_a.pdf (vector,
TrueType) and fig1_a.png (600 dpi, RGB) at 180 mm width with the shared Nature Portfolio style in
manuscript_material/scripts/style.py. Task counts are read from the repository.
```
