# Paper outline: Nature Methods Brief Communication

Proposed outline for the paper, written on 16 November 2026 from the 28 October 2026 results release.
This file is not rendered into the manuscript.
The current draft, `brief-communication.qmd`, still follows `outline-brief-communication.md`; the section "What changes from the current draft" lists the differences.
The two conditions are called "Galaxy" and "custom code", as fixed in `outline.md`.
Every number below was recomputed from `data/site/` or read from a table listed under "Where each number comes from".
All numbers stay provisional until one results release is frozen.

## The argument

AI agents analyse biological data as accurately through Galaxy as with custom code, and every Galaxy run leaves a record a researcher can open and review.
The paper is a tool report: the agent interface is the method, and the paired comparison is its validation.

| Claim | Evidence | Paragraph | State of the evidence |
|---|---|---|---|
| Agents can operate Galaxy on their own | The interface, and 2,010 completed Galaxy runs, each linked to a history | 2 | In hand; the interface code is not public yet |
| Working through Galaxy costs no accuracy on tasks written for code-writing agents | Paired differences on 150 published questions | 3 | In hand; no equivalence margin stated; CompBioBench has no item-level official grades |
| It costs none when the analysis has many steps | Ten multi-step analyses, 180 runs | 4 | Three models; wide interval; references built in Galaxy |
| Each run is reviewable | A history per run, the share of runs with agent-written tools, one traced example | 5 | Counts exist, some on a side branch; no rerun test yet |
| Checking, not execution, limits accuracy | Failure-cause audit and agreement between replicates | 6 | BixBench only; 7 of 133 failures unreviewed |
| The token cost can be engineered down | Token ratios in the main runs and after interface changes | 7 | One model on one benchmark; the early baseline has no run records |

What the paper does not claim:

- That Galaxy beats custom code.
  The BixBench and multi-step intervals include zero, and the IWC references were built in Galaxy.
- That it introduces a benchmark.
  BixBench-Verified-50 and CompBioBench are published by others, and the IWC tasks are a stress test described in Methods.
- That analyses were reproduced.
  A recorded history is not a rerun; claim "rerunnable" only after rerunning a sample.
- That consensus improves accuracy.
  The gains are estimated from existing runs, and no voting step was executed.

Title options:

- "Galaxy lets AI agents run accurate, inspectable bioinformatics analyses" names the tool, as tool papers usually do.
- "AI agents can perform accurate bioinformatics analyses through a computational workbench" is the candidate adapted from Jeremy Goecks's title comment.
- The current title, "Improving Galaxy's interface for agents running biological analyses", fits the earlier framing and not this one.

## Which IWC results the paper reports

The repository holds two sets of ten IWC tasks, and the paper's IWC result is the harder set.

| | IWC workflow tasks | IWC multi-step tasks |
|---|---|---|
| Task | Reproduce one IWC workflow of 2 to 27 tool steps; the final output is compared with the reference | Carry a full analysis from raw data to 8–12 scored results; the task text names no software |
| Source file | `data/site/iwc/data/results.json` | `data/site/iwc/long-chain/data/results.json` |
| Runs | 240, four models | 180, three models (GPT-5.5 not run) |
| Galaxy versus custom code | 99.0% versus 95.3% mean output agreement | 67.5% versus 58.7% of results passing |
| Spread between models | 98.5% to 99.9% in Galaxy | 49.5% to 89.9% in Galaxy |
| Role in the paper | One clause in P4 and a supplementary figure | Abstract, P4 and Fig. 1b,c |

The workflow tasks cannot separate conditions or models, because five of the ten are at ceiling in both conditions.
The multi-step tasks can, and each one is a whole analysis and not a single workflow.
Any plan that reports 0.990 against 0.953 as "the IWC result" is describing the easier set.
The current draft excludes the multi-step tasks as a pilot, so using them means bringing their analysis onto the paper branch and closing the gaps listed under "Work before submission".

## Format and word budget

A Brief Communication allows 1,200 words including abstract, references and figure legends, or 1,600 at the editor's discretion.
This plan totals about 1,520 words and so relies on that discretion.

