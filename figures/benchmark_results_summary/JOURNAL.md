# Build journal

## 2026-11-05 · Repository and scope

1. Reviewed the repository instructions, contribution policy, manuscript sources and outlines, figure registry, existing token figures, analysis scripts and frozen website exports. The starting manuscript commit was `90a55f38c14827a82ab48bb509018a417b796a15`. Its results manifest contained a header only. The historical prose and token figures described several earlier grading editions.
2. Selected the two-display-item Brief Communication format from the existing outline. The active manuscript now frames the work as engineering Galaxy’s external agent interface. Existing author and competing-interest metadata were retained. Earlier long-form section files and the archived editorial plan remain available for comparison.
3. Treated the supplied report as scientific evidence. Its embedded task prompts and descriptions of past actions were read as records. The attachment has 20 pages and SHA-256 `02bf8e543cf10e45b0f6247c0b36db7fb65f6305c4a418b076ba0880c39cda19`.

## 2026-11-05 · Acquisition and edition control

4. Opened the three supplied pages, then followed links to the item specifications, IWC score explanations and multi-step pilot, CompBioBench timeline and UDT information, BixBench token tables and the October optimization export. Indexed 160 individual task pages and 12 navigation, cost and error-analysis pages in [web_pages.csv](sources/web_pages.csv). For each page recorded its own hash, byte count, last-modified header and link counts. Some search-engine versions of linked pages showed older results. The downloaded October data index matched the repository snapshot exactly.
5. Reused the public JSON and TSV files from `data/site/`, with upstream website repository commit `804299a12ca57d27c2b08b0f5b2d74153c2acedc`. Verified every entry against `data/site/MANIFEST.csv`. This Windows checkout changes LF to CRLF; the check accepts a file only if its exact bytes, or those bytes after undoing Git newline conversion, match both the published length and SHA-256. No site snapshot was refreshed in place.
6. Downloaded the public October optimization results separately. The published batch identifies HF evidence revision `4def1c34763afd79d6271ffe86663d3d6be2a426`. Also retained the July 6 token-driver page and the exact IWC explanation page consumed by the build. The latter covers the 98 below-full scores in this edition.
7. Recovered the historical request-failure, parameter, lookup, coverage and BixBench adjudication tables with `git show` at manuscript export `9165a8eaf50569806fbb8af67cb68633316e7359`. Extracted distinct task/capsule pairs from its BixBench score table. The export identifies archive commit `0fe43954c77f87dddbaf219c62b48b95c7c9f866`. Historical request counts stay in a separate panel with their original denominator.
8. Checked the upstream Verified-50 deposit. Its public metadata identified revision `c77fc8ea4611b546947b8a4710ed36ab72ee233c`; original file access returned HTTP 401 and the dataset is gated. The run environment had no HF token. Recorded the permission boundary and supplied an optional script that reads `HF_TOKEN` for an authorized later cross-check. No private traces, credentials or account payloads were collected.

## 2026-11-05 · Reconciliation

9. Extracted the PDF tables using cell boundaries and link annotations. Read 77 run rows and 25 aggregate entries. Stored original and replacement strings, reasons, pages and record links. Validated each benchmark/model/condition/replicate/task key against the frozen site. Compared BixBench pass/fail and whitespace-normalized answer cells, CompBioBench answer strings and official scores, and IWC F1 to the precision reported in the PDF. Counts, changes of string, post-rerun scores and denominators reconciled.
10. Built the primary cohort of 3,840 assignments and checked unique run keys and complete replicate triples. Excluded unpaired Astra, superseded Claude Code DeepSeek, the separate token-optimization batch and IWC’s multi-step pilot. Used reviewed BixBench grades, official CompBioBench submission scores and continuous IWC output agreement. Retained CompBioBench reference matches as a separate diagnostic.
11. Verified BixBench pass and token totals by aggregating individual runs and checking the published replicate fields. Verified the CompBioBench route classification against its public history-level TSV. Calculated the new pooled token ratios and recorded coverage. Identified the one missing CompBioBench Galaxy usage record; the totals omit it.
12. Joined the historical cause ledger only to current failures for executions absent from the replacement list. Retained 122 run-audit labels and four task-level labels. Marked seven replacement failures as requiring new adjudication. Computed outcome agreement per replicate group and item-level error concentrations. Kept correctness-based selection bounds separate from exact-answer-string votes.
13. Reapplied the new PhyKIT tolerance to all 24 primary answers and separately to the three affected answers in the October optimization batch. The latter changes its count from 137 to 140 under that single-rule sensitivity analysis. The filed batch result remains 137/150.
14. Downloaded the UCSC GENCODE V49 transcript annotation and the hg38 sequence for the independently derived promoter interval. Verified strand, interval convention, sequence length, GC count and fraction against the reported replacement. Opened the public agent and curated IWC yeast histories, followed the agent dataset to its creating job, and retrieved the two DESeq2 output tables. Compared shared genes, adjusted-P calls and fold changes. The raw reference table and the evaluator’s prefiltered universe have different denominators.

