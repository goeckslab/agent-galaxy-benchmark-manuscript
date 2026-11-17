# Paper outline: Nature Methods Brief Communication

Proposed outline for the paper, revised on 17 November 2026 from the 28 October 2026 results release.
This file is not rendered into the manuscript.
The current draft, `brief-communication.qmd`, still follows `outline-brief-communication.md`.
The two conditions are called "Galaxy" and "custom code", as fixed in `outline.md`.
Every number below was recomputed from `data/site/` or read from a table listed under "Where each number comes from".
All numbers stay provisional until one results release is frozen.

## The argument

Galaxy now has an interface that AI agents can operate, built from a Model Context Protocol (MCP) server and skills.
An agent's work has two parts: knowledge, deciding which analysis answers the question, and execution, carrying it out.
Handing execution to Galaxy costs no accuracy, and it leaves every step in a history where the remaining mistakes can be seen.
The paper is a tool report: the interface is the method, and three benchmarks of biological data analysis are its validation.

The argument runs in five steps, one per result paragraph, and each step is worded as far as the results carry it:

1. Agents lose no accuracy by working through Galaxy instead of writing custom code.
2. One Galaxy run is close to the consensus of three, so repeating a task and voting adds little.
3. A correct answer was usually produced in at least one of three runs, and model knowledge was rarely the cause of a wrong one.
4. A Galaxy history shows where an execution went wrong, without rerunning anything.
5. The extra tokens are interface overhead, present in correct runs too, and each measured interface change has reduced it.

## Paragraph outline

Eight paragraphs, about 870 words.
Each paragraph has a title stating its one message and three bullets.
The last bullet of every paragraph is its closing sentence: what the result changes for people who run agents on biological data.
The titles are drafting labels and come out before submission.
Each pair of numbers is Galaxy first, then custom code.

### Abstract

- Affirm, then turn: agents can plan bioinformatics analyses, but they execute them as custom code that is hard to check.
- What we did: gave agents an interface to Galaxy and tested it on three benchmarks with four models.
- Result and payoff: accuracy was sustained, and each run left a history in which execution errors can be found.

Draft, 68 words of the 70 allowed:

> AI agents can plan bioinformatics analyses, but they execute them as custom code that is hard to check. Here we give agents an interface to the Galaxy workbench, a Model Context Protocol server with skills, and test it on three benchmarks with four models in 3,780 runs. Accuracy was sustained (89.5% versus 88.3% on BixBench), and each run left a history in which execution errors can be found.

### P1. Agents know the biology; the open problem is how their analyses are executed and checked

- Affirm: AI agents now plan and run whole bioinformatics analyses, and benchmarks such as BixBench and CompBioBench measure how well.
- Turn: an agent's work has two parts, knowledge and execution.
  Today execution means custom code in an ad hoc environment, where mistakes enter and are hard for a researcher to see.
- Shift: Galaxy already gives people curated, versioned tools, managed compute and a recorded history of every step.
  The question for the field is whether agents can hand it the execution without losing accuracy.

### P2. Galaxy now has an interface that agents can operate

- What we built: an MCP server through which an agent searches tools, reads parameter schemas, submits and monitors jobs and inspects histories, and skills that supply analysis know-how.
- Why it differs: the agent keeps the knowledge role and Galaxy takes over execution.
  Agents can still write code through user-defined tools (UDTs), but every step runs as a Galaxy job and is recorded.
  Define "Galaxy" and "custom code" here, once.
- Shift: agents completed 1,890 runs through this interface, each linked to a Galaxy history.
  Galaxy is therefore an execution environment that an agent can use unaided, not only one built for people.

### P3. On three benchmarks of biological analysis, agents lose no accuracy through Galaxy

- Evidence: four model configurations in one Codex harness ran each task three times per condition, 160 tasks and 3,780 runs in all.
  BixBench 89.5% versus 88.3% of answers accepted (difference 1.2 points, 95% interval −1.5 to 4.2).
  CompBioBench 87.0% versus 86.8% of official points.
  Ten multi-step IWC analyses 67.5% versus 58.7% of results passing (difference 8.8 points, interval −6.1 to 27.1).
- Scope: the model mattered more than the condition, with 10 points between models on BixBench and −0.7 to +3.3 points between conditions per model.
  On the multi-step analyses Galaxy was higher in 7 of 10 tasks.
  The gap is widest where the toolchain is hard to assemble (multiplex tissue imaging, 86.4% versus 8.6%) and reverses for 16S amplicon analysis (59.7% versus 90.3%).
