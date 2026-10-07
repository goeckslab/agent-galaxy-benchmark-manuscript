> Version of this figure in pull request #11 before every run was scored as the public results site shows it (2026-10-07), kept for comparison. The current figure is in `figures/ed_fig2_failure_causes/`. This version was ported from the run archive at commit b3cbb94 and replays panel data recorded there; after the re-export, `data/figure_panels/` holds the panel data of commit 0dbf3f4, so rerunning it no longer reproduces the image stored here.

# Extended Data Fig. 2: Failure causes and sensitivity of the accuracy comparison

Supports Results section 1 (failure causes and sensitivity analyses for Figure 2).
The legend draft is in [legend.md](legend.md).

## Files

- `make_figure.py`: the drawing code of the run archive's `figures/make_fig2.py`, copied unchanged; it replays the values that script computed and writes every file below.
- `ed_fig2_failure_causes.pdf`, `.png` (600 dpi, RGB) and `.svg` (editable text).
- `source_data.csv`: every plotted value, interval, *P* value and count, one row each (the archive's `ed_fig2_source_data.csv`).
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the archive changes
python figures/ed_fig2_failure_causes/make_figure.py
```

## Provenance

Every estimate, interval and *P* value was computed by `figures/make_fig2.py` in the run archive, [paulocilasjr/Galaxy_benchmark@b3cbb94](https://github.com/paulocilasjr/Galaxy_benchmark/tree/b3cbb944648a57104a6837d1640b255854dd7e3e).
While drawing, that script recorded the arguments of each drawing call in `figures/panel_data/fig2.json` (`figures/panel_io.py`); `analysis/export_galaxy_benchmark_tables.py` copies the file to `data/figure_panels/`.
`make_figure.py` replays those calls with the same drawing code, so this figure is the archive's figure: the two PNGs were compared pixel for pixel and the source data byte for byte.
Nothing is recomputed in this repository; the recorded tables hold identifiers, scores, counts and estimates only (no trace text, prompts or answers).

## Panels and methods (from the archive script)

```text
Fig. 2: Agents show similar observed benchmark performance in Galaxy and custom code.

Panels:
a, score of each model in each condition, one facet per benchmark and its own scoring contract: evaluator acceptance
   (BixBench-Verified-50), agreement with a reconstructed answer key (CompBioBench) and agreement with curated workflow
   outputs on a 0-1 scale (IWC); paired points with 95% intervals, and each replicate as a small dot;
b, the paired estimates: Galaxy minus custom code for each model and for the four models pooled, as two aligned groups
   that are never mixed in one row: the mean score (the primary endpoint of each benchmark) and the share of replicate
   sets with all three runs correct (reliability; IWC at >= 0.99 agreement);
c, correct runs of three for each task and model, custom code against Galaxy, one matrix per benchmark;
d, why the conditions disagree on BixBench-Verified-50: the AI-assisted audit's primary cause of each incorrect run,
   split by whether the task-model pair was discordant (one condition had more correct runs) or had the same count, with
   one traced discordant case (bix-45-q1, a tool-version difference).

Extended Data Fig. 2 (written by the same script): a, the full census of causes by the number of incorrect runs in the
set (the first version's panel d); b, sensitivity of the condition difference to the IWC correctness threshold and to
the archive's population sensitivities.

A run is correct when accepted or at >= 0.99 IWC output agreement. Intervals are 95% percentile cluster-bootstrap
intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). P values come from paired cluster
sign-flip randomization tests (200,000 draws, or exact enumeration with at most 16 clusters), Holm-adjusted within each
family. No test here is an equivalence test: the figure reports estimates and intervals.
Writes figures/fig2.{svg,pdf,png}, figures/fig2_source_data.csv, figures/ed_fig2.{svg,pdf,png} and
figures/ed_fig2_source_data.csv, and prints the statistics.
```
