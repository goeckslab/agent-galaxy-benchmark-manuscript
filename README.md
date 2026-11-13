# Agent benchmark manuscript

Manuscript, figures, and analysis code for a paper benchmarking AI coding agents on computational biology tasks, comparing runs that use Galaxy with runs that use custom code.

- Benchmark: [goeckslab/galaxy-agent-benchmark](https://github.com/goeckslab/galaxy-agent-benchmark)
- Run traces (Hugging Face): [goeckslab/galaxy-agent-benchmark-run-traces](https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces)

Status: draft Brief Communication for Nature Methods, built from the 28 October 2026 results release.
Open author items are marked as `TODO` comments in the manuscript source.

## Layout

```text
manuscript/    paper source (Quarto): index.qmd renders brief-communication.qmd; references.bib
figures/       figures generated from code; benchmark_results_summary/ holds the paper's
               two main and seven supplementary figures, their source data and build records
analysis/      scripts that fetch the data and build every table, figure and check
data/          small derived tables, the results manifest, and a frozen copy of the
               results website's data (data/site/)
supplement/    supplementary notes
.github/       issue templates, PR template, CI that builds a preview on every PR
```

The earlier long-form draft (`abstract.qmd`, `introduction.qmd`, `results.qmd`, `discussion.qmd`, `methods.qmd` and `outline.md` in `manuscript/`) and the PLOS Computational Biology profile are kept for reference; they are not rendered.

Large trace files are never committed. They are fetched from Hugging Face by `analysis/fetch_traces.py` into `traces/`, which is git-ignored.

## Quick start

Requirements: [Quarto](https://quarto.org/docs/get-started/) and Python 3.10+.
A devcontainer is provided for GitHub Codespaces and VS Code.

```bash
pip install -r requirements.txt
quarto render manuscript          # HTML, DOCX and PDF into manuscript/_output/
```

PDF output needs a LaTeX install (`quarto install tinytex`).

### Rebuilding the figures and checking the numbers

The figures, their source data, the results manifest and the supplementary figures PDF are rebuilt offline from pinned sources, and a verifier checks the artwork and the reported numbers.
The commands and exact package versions are in [figures/benchmark_results_summary/README.md](figures/benchmark_results_summary/README.md#rebuild-and-verify).

### Journal profiles

Quarto profiles switch the citation style and other journal-specific settings:

```bash
QUARTO_PROFILE=nmeth quarto render manuscript      # Nature Methods
QUARTO_PROFILE=ploscb quarto render manuscript     # PLOS Computational Biology
```

### Fetching traces

```bash
export HF_TOKEN=...   # never commit this; in CI it comes from GitHub Actions secrets
python analysis/fetch_traces.py --pattern "compbiobench/**/cryptic-exon-q1/**"
```

The script prints the dataset revision. Record it in `data/results_manifest.csv` so every number can be traced.

## Contributing

Humans and agents contribute the same way: open an issue, work on a branch, open a pull request, get a review.
See [CONTRIBUTING.md](CONTRIBUTING.md). Agents should also read [AGENTS.md](AGENTS.md).

## Licenses

- Code: MIT ([LICENSE](LICENSE))
- Text, figures, and supplementary material: CC BY 4.0 ([LICENSE-CC-BY-4.0.txt](LICENSE-CC-BY-4.0.txt))
- Data in `data/`: MIT, the license of the source repository `goeckslab/galaxy-agent-benchmark`. Tables built here are under [LICENSE](LICENSE); the copy of the results website's data in `data/site/` is under that repository's own license ([data/site/LICENSE](data/site/LICENSE)). Benchmark questions and answers in that copy keep their original licenses (see [data/README.md](data/README.md)).
- Hugging Face trace dataset: license to be decided

## Citing

See [CITATION.cff](CITATION.cff). A Zenodo-archived release with a DOI will be created at submission.