| Element | Journal limit | This plan |
|---|---|---|
| Abstract | 70 words, unreferenced | 70-word draft |
| Main text | Inside the 1,200 (1,600) total; no sections or subheadings | 8 paragraphs, 900 words |
| Display items | 2 figures or tables, 3 at discretion | 2 figures of 3 panels each; legends 250 words |
| References | About 20 as a guideline | 20, about 300 words |
| Online Methods | Required, with subheadings; outside the count | All implementation detail |

Fit with the article type.
The journal lists software platforms and practical improvements to existing tools as Brief Communication material.
A paper that reads as a comparison of established tools may be redirected to the longer Analysis format, so keep the agent interface as the subject.

If the editor holds to 1,200 words, cut in this order:

1. Move P7 to a Supplementary Note, leaving one sentence in P8 (saves about 90).
2. Trim references to 15 (saves about 75).
3. Trim legends to 180 words (saves about 70).
4. Move the robustness sentence of P3 and the consensus bullet of P6 to Methods (saves about 60).
5. Move the interface detail of P2 to Methods (saves about 30).

Keep P4.
It is the paper's own task set and its least saturated result.

## Drafting rules

These come from the three model papers named in the planning notes (Tangermeme, Multi-Embed and continuous mass photometry).

1. Affirm, then turn: open with what the field can do and pivot on "but" in the same sentence.
2. Name the method in sentence two, starting "Here we".
3. Narrow the gap in steps: field, current approach, what is still missing.
4. Introduce the solution in one sentence that says what it is and why it differs.
5. One angle per paragraph: the angle, the setup in a clause, the numbers, then one sentence on what they mean.
6. End on what the tool is, what it enables and its limits, with no separate discussion.

## Paragraph outline

Eight paragraphs and 900 words.
Each has a title stating its one message and bullets saying how it is delivered.
The titles are drafting labels and come out before submission.
Each pair of numbers is Galaxy first, then custom code.

### Abstract (70 words, three sentences)

- Affirm, then turn: agents can run bioinformatics analyses, but by writing code that is hard to inspect and reproduce.
- What we did: made Galaxy usable by agents and compared it with custom code in 4,020 runs of 170 tasks.
- Result and payoff: accuracy was at least as high through Galaxy, and each run left a record of tools, parameters and data.

Draft, 70 words:

> AI agents can run bioinformatics analyses, but only by writing code that is hard to inspect and reproduce. Here we make the Galaxy workbench usable by agents and compare it with custom code in 4,020 runs of 170 tasks. Through Galaxy, agents were at least as accurate on BixBench (89.5% versus 88.3%) and on multi-step analyses (67.5% versus 58.7%), and each run left a record of tools, parameters and data.

"At least as accurate" describes the point estimates.
Change it to "as accurate" only if an equivalence margin is stated and met.

### P1. Agents can run whole analyses, but only as programmers

100 words. Job: affirmation, problem, gap.

- Affirmation: agents now plan and execute multi-omic, single-cell and machine-learning analyses, and benchmarks such as BixBench and CompBioBench measure how well.
- Problem: in these benchmarks the agent writes and runs its own code.
  The result is scripts, ad hoc environments and intermediate files that a reader must reconstruct to check an answer.
- Gap: workbenches such as Galaxy give people versioned tools, managed compute and recorded histories.
  Whether agents can work through one without losing accuracy has not been tested.

### P2. An interface lets agents operate Galaxy, and we test it against custom code

130 words. Fig. 1a. Job: the solution in one sentence, why it differs, how it was tested.

- The tool: a Model Context Protocol server gives agents tool search, parameter schemas, job submission and monitoring, and history inspection.
  One call submits a job, waits for it, checks the resolved inputs and parameters and returns a compact result.
  Skills supply analysis know-how.
- Why it differs: agents keep the freedom to write code through user-defined tools (UDTs), but every step runs as a Galaxy job and is recorded.
  Define "Galaxy" and "custom code" here, once.
- The test: four model configurations in one Codex harness (GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro), two conditions, three replicates.
  The tasks are 150 questions from two published benchmarks (3,600 runs), ten IWC workflow tasks (240 runs) and ten multi-step IWC analyses run by three of the models (180 runs).
  That gives 170 tasks and 4,020 runs, 2,010 of them through Galaxy.

### P3. Accuracy is the same in Galaxy and custom code on platform-neutral tasks