- Shift: accuracy is no longer a reason to keep agents on custom code.
  On these benchmarks the choice of where an agent runs its analysis can rest on what else the environment offers.

### P4. One Galaxy run is close to the consensus of three

- Evidence: each model ran each task three times, so a consensus can be scored as at least two of three runs correct.
  A consensus changed Galaxy accuracy by 0.5 points on BixBench, 0.9 on CompBioBench and 1.5 on the multi-step analyses.
  It changed custom-code accuracy by 2.2, 1.5 and −0.6 points.
- Scope: on the 150 benchmark questions Galaxy's three runs agreed more often, splitting in 15 versus 19 of 200 BixBench groups and 51 versus 68 of 400 CompBioBench groups.
  On the multi-step analyses Galaxy runs differed more among themselves, but a result failed in all three runs half as often (34 versus 74 of 261).
  Agreement is not correctness: all three runs were wrong in 30 versus 16 CompBioBench groups.
- Shift: repeating a task and voting bought at most 2.2 points in either condition, so reliability will not come from repetition.
  A researcher can take one Galaxy run and spend the effort on checking it.

### P5. Model knowledge is rarely the limit: a correct answer was usually produced

- Evidence: at least one of three runs was correct in 93.0% versus 92.0% of BixBench groups and 92.5% versus 96.0% of CompBioBench groups.
  On the multi-step analyses a result passed in at least one run for 86.5% versus 70.9% of results, against 67.5% and 58.7% in a single run.
- Scope: of 133 incorrect BixBench runs, the audit traces 5 to model knowledge, and in all five the same model answered the same question correctly in another run.
  It traces 27 to a check the agent did not make, 6 to the platform or harness and 84 to an ambiguous task or scoring rule.
  Choosing the correct run needs the answer key, so "at least one" is a ceiling on what validation could recover, not a method.
- Shift: answers are lost after the model knows what to do, in execution and in results that nobody checked.
  For the field the bottleneck moves from what models know to how their work is executed and checked, which is the part a workbench supplies.

### P6. A Galaxy history shows where an execution went wrong

- Evidence: BixBench question bix-52-q7 asks how many rows a methylation filter removes, and the accepted answer is 19,159.
  Two Galaxy runs answered 19,160.
  Their seven-item histories show why: the filtered table has 19,160 lines, its first line is the column header, and the line-count step reports 19,160.
  Another run by one of the same models took the same steps, saw the same count and answered 19,159.
- Scope: every Galaxy run records tool identity and version, parameters, datasets and job states, viewable in the standard interface without spending tokens.
  The mistake arose in Galaxy, so the claim is that the record makes mistakes catchable, not that Galaxy prevents them.
  The example uses installed tools only; a step run as a UDT records a script that a reviewer must read.
- Shift: the person who asked the biological question can check the agent's answer by opening the history, with no rerun and no code to read.
  Reviewing an agent's analysis becomes ordinary Galaxy work instead of a programming task.

### P7. Galaxy's token cost is interface overhead, and every interface change has lowered it

- Evidence: Galaxy used 4.07 times the tokens of custom code on BixBench, 2.48 on CompBioBench and 1.47 on the multi-step analyses.
  The overhead is not the price of failure: counting only runs that reached the accepted answer, the BixBench ratio is still 3.8, and four-fifths of Galaxy's tokens were spent on correct runs.
- Scope: the tokens went to context re-read over more turns, 2.66 times as many turns each carrying 2.20 times as much cached context.
  Each measured change lowered the ratio: moving routine operations into the MCP server took GPT-5.5 from 5.48 to 2.81, and compact replies, parameter templates and longer waits took GPT-5.6 Sol from 3.45 to 2.42 to 1.53.
  Accepted answers were retained (137 of 150 after, 136 before); 1.53 is one model on one benchmark.
- Shift: the cost of running an agent in Galaxy is an engineering variable, not a fixed price.
  It has fallen with each interface change, and on short workflow tasks it already equals custom code (0.96).

### P8. What the interface is, what it enables, and its limits

- What it is: one sentence.
  An interface through which agents analyse biological data in Galaxy with no loss of accuracy, leaving a history a researcher can review.
- Limits: four model configurations, one harness, prompts that differ between conditions, IWC references built in Galaxy, and consensus and validation estimated from existing runs.
  The next test is prospective: a validation step that reads the history before an answer is reported.
- Shift: for biological data analysis, an agent no longer has to write and run its own code to be accurate.
  Through Galaxy its work can be checked by the researcher who asked the question, at a token cost that is falling.

### Words and panels

