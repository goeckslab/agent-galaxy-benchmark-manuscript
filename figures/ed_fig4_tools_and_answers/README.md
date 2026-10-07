# Extended Data Fig. 4: Tool inventory, route similarity, answer matching, difficulty and UDT methods

Supports Results section 3 (tools, route similarity, answer matching and UDT methods for Figure 4).
The legend draft is in [legend.md](legend.md).

## Files

- `make_figure.py`: the drawing code of the run archive's `figures/make_fig4.py`, copied unchanged; it replays the values that script computed and writes every file below.
- `ed_fig4_tools_and_answers.pdf`, `.png` (600 dpi, RGB) and `.svg` (editable text).
- `source_data.csv`: every plotted value, interval, *P* value and count, one row each (the archive's `ed_fig4_source_data.csv`).
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the archive changes
python figures/ed_fig4_tools_and_answers/make_figure.py
```

## Provenance

Every estimate, interval and *P* value was computed by `figures/make_fig4.py` in the run archive, [paulocilasjr/Galaxy_benchmark@0dbf3f4](https://github.com/paulocilasjr/Galaxy_benchmark/tree/0dbf3f443b83a91322098c9918d86a5846129215).
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
intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). Scores come from figures/scored_runs.csv (make_scored_runs.py): every run as the public results site shows it
(https://goeckslab.github.io/galaxy-agent-benchmark/), the IWC host-read removal task included.
Writes figures/fig4.{svg,pdf,png},
fig4_source_data.csv, fig4_tool_family_codebook.csv, ed_fig4.{svg,pdf,png} and ed_fig4_source_data.csv.
```