## 2026-11-05 · Figures and manuscript

15. Generated two main and six supplementary figures. Each directory contains its plotted values, supporting tables, executable plotting code, legend, PDF, editable-text SVG and 450-dpi PNG. Main contrasts resample capsules for BixBench or workflows for IWC and retain all linked runs. The CompBioBench point estimate uses official submissions; there are no official item labels for a comparable paired interval.
16. Updated the active Quarto entry point and Brief Communication outline. Wrote [the findings](RESULTS.md), including which conclusions change with the score edition, the engineering actions supported by the failure records, and which claims require further experiments. Registered the new figures in the repository registry.
17. Used an isolated project environment for dependencies. The Python installer for Quarto encountered a long-path error; the official portable Quarto 1.11.9 release and TinyTeX 2026.11 were used for the manuscript build. Tooling stayed in the ignored virtual environment.
18. Rendered all eight exported PDFs for visual inspection. Shortened a clipped workflow label, made the request heatmap use vector cells, and checked axis labels, legend positions and PNG dimensions. Checked the manuscript HTML’s image references and enabled embedded resources so the HTML remains readable when moved. Verified the manuscript render in the Nature Methods citation profile across HTML, DOCX and PDF.
19. Fingerprinted source data and publication artifacts. The offline verification command checks source hashes, local links, figure registrations, format properties and headline numerical reconciliations. The [source register](sources_manifest.csv) and [output inventory](artifact_manifest.csv) identify the contents of this edition.
20. Repeated the offline table build against the recorded output hashes. The rebuilt tables passed the inventory check. The final Quarto render embedded both main figures in HTML, Word and the six-page PDF. Inspected the PDF pages and verified that the rendered text included the current BixBench sensitivity result.

## 2026-11-05 · Second artwork review at final print size

21. Opened the journal's current Brief Communication content-type guidance and its research-journal artwork guide. Compared the existing eight plates with the two-column dimensions, typography, color and vector requirements. Recorded the sources, criteria and panel-by-panel changes in the [figure review](FIGURE_REVIEW.md).
22. Reworked the main sequence into paired execution, benchmark-specific endpoints and model contrasts (Figure 1), followed by answer errors, historical failed requests, and observed token and interaction counts (Figure 2). Used separate denominators and source series for answer errors and request failures. Displayed the individual 50-task replicates and their means, including the single compact-stage observation.
23. Rebuilt six supplementary plates for execution routes and the yeast output comparison, replicate consistency, selection and regrading, request-failure classes, token campaigns and individual workflow scores. The IWC binning now uses the source-precision numerical values, and every one of the 240 cells has a task, model, policy, replicate and upstream locator. Preserved source versions and added the historical request ledger to Figure 2's input register.
24. Set the physical plate width to 180 mm, used editable Arial type within the publisher's point range, and added shape or pattern distinctions where meaningful. Used Poppler to proof all eight vector PDFs. Corrected an overlong design-box label and an overflowing request-count column header. Replaced the two final mean-only interaction plots with per-replicate marks.
25. Added a six-page supplementary PDF from the six original vector files and their canonical README legends. Windows denied access to a system temporary folder during the first assembly attempt. The working build uses only the project's ignored render tree for TeX intermediates. Selected vector PDF for the paper PDF, SVG for self-contained HTML, and a high-resolution PNG for Word. Added descriptive alternative text to the main figures and placed the figures next to their results.
26. Added automatic checks for physical dimensions, glyph bounds, embedded TrueType fonts, lettered panels, SVG text, RGB print resolution, legend consistency, and the three rendered manuscript formats. Rechecked the counts and scores against the benchmark records. Recorded the per-figure results in [artwork_checks.csv](artwork_checks.csv).
27. Fixed the plotting subprocess's hash seed and build timestamp, and made the supplementary assembly deterministic. Ran two independent full table, figure and supplementary builds on the recorded stack. All 62 files under the eight figure data and output folders plus the combined supplementary PDF matched by SHA-256 across builds. The [artifact inventory](artifact_manifest.csv) fingerprints the final version.

