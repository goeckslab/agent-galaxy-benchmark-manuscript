# Outline: Nature Methods Brief Communication

Working outline for a Brief Communication version of the paper.
This file is not rendered into the manuscript.
The full-paper outline is in `outline.md`; this file reuses its terminology ("Galaxy" and "custom code") and its rule that every number traces to `data/results_manifest.csv` or a script in `analysis/`.

## Format constraints

From the Nature Methods Brief Communication guidelines (supplied by Jeremy Goecks, 2026-10-10).

- Abstract: up to 70 words, unreferenced.
- Main text: 1,200 words, or up to 1,600 at editorial discretion, counting abstract, references and figure legends.
  The target here is 1,500 words, which is above the standard limit and relies on editorial discretion.
- No sections or subheadings in the main text.
- Display items: at most 2 figures or tables (3 at editorial discretion).
- Online Methods with subheadings.
- References: about 20 as a guideline.
- Supplementary information is allowed.
  Whether Brief Communications may also carry Extended Data figures is not stated in the guidelines; confirm before planning on them.

## Framing

The article type covers "software platforms" and "highly practical tweaks to an existing method or tool".
The paper fits as a tool report: an interface that lets AI agents run bioinformatics analyses in Galaxy, with a paired evaluation showing that accuracy holds.

- Main claim: AI agents can perform bioinformatics analyses through Galaxy as accurately as with custom code, and the analyses they produce are recorded, inspectable and rerunnable.
- Not the claim: that this paper introduces a new benchmark ("Galaxy-Bench"), or that Galaxy beats custom code.
  Both follow Jeremy Goecks's review comments on the title and abstract (2026-09-07).
- Candidate title, adapted from Jeremy Goecks's title comment: "AI agents can perform accurate bioinformatics analyses through a computational workbench".

## Word budget (1,500 words)

| Part | Words |
|---|---|
| Abstract | 70 |
| Main text, six paragraphs | 830 |
| Figure 1 legend | 150 |
| Figure 2 legend | 150 |
| References, 20 entries | about 300 |
| Total | about 1,500 |

The reference estimate assumes about 15 words per entry in Nature style; check it with a word count of the rendered references.
If references count for more, cut main text first, then legends.

## Abstract (70 words)

One sentence each:

1. Gap: agent benchmarks in computational biology ask agents to write their own code; whether agents can work through a scientific workbench is untested.
2. What we did: an interface that lets agents run analyses in Galaxy, evaluated against custom code on 160 tasks from three benchmarks with four models.
3. Result: accuracy was similar in the two conditions on every benchmark.
4. Payoff: Galaxy runs leave a structured record of every tool, parameter and dataset, at a token cost that interface changes can reduce.

The abstract comment asks for concrete numbers (tasks, agents, accuracy); fit tasks and models into sentence 2 and, if words allow, one accuracy pair into sentence 3.

## Main text (six paragraphs, no headings)

### P1. The gap (about 130 words)

- Agents are being used for biomedical data analysis, and benchmarks now test whether they can complete whole bioinformatics analyses.
- These benchmarks evaluate agents as programmers: each agent writes and runs its own code.
- Scientific workbenches such as Galaxy are a widely used alternative for people: versioned tools, managed compute, and histories that record parameters, inputs and outputs and can be shared, turned into workflows and rerun.
- Whether agents can work through a workbench to complete bioinformatics tasks as accurately as they can write code has not been tested.

### P2. The tool and the study (about 160 words; Fig. 1a)

- One sentence about how we're filling this gap: a study evaluating agent performance on three bioinformatics benchmarks using Galaxy and using custom code.
- Define the two conditions here, once: Galaxy (all analysis runs as Galaxy jobs, including UDTs) and custom code (the agent installs software and writes its own code), with custom code as the baseline.
- Galaxy provides a Model Context Protocol server that gives agents tool search, parameter descriptions, history inspection, job submission and monitoring, and user-defined tools (UDTs) for operations no installed tool covers.
- Summarize evaluation: four model configurations in the Codex harness, 160 tasks (BixBench-Verified-50, CompBioBench, IWC-derived tasks), three replicates per task and condition, 3,840 runs.
- One sentence on why IWC is included: its tasks come from Galaxy workflows, so they test whether workbench-native tasks behave differently from platform-neutral ones.

### P3. Result 1: Agents can use Galaxy to accurately complete bioinformatics tasks at the same level of accuracy as custom code (about 170 words; Fig. 1b–d)

- BixBench-Verified-50, CompBioBench and IWC, one sentence each with the two condition values and the difference with its 95% interval.
- One sentence on robustness: differences stay near zero after removing tasks with audited benchmark-side problems.
- Use the numbers from PR #12 ("Results: update numbers to the site-matched scores"), which match the public results site and resolve the inconsistencies listed in `outline.md`.
  Do not draft numbers until #12 and the figure PRs it depends on (#4, #5, #11) are merged.

### P4. Error analysis, lack of rigor/validation of results, and opportunities for using consensus to improve results (about 150 words; Fig. 2a)

