> Version of this figure in pull request #10 before every run was scored as the public results site shows it (2026-10-07), kept for comparison. The current figure is in `figures/fig4_solution_variability/`. This version was ported from the run archive at commit b3cbb94 and replays panel data recorded there; after the re-export, `data/figure_panels/` holds the panel data of commit 0dbf3f4, so rerunning it no longer reproduces the image stored here.

# Figure 4: Answer agreement and tool use vary across model configurations

Supports Results section 3 of `manuscript/outline.md` (task solution variability).
The legend draft is in [legend.md](legend.md).

## Files

- `make_figure.py`: the drawing code of the run archive's `figures/make_fig4.py`, copied unchanged; it replays the values that script computed and writes every file below.
- `fig4_solution_variability.pdf`, `.png` (600 dpi, RGB) and `.svg` (editable text).
- `source_data.csv`: every plotted value, interval, *P* value and count, one row each (the archive's `fig4_source_data.csv`).
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the archive changes
python figures/fig4_solution_variability/make_figure.py
```

## Provenance

Every estimate, interval and *P* value was computed by `figures/make_fig4.py` in the run archive, [paulocilasjr/Galaxy_benchmark@b3cbb94](https://github.com/paulocilasjr/Galaxy_benchmark/tree/b3cbb944648a57104a6837d1640b255854dd7e3e).
While drawing, that script recorded the arguments of each drawing call in `figures/panel_data/fig4.json` (`figures/panel_io.py`); `analysis/export_galaxy_benchmark_tables.py` copies the file to `data/figure_panels/`.
`make_figure.py` replays those calls with the same drawing code, so this figure is the archive's figure: the two PNGs were compared pixel for pixel and the source data byte for byte.
Nothing is recomputed in this repository; the recorded tables hold identifiers, scores, counts and estimates only (no trace text, prompts or answers).

## Panels and methods (from the archive script)

```text
Fig. 4: Answer agreement and tool use vary across model configurations.

Panels:
a, what each model ran in Galaxy: the share of its traced Galaxy runs with at least one completed job in each method
   family, by benchmark (the same stage as Fig. 3b: completed jobs); data handling is separated from scientific methods,
   and user-defined tools (UDTs) are one row because their methods have not been annotated. The family codebook is
   written to figures/fig4_tool_family_codebook.csv;
b, the share of replicate sets (three runs of one task by one model in one condition) that gave the same answer in all
   three runs, for BixBench-Verified-50 and CompBioBench, paired by condition; a set with a missing submission does not
   agree. P values test a model effect within each benchmark and condition (model labels permuted within tasks), Holm-
   adjusted over the four tests;
c, tool-set similarity against task accuracy, one facet per benchmark: the mean pairwise Jaccard index of the three
   replicate runs' sets of tools (installed tools by Tool Shed identifier without version, plus one item for any UDT),
   for task-model cells whose three runs all completed a job. It ignores order, repetition, versions and parameters;
d, every replicate set's outcome by held-out task difficulty (the share of the task's other 21 runs that were
   incorrect, so the set's own runs never define its difficulty), one facet per model: all three accepted, mixed,
   all rejected with different answers, the same rejected answer in all three runs, or a missing submission.

Extended Data Fig. 4: a, the 15 installed tools in the most Galaxy runs (completed jobs), per model; b, tool-set
similarity by model and benchmark, with sensitivity analyses; c, answer agreement under three answer-matching rules.

A run is correct when accepted or, for IWC, at >= 0.99 output agreement. Intervals are 95% percentile cluster-bootstrap
intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). Writes figures/fig4.{svg,pdf,png},
fig4_source_data.csv, fig4_tool_family_codebook.csv, ed_fig4.{svg,pdf,png} and ed_fig4_source_data.csv.
```
