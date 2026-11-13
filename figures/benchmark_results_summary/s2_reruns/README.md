# Supplementary Figure 2. Selection of reruns and effects on reported scores

**a**, Reasons for selecting individual runs from the previous release, as classified from the 28 October report. Zero denotes no selected run for that reason. **b**, Each shaded cell gives the change in official CompBioBench score in percentage points for a 100-answer submission. Dashes identify unaffected submissions. Forty percent of the 55 replacement answer strings changed. The pooled official means were unchanged in both policies. **c**, BixBench changes include regrading of a PhyKIT question with two accepted version-dependent answers. Open markers identify model–policy groups with zero replacements. Filled markers identify groups with replacements and regrading. Each group comprises 150 runs. **d**, IWC DeepSeek V4 Pro means include three replacements on the peptide-verification task across the two policies. The means summarize 30 workflow runs per policy.

The [replacement ledger](dataset/report_runs.csv) preserves report page, reason, before and after values and public links. The [effect table](dataset/report_effects.csv) contains all 25 reported changes, and the [verified replacements](dataset/verified_replacements.csv) reconcile all 77 runs to published results.

[Plotted values](dataset/source_data.csv) · [Original sources, versions and checksums](dataset/inputs.csv) · [Plotting code](code/make_figure.py) · [Vector PDF](output/s2_reruns.pdf) · [Editable SVG](output/s2_reruns.svg) · [PNG](output/s2_reruns.png)

After building the source tables, run `python analysis/build_benchmark_summary.py --figure s2_reruns` from the repository root. The [package guide](../README.md) gives the complete offline build.
