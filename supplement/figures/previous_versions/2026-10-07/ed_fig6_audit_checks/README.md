> Version of this figure in pull request #11 before every run was scored as the public results site shows it (2026-10-07), kept for comparison. The current figure is in `figures/ed_fig6_audit_checks/`. This version was ported from the run archive at commit b3cbb94 and replays panel data recorded there; after the re-export, `data/figure_panels/` holds the panel data of commit 0dbf3f4, so rerunning it no longer reproduces the image stored here.

# Extended Data Fig. 6: Independent checks of the audits and of benchmark integrity

Supports Results sections 1 and 2 (independent checks of the audits and of benchmark integrity).
The legend draft is in [legend.md](legend.md).

## Files

- `make_figure.py`: the drawing code of the run archive's `figures/make_ed_validation.py`, copied unchanged; it replays the values that script computed and writes every file below.
- `ed_fig6_audit_checks.pdf`, `.png` (600 dpi, RGB) and `.svg` (editable text).
- `source_data.csv`: every plotted value, interval, *P* value and count, one row each (the archive's `ed_fig6_source_data.csv`).
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the archive changes
python figures/ed_fig6_audit_checks/make_figure.py
```

## Provenance

Every estimate, interval and *P* value was computed by `figures/make_ed_validation.py` in the run archive, [paulocilasjr/Galaxy_benchmark@b3cbb94](https://github.com/paulocilasjr/Galaxy_benchmark/tree/b3cbb944648a57104a6837d1640b255854dd7e3e).
While drawing, that script recorded the arguments of each drawing call in `figures/panel_data/ed_validation.json` (`figures/panel_io.py`); `analysis/export_galaxy_benchmark_tables.py` copies the file to `data/figure_panels/`.
`make_figure.py` replays those calls with the same drawing code, so this figure is the archive's figure: the two PNGs were compared pixel for pixel and the source data byte for byte.
Nothing is recomputed in this repository; the recorded tables hold identifiers, scores, counts and estimates only (no trace text, prompts or answers).

## Panels and methods (from the archive script)

```text
Extended Data Figs 6 and 7: independent checks of the annotations, benchmark integrity, verification and recovery.

Extended Data Fig. 6 (checks of the audits and of benchmark integrity):
a, runs that reached a source of benchmark answers during the run, by exposure tier (make_answer_exposure.py);
b, the Galaxy - custom code accuracy difference with all runs, without runs with verified or probable exposure, and
   without any run that searched for the benchmark;
c, an independent AI-assisted second rater against the original failure-cause audit (45 BixBench-Verified-50 runs);
d, an independent AI-assisted second rater against the rule-based failure classes of failed Galaxy requests (150).

Extended Data Fig. 7 (verification and recovery):
a, verification checks coded in 80 runs (coder blind to the grade), by outcome and by condition;
b, failure episodes: failed steps later re-run without error in the same run, and final correctness;
c, a worked parameter check (bix-43-q4): a request blocked before the job, then corrected;
d, a selected case (variant-status-q1): outcomes of all 24 runs and the runs that ran a read-position diagnostic.

Writes figures/ed_fig6.{svg,pdf,png}, ed_fig7.{svg,pdf,png}, ed_fig6_source_data.csv and ed_fig7_source_data.csv.
CompBioBench answers are never written.
```
