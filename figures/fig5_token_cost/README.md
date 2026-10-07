# Figure 5: Galaxy records analyses as structured provenance and uses more input tokens on question-answering tasks

Supports Results section 4 of `manuscript/outline.md` (inspectability and token cost).
The legend draft is in [legend.md](legend.md).

## Files

- `make_figure.py`: the drawing code of the run archive's `figures/make_fig5.py`, copied unchanged; it replays the values that script computed and writes every file below.
- `fig5_token_cost.pdf`, `.png` (600 dpi, RGB) and `.svg` (editable text).
- `source_data.csv`: every plotted value, interval, *P* value and count, one row each (the archive's `fig5_source_data.csv`).
- `legend.md`: figure legend draft.

## Regenerate

```bash
python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark   # only if the archive changes
python figures/fig5_token_cost/make_figure.py
```

## Provenance

Every estimate, interval and *P* value was computed by `figures/make_fig5.py` in the run archive, [paulocilasjr/Galaxy_benchmark@0dbf3f4](https://github.com/paulocilasjr/Galaxy_benchmark/tree/0dbf3f443b83a91322098c9918d86a5846129215).
While drawing, that script recorded the arguments of each drawing call in `figures/panel_data/fig5.json` (`figures/panel_io.py`); `analysis/export_galaxy_benchmark_tables.py` copies the file to `data/figure_panels/`.
`make_figure.py` replays those calls with the same drawing code, so this figure is the archive's figure: the two PNGs were compared pixel for pixel and the source data byte for byte.
Nothing is recomputed in this repository; the recorded tables hold identifiers, scores, counts and estimates only (no trace text, prompts or answers).

## Panels and methods (from the archive script)

```text
Fig. 5: Galaxy records analyses as structured provenance and uses more input tokens on question-answering tasks.

Panels:
a, Galaxy / custom-code token ratios for each benchmark (including IWC, where Galaxy did not use more input): total
   input (including cached context), uncached input and output tokens. Primary estimate, the geometric mean of paired
   task-model ratios (typical paired-task demand); secondary, the ratio of total tokens over the same cells (aggregate
   consumption). Below, input tokens of incorrect relative to correct runs of the same task and model;
b, where the extra input comes from: Galaxy / custom-code ratios of actions and of input tokens per action, by
   benchmark; right, the characters Galaxy returned to the agent, by what the request was for;
c, reducing Galaxy token use: Galaxy / custom-code tokens per complete 50-task BixBench-Verified-50 run before and after
   each round of interface changes (July, GPT-5.5: archived July 6 batch, then the archived runs; October, GPT-5.6 Sol:
   archived runs, the one-replicate intermediate round from the batch summary, then the token-optimization batch), from
   token_improvment/ (run_inventory.csv, earlier_rounds/, site_snapshot/summary.json);
d, what the retained record holds for each analysis step in each condition, separating structured records from free
   text in the retained trace, records of the environment only, and evidence that was not retained or not recorded
   (unknown, not absent);
e, one analysis step recorded both ways: PhyKIT relative composition variability on bix-45-q1 (GPT-5.6 Sol, replicate
   1), the tool-version case of Fig. 2d.

Extended Data Fig. 5: a, accuracy against median input tokens per model and condition, by benchmark; b, input tokens of
correct and incorrect runs (the first version's panel b); c, input tokens against actions (the first version's panel c).

Input tokens include cached context unless stated. Actions are the agent's tool calls (shell commands, Galaxy interface
calls, web searches or fetches, file reads, writes and edits), as in On-demand Fig. 6. Tokens differ between models in
price, so ratios are not monetary costs. A run is correct when accepted or, for IWC, at >= 0.99 output agreement.
Intervals are 95% percentile cluster-bootstrap intervals (clusters are BixBench source capsules, otherwise tasks); P values
come from paired cluster sign-flip randomization tests (200,000 draws; exact with at most 16 clusters).
Scores come from figures/scored_runs.csv (make_scored_runs.py): every run as the public results site shows it
(https://goeckslab.github.io/galaxy-agent-benchmark/), the IWC host-read removal task included.
Writes figures/fig5.{svg,pdf,png}, fig5_source_data.csv, ed_fig5.{svg,pdf,png} and ed_fig5_source_data.csv.
```