| Paragraph | Words | Figure panel |
|---|---|---|
| P1 | 100 | |
| P2 | 110 | 1a |
| P3 | 130 | 1b |
| P4 | 110 | 1c |
| P5 | 110 | 1c, 2a |
| P6 | 120 | 2b |
| P7 | 120 | 2c |
| P8 | 70 | |

## How each point is worded so that the results support it

Each row gives a point as first proposed, the wording the outline uses, and the evidence that carries it.

| Point as first proposed | Wording the results support | Evidence |
|---|---|---|
| Galaxy gives the best accuracy | Agents lose no accuracy by working through Galaxy | All three point estimates are at least as high in Galaxy; no interval excludes zero; the reconstructed CompBioBench key points the other way (86.6% versus 88.3%) and is disclosed |
| Galaxy answers are more consistent | On the benchmark questions Galaxy's three runs agree more often; on every benchmark one Galaxy run is within 1.5 points of its consensus | Runs split in 15 versus 19 and 51 versus 68 groups; consensus adds 0.5, 0.9 and 1.5 points in Galaxy |
| Consistency holds on every benchmark | On the multi-step analyses Galaxy runs differ more, but a result fails in all three runs half as often | Results split 105 versus 63 of 261; no run passed for 34 versus 74 |
| A consensus raises accuracy, mostly for custom code | A consensus adds little in either condition | Changes range from −0.6 to +2.2 points; with a consensus custom code is at 90.5% and Galaxy at 90.0% on BixBench |
| With validation, accuracy rises in both conditions | A correct answer was produced in at least one of three runs far more often than in a single run; this is a ceiling on what validation could recover | Gains of 3.5 to 19.0 points; no validation step was run; on CompBioBench the ceiling is higher for custom code (96.0% versus 92.5%) |
| Model knowledge is enough, and the execution environment causes the mistakes | Model knowledge was rarely the cause of a wrong answer, and failures on the agent's side were mostly unchecked analyses | 5 of 133 BixBench failures were knowledge, 27 a missing check and 6 platform or harness; 84 were task or scoring ambiguity, which is the benchmark and not execution |
| A person would catch the header mistake | The header mistake is visible in a seven-item history | Verified in three public histories; that a person catches it is untested until the prospective validation test |
| Correct and incorrect runs cost the same tokens | The token overhead is present in correct runs | Correct runs alone cost 3.8 times custom code; 79.6% of Galaxy tokens went to correct runs; the medians are close (2.15 against 1.85 million) but the mean incorrect run used 2.2 times the mean correct one |
| Galaxy and custom code are now close in tokens | Each measured interface change lowered the ratio, to 1.53 for one model on one benchmark | 5.48 to 2.81, then 3.45 to 2.42 to 1.53; the stages are sequential batches, not a controlled comparison |

## Numbers behind P4 to P7

Three ways to score three runs, in percent.
A group is the three runs of one model on one question in one condition; on the multi-step analyses it is the three runs of one model on one required result.

| Benchmark | Single run | At least 2 of 3 correct | At least 1 of 3 correct |
|---|---|---|---|
| BixBench-Verified-50, 200 groups | 89.5 / 88.3 | 90.0 / 90.5 | 93.0 / 92.0 |
| CompBioBench, reconstructed key, 400 groups | 86.6 / 88.3 | 87.5 / 89.8 | 92.5 / 96.0 |
| IWC multi-step, 261 groups | 67.5 / 58.7 | 69.0 / 58.1 | 86.5 / 70.9 |

How often the three runs agree, in groups.

| Benchmark | All 3 correct | Exactly 2 | Exactly 1 | None |
|---|---|---|---|---|
| BixBench-Verified-50, 200 groups | 171 / 165 | 9 / 16 | 6 / 3 | 14 / 16 |
| CompBioBench, reconstructed key, 400 groups | 319 / 316 | 31 / 43 | 20 / 25 | 30 / 16 |
| IWC multi-step, 261 groups | 122 / 124 | 59 / 28 | 46 / 35 | 34 / 74 |

Tokens per BixBench run by outcome, in millions.

| Measure | Galaxy | Custom code | Ratio |
|---|---|---|---|
| All runs, total tokens | 2,782.5 | 684.3 | 4.07 |
| Correct runs only, mean per run | 4.12 | 1.09 | 3.79 |
| Median correct run | 2.15 | 0.46 | |
| Median incorrect run | 1.85 | 0.67 | |
| Share of tokens spent on correct runs | 79.6% | 84.2% | |

## Display items

Two figures of three panels each.
Figure 1 shows the interface and that accuracy is sustained; Figure 2 shows where answers are lost, how a history shows it, and what it costs.