- Most incorrect runs come from a few tasks, and their causes are analytical decisions rather than execution failures (BixBench failure-cause adjudication, `data/bixbench_failure_causes.csv` in PR #12).
- Two contrasting examples:
  - bix-30-q3: Galaxy 12/12 correct versus custom code 4/12; failed custom-code runs added unrequested steps.
  - bix-45-q1: custom code 8/12 versus Galaxy 0/12, caused by a PhyKIT version difference between the Galaxy tool and the accepted answer.
- One-clause takeaway linking to analytical rigor: accuracy is limited more by analytical judgment than by the ability to run analyses (only if Results part 3 analyses in `outline.md` support it).

### P5. What Galaxy adds, and what it costs (about 140 words; Fig. 2b,c)

- Every Galaxy run leaves a structured record: tool identities and versions, requested and resolved parameters, datasets and job states (archive totals of Galaxy jobs and interface calls from the Fig. 1 legend).
  People can review the analysis in the existing Galaxy interface and rerun or continue it without using model tokens.
- Cost: Galaxy runs used more tokens than custom-code runs (CompBioBench total in the Fig. 4 legend draft).
- The overhead comes from the interface rather than from failed analyses: on BixBench with GPT-5.6 Sol, interface and waiting-behavior changes cut the Galaxy-to-custom-code ratio from 3.45× to 1.53× with accuracy unchanged (Junhao Qiu's update in `outline.md` Results part 4).
  This depends on decisions still open there: whether those runs are reported as a follow-up, and adding them to the manifest.

### P6. Implications (about 80 words)

- Agents act as virtual users of Galaxy: their traces point to specific fixes in documentation, API design and tool and parameter descriptions (the token-reduction work is an example).
- Galaxy makes rigor-improving approaches cheap, such as running several methods for the same step and comparing them, or validating results before reporting; present these as hypotheses this study did not test.
- One sentence of limitations: a fixed set of models and benchmarks, prompts that differ between conditions, and models that change quickly.

## Display items (2)

### Figure 1: Design and accuracy

- a: Study design schematic: same model configuration, two conditions, the Galaxy interface (from Fig. 1 in PR #4).
- b–d: Condition difference (Galaxy − custom code) per benchmark with 95% intervals, by model and pooled (from Fig. 2a–c in PR #5).
- Legend: about 150 words; the current draft legends for Figs. 1 and 2 total about 450 words and need cutting by two-thirds.

### Figure 2: What Galaxy records and costs

- a: Tasks with the largest condition-specific differences, including bix-30-q3 and bix-45-q1 (from draft Fig. 3d or Fig. 4 in PR #10).
- b: An example Galaxy history or provenance record for one run (from Fig. 5 in PR #7).
- c: Tokens per run by condition, with the reduced-overhead BixBench runs if they are reported (from Fig. 5 in PR #7, plus a new panel).
- Legend: about 150 words.

### Optional third item (editorial discretion)

A table of benchmark materials and building blocks (prompts, code, traces, results site), planned as Extended Data Table 1 in `outline.md`.
Move it to the Supplementary Information if the editor does not allow a third item.

### Moved to Supplementary Information

Fig. 3 (structured environment, PR #6), Fig. 4 (answer agreement and tool use by model, PR #10), Extended Data Figs. 2–7 (PR #11), sensitivity analyses, failure-cause adjudication, and per-model results.

## Online Methods (with subheadings)

Online Methods are outside the main-text word count.
Start from the existing `methods.qmd` sections and add what is missing.

- Benchmarks: BixBench-Verified-50, CompBioBench, and IWC-derived tasks (add the IWC subsection; current Methods describe only two benchmarks).
- Galaxy interface: the MCP server, its operations, UDTs, and the server used (usegalaxy.org); new.
- Models and agent harness: settle the harness inconsistency listed in `outline.md` (Codex versus Claude Code for DeepSeek V4 Pro; treatment of GPT-6 Astra).
- Execution conditions and prompts: including the execution policy in Galaxy prompts and prompt lengths.
- Experimental design.
- Answer evaluation: one subsection per benchmark, including the reconstructed CompBioBench answer key and results-site scoring.
- Failure-cause adjudication.
- Token accounting: extend from CompBioBench to all benchmarks.
- Statistical analysis: fill in the bracketed placeholders (bootstrap replicates and others).
- Data availability, code availability, and use of AI tools.

## References (about 20)

Slots to fill with checked entries, never with unverified citations:

- Biomedical AI agents: 2–3.
- Agent benchmarks for bioinformatics: BixBench, CompBioBench, plus 1–2 others.
- Agent systems and scaffolds: Biomni, Agentomics, and 1–2 studies showing that the scaffold affects performance.
- Galaxy and the Intergalactic Workflow Commission: 2–3.
- Model Context Protocol: 1.
- Tools named in the text, such as PhyKIT: 1–2.
- Models and harness (Codex, model reports): 2–3.

## Decisions before drafting

- Article type: Brief Communication versus Analysis or Resource (`_quarto-nmeth.yml` lists it as undecided).
- Word target: 1,500 words needs editorial discretion; plan cuts down to 1,200 if the editor holds to the standard limit.
- Whether the token-reduction runs appear in the main text, in the supplement, or not at all.
- Which models are reported: the four paired configurations only, or also DeepSeek V4 Pro under Claude Code and GPT-6 Astra.
- Whether IWC stays in the main text or moves to the supplement to save words.
