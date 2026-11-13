# Supplementary Figure 5. Where recorded Galaxy requests failed

**a**, The historical audit covers 600 BixBench, 1,188 CompBioBench and 108 IWC Galaxy runs. Counts refer to failed requests during those traced runs. A run may contribute several failures and still return a correct answer. **b**, Each cell gives the number of requests in one failure class. The shade uses the total failed requests for that benchmark as its denominator. Zeros include classes with no recorded event in that benchmark. A1–A8 in the source precede job execution, B1–B5 concern running jobs, and the other two classes cover exceptions.

The [trace coverage table](dataset/historical_trace_coverage.csv) retains the original benchmark identifiers. The source table preserves the complete upstream taxonomy and the stage and benchmark totals.

[Plotted values](dataset/source_data.csv) · [Original sources, versions and checksums](dataset/inputs.csv) · [Plotting code](code/make_figure.py) · [Vector PDF](output/s5_request_failures.pdf) · [Editable SVG](output/s5_request_failures.svg) · [PNG](output/s5_request_failures.png)

After building the source tables, run `python analysis/build_benchmark_summary.py --figure s5_request_failures` from the repository root. The [package guide](../README.md) gives the complete offline build.
