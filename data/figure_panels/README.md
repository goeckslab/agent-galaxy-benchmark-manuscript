# Figure panel data

The values each figure is drawn from, as computed in the run archive (`paulocilasjr/Galaxy_benchmark`).

- `<script>.json`: the arguments of every drawing call made by the archive's figure script, in call order, written by its `figures/panel_io.py` (tables keep their index and column labels and types).
  `figures/*/make_figure.py` replays them with the same drawing code; nothing is recomputed here.
- `<figure>_source_data.csv`: the archive's source data for each figure; `make_figure.py` copies it to the figure folder as `source_data.csv`.
- `manifest.json`: the archive commit and the SHA-256 of every file (written by `analysis/export_galaxy_benchmark_tables.py`).

The files hold identifiers, scores, counts and estimates only: no trace text, prompts or answers.