120 words. Fig. 1b. Job: the central result.

- Angle: BixBench-Verified-50 and CompBioBench were written for code-writing agents, so they give Galaxy no home advantage.
- Numbers: BixBench 89.5% versus 88.3% of answers accepted (537 and 530 of 600; difference 1.2 points, 95% interval −1.5 to 4.2).
  CompBioBench 87.0% versus 86.8% of official points (87.00 and 86.75).
- Reading: the model mattered more than the condition.
  BixBench accuracy ranged over 10 points between models (83.3% to 93.3% in Galaxy), while the per-model difference between conditions ranged from −0.7 to +3.3 points across both benchmarks.
- Robustness, one sentence: the raw BixBench key gives 87.2% versus 86.8% (523 and 521).
  State openly that the sign rests on one question: grading bix-45-q1 by its earlier key gives 525 versus 526.
  The reconstructed CompBioBench key points the other way, 86.6% versus 88.3% (1,039 and 1,059 of 1,200; difference −1.7, interval −3.8 to 0.5).
  Each of these differences, and both intervals, lie inside ±5 points.

### P4. On ten harder multi-step analyses, Galaxy holds, and leads where the toolchain is hard to assemble

120 words. Fig. 1b,c. Job: a different question from P3, namely whether parity survives a whole analysis.

- Angle: a benchmark question ends in one answer, and a real analysis chains many steps.
  Ten tasks based on reviewed IWC workflows each run from raw data to 8–12 scored results, and the task text names no software.
  Setup clause: ten shorter IWC workflow tasks were near ceiling in both conditions (99.0% versus 95.3% output agreement), so they go to the supplement.
- Numbers: 67.5% versus 58.7% of results passed (difference 8.8 points, 95% interval −6.1 to 27.1), and Galaxy was higher in 7 of the 10 tasks.
  For the strongest model, GPT-5.6 Sol, the values were 89.9% versus 88.0%.
- Where the gap is: multiplex tissue imaging, 86.4% versus 8.6%.
  Galaxy supplied the whole imaging toolchain; custom-code agents substituted other methods, in some cases because a package could not be installed.
  Without that task the values are 65.4% versus 64.3%.
  The gap can also run the other way: 16S amplicon analysis, 59.7% versus 90.3%.
- Reading: conclude "no penalty as analyses lengthen, and an advantage where specialized software is hard to install", not "Galaxy wins on hard tasks".
  The references were built in Galaxy, and ten tasks cannot support the second.
  Close on the strictest measure, which leads into P6: every result was right in only 22 versus 21 of 90 runs.

### P5. Every Galaxy run leaves a record a researcher can open

120 words. Fig. 2a. Job: the differentiator, with counts.

- What is recorded: tool identity and version, requested and resolved parameters, input and output datasets, and job states, viewable in the standard Galaxy interface without spending tokens.
- Counts: each of the 2,010 Galaxy runs links to a Galaxy history.
  On CompBioBench agents used a UDT in 844 of 1,200 runs (70%) and installed tools alone in 352 (29%), so the record covers agent-written steps too, and the text must say what it keeps for them.
  On BixBench a UDT was recorded in 234 of 600 runs.
- What a reader has to open: a multi-step Galaxy history held a median of 89 items, and the agent wrote a median of 21 lines of code, against at least 244 lines in a custom-code run.
  Do not extend the code comparison to the question benchmarks, where the medians are 109 and 123 lines.
- Traced example: bix-45-q1.
  Under the original answer key all 12 Galaxy runs failed and 8 of 12 custom-code runs passed.
  The tool version recorded in the histories shows why: Galaxy's PhyKIT release differs from the one behind the accepted answer.
  Both values are now accepted, and all 24 runs pass.

### P6. Checking, not execution, limits accuracy

130 words. Fig. 2b. Job: the unexpected finding, and the honest reading of consensus.

- Errors are systematic: on BixBench three questions account for 71 of the 133 incorrect runs and fail in both conditions, while 30 of the 50 questions were answered correctly in all 24 runs.
  The audit attributes 84 incorrect runs to task or scoring ambiguity and 27 to missing validation by the agent.
- Execution is rarely the cause: 6 of 133 incorrect runs trace to the platform or harness, all in Galaxy, and 5 to model knowledge.
  Eleven have no cause assigned (4 unresolved, 7 awaiting review).