| Figure | Panel | Shows | Supports | Exists today |
|---|---|---|---|---|
| 1. Interface and accuracy | a | The agent's knowledge and execution roles, the two conditions, and the MCP server and skills between agent and Galaxy | P2 | Fig. 1a; redraw around the two roles |
| 1 | b | Galaxy minus custom code on the three benchmarks, with 95% intervals; one point per model and one pooled | P3 | Fig. 1d, pooled only and with the IWC workflow tasks; rebuild |
| 1 | c | Single run, at least two of three and at least one of three, per benchmark and condition | P4, P5 | Fig. 2b; replace its IWC rows with the multi-step values |
| 2. Errors, record and cost | a | Causes of the 133 incorrect BixBench runs, with model knowledge and missing checks set apart | P5 | Fig. 2a |
| 2 | b | The seven-item history of bix-52-q7, with the header row and the line count marked | P6 | Not built |
| 2 | c | Galaxy tokens relative to custom code: the three benchmarks, correct runs only, then the stages down to 1.53 | P7 | Fig. 2c and Supplementary Fig. 6; merge |

Panel 1b should plot the difference, not two bars side by side.
CompBioBench has no interval under the official score; plot the reconstructed-key interval (−3.8 to 0.5) as an open marker until item-level official grades are available.

Supplementary Information takes the rest: per-model accuracy, the multi-step analyses by task, the ten shorter IWC workflow tasks, raw against reviewed scoring, UDT use by benchmark, the selected reruns, failed Galaxy requests and the main-run token totals.

## Format and word budget

A Brief Communication allows 1,200 words including abstract, references and figure legends, or 1,600 at the editor's discretion.
This plan totals about 1,490 words and so relies on that discretion.

| Element | Journal limit | This plan |
|---|---|---|
| Abstract | 70 words, unreferenced | 68-word draft |
| Main text | Inside the 1,200 (1,600) total; no sections or subheadings | 8 paragraphs, 870 words |
| Display items | 2 figures or tables, 3 at discretion | 2 figures of 3 panels each; legends 250 words |
| References | About 20 as a guideline | 20, about 300 words |
| Online Methods | Required, with subheadings; outside the count | All implementation detail |

The journal lists software platforms and practical improvements to existing tools as Brief Communication material.
A paper that reads as a comparison of established tools may be redirected to the longer Analysis format, so keep the interface as the subject.

If the editor holds to 1,200 words, cut in this order:

1. Merge P4 into P5 as one paragraph on the three ways to score three runs (saves about 80).
2. Trim references to 15 (saves about 75).
3. Trim legends to 180 words (saves about 70).
4. Move the turn and context detail of P7 to Methods (saves about 40).
5. Move the interface detail of P2 to Methods (saves about 30).

Title options:

- "An agent interface to Galaxy for accurate, inspectable bioinformatics analyses" names the tool and what is new.
- "AI agents can perform accurate bioinformatics analyses through a computational workbench" is the candidate adapted from Jeremy Goecks's title comment.

## Which IWC results the paper reports

The repository holds two sets of ten IWC tasks, and the paper's third benchmark is the harder set.

| | IWC workflow tasks | IWC multi-step tasks |
|---|---|---|
| Task | Reproduce one IWC workflow of 2 to 27 tool steps | Carry a full analysis from raw data to 8–12 scored results; the task text names no software |
| Source file | `data/site/iwc/data/results.json` | `data/site/iwc/long-chain/data/results.json` |
| Runs | 240, four models | 180, three models (GPT-5.5 not run) |
| Galaxy versus custom code | 99.0% versus 95.3% mean output agreement | 67.5% versus 58.7% of results passing |
| Role in the paper | Supplementary Information, and the token ratio in P7 | The third benchmark: abstract and P3 to P7 |

Five of the ten workflow tasks are at ceiling in both conditions, so that set cannot separate conditions or models.
Counting it as well would give 170 tasks and 4,020 runs.

## Work before submission

Needed for a tool paper to be reviewed:

- [ ] Release the interface: the MCP server, skills and prompts, under an open licence with a version and a DOI.
  The benchmark repository is private today.
- [ ] Freeze one results release and regenerate every number in the text from it.
- [ ] Send a presubmission enquiry asking the editor to confirm Brief Communication over Analysis, and the 1,600-word ceiling.

Needed for P4 to P7, which rest on numbers computed for this outline:

- [ ] Add scripts in `analysis/` for agreement between the three multi-step runs, tokens by outcome and the bix-52-q7 history check.
  Until then these numbers do not meet the repository's tracing rule.