## 2026-11-06 · Independent review and second pass

28. Re-read the repository, the package, the manuscript and the 20-page report. Snapshotted the package, then reran the documented offline build. All tables, plates and the supplementary PDF were byte-identical to the 5 November files, and the verifier passed.
29. Checked the live website for drift. The three entry pages and `data/index.json` still carried `Last-Modified: Wed, 28 Oct 2026 01:15:59 GMT`, and the index hash matched `data/site/MANIFEST.csv`.
30. Recomputed the 14 headline claims independently. A separate agent wrote new code from `data/site` and the raw `sources/` files without reading `analysis/` or any figure `code/` or `dataset/` folder. All 14 matched:
    - BixBench 537/600 and 530/600.
    - CompBioBench 87.00 and 86.75, and reconstructed matches 1,039 and 1,059.
    - IWC 0.990 and 0.953.
    - 496/516 after the seven-question exclusion.
    - Execution routes, the six replicate-outcome distributions and the 133-failure census.
    - 7,098 historical request failures and the pooled token ratios 4.07, 2.48 and 0.96.
    - All optimization-batch values, all 77 report replacements, the promoter window and GC count, and the yeast DESeq2 comparison.

    Its additional observations are handled in steps 34–37.
31. Found that the page catalogue had been built from a fixed list of 12 supporting pages. A link-following crawl from the three entry pages found 67 linked pages and files that the list missed:
    - the 50 July 6 archive item pages;
    - `bixbench/july6/error-analysis/` and `bixbench/july6/tokens/`;
    - the ten IWC multi-step task pages;
    - five data files, including `iwc/data/wf007_ERR12833637_token_usage.tsv`.

    The token-drivers page is linked from no crawled page, so the crawler also refetches every previously catalogued URL. Rewrote `analysis/catalog_benchmark_pages.py` to discover pages, label archive and multi-step pages, and keep the original row and date for unchanged pages. All 172 earlier entries were byte-identical. The catalogue now holds 239 entries.
32. Read the pages that bear on the framing. Archived three pages in `sources/` and registered them with `summary_provenance.py --record-sources`. Only `web_pages.csv` changed fingerprint, and three rows were added:
    - `bixbench_index.html`, whose `#no-udt-baseline` card reports a May 2026 campaign without UDTs: 42/50 tasks, single runs, model not stated.
    - `bixbench_july6_index.html`, with four-condition accuracy.
    - `bixbench_july6_tokens_index.html`, with four-condition token totals.

    The July 6 model, GPT-5.5, comes from `supplement/notes/token_usage.md`, because the pages name only Codex.
33. Added the token-mechanism evidence that the outline planned but the package omitted, as Supplementary Fig. 7 (`s7_token_drivers`). The build parses the archived tables and checks them before plotting:
    - class shares sum to 100% and class totals to the total within page rounding;
    - per-run means equal totals divided by 150;
    - cached input per turn equals cached tokens divided by turns;
    - the turn and command ratios equal the totals' ratio within 0.006.

    The plate prints the page's own ratios (2.66×, 1.90×, 2.20×), not ratios of rounded means. Colours are the existing pair. In OKLab, normal-vision ΔE is 20.8; simulated protan, deutan and tritan ΔE are 10.0, 14.0 and 24.9. Contrast on white is 6.6 and 5.9.
34. Split the current BixBench failure census by policy in Figure 2a:
    - 63 Galaxy and 70 custom-code failures;
    - task specification 34 and 43, missing validation 15 and 16;
    - platform 3 and 0, harness 3 and 0, all three harness failures from DeepSeek.

    The independent recomputation produced the same split.
35. Added BixBench grading sensitivities to `s3_repeatability/dataset/sensitivity.csv`:
    - pre-review `raw_status` for every question: 523 and 521;
    - only bix-45-q1 graded by its pre-October status: 525 and 526, which reverses the sign;
    - bix-45-q1 excluded: 525/588 and 518/588.

    The manuscript reports the sign reversal.
