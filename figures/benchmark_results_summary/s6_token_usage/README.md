# Supplementary Figure 6. Token use across benchmarks and successive interface versions

**a–c**, The token ratio divides recorded Galaxy input plus output tokens by the corresponding custom-code total, including cached input once. Points show individual models and diamonds pool token sums. The shared logarithmic scale marks equal token use at one. The headings express the pooled change as a percentage of custom-code token use. One CompBioBench Galaxy run lacked token usage. All other October runs have recorded usage. **d,e**, Rows follow BixBench campaigns in time order within each model. Open circles denote approximate author estimates and filled circles use reported totals. Replicates contain 50 tasks each. The last two GPT-5.6 Sol stages reuse the preceding custom-code baseline. Stages differ in interface behavior, model or CLI version and replicate coverage. They are descriptive comparisons.

The [replicate records](dataset/replicate_usage.csv) contain assigned and observed denominators and cache counts. The [historical rounds](dataset/historical_rounds.csv) identify the source and precision of each measurement.

[Plotted values](dataset/source_data.csv) · [Original sources, versions and checksums](dataset/inputs.csv) · [Plotting code](code/make_figure.py) · [Vector PDF](output/s6_token_usage.pdf) · [Editable SVG](output/s6_token_usage.svg) · [PNG](output/s6_token_usage.png)

After building the source tables, run `python analysis/build_benchmark_summary.py --figure s6_token_usage` from the repository root. The [package guide](../README.md) gives the complete offline build.
