# Figure 1. Experimental design and model performance across three benchmarks

**a**, Each model attempted every task three times per policy. **b**, Paired bars show the percentage of BixBench answers accepted (600 runs per policy), the percentage of official CompBioBench points earned (12 submissions of 100 answers per policy) and mean IWC workflow-output agreement (120 runs per policy), expressed as a percentage. **c**, Cells give each model’s score in Galaxy (G) and custom code (C). Darker cells indicate higher percentages. **d**, Diamonds show pooled Galaxy minus custom-code differences in percentage points. Whiskers span paired 95% percentile intervals from 200,000 resamples of 33 BixBench data capsules or ten IWC workflows. The open diamond marks the official CompBioBench difference, for which item-level grades were unavailable.

The [item scores](dataset/item_scores.csv), [official submissions](dataset/official_submissions.csv) and [question index](dataset/question_index.csv) link each score to its evaluation. For IWC, the continuous agreement score on the native 0–1 scale is multiplied by 100 before rounding. The source data include paired model-specific intervals where available.

[Plotted values](dataset/source_data.csv) · [Original sources, versions and checksums](dataset/inputs.csv) · [Plotting code](code/make_figure.py) · [Vector PDF](output/fig1_performance.pdf) · [Editable SVG](output/fig1_performance.svg) · [PNG](output/fig1_performance.png)

After building the source tables, run `python analysis/build_benchmark_summary.py --figure fig1_performance` from the repository root. The [package guide](../README.md) gives the complete offline build.