36. Recorded each run's execution batch in `s2_reruns/dataset/run_batches.csv`. Besides the 77 report replacements, the exports identify:
    - 78 BixBench Galaxy runs from recovery or repeat batches (72 GPT-5.6 Luna, 2 GPT-5.6 Sol, 4 DeepSeek);
    - 52 CompBioBench runs marked as reruns that are not in the report, 34 of them GPT-5.5 Galaxy, with history names from 23 September to 1 October.

    No frozen source explains these replacements. The manuscript now discloses them, and the reason is listed for the authors.
37. Raised the bootstrap from 20,000 to 200,000 draws. The independent check found about 0.1-point seed-to-seed variation in the ten-cluster IWC bounds at 20,000 draws. Pooled intervals are now −1.48 to 4.25 (BixBench) and 0.80 to 7.31 (IWC), reported as −1.5 to 4.2 and 0.8 to 7.3. The point estimates are unchanged.
38. Populated `data/results_manifest.csv` with `analysis/build_results_manifest.py`. It holds one row for each of the 3,840 primary runs in the schema of `data/README.md`. 1,227 rows carry a run-specific trace path: all 1,200 BixBench runs and 27 IWC runs. CompBioBench publishes only a dataset folder. Trace dataset revisions are not published per run and are left blank with a note. CompBioBench `correct` marks the reconstructed item match, and IWC `correct` is blank because its endpoint is continuous.
39. Revised the manuscript:
    - Rewrote the abstract to give both conditions.
    - Added the BixBench sign sensitivity, the opposite direction of CompBioBench item matches, the concentration of the IWC difference, the condition split of failures and the custom-code any-of-three value (92%).
    - Added the no-UDT campaign, the July 6 token mechanism and the per-replicate unit for wait and request counts.
    - Added the replacement-batch disclosure, the sensitivity analyses, Data availability and Code availability statements, and Claude Code to the AI disclosure.
    - Added author TODO comments, which do not render, for the batch reasons, the Luna reasoning setting, trace access, the Zenodo DOI and author contributions.

    The main text, abstract and legends total 1,164 words before references.
40. Rebuilt the tables, nine plates, the seven-page supplement and the Nature Methods render. The verifier first rejected Figure 2d, whose new subtitle crossed the 180-mm edge; the subtitle was shortened. It then passed for nine plates, artwork, numbers, the results manifest and all three manuscript formats. A second full build reproduced all 70 data, output, supplement and results-manifest files byte for byte. The artwork measurements and output inventory were then rewritten.

## 2026-11-12 · Shared site loader from Jeremy Goecks's `accuracy-by-model` branch

41. Fast-forwarded the local branch to `421acfd` (origin `accuracy-by-model`), which adds `analysis/site_data.py`, `analysis/accuracy.py`, `data/accuracy_by_model.csv`, `data/accuracy_summary.csv` and `figures/sfig_accuracy_by_model/`. Its per-model and all-models accuracy agreed with this package for all 19 benchmark–model rows in both conditions, within the 0.005-point rounding of the new table; rerunning `accuracy.py` reproduced both committed tables byte for byte.
42. Removed this package's duplicate loader code in favour of `site_data.py`: `benchmark_records.py` now takes the website data path, JSON loader, model order and the BixBench, CompBioBench and IWC model and condition names from it, and `build_results_manifest.py` its condition names. `site_data._load` was changed to read UTF-8 explicitly; without it, Windows decoded three of the four exports as cp1252 (accuracy values were unaffected). `verify_site()` is kept, because `fetch_site_data.py --check` rejects Windows checkouts whose line endings Git converted.
43. `build_benchmark_summary.py` now stops unless its accuracy values match `data/accuracy_by_model.csv`, and the output inventory now covers `site_data.py`, `accuracy.py` and that table. The rebuilt results manifest and all package tables were byte-identical to their versions before the change, and the verifier passed.

## 2026-11-12 · Repository organization for the pull request

44. Kept work outside this paper on separate local branches: the IWC multi-step snapshots (`iwc-multistep-snapshots`), the AACR 2027 abstract and its code-versus-history counts (`aacr-2027-abstract`, embargoed until 2 March 2027) and the replicate-consensus table (`replicate-consensus`). The Brief Communication cites none of them.
45. Kept the author-supplied rerun report out of the public repository until its redistribution terms are confirmed. Its SHA-256 stays in the source manifest and its transcription in `s2_reruns/dataset/`. When the PDF is absent, `summary_provenance.py` skips only that checksum and `build_benchmark_summary.py` uses the transcription. Rebuilding the tables without the PDF reproduced every inventoried file byte for byte.
46. A build from a fresh export of the staged files failed the `sources/web_pages.csv` checksum. In `.gitattributes`, the later `*.csv text eol=lf` line overrode `sources/* -text`, so Git would have converted the CRLF line endings of the seven archived source CSVs. Moved the `sources/` rule last; the staged sources are now byte-identical to the registered files.
47. Ignored the outputs of the optional gated Verified-50 fetch, merged the manuscript's ignore rules into the repository's, removed the empty `figures/fig1_benchmark_overview` placeholder, updated the repository and folder READMEs, and rewrote the output inventory.

