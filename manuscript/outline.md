# Manuscript outline

Working outline for the paper.
This file is not rendered into the manuscript; it records the structure the sections are being written toward.
The Results outline below comes from Paulo Lyra's review comment on the Results heading in the Word draft (`Manuscript_2.docx`, 2026-09-28).

## Results

Each subsection lists the questions its text should answer.

### 1. Agents maintain bioinformatics accuracy when operating through Galaxy

- What is the performance in each benchmark? Does Galaxy differ from open-ended code?
- On Galaxy-derived IWC tasks, is performance higher and more consistent than on platform-neutral tasks?
- Why is performance preserved, and what explains the cases where the two environments disagree?
- What does this level of accuracy mean for the field?

Current draft text: "A paired benchmark of biomedical agents in Galaxy and open-ended code" (study design, Fig. 1) and "Agents perform similarly in Galaxy and open-ended code" (Fig. 2) in `results.qmd`.

### 2. Galaxy provides a structured environment for agent analyses

- Which tasks did agents complete through Galaxy?
- What enables agents to complete these tasks, and when and how do they use user-defined tools (UDTs)?
- What are the major error categories, and how do they differ between Galaxy tools, UDTs and open-ended code?
- Does Galaxy help agents recover from failures or set parameters better? What infrastructure changes would reduce these errors?

Current draft text: none yet.

### 3. Task solution variability is model-dependent

- Which tools and analytical routes did each model use?
- Does variability differ by model, and by benchmark?
- Is solution consistency related to task difficulty?
- Is path diversity good, bad, or neutral, and what should be expected?

Current draft text: none yet.

### 4. Galaxy increases analysis inspectability at higher token cost

- How many more input tokens does Galaxy use than open-ended code?
- Why does Galaxy use more tokens: more failed attempts, or something else?
- Is token use related to model capability?
- What does the extra cost buy, and when is it worth it?

Current draft text: none yet. The Figure 4 legend in `results.qmd` reports token totals for CompBioBench.

## Observations to fold into Results and Discussion

From Jeremy Goecks's review comment on the Results heading (2026-09-02).

Short notes:

- UDTs are a big win.
- Agents using Galaxy infrastructure is important.
- UI already exists in Galaxy for agents to use.
- Can use Galaxy even when agent quotas are met.

Junhao Qiu's longer version:

- Users don't need to rely on local storage or local computing resources.
  Some CompBioBench items generate tens to over 100 GB of intermediate artifacts, and in real-world day-to-day analyses, storage and computing requirements could be even larger.
- Galaxy already has a web-based interface that makes it easy to review what the agent did.
  AI can now generate content and perform tasks so quickly that it can be difficult for users to keep track of everything.
  People are starting to ask agents to create dashboards to track their work, but Galaxy already provides a system that has been developed and used for more than 20 years for reviewing analysis steps, outputs, and provenance.
- Users can easily continue from the agent's work in Galaxy or rerun the analysis themselves, at any time, in a no-code environment that uses no tokens.

## Open notes from the Word draft

These review comments were attached to Results text that was deleted in the draft's tracked changes, so they are kept here rather than in a section file.

- Confirm use of the MCP server and how we're using it. (Jeremy Goecks)
- Need a paragraph on Galaxy. Key points: Galaxy vs. no Galaxy; three sets of tasks; UDTs for Galaxy. (Jeremy Goecks)
- Write that we use open-ended code as a baseline comparison for agent performance. (Jeremy Goecks)
- Add a table with links to the benchmark materials and to the building blocks of the experiments (prompts, code, and so on); planned as Extended Data Table 1. (Paulo Lyra)

Comments attached to surviving text are kept as `REVIEW COMMENT` blocks in the relevant `.qmd` files.

## Inconsistencies to resolve

Noted while moving the draft into the repository; none of these were changed in the text.

- Scope: Introduction and Results describe three benchmarks (160 tasks, 3,840 runs, including IWC), but Online Methods describe only BixBench-Verified-50 and CompBioBench (3,600 runs) and have no IWC subsection.
- BixBench numbers: Results text gives 85.2% (open-ended code) and 86.5% (Galaxy); the Figure 3 legend gives 87.2% and 87.7%.
- CompBioBench numbers: Results text gives 86.7% and 87.1%; the Figure 4 legend gives 86.7% and 86.9%.
- Harness: Results say "Four Codex model configurations", Methods say DeepSeek V4 Pro was run through Codex, and the Fig. 1 legend says "DeepSeek V4 Pro (Claude Code, superseded) is reported separately" and mentions an unpaired GPT-6 Astra configuration.
- Naming: the Abstract and Discussion use "Galaxy-Bench"; the title comment and abstract comment question whether this paper introduces a benchmark.
  Condition names also vary ("Galaxy", "Galaxy-API code", "Galaxy-mediated execution").
- Figures 3 and 4 have legends but their Results text was deleted; the Results text cites Fig. 2d,e for the sensitivity analysis and Fig. 2f for IWC, but the Fig. 2 legend has panels a–e only, with d showing IWC runs and e showing BixBench failure causes.
- Bracketed placeholders remain in Methods (for example `[time limit]`, `[verifier model, version and provider]`, `[N]` bootstrap replicates, Galaxy commit hash).
- The draft has no reference list; citation numbers in the text are placeholders until entries are added to `references.bib`.
- Typos carried over: "envrionments", "taks-configuration", "open-coded".
