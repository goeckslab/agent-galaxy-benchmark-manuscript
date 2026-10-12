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
| Main text, six paragraphs | 855 |
| Figure 1 legend | 125 |
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

### P2. The tool and the study (about 135 words; Fig. 1a)

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

### P4. Error analysis, lack of rigor/validation of results, and opportunities for using consensus to improve results (about 200 words; Fig. 2a,b)

The thread: errors come in two kinds.
Systematic errors repeat in every replicate and come mostly from the benchmark; random errors differ between replicates and come mostly from missing validation.
Consensus across replicates can only fix the second kind, and a validation step that picks a correct replicate would help more than a vote.

Sources: BixBench failure causes from `data/bixbench_failure_causes.csv` (PR #12); everything else from `analysis/replicate_consensus.py`, which writes `data/replicate_consensus.csv`, `data/bixbench_causes_by_agreement.csv`, `data/run_errors_by_correctness.csv` and `data/compbiobench_errors_by_domain.csv`.
A replicate group is the three replicates of one task, model and condition.
A run is correct when accepted (BixBench-Verified-50, CompBioBench) or at IWC output agreement ≥ 0.99, the threshold the figures use.

What each benchmark supports:
- BixBench-Verified-50: failure causes assigned from the traces of every incorrect run, plus everything below.
- CompBioBench: no failure-cause audit exists, so errors can be split by replicate agreement, answer agreement, task domain and execution errors, but not by cause.
- IWC: no failure-cause audit and no answer text; 44 incorrect runs over ten tasks, so treat its numbers as small-sample.

- Where errors come from:
  - BixBench (151 incorrect runs, causes from execution traces): 71% came from the benchmark, an under-specified task or reference answer (94) or a scorer rejecting a valid answer (13); 25% were agent errors, no validation of the answer (32) or wrong biological or statistical knowledge (5); Galaxy itself caused 3, and 4 runs submitted no answer.
  - Errors are concentrated in a few tasks on every benchmark: the five tasks with the most incorrect runs hold 97 of 151 (BixBench), 102 of 316 (CompBioBench) and all 44 (IWC).
  - CompBioBench by domain: epigenomics has 113 of the 316 incorrect runs from 20 of the 100 tasks, and its single structure task failed in 17 of 24 runs; machine-learning tasks failed 7 times with custom code and never in Galaxy.
  - Execution errors mark harder runs but do not separate right from wrong: incorrect runs had more failed commands or Galaxy jobs than correct ones (BixBench about 3.2 versus 2.0 per run; CompBioBench 6.2 versus 3.9 in Galaxy and 5.4 versus 2.5 with custom code), but 69–95% of correct runs also hit at least one error and recovered.
    So most wrong answers are not runs that broke; they are runs that finished and reported the wrong thing.
- Lack of rigor when agents are wrong: missing validation is the main agent-side cause in BixBench, and it is a primary or secondary cause in 116 of the 151 incorrect runs.
  It often turns an ambiguous task into a confidently wrong answer.
  - bix-30-q3: failed custom-code runs added exclusions, normalization and a statistical test the task did not ask for (Galaxy 12/12 correct, custom code 4/12).
  - Counter-example, CompBioBench variant-status-q1: the Galaxy runs that added a read-position check reached the right answer.
- Systematic versus random errors:
  - Incorrect runs in replicate groups where all three replicates were wrong: 105 of 151 (BixBench), 144 of 316 (CompBioBench), and 30 of 44 (IWC: 18 of 20 in Galaxy, 12 of 24 with custom code).
  - When all three replicates are wrong, they usually give the same wrong answer: 77–83% of such groups in BixBench and 61–64% in CompBioBench, which points to the task or the answer key rather than chance.
  - In BixBench, 85 of the 94 benchmark-specification errors are in all-wrong groups, while missing-validation errors are spread out: 16 of the 32 are in groups where the other two replicates were correct.
- Consensus helps a little; a validation step that picks the correct replicate would help more (Fig. 2b; table below):
  - A majority vote over three replicates adds 0 to 2.3 points.
  - At least one replicate was correct in 85–94% of replicate groups, so most of the room left is in groups where a correct answer was produced but not chosen.
  - A majority over all 12 runs of a task (four models × three replicates) reaches 89–92% on BixBench and CompBioBench, and 80% on IWC.
  - A vote on the answers themselves needs answers that can be compared: 10% of BixBench groups with three correct runs gave differently worded correct answers, so a text vote on BixBench scores below a single run; CompBioBench answers are more uniform (under 1%), and its text vote matches the estimate from correctness.
  - On IWC's continuous score, the median of three replicates raises mean agreement from 0.982 to 0.991 in Galaxy and from 0.946 to 0.964 with custom code; the best of three reaches 0.995 and 0.994, closing the gap between conditions.
- Disagreement between replicates flags answers to check: replicates split on 8–10% of BixBench groups, 15–17% of CompBioBench groups and 5–20% of IWC groups, without needing the true answer.
- Galaxy runs are more consistent, which cuts both ways: Galaxy replicates agree more often, so voting gains less in Galaxy (0.3 points against 2.3 for custom code on BixBench and CompBioBench; 1.7 against 0 on IWC, where 18 of the 20 Galaxy errors are in all-wrong groups).
  Consistent wrong answers need fixes in the tools, not votes: bix-45-q1 failed in all 12 Galaxy runs because the Galaxy PhyKIT version differs from the one behind the accepted answer (custom code 8/12).
  This leads into P6: agents as virtual users, and consensus across different methods rather than repeats of the same one.

Consensus table (`data/replicate_consensus.csv`; IWC correct at agreement ≥ 0.99):

| Benchmark, condition | Single run | Majority of 3 (from correctness) | Majority of 3 (from answers) | At least 1 of 3 correct (ceiling for picking a correct replicate) | Majority of 12 runs |
|---|---|---|---|---|---|
| BixBench-Verified-50, Galaxy | 87.7% | 88.0% | 86.5% | 91.5% | 92.0% |
| BixBench-Verified-50, custom code | 87.2% | 89.5% | 85.5% | 91.0% | 90.0% |
| CompBioBench, Galaxy | 87.0% | 87.3% | 87.3% | 94.3% | 91.0% |
| CompBioBench, custom code | 86.7% | 89.0% | 88.5% | 93.8% | 89.0% |
| IWC, Galaxy | 83.3% | 85.0% | – | 85.0% | 80.0% |
| IWC, custom code | 80.0% | 80.0% | – | 90.0% | 80.0% |

Caveats to state in Methods:
- The vote from correctness assumes correct answers agree; the vote from answers compares normalized answer text (trimmed, lower-cased, numbers rounded to three significant digits), which treats differently worded correct answers as disagreeing.
  Neither is a semantic comparison, which a real consensus step would need.
- In 3 groups, identical normalized answers were graded differently across replicates (1 BixBench, 2 CompBioBench); check these as possible grading inconsistencies.
- The 12-run vote counts ties as incorrect, so it is conservative.
- None of these consensus strategies were run; they are estimates from the existing runs.
- The committed tables were generated from PR #12's data before it merged; rerun the script once #12 merges.
- Before the paper claims anything about causes on CompBioBench or IWC, those benchmarks need the same trace-based cause audit as BixBench (316 and 44 incorrect runs).

### P5. What Galaxy adds, and what it costs (about 140 words; Fig. 2c,d)

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
- Legend: about 125 words; the current draft legends for Figs. 1 and 2 total about 450 words and need cutting by more than two-thirds.

### Figure 2: Errors, consensus, and what Galaxy records and costs

- a: Causes of incorrect BixBench runs, split by how many of the other replicates were correct (0, 1 or 2): shows systematic benchmark errors against random validation errors (`data/bixbench_causes_by_agreement.csv`).
  Extended Data Fig. 2a in PR #11 already draws this census; adapt it rather than build a new panel.
- b: Consensus panel, drawing the consensus table under P4: for each benchmark and condition (IWC at agreement ≥ 0.99), accuracy of a single run, a majority of 3 replicates, at least 1 of 3 correct, and a majority of 12 runs (new panel from `data/replicate_consensus.csv`).
  Show the vote from correctness and note the answer-text vote in the legend, or show both if space allows.
  For example, one row per benchmark and condition with the four values as points on a shared accuracy axis, so the gap between the vote and the ceiling is visible.
- c: An example Galaxy history or provenance record for one run (from Fig. 5 in PR #7).
- d: Tokens per run by condition, with the reduced-overhead BixBench runs if they are reported (from Fig. 5 in PR #7, plus a new panel).
- The task-level examples (bix-30-q3, bix-45-q1) move from the figure to the text.
- Legend: about 150 words for four panels is tight; if it runs over, move panel c to the Supplementary Information.

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
