# Galaxy benchmark results for the Brief Communication

**Start with [the findings and answers to the rerun report](RESULTS.md).** The [current paper](../../manuscript/brief-communication.qmd) and [outline](../../manuscript/outline-brief-communication.md) follow an agent from tool selection and job submission to biological validation. The [journal](JOURNAL.md) records how the evidence was collected and checked.

[Review the artwork assessment and measured print specifications](FIGURE_REVIEW.md) or [open the seven-page supplement with each plate and legend fitted to one page](supplementary_figures.pdf).

The primary cohort is the October 28 release. Each benchmark keeps its own endpoint. The package separates current results, earlier trace audits, the October token-optimization batch and author-reported early estimates. The two earlier token figures elsewhere in the repository document an older edition.

| Figure | Contents |
|---|---|
| [Figure 1](fig1_performance/README.md) | Experimental design and model performance across three benchmarks |
| [Figure 2](fig2_interface/README.md) | Answer selection, errors and the cost of Galaxy interactions |
| [Supplementary Figure 1](s1_execution/README.md) | Experimental architecture and the provenance of a Galaxy output |
| [Supplementary Figure 3](s3_repeatability/README.md) | Repeated attempts, answer consensus and independent validation |
| [Supplementary Figure 2](s2_reruns/README.md) | Selection of reruns and effects on reported scores |
| [Supplementary Figure 5](s5_request_failures/README.md) | Where recorded Galaxy requests failed |
| [Supplementary Figure 6](s6_token_usage/README.md) | Token use across benchmarks and successive interface versions |
| [Supplementary Figure 4](s4_iwc_outputs/README.md) | Individual run agreement with each reference workflow |
| [Supplementary Figure 7](s7_token_drivers/README.md) | Where Galaxy runs spent tokens before the interface changes |

Each figure directory contains `dataset/source_data.csv`, any supporting row-level tables, `code/make_figure.py`, a legend, and `output/` with a vector PDF, editable-text SVG and 450-dpi PNG. The panel counts and values are available in the CSVs. For the Galaxy history example, `dataset/workflow_check.csv` supplies the output comparison and tool version. The [question index](fig1_performance/dataset/question_index.csv) contains task text, reference type and source page; the [page catalogue](sources/web_pages.csv) records 239 linked or cited pages and files: the 160 task pages, 50 July 6 archive item pages, 10 IWC multi-step task pages, 14 supporting pages and 5 data files. `data/results_manifest.csv` gives one row per primary run with its answer, score, Galaxy history and, where published, trace path.

Each `dataset/inputs.csv` lists the version, source URL, repository path and checksum of that figure's original inputs. Shared raw records are stored once and can be retrieved through this per-figure inventory.

## Rebuild and verify

From the repository root, use Python 3.12 in a virtual environment. The analysis uses pandas, NumPy and lxml; plotting uses matplotlib. PDF extraction uses pdfplumber. The exact package versions used here are in [requirements.txt](requirements.txt). Quarto and a TeX distribution are needed for the manuscript and combined supplementary PDF. No network or credentials are needed to reproduce the supplied tables and figures; the author-held rerun report is optional (see below).

```sh
python -m pip install -r figures/benchmark_results_summary/requirements.txt
python analysis/summary_provenance.py
python analysis/build_benchmark_summary.py
python analysis/build_results_manifest.py
python analysis/assemble_supplement.py
quarto render manuscript
python analysis/verify_benchmark_package.py --with-manuscript
```

The Nature Methods citation profile can be selected with `QUARTO_PROFILE=nmeth` (PowerShell: `$env:QUARTO_PROFILE='nmeth'`). The render produces HTML, DOCX and PDF in `manuscript/_output/`. To regenerate one plate with the archived hash seed and timestamp, run `python analysis/build_benchmark_summary.py --figure fig1_performance`, substituting any figure directory name. Figures open as vector PDF in the manuscript PDF, editable SVG in HTML and PNG in Word. The supplementary builder needs pdfLaTeX and performs its temporary work under the project’s ignored render directory. A complete rebuild reads each shared source once where practical. Running with `--tables-only` skips rendering. Updating source fingerprints is an explicit edition change; never use `--record-sources` to bypass a failed checksum.

For an intentional artwork revision, run `python analysis/verify_benchmark_package.py --write-artwork-checks --without-inventory --with-manuscript`, review the changes, record `python analysis/summary_provenance.py --inventory`, and rerun the verifier with the inventory enabled. The [artwork measurements](artwork_checks.csv) and [review](FIGURE_REVIEW.md) document the published plate sizes, not the size of an on-screen thumbnail.

## Source and output records

- [Source manifest](sources_manifest.csv) identifies upstream URLs, revisions, exact content hashes and the handling of Git line endings. The existing [site snapshot](../../data/site/MANIFEST.csv) supplies the frozen machine-readable exports. Its upstream commit is `804299a12ca57d27c2b08b0f5b2d74153c2acedc`.
- [Artifact manifest](artifact_manifest.csv) inventories the analysis code, manuscript source, figure source tables, plotting scripts and rendered outputs. Binary hashes use exact bytes. Tracked text hashes normalize CRLF to LF. The inventory excludes itself and the shared inputs already covered by the source manifest.
- [Run-level PDF transcription](s2_reruns/dataset/report_runs.csv) preserves the page and original links. The original PDF (`sources/Rerun_Impact_20261028.pdf`) is held by the authors and kept out of the repository until its redistribution terms are confirmed; the source manifest records its SHA-256. Without it, the build uses the committed transcription and skips only that checksum. A link containing `main` is the original locator supplied by the report; it does not pin third-party trace contents. The frozen published result and its hash identify what was used here.
- Historical tables come from manuscript export `9165a8eaf50569806fbb8af67cb68633316e7359`, which identifies source archive `0fe43954c77f87dddbaf219c62b48b95c7c9f866`. The historic BixBench cluster table is the distinct task/cluster projection of that export’s run scores. Original [export code](https://github.com/goeckslab/agent-galaxy-benchmark-manuscript/blob/9165a8eaf50569806fbb8af67cb68633316e7359/analysis/export_galaxy_benchmark_tables.py).
- The public item-page inventory can be refreshed separately with `python analysis/catalog_benchmark_pages.py` for a new edition. It downloads pages, stores fingerprints and link counts, and leaves execution traces on their original host. Access to the original Verified-50 capsule deposit requires a dataset grant and `HF_TOKEN`; the optional `analysis/fetch_verified50_key.py` is outside the offline build.
- Source licensing follows the [repository data notes](../../data/README.md) and [upstream website license](../../data/site/LICENSE). The report is an author-supplied source. Its redistribution terms have not been independently established; confirm them before depositing the original attachment in a public archive. Source URLs and hashes remain usable without republishing it.

## Scientific limits

Besides the 77 report replacements, 78 BixBench Galaxy runs come from recovery or repeat batches. Another 52 CompBioBench runs are marked as reruns that the report does not cover. The [batch table](s2_reruns/dataset/run_batches.csv) lists them, and their selection must be explained before submission. The sign of the BixBench difference reverses if bix-45-q1 keeps its pre-October grading. The seven uncovered BixBench failures are marked in the ledger. Four other classifications are based on task-level audit evidence. CompBioBench item-match labels must be kept separate from its official aggregate endpoint. The promoter and RNA-seq checks are independent biological spot checks; the remaining records received source reconciliation. Supplementary token stages differ in version, coverage and scoring rule. Formal equivalence, the necessity of a UDT, accuracy gains from a deployable consensus algorithm, and effects on human Galaxy users remain untested.
