# Figure 2. Answer selection, errors and the cost of Galaxy interactions

**a**, Primary audit labels for incorrect BixBench runs. Task or scoring ambiguity covers under-specified tasks, reference answers and scoring rules. Missing validation denotes an analysis or answer that the agent did not check. Platform or harness covers tool, job and submission problems, and model knowledge covers wrong biological or statistical concepts. Percentages use all incorrect runs in each policy, including four unresolved audits and seven runs awaiting review. **b**, Circles show single-run pass rates. Open triangles and squares show the percentage of task–model groups with at least two or at least one pass in three attempts, respectively. BixBench uses reviewed acceptance, CompBioBench uses reconstructed item matches and IWC requires ≥99% workflow-output agreement (200, 400 and 40 groups per policy, respectively). Both group rates require the benchmark grades, so they bound what answer selection could achieve. **c**, Galaxy-to-custom-code token ratios on BixBench across five development stages, on a logarithmic scale. The first two GPT-5.5 points are author estimates. The dotted segment joins the single-replicate estimate to the three-replicate measurement at the same stage. The shaded MCP stage uses the 12 October snapshot for all four models. The model and CLI version also changed between campaigns.

Panel a groups each failed run once using its primary audit label. Secondary labels and confidence remain available in the [failure ledger](dataset/bixbench_current_failures.csv). A separate column counts accepted attempts by the same model on the same task under the same policy. [Archived audit definitions](https://github.com/goeckslab/agent-galaxy-benchmark-manuscript/blob/9165a8eaf50569806fbb8af67cb68633316e7359/data/README.md)

| Figure category or status | Original audit evidence |
|---|---|
| Task or scoring ambiguity | `SPEC` and `EVALUATOR` cover task or reference ambiguity and scoring problems. These are properties of the benchmark. |
| Missing validation | `RIGOR` covers a missing check on the analysis or answer. |
| Platform or harness | `PLATFORM` and `HARNESS` cover tool, job or submission problems. |
| Model knowledge | `KNOWLEDGE` identifies an incorrect biological or statistical concept. |
| Cause unassigned | The primary audit confidence is `unresolved`, or the current run has no applicable audit. Both statuses remain in each policy's denominator. |

The [replicate groups](../s3_repeatability/dataset/replicate_groups.csv) give the pass counts for panel b. [Supplementary Fig. 3b](../s3_repeatability/README.md) evaluates an exact answer vote, including its abstentions. The [optimized runs](dataset/optimized_runs.csv) and [scoring sensitivity](dataset/optimization_key_sensitivity.csv) distinguish published and revised-key acceptance. Historical request failures appear in [Supplementary Fig. 5](../s5_request_failures/README.md).

Panel c follows the historical BixBench series on page 18 of the CSHL presentation. The four MCP ratios use the [12 October token snapshot](../../../data/site_token_totals.csv), which gives 3.67× for DeepSeek V4 Pro. The [28 October main cohort](../s6_token_usage/dataset/source_data.csv) gives 3.30× for that model. The estimates and the other measured stages come from the [development-round records](../../../data/token_optimization_rounds.csv). The stage timeline uses different models and replicate coverage across campaigns.

In the [source data](dataset/source_data.csv), `figure_panel` identifies the rows plotted in a, b and c. The `optimization` and `replicates` records give the wait-call and model-request counts cited in the text.

[Plotted values](dataset/source_data.csv) · [Original sources, versions and checksums](dataset/inputs.csv) · [Plotting code](code/make_figure.py) · [Vector PDF](output/fig2_interface.pdf) · [Editable SVG](output/fig2_interface.svg) · [PNG](output/fig2_interface.png)

After building the source tables, run `python analysis/build_benchmark_summary.py --figure fig2_interface` from the repository root. The [package guide](../README.md) gives the complete offline build.
