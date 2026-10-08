# Manuscript outline

Working outline for the paper.
This file is not rendered into the manuscript; it records the structure the sections are being written toward.
The Results outline below comes from Paulo Lyra's review comment on the Results heading in the Word draft (`Manuscript_2.docx`, 2026-09-28).

## Terminology

The two execution conditions are called **Galaxy** and **custom code** throughout the repository.

- **Galaxy:** all analysis ran as Galaxy jobs, using installed Galaxy tools or user-defined tools (UDTs). Agents may write code to drive Galaxy through its API or to build a UDT; the condition is still Galaxy.
- **Custom code:** agents installed software and wrote and ran their own analysis code in a local workspace.
- Use "the Galaxy condition" and "the custom-code condition" when a noun phrase is needed, and hyphenate "custom-code" before a noun ("custom-code runs").
- Retired terms: "open-ended code", "open-ended code execution", "unrestricted code execution", "direct code generation", "Galaxy-API code", "Galaxy-mediated execution" and "code-only".
- Define both terms once in the paper, where the conditions are first introduced.

## Results

Each subsection lists the questions its text should answer.

### 1. Agents maintain bioinformatics accuracy when operating through Galaxy

- What is the performance in each benchmark? Does Galaxy differ from custom code?
- On Galaxy-derived IWC tasks, is performance higher and more consistent than on platform-neutral tasks?
- Why is performance preserved, and what explains the cases where the two environments disagree?
- What does this level of accuracy mean for the field?

Current draft text: "A paired benchmark of biomedical agents in Galaxy and custom code" (study design, Fig. 1) and "Agents perform similarly in Galaxy and custom code" (Fig. 2) in `results.qmd`.

### 2. Galaxy provides a structured environment for agent analyses

- Which tasks did agents complete through Galaxy?
- What enables agents to complete these tasks, and when and how do they use user-defined tools (UDTs)?
- What are the major error categories, and how do they differ between Galaxy tools, UDTs and custom code?
- Does Galaxy help agents recover from failures or set parameters better? What infrastructure changes would reduce these errors?

Current draft text: none yet.

Agents as virtual users of Galaxy (Jeremy Goecks, 2026-10-05): agent use of Galaxy can identify where Galaxy can be improved, through better documentation, API design, and clarity of tools and parameters.
This subsection should carry the evidence; the Discussion carries the framing (see below).

- Evidence still to produce: a breakdown of Galaxy-condition failures by what would fix them (documentation, API design, tool or parameter descriptions, tool versions), building on the planned split of failures into platform limitations and agent errors.
  No such analysis exists yet in `analysis/`, and every number must trace to `data/results_manifest.csv` or a script there.
