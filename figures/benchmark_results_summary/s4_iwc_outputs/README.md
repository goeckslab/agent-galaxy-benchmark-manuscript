# Supplementary Figure 4. Individual run agreement with each reference workflow

**a**, Each cell denotes one continuous agreement score for an IWC workflow. Within each policy, every model contributed three replicates. The key distinguishes exact agreement, small deviations, larger deviations and zero agreement. Scores retain full source precision for binning. Crosses identify zeroes. **b**, Each entry gives the mean over the 12 runs for that workflow and policy, expressed as a percentage and rounded to two decimals. Parentheses count individual scores strictly below 99% agreement. The diagnostic threshold distinguishes near-matches and is separate from the continuous endpoint in Fig. 1. Different workflows use different output evaluators.

The [run-level explanations](dataset/score_explanations.csv) link all 98 submaximal scores to published interpretations. The source data include all 240 scores, their original locators, per-workflow evaluator and reference-history URLs.

[Plotted values](dataset/source_data.csv) · [Original sources, versions and checksums](dataset/inputs.csv) · [Plotting code](code/make_figure.py) · [Vector PDF](output/s4_iwc_outputs.pdf) · [Editable SVG](output/s4_iwc_outputs.svg) · [PNG](output/s4_iwc_outputs.png)

After building the source tables, run `python analysis/build_benchmark_summary.py --figure s4_iwc_outputs` from the repository root. The [package guide](../README.md) gives the complete offline build.