- Two kinds of error: 72 of the 77 task-specification errors, the larger part of the 84, sit in groups where all three replicates failed.
  By contrast, 16 of the 31 runs with a missing-validation label (27 assigned, 4 unresolved) had two correct sibling runs.
- Repeats help little: on BixBench a majority of three adds 0.5 points in Galaxy and 2.2 with custom code.
  At least one replicate is correct in 93% and 92% of groups, but choosing it needs the answer, so it is a ceiling and not a method.
  A real vote on answer strings scored below a single run (82.5% and 80.0%), because correct answers are worded differently.

### P7. The token cost comes from the interface and can be engineered down

110 words. Fig. 2c. Job: practicality.

- Cost in the main runs: Galaxy used 4.07 times the tokens of custom code on BixBench, 2.48 on CompBioBench, 1.47 on the multi-step analyses and 0.96 on the IWC workflow tasks.
- Where it went: cached context re-read over more steps, not reasoning.
  In an earlier GPT-5.5 batch, Galaxy runs took 2.66 times as many agent turns, each carrying 2.20 times as much cached context; cached input was 94.8% of Galaxy tokens and output 0.7%.
- How it fell: compact replies, parameter templates, UDT checks before submission and longer waits took GPT-5.6 Sol on BixBench from 3.45 to 1.53 times custom code (122.4 to 54.3 million tokens per 50-task replicate, against 35.5 million).
  Accepted answers were 137 of 150 after the changes and 136 before, under the scoring then in force.
- Framing: agents act as virtual users whose traces show where software is hard to use.
  Say accuracy was retained, not unchanged.
- Time is a second cost and needs one clause: a multi-step Galaxy run took a median of 233 minutes against 75.

### P8. What the tool is, what it enables, and its limits

70 words. Job: close as the model papers do.

- What it is: one sentence.
  An interface through which agents analyse data in Galaxy as accurately as with custom code, leaving a reviewable record.
- What it enables: review in a familiar interface, continuing an analysis without tokens, and cheap cross-method checks.
  Offer the last as an untested hypothesis.
- Limits: four model configurations, one harness, prompts that differ between conditions, IWC references built in Galaxy, and models that change quickly.

## Display items

Two figures of three panels each: Figure 1 proves parity, and Figure 2 shows what Galaxy adds and what it costs.
Six panels fit a 250-word legend budget; eight do not.

| Figure | Panel | Shows | Supports | Exists today |
|---|---|---|---|---|
| 1. Design and accuracy | a | Study design: one model configuration, two conditions, and the interface between agent and Galaxy | P2 | Fig. 1a; add the multi-step arm |
| 1 | b | Galaxy minus custom code for BixBench, CompBioBench and the multi-step tasks, with 95% intervals; one point per model and one pooled | P3, P4 | Fig. 1d, pooled only and with the workflow tasks; rebuild |
| 1 | c | Share of results passing in each of the ten multi-step tasks, both conditions, one mark per model, ordered by the difference | P4 | New panel |
| 2. Record, errors and cost | a | One Galaxy history, annotated: an installed tool, a UDT, a failed job and its recovery | P5 | Not built; Supplementary Fig. 1d,e holds a DESeq2 example |
| 2 | b | Incorrect BixBench runs by cause, split by how many sibling replicates were correct | P6 | Data in the Fig. 2 source table; the current panel splits by condition |
| 2 | c | Galaxy tokens relative to custom code: four task sets in the main runs, then the BixBench stages down to 1.53 | P7 | Fig. 2c and Supplementary Fig. 6; merge |

Panel 1b should plot the difference, not two bars side by side.
The claim is about the gap and its interval, and bars at 87–90% hide both.
CompBioBench has no interval under the official score; plot the reconstructed-key interval as an open marker until item-level official grades are available.

Supplementary Information takes the rest: per-model accuracy, the IWC workflow tasks (the current Supplementary Fig. 4), raw against reviewed scoring, the consensus table, UDT use by benchmark, the selected reruns, failed Galaxy requests and the main-run token totals.
A table of benchmark materials, prompts, code and traces is the natural third display item if the editor allows one.

## What changes from the current draft