## Items for author review

- Review the seven unclassified current failures against their replacement traces; approve any new cause assignment at run level.
- Explain the 78 BixBench recovery or repeat runs and the 52 earlier CompBioBench reruns (`s2_reruns/dataset/run_batches.csv`), including whether replacement depended on the original outcome.
- Confirm the GPT-5.6 Luna reasoning setting (BixBench `max`, CompBioBench `high`) and the model of the May 2026 no-UDT campaign.
- Keep the official CompBioBench scores distinct from reconstructed item matches when citing results. The two point in opposite directions, and the private answer key remains unavailable.
- Confirm access and redistribution terms for the author-supplied report and the gated trace dataset before public archival deposit. Confirm author sign-off on the framing, labels, disclosures and journal submission.
- Testing whether specific Galaxy core changes, new installed tools or a prospective answer validator improve outcomes requires new evidence.

Steps 1–27 were prepared locally with OpenAI Codex (GPT-6). Steps 28–47 were prepared with Claude Code (Claude Opus 5.5). No new agent benchmark executions were launched.

## 2026-11-12 · Experimental design, model scores and answer validation

OpenAI Codex (GPT-6) redrew Figures 1 and 2 and Supplementary Figures 1 and 3 (numbered 1 and 2 at the time). The CSHL talk informed the visual sequence on pages 10, 13, 14 and 15. The October run manifest, official submissions and workflow scores supply the plotted data. The independent checks compare exact votes with run-level grades, the yeast gene sets with the raw curated output, and the promoter answer with the GRCh38 sequence. The [figure review](FIGURE_REVIEW.md) describes the panel changes and print checks.

The subsequent print revision set type to 6.5–7 pt at 180 mm, shortened all nine plates and fitted the supplement pages to their captions. Figure 1 uses one grouped bar chart with a zero baseline, a model-by-policy matrix in percent and paired intervals in percentage points. IWC means come from the unrounded workflow scores. The build retains native scores, counts and denominators alongside the plotted units.

## 2026-11-12 · Text review, citation order and failure categories

Claude Code (Claude Fable 5.2) checked the manuscript against the outline, the figures and their source data, then made these changes.

- Renumbered the supplementary figures in order of first citation. Reruns became Supplementary Fig. 2 (was 3), repeatability 3 (was 2), IWC outputs 4 (was 6), request failures 5 (was 4) and token use 6 (was 5). Folders, files, the figure list, legends and every cross-reference follow the new numbers, and earlier entries in this journal now use them.
- Split the Figure 2a "environment setup" group into task or scoring ambiguity (`SPEC`, `EVALUATOR`; 36 Galaxy and 48 custom-code runs), missing validation (`RIGOR`; 14 and 13) and platform or harness (`PLATFORM`, `HARNESS`; 6 and 0), beside model knowledge (1 and 4). The single group had placed benchmark problems under a label that reads as a Galaxy fault. The verifier now asserts these counts.
- Replaced the Figure 2c headline with a neutral heading. The old one joined an author estimate for GPT-5.5 to a measurement for GPT-5.6 Sol.
- Revised the main text: one topic sentence per paragraph, "X% versus Y%" result sentences, MCP defined at first use, the GPT-5.5 series in Fig. 2c described, and the prospective test added to the close.
- Added a Methods subsection on models and the Galaxy interface from the results exports and the token-usage note. Details those sources do not record are listed in an author TODO.
- Added references for Codex, IWC, MCP, DESeq2, PhyKIT, GENCODE and the UCSC Genome Browser, and replaced the CompBioBench runner link with the Zenodo record. Journal articles were checked against Crossref, the Zenodo record and web pages against their own pages.
- Rebuilt all tables, the nine plates, the results manifest, the supplement and the Nature Methods render, then rewrote the artwork measurements and output inventory. The verifier passed with the manuscript checks.