- [ ] Trace every Galaxy failure labelled as a missing check (14 on BixBench) in its history, and report in how many the mistake is visible.
  This turns the one example in P6 into a count.
- [ ] Test a validation step prospectively: give a person or an agent the history before the answer is reported, and count the mistakes caught.
  No other experiment would strengthen P5 and P6 as much, because it turns the ceiling into a method.
- [ ] Obtain item-level official grades for CompBioBench.
  Consensus and validation on that benchmark currently rest on the reconstructed key, which is a diagnostic.
- [ ] Adjudicate the 7 unreviewed BixBench failures, and extend the cause audit to CompBioBench or limit the knowledge claim to BixBench.

Needed for the multi-step benchmark:

- [ ] Run GPT-5.5, so that all four models cover the ten tasks.
- [ ] Replace the 16 GPT-5.6 Luna trial runs that count as run 1 in both conditions on eight tasks.
- [ ] Address the home advantage: the references were made by running the IWC workflows in Galaxy.
- [ ] Disclose or equalise the resources: the Galaxy agent worked from a container with 8 GB of memory and ran its jobs on usegalaxy.org, and the custom-code agent had 64 GB and internet access.
- [ ] Report run time: a multi-step Galaxy run took a median of 233 minutes against 75.
- [ ] Move the multi-step analysis from the local branch `iwc-multistep-snapshots` onto the paper branch.

Needed for the statistics and the record:

- [ ] State an equivalence margin before computing the final intervals, and pair by task.
- [ ] Report both BixBench scorings; the sign of the difference rests on one question, bix-45-q1.
- [ ] Archive the histories with a DOI, and say what the record keeps for a UDT.
  Agents used a UDT in 844 of 1,200 CompBioBench runs.
- [ ] Decide whether "rerunnable" is claimed, and if so rerun a sample of histories without an agent.

Needed in Methods:

- [ ] Explain every replaced run and whether replacement depended on the outcome.
- [ ] Disclose that prompts differ between conditions (707 against 366 median words on BixBench, from the Word draft).
- [ ] Deposit run records for the early token baseline, or start the series at the measured 5.48.
- [ ] Complete the reference list: `references.bib` holds 12 checked entries, and every added entry must be checked against its source.

## Where each number comes from

| Numbers | Source | On the paper branch |
|---|---|---|
| Tasks and runs per benchmark | `data/results_manifest.csv`; multi-step runs in `data/site/iwc/long-chain/data/results.json` | Yes |
| BixBench and CompBioBench scores, interval and per-model values | `figures/benchmark_results_summary/fig1_performance/dataset/source_data.csv` | Yes |
| Multi-step results passing, per model and pooled | `data/accuracy_summary.csv` and `data/accuracy_by_model.csv`, written by `analysis/accuracy.py` | Yes |
| Multi-step interval, per-task values, tokens, minutes and trial-run flags | Recomputed on 16 November from the multi-step results file; tables in `data/iwc_long_chain/derived/` | No: local branch `iwc-multistep-snapshots` |
| Why the imaging task differs between conditions | Task 9 page of the results website, "What Galaxy added" | No: archived on `iwc-multistep-snapshots` |
| Single run, consensus and at least one correct, BixBench and CompBioBench; groups by number of correct runs | `s3_repeatability/dataset/source_data.csv` | Yes |
| The same for the multi-step analyses, per required result | Computed on 17 November from the multi-step results file | No script yet |
| CompBioBench reconstructed key and its interval | `fig1_performance/dataset/item_scores.csv`; interval recomputed on 16 November | Counts yes; interval not yet written by a script |
| Failure causes | `fig2_interface/dataset/bixbench_current_failures.csv` and `RESULTS.md` | Yes |
| bix-52-q7 answers and cause labels | `data/site/bixbench/data/results.json`; the failure ledger above | Yes |
| bix-52-q7 histories: items, line counts and header row | Three public histories opened through the usegalaxy.org API on 17 November | No script yet |
| Token ratios on BixBench, CompBioBench and the IWC workflow tasks | `s6_token_usage/dataset/source_data.csv` | Yes |
| Tokens by outcome on BixBench | Computed on 17 November from per-run `usage` in `data/site/bixbench/data/results.json` | No script yet |
| Agent turns and cached context | `s7_token_drivers/dataset/source_data.csv` | Yes |
| Token stages and accepted answers | `data/token_optimization_rounds.csv` | Yes |
| Histories and UDT use | `s1_execution/dataset/run_histories.csv` and `source_data.csv` | Yes |
| Prompt lengths | `outline.md`, from the Word draft | No script |
| Format limits | `outline-brief-communication.md`, from the journal's content-type guidance | Yes |
