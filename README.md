# Agent benchmark manuscript

Manuscript, figures, and analysis code for a paper benchmarking AI coding agents on computational biology tasks, comparing runs that use Galaxy with runs that use custom code.

- Benchmark: [goeckslab/galaxy-agent-benchmark](https://github.com/goeckslab/galaxy-agent-benchmark)
- Run traces (Hugging Face): [goeckslab/galaxy-agent-benchmark-run-traces](https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces)

Status: early scaffolding. The working title, target journal, and article type are still open.

## Layout

```text
manuscript/    paper source (Quarto): one file per section, plus references.bib
figures/       one folder per figure: generating script, rendered output, source data
analysis/      trace fetching and analysis code that feeds the paper
data/          small derived tables only, including the results manifest
supplement/    supplementary tables, notes, and figures
.github/       issue templates, PR template, CI that builds a preview on every PR
```

Large trace files are never committed. They are fetched from Hugging Face by `analysis/fetch_traces.py` into `traces/`, which is git-ignored.

## Quick start

Requirements: [Quarto](https://quarto.org/docs/get-started/) and Python 3.10+.
A devcontainer is provided for GitHub Codespaces and VS Code.

```bash
pip install -r requirements.txt
quarto render manuscript          # HTML, DOCX and PDF into manuscript/_output/
```

PDF output needs a LaTeX install (`quarto install tinytex`).

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
- Derived tables in `data/` and the Hugging Face trace dataset: license to be decided

## Citing

See [CITATION.cff](CITATION.cff). A Zenodo-archived release with a DOI will be created at submission.