- Candidate examples from the Word draft:
  - BixBench bix-45-q1: Galaxy used PhyKIT v.2.1.93, whose handling of gaps and ambiguous residues differed from PhyKIT v.2.0.3, the version associated with the accepted answer; this points to clearer tool versioning and documentation of version differences (from Results text deleted in the draft's tracked changes).
  - Prompt length: Galaxy prompts needed an execution policy (history use, permitted tools, UDT rules, interface timeouts) and were longer than custom-code prompts on BixBench (707 versus 366 median words) and CompBioBench (938 versus 227), though not on IWC (333 versus 344).
    Each rule in that policy marks something an agent could not work out from Galaxy alone, so it is a candidate documentation or API gap.

### 3. Task solution variability is model-dependent

- Which tools and analytical routes did each model use?
- Does variability differ by model, and by benchmark?
- Is solution consistency related to task difficulty?
- Is path diversity good, bad, or neutral, and what should be expected?
- Do agents show less analytical rigor than they could, especially on harder tasks?

Current draft text: none yet.

Analytical rigor (Jeremy Goecks, 2026-10-05): benchmarking results suggest agents are not as rigorous as they could be, especially on more difficult problems.
This subsection should carry the evidence; the Discussion carries the recommendation (see below).

- Evidence still to produce: whether verification steps, or agreement of answers across replicates, track accuracy, and whether the gap widens with task difficulty (for example, difficulty measured as the replicate failure rate per task).
  No such analysis exists yet in `analysis/`, and every number must trace to `data/results_manifest.csv` or a script there.
- Candidate examples from the Word draft (mostly in Results text deleted in its tracked changes):
  - CompBioBench variant-status-q1 (GPT-5.6 Sol): two of three Galaxy replicates reached the correct homozygous call after adding a read-position allele audit or position-aware diagnostic; all three custom-code replicates returned an incorrect heterozygous call.
  - BixBench failures were analytical decisions rather than execution failures: bix-26-q5 combined directional enrichment results incorrectly, bix-54-q7 depended on which observations were included, and failed custom-code runs of bix-30-q3 added unrequested exclusions, normalization and a statistical test.
  - IWC: every required step ran in all runs, yet parameter choices (for example, amplicon filtering and truncation) still lowered output scores.
  - IWC ATAC-seq: agents switched between MACS2, MACS3 and Genrich across replicates, a natural experiment for whether a consensus across methods would help.

### 4. Galaxy increases analysis inspectability at higher token cost

- How many more input tokens does Galaxy use than custom code?
- Why does Galaxy use more tokens: more failed attempts, or something else?
- Is token use related to model capability?
- What does the extra cost buy, and when is it worth it?

Current draft text: none yet. The Figure 4 legend in `results.qmd` reports token totals for CompBioBench.

Reducing Galaxy token overhead on BixBench (Junhao Qiu, added 2026-10-07): a third round of interface and execution changes cut Galaxy token use on BixBench by more than half without lowering accuracy.
It follows the process of identifying where the extra tokens come from, changing the interface and execution behavior, and measuring the complete benchmark again.

- Setup: GPT-5.6 Sol, all 50 BixBench tasks, three new Galaxy replicates.
  The custom-code baseline is the existing three custom-code replicates of the same tasks with the same model.
- Tokens per 50-task run:
  - Custom code: 35.51M.
  - Previous Galaxy runs: 122.41M (3.45× custom code).
  - Interface changes 1 and 2 below, one complete replicate: 85.93M (2.42×).
  - Interface changes 1 and 2 plus the longer-wait instructions, mean of three replicates: 54.35M (1.53×), 55.6% lower than the previous Galaxy runs.
- Accuracy of the three new replicates: 46/50, 46/50 and 45/50.
- Changes, each aimed at one source of overhead:
  1. Repeated context: the MCP interface already returned summaries and saved full execution records, but summaries could still repeat output text and detailed check results.
     It now returns short check statuses, removes duplicate output references, and returns an "unchanged" notice pointing to the earlier record when the agent re-inspects unchanged content such as tool parameters.
     Inline result text is capped at 4 KiB per output and 8 KiB per reply; full requests, responses and job details are still saved for inspection.
  2. Parameter submission and retries: shorter parameter descriptions, fill-in templates showing required fields and format (for example, where a Galaxy dataset ID goes), and parameter checks with fewer false warnings.
     For UDTs, checks before job submission now catch errors such as a script referring to an undeclared input or two outputs with the same name.
  3. Repeated waiting requests: agents were told to wait at least five minutes, preferably thirty, before checking an asynchronous operation again, reusing instructions from some later CompBioBench runs.
     MCP already waited for Galaxy jobs; the remaining overhead was the model repeatedly checking whether the MCP call had returned.
     Waiting calls fell from 481 in the preceding complete replicate to a mean of 78 per run across the three new replicates, and model requests from 1,799 to a mean of 1,332.
- Why it matters: it answers "why does Galaxy use more tokens" with measured sources of overhead (repeated context, retries, polling) rather than failed analyses, and shows the cost gap is largely an interface property that can be engineered down.
  It is also a worked example of agents as virtual users (Results part 2 and Discussion): agent traces pointed to specific interface fixes.
- Open questions before this goes into the text:
  - These numbers are not yet in `data/results_manifest.csv` or a script in `analysis/`; the run records exist alongside the previous results and need to be added before any number is cited.
  - Whether these runs replace the main Galaxy BixBench results or are reported as a follow-up experiment, since they use a different interface from the other Galaxy runs.
  - Online Methods describe token accounting for CompBioBench only; it needs extending to BixBench, and the message does not say whether these are total or input tokens.
  - "Previous Galaxy runs" is "the previous website Galaxy runs" in Junhao's message; confirm which runs these are.

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

## Discussion

### Improving analytical rigor

From Jeremy Goecks (2026-10-05).
Agents and Galaxy would benefit from approaches that improve rigor, such as consensus across different methods and automated follow-up validation.

- Placement: a new paragraph after the one beginning "The benchmark is designed to define practical reliability boundaries" and before the paragraph on skills and prompts in `discussion.qmd`.
  - It follows from the reliability-boundaries paragraph, which already names "subtle parameter choices" as a risk.
  - It extends the skills-and-prompts paragraph, which already mentions prompting agents to "verify outputs" and notes that guidance does not fix "scientific judgment": the point is to build verification into the system rather than leave it to the agent.
- Proposals:
  - Consensus: run several methods for the same analytical step and compare or combine their answers.
  - Automated follow-up validation: run checks on results before the agent reports an answer.
- The Galaxy angle: these approaches are cheap in Galaxy and costly with custom code.
  Galaxy offers several tools for the same step, workflows can run them side by side, and histories make the comparison auditable.
  Reruns and extra workflows cost no model tokens, which ties to Results part 4 (token cost) and Junhao's point about rerunning at no token cost.
- Smaller mentions:
  - Add consensus and automated validation to the future-extensions paragraph.
  - The study did not test these approaches, so present them as hypotheses in the limitations paragraph or wherever they appear.
  - Once Results support it, one sentence in the Abstract or Introduction, for example that accuracy is limited more by analytical rigor than by the ability to execute analyses.

### Agents as virtual users of Galaxy

From Jeremy Goecks (2026-10-05).
Agents using Galaxy act as virtual users, and their use can identify where Galaxy can be improved: documentation, API design, and clarity of tools and parameters.

- Placement: expand the `discussion.qmd` paragraph beginning "Galaxy-Bench reframes biomedical agent evaluation", or add a paragraph right after it.
  - That paragraph already says Galaxy "exposes weaknesses" such as "tool-search inefficiency, state-tracking errors and difficulty substituting available tools for unavailable operations".
  - The next paragraph already says that classifying failures as platform limitations or agent errors "identifies which problems require better Galaxy tooling and which require better agent reasoning".
- Framing: agent runs work as large-scale, repeatable usability testing.
  Every failed tool search, misread parameter or retry is recorded in the Galaxy history, which points to specific fixes in documentation, API design, and tool and parameter descriptions.
- Smaller mentions:
  - Future-extensions paragraph: feed agent traces back to Galaxy developers and tool authors as a continuous improvement loop.
  - Junhao's point about the existing Galaxy interface (see "Observations to fold into Results and Discussion"): the same interface that helps people review an agent's work also shows where agents struggle.

## Open notes from the Word draft

These review comments were attached to Results text that was deleted in the draft's tracked changes, so they are kept here rather than in a section file.

- Confirm use of the MCP server and how we're using it. (Jeremy Goecks)
- Need a paragraph on Galaxy. Key points: Galaxy vs. no Galaxy; three sets of tasks; UDTs for Galaxy. (Jeremy Goecks)
- Write that we use custom code as a baseline comparison for agent performance. (Jeremy Goecks)
- Add a table with links to the benchmark materials and to the building blocks of the experiments (prompts, code, and so on); planned as Extended Data Table 1. (Paulo Lyra)

Comments attached to surviving text are kept as `REVIEW COMMENT` blocks in the relevant `.qmd` files.

## Inconsistencies to resolve

Noted while moving the draft into the repository; none of these were changed in the text.

- Scope: Introduction and Results describe three benchmarks (160 tasks, 3,840 runs, including IWC), but Online Methods describe only BixBench-Verified-50 and CompBioBench (3,600 runs) and have no IWC subsection.
- BixBench numbers: Results text gives 85.2% (custom code) and 86.5% (Galaxy); the Figure 3 legend gives 87.2% and 87.7%.
- CompBioBench numbers: Results text gives 86.7% and 87.1%; the Figure 4 legend gives 86.7% and 86.9%.
- Harness: Results say "Four Codex model configurations", Methods say DeepSeek V4 Pro was run through Codex, and the Fig. 1 legend says "DeepSeek V4 Pro (Claude Code, superseded) is reported separately" and mentions an unpaired GPT-6 Astra configuration.
- Naming: the Abstract and Discussion use "Galaxy-Bench"; the title comment and abstract comment question whether this paper introduces a benchmark.
- Figures 3 and 4 have legends but their Results text was deleted; the Results text cites Fig. 2d,e for the sensitivity analysis and Fig. 2f for IWC, but the Fig. 2 legend has panels a–e only, with d showing IWC runs and e showing BixBench failure causes.
- Bracketed placeholders remain in Methods (for example `[time limit]`, `[verifier model, version and provider]`, `[N]` bootstrap replicates, Galaxy commit hash).
- The draft has no reference list; citation numbers in the text are placeholders until entries are added to `references.bib`.
- Typos carried over: "envrionments", "taks-configuration".
