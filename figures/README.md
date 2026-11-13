# Figures

The current Brief Communication uses the two main figures and seven supplementary figures in [benchmark_results_summary](benchmark_results_summary/README.md).
Each of its figures has a `code/`, `dataset/` and `output/` folder, and one build script draws them all; its README gives the commands.
The [artwork review](benchmark_results_summary/FIGURE_REVIEW.md) records the panel design decisions and checks against the journal’s print specifications.

The [experimental architecture](benchmark_results_summary/s1_execution/README.md) follows the two execution paths to a scored output. [Figure 1](benchmark_results_summary/fig1_performance/README.md) compares the policies across benchmarks and models. The [consensus and validation figure](benchmark_results_summary/s3_repeatability/README.md) shows which repeated answers a vote actually returns and checks one answer against independent sequence data.

The other folders are not in the current paper: `sfig_token_main_runs` and `sfig_token_optimization` document an earlier results edition, and `sfig_accuracy_by_model` shows accuracy by model for all four benchmarks.

Every figure is generated from code, never pasted in as an image.
A standalone figure has its own folder:

```text
figures/figN_short_name/
├── make_figure.py      # reads data/ and analysis/ outputs, writes the files below
├── figN_short_name.pdf
├── figN_short_name.png
└── source_data.csv     # the exact values plotted
```

Start from `_template/make_figure.py`.
Register every figure in `figures.csv` and mark it `main` or `supplementary` from the start, because journals cap main-text display items.
Use consistent model names and a colorblind-safe palette across all figures.
