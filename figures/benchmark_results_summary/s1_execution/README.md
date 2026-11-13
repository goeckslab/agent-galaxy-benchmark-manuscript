# Supplementary Figure 1. Experimental architecture and the provenance of a Galaxy output

**a**, Four Codex model configurations received the same 160 tasks in Galaxy and custom code, with three replicates of each assignment. Benchmark readouts correspond to the task sets in the order shown. **b,c**, Stacked bars classify 150 BixBench or 300 CompBioBench Galaxy runs per model by observed tool use. A user-defined tool (UDT) packages a custom operation in Galaxy. BixBench records whether a UDT was observed. CompBioBench also distinguishes installed-tool-only histories and histories with no analysis job. **d**, A versioned DESeq2 wrapper processed four prefiltered yeast count tables in a recorded Galaxy job. **e**, Each column represents a gene significant at adjusted P < 0.05 in the agent or raw curated output. Filled circles mark shared genes and open squares mark genes unique to one list. The official IWC evaluator uses a prefiltered gene universe.

The [history index](dataset/run_histories.csv) identifies individual Galaxy histories. The [direct output comparison](dataset/workflow_check.csv) identifies the creating job, wrapper and compared gene sets.

[Plotted values](dataset/source_data.csv) · [Original sources, versions and checksums](dataset/inputs.csv) · [Plotting code](code/make_figure.py) · [Vector PDF](output/s1_execution.pdf) · [Editable SVG](output/s1_execution.svg) · [PNG](output/s1_execution.png)

After building the source tables, run `python analysis/build_benchmark_summary.py --figure s1_execution` from the repository root. The [package guide](../README.md) gives the complete offline build.