| Topic | Current draft | This outline |
|---|---|---|
| Framing | Agents as virtual users for improving Galaxy's interface | A tool report; virtual users move to P7 and P8 |
| Paragraphs | Six | Eight shorter ones, one message each |
| IWC result | Workflow tasks, 99.0% versus 95.3%; multi-step tasks left out as a pilot | Multi-step tasks, 67.5% versus 58.7%; workflow tasks in one clause |
| Tasks and runs | 160 tasks, 3,840 runs | 170 tasks, 4,020 runs |
| Fig. 1 | Bars, a model matrix and pooled differences | Differences with intervals, and a per-task multi-step panel |
| Fig. 2 | Causes, answer selection, token stages | An annotated history, causes by sibling replicates, token ratios |
| UDTs | Reported as execution routes | Stated as a limit: the claim is about the workbench, not only its installed tools |
| Costs | Tokens | Tokens and run time |

If the lab prefers to drop the workflow tasks from the paper altogether, the totals become 160 tasks and 3,780 runs.

## Numbers: use the 28 October release

The earlier editorial plan in `outline-brief-communication.md` and the token note quote an older edition.
The parity conclusion survives both, but the paper needs one frozen release.

| Number | Earlier plan or note | 28 October release |
|---|---|---|
| BixBench accuracy | 87.7%, 87.2% | Reviewed key 89.5%, 88.3%; raw key 87.2%, 86.8% |
| CompBioBench score | 87.0, 86.7 | 87.00, 86.75; fix one rounding rule |
| IWC workflow tasks, runs at 0.99 agreement or above | 83.3%, 80.0% | 79.2%, 72.5% (95 and 87 of 120); lead with mean agreement |
| IWC multi-step tasks | Not included | 67.5%, 58.7% of results passing |
| Gain from a majority of three | 0 to 2.3 points | BixBench: 0.5, 2.2 |
| Incorrect BixBench runs in the cause audit | 151 | 133 |
| Tokens in the main runs | 4.2, 2.7 and 0.92 times custom code | 4.07, 2.48 and 0.96 |
| Optimized Galaxy runs accepted | 136 before, 137 after | Unchanged; under the revised PhyKIT rule 139 before and 140 after |

## Work before submission

Needed for a tool paper to be reviewed:

- [ ] Release the interface: the MCP server, skills and prompts, under an open licence with a version and a DOI.
  The benchmark repository is private today.
- [ ] Freeze one results release and regenerate every number in the text from it.
- [ ] Send a presubmission enquiry asking the editor to confirm Brief Communication over Analysis, and the 1,600-word ceiling.

Needed for the multi-step result to carry P4:

- [ ] Run GPT-5.5, so that all four models cover the ten tasks.
- [ ] Replace the 16 GPT-5.6 Luna trial runs that count as run 1 in both conditions on eight tasks.
- [ ] Address the home advantage: the references were made by running the IWC workflows in Galaxy.
  Score a few tasks against a reference built outside Galaxy, or keep the claim at "no penalty".
- [ ] Disclose or equalise the resources: the Galaxy agent worked from a container with 8 GB of memory and ran its jobs on usegalaxy.org, and the custom-code agent had 64 GB and internet access.
- [ ] State whether UDTs were allowed and used, and which interface version ran (Codex 0.156.0, against 0.146.0 in the main runs).
- [ ] Move the multi-step analysis from the local branch `iwc-multistep-snapshots` onto the paper branch.

Needed for the statistics:

- [ ] State an equivalence margin before computing the final intervals, and pair by task.
  On BixBench a margin of ±5 points is smaller than the spread between replicates of one configuration (up to 8 points) and between models (10 points).
  Declare it as chosen after these data were seen, or apply it to the new runs above.
- [ ] Obtain item-level official grades for CompBioBench, or report both keys as P3 does.
- [ ] Report both BixBench scorings.
  Reviewers will ask whether the answer-key review favoured Galaxy.

Needed for the record claim:

- [ ] Decide whether "rerunnable" is claimed.
  If so, rerun a sample of histories without an agent and report how many reproduce the answer; no other experiment would strengthen P5 as much.
- [ ] Archive the histories.
  On 9 November the public API opened 1,955 of the 2,010; 51 CompBioBench links give a history name instead of an identifier, and 4 histories were no longer public.
