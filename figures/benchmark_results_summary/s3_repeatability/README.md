# Supplementary Figure 3. Repeated attempts, answer consensus and independent validation

**a**, Points compare individual runs with groups in which at least two or at least one of three attempts met the criterion. Each group contains one task and one model under one policy. BixBench uses reviewed acceptance, CompBioBench uses reconstructed item matches and IWC uses workflow-output agreement ≥99%. The two group criteria require known grades. **b**, A vote selects a nonempty answer string returned at least twice after trimming whitespace and ignoring case. Each percentage uses all task–model groups under that policy, including abstentions. The selected answer is graded afterwards. IWC outputs have no comparable answer strings. **c**, For one promoter question, the GRCh38 sequence at the strand-aware GENCODE V49 interval independently reproduces the submitted GC fraction. Coordinates are one-based and inclusive.

The [replicate groups](dataset/replicate_groups.csv), [answer-string votes](dataset/answer_string_votes.csv) and [task-exclusion sensitivity](dataset/sensitivity.csv) retain the underlying observations. The promoter check uses the [transcript annotation](../sources/hg38_gencode_v49.json) and the [reference sequence](../sources/hg38_promoter_sequence.json).

[Plotted values](dataset/source_data.csv) · [Original sources, versions and checksums](dataset/inputs.csv) · [Plotting code](code/make_figure.py) · [Vector PDF](output/s3_repeatability.pdf) · [Editable SVG](output/s3_repeatability.svg) · [PNG](output/s3_repeatability.png)

After building the source tables, run `python analysis/build_benchmark_summary.py --figure s3_repeatability` from the repository root. The [package guide](../README.md) gives the complete offline build.
