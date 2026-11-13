# Figure review for Nature Methods

The 12 November 2026 revision uses the frozen 28 October release. The CSHL presentation supplied the visual sequence on pages 10 and 13–15. The paired design, model scores and selection results come from the run records and official submissions in this package.

## Editorial and artwork criteria

The Brief Communication format normally allows two main display items. Both main plates are multi-panel figures. The seven supplementary figures accompany them in a single PDF, with a caption on the same page as each plate. [Nature Methods content types](https://www.nature.com/nmeth/content) · [Journal submission guidance](https://www.nature.com/nmeth/submission-guidelines/preparing-your-submission)

The journal specifies a maximum width of 180 mm, at least 300 dpi and 5–7 pt sans-serif labels. At that width all nine plates use 6.5–7 pt Arial, with bold panel headings, axis titles and selected result labels. Figure 1 is 111 mm tall and Figure 2 is 132 mm tall. Each supplementary page fits the plate and its caption at the same print width. The PDFs embed TrueType fonts, the SVGs retain editable text and the RGB PNGs are 450 dpi. [Nature Methods artwork and legend requirements](https://www.nature.com/nmeth/submission-guidelines/aip-and-formatting) · [Measured dimensions and typography](artwork_checks.csv)

## Decisions at panel level

| Figure | Finding in the earlier version | Revision and interpretation |
|---|---|---|
| [1](fig1_performance/README.md) | Separate pooled axes and repeated model labels made comparisons slow. | **a** shows the crossed design. **b** uses one zero-based grouped bar chart for the three benchmark percentages. **c** gives each model–policy score once in a labeled matrix. **d** gives paired differences and available intervals in percentage points. |
| [2](fig2_interface/README.md) | The original error labels and single-benchmark voting panel obscured the questions about environment setup and repeatability. | **a** separates primary labels into task or scoring ambiguity, missing validation, platform or harness, and model knowledge, so benchmark problems are not read as Galaxy faults. **b** follows page 15 of the CSHL talk, with two policy rows per benchmark. **c** spans the bottom row and reproduces the page 18 ratio chart, including its historical MCP cohort, logarithmic scale, estimates and four model symbols. |
| [S1](s1_execution/README.md) | The execution diagram began at tool invocation, after the model and policy had already been assigned. | **a** follows the benchmark inputs through both policies to their readouts. **b,c** quantify observed tool use. **d,e** trace one yeast result to its job and align the significant gene sets against the raw curated output. |
| [S2](s2_reruns/README.md) | Abbreviated rows put substitution and score-only changes on the same footing. | **a** gives selection reasons. **b** shows every affected official submission, distinguishing a measured zero from an unaffected submission. **c** distinguishes regrading-only groups from groups that also had replacements. **d** gives before and after IWC means with their denominators. |
| [S3](s3_repeatability/README.md) | Counting passes across three attempts did not show which submitted answer would win a vote. | **a** shows reference-based rates by benchmark and policy. **b** tallies passing and failing selected strings and abstentions over all groups with answer strings. **c** independently checks one CompBioBench consensus against a strand-aware reference sequence. |
| [S4](s4_iwc_outputs/README.md) | Means and ranges concealed which runs were zero or near-perfect. | **a** displays all 240 run scores by workflow, policy, model and replicate. The percentage bands distinguish scores near 100% and crosses mark zeros. **b** gives percentage agreement and the count below 99% for each group of 12. Exact scores and published explanations are linked. |
| [S5](s5_request_failures/README.md) | A heatmap alone hid the traced-run denominators and the difference between pre-submission and execution failures. | **a** gives traced runs and failed requests by stage. **b** prints counts for every class, with benchmark-specific shading. The denominator for color is stated directly above the matrix. |
| [S6](s6_token_usage/README.md) | Approximate early values resembled directly measured results in the historical trend. | **a–c** share a log-ratio scale and identify each pooled value. **d,e** separate model campaigns, name their stages and report replicate coverage. Open and filled marks distinguish estimates and measurements. |
| [S7](s7_token_drivers/README.md) | Added on 6 November. The package archived the July 6 token-driver page but did not use it, although it explains why Galaxy cost more. | **a** shows that cached context makes up 94.8% of Galaxy tokens. **b** separates more turns (2.66×) from more context per turn (2.20×), each on its own axis and with the page's own ratios. **c** counts commands by purpose. **d** compares skill guidance within the same batch. One model, one batch and the round-1 interface are stated in the legend. |

## Checks performed

- Rebuilt source tables against the pinned inputs. Reconciled paired endpoints, all 77 replacements and 25 reported changes, token totals and all 240 IWC records. Independently rechecked a version-dependent BixBench answer, one sequence-derived CompBioBench answer and the yeast output tables. [Scientific checks](../../analysis/build_benchmark_summary.py) · [Original source versions and hashes](sources_manifest.csv)
- Inspected each exported PDF as a full-page Poppler rendering, then viewed the integrated manuscript and supplementary pages. Shortened the Figure 1 cohort label, corrected the S5 right-hand column heading, and replaced mean-only interaction bars with individual observations. All lowercase panel labels, captions, units and keys were reviewed at the designed scale.
- Checked PDF geometry, all glyph bounds, font embedding, SVG text objects and font sizes, PDF and SVG raster-object absence, and PNG color mode, dimensions and print resolution. Compared the actual manuscript captions to the canonical figure legends. These checks can be repeated using the commands in the [package guide](README.md). [Verification code](../../analysis/verify_benchmark_package.py)
- The 5–6 November build reproduced the archived data and figures twice. For the 12 November plates, the verifier additionally reconstructs exact answer votes from the run manifest, checks each benchmark’s full factorial count and tests the sequence calculation. The [artifact inventory](artifact_manifest.csv) fingerprints the current code, source tables and exports. Font selection falls back to an installed sans-serif on other systems.

### Reproduction environment

The archived plates were built with Python 3.12.10, Matplotlib 3.11.2, fontTools 4.68.0 and FreeType 2.14.3. The PDF manuscript used Quarto 1.11.9 and the supplement used pdfTeX 1.40.29 (TeX Live 2026). The rebuild command pins the Python hash seed to 0 and the artwork timestamp to the October edition. [Python package versions](requirements.txt)

| Local typeface used | Version | SHA-256 of installed font |
|---|---|---|
| Arial regular | 7.06 | `b3658eadae55e682b5f69eb64c439c1ecc8f196c0bb8d4756d145d13bc86476a` |
| Arial bold | 7.06 | `e8f4e3baf6cc35fed6fcce3a540e8b39e8f6cda1d22a28f2ec8f526fef7a43f5` |

Seven BixBench failures are pending run-level adjudication. The optimization campaigns do not isolate the independent effect of compact replies or longer waits. The displays label both limitations for scientific review.
