# Figure 3: Galaxy provides a structured environment for agent analyses

Supports Results section 2 of `manuscript/outline.md` (Galaxy as a structured environment).
The legend draft is in [legend.md](legend.md).

## Files

- `make_figure.py`: the drawing code of the run archive's `figures/make_fig3.py`, copied unchanged; it replays the values that script computed and writes every file below.
- `fig3_structured_environment.pdf`, `.png` (600 dpi, RGB) and `.svg` (editable text).
- `source_data.csv`: every plotted value, interval, *P* value and count, one row each (the archive's `fig3_source_data.csv`).
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the archive changes
python figures/fig3_structured_environment/make_figure.py
```

## Provenance

Every estimate, interval and *P* value was computed by `figures/make_fig3.py` in the run archive, [paulocilasjr/Galaxy_benchmark@b3cbb94](https://github.com/paulocilasjr/Galaxy_benchmark/tree/b3cbb944648a57104a6837d1640b255854dd7e3e).
While drawing, that script recorded the arguments of each drawing call in `figures/panel_data/fig3.json` (`figures/panel_io.py`); `analysis/export_galaxy_benchmark_tables.py` copies the file to `data/figure_panels/`.
`make_figure.py` replays those calls with the same drawing code, so this figure is the archive's figure: the two PNGs were compared pixel for pixel and the source data byte for byte.
Nothing is recomputed in this repository; the recorded tables hold identifiers, scores, counts and estimates only (no trace text, prompts or answers).

## Panels and methods (from the archive script)

```text
Fig. 3: Galaxy provides a structured environment for agent analyses.

Panels:
a, correct runs by task domain, Galaxy against custom code (a run is correct when accepted, not merely completed);
b, how each traced Galaxy run used Galaxy and how it ended: the kinds of job that completed (installed tools, user-defined
   tools (UDTs), both), runs whose jobs all failed and runs that submitted no job, with the share of runs correct and the
   exact number of runs per row;
c, how often each kind of execution step failed: the share of installed-tool jobs, UDT jobs and shell commands that
   failed, and all execution errors per run; right, the main error types in each channel (the seven-type breakdown is in
   Extended Data);
d, final correctness among runs with execution errors, by the number of errors, with the unadjusted and the
   error-bin-adjusted (exploratory) Galaxy - custom code differences;
e, what the interface's parameter check found for installed-tool requests: matched; a value Galaxy would set or set
   differently (blocked before the job, or after it ran); a requested value with no recorded counterpart; no comparison;
f, failed Galaxy requests by failure class, grouped into candidate infrastructure improvements (an unvalidated codebook,
   written to figures/fig3_failure_class_codebook.csv), with the runs each group affected.

Extended Data Fig. 3: a, the status of every task (correct runs of three per model and condition); b, the full seven-type
error breakdown by channel; c, final correctness by error bin for each benchmark.

A run is correct when accepted (BixBench-Verified-50, CompBioBench) or at >= 0.99 IWC output agreement. Intervals are
95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks).
P values come from paired cluster randomization tests (200,000 draws), Holm-adjusted within each panel.
Writes figures/fig3.{svg,pdf,png}, fig3_source_data.csv, fig3_failure_class_codebook.csv, ed_fig3.{svg,pdf,png} and
ed_fig3_source_data.csv, and prints the statistics.
```