- [ ] Say what the record keeps for a UDT (script, environment, inputs), and report UDT use for the multi-step tasks.
- [ ] Choose the run for Fig. 2a and confirm the two PhyKIT versions from the job records.

Needed in Methods:

- [ ] Explain every replaced run and whether replacement depended on the outcome: the 77 in the rerun report (14 BixBench originals had read earlier answers or traces of the same question), 78 BixBench Galaxy recovery or repeat runs, and 52 earlier CompBioBench reruns.
- [ ] Disclose that prompts differ between conditions: 707 against 366 median words on BixBench and 938 against 227 on CompBioBench, from the Word draft and not yet computed by a script.
- [ ] Report the effect of skills: in the earlier GPT-5.5 batch they raised accepted answers from 126 to 139 of 150 in Galaxy and from 122 to 135 with custom code.
- [ ] Fill the open items already marked in the draft: Codex version of the GPT-5.5 runs, how DeepSeek V4 Pro was served, Galaxy and MCP server versions, run time limits and the GPT-5.6 Luna reasoning setting.

Would strengthen the paper:

- [ ] Adjudicate the 7 unreviewed BixBench failures, and extend the cause audit to CompBioBench or limit P6 to BixBench.
- [ ] Recompute on the October runs how many correct runs recovered from a failed step; the earlier 69–95% predates the reruns.
- [ ] Deposit run records for the early token baseline, or drop the estimated 20 and 8 times custom code and start the series at the measured 5.48.
- [ ] Separate job queue time from agent time before interpreting the run-time difference.
- [ ] Complete the reference list: `references.bib` holds 12 checked entries, and every added entry must be checked against its source.

## Where each number comes from

| Numbers | Source | On the paper branch |
|---|---|---|
| 160 tasks and 3,840 primary runs | `data/results_manifest.csv` | Yes |
| Multi-step results passing, per model and pooled; runs with every result passing | `data/accuracy_summary.csv` and `data/accuracy_by_model.csv`, written by `analysis/accuracy.py` | Yes |
| Multi-step interval, per-task values, the value without imaging, tokens, minutes and trial-run flags | Recomputed on 16 November from `data/site/iwc/long-chain/data/results.json`; tables in `data/iwc_long_chain/derived/` | No: local branch `iwc-multistep-snapshots` |
| Why the imaging task differs between conditions | Task 9 page of the results website, "What Galaxy added" | No: archived on `iwc-multistep-snapshots` |
| BixBench, CompBioBench and IWC workflow-task scores and intervals | `figures/benchmark_results_summary/fig1_performance/dataset/source_data.csv` | Yes |
| BixBench scoring sensitivities | `figures/benchmark_results_summary/s3_repeatability/dataset/sensitivity.csv` | Yes |
| CompBioBench reconstructed key | `fig1_performance/dataset/item_scores.csv`; the interval was recomputed on 16 November (200,000 resamples of tasks, seed 20261028) | Counts yes; interval not yet written by a script |
| Histories and UDT use | `s1_execution/dataset/run_histories.csv` and `source_data.csv`; multi-step history links in the results JSON | Yes |
| Histories opened through the public API, history items and code lines | `data/code_and_history/`, written by `analysis/count_history_items.py` and `analysis/count_trace_code.py` | No: local branch `aacr-2027-abstract` |
| Failure causes and sibling replicates | `fig2_interface/dataset/bixbench_current_failures.csv` and `source_data.csv` | Yes |
| Single run, majority, any-of-three and answer vote | `s3_repeatability/dataset/source_data.csv` | Yes |
| Token ratios in the main runs | `s6_token_usage/dataset/source_data.csv` | Yes |
| Agent turns, cached context and the effect of skills | `s7_token_drivers/dataset/source_data.csv` | Yes |
| Token stages and accepted answers | `data/token_optimization_rounds.csv`; `fig2_interface/dataset/optimization_key_sensitivity.csv` | Yes; the 20 and 8 are author estimates |
| Replaced runs | `s2_reruns/dataset/` and `figures/benchmark_results_summary/RESULTS.md` | Yes |
| Prompt lengths | `outline.md`, from the Word draft | No script |
| Format limits | `outline-brief-communication.md`, from the journal's content-type guidance | Yes |
