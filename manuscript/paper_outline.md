# Paper outline: Nature Methods Brief Communication

Proposed outline for the paper, rewritten on 18 November 2026 from the authors' storyline of that day, the eight slides of the lab presentation "Benchmarking Agent Use of Galaxy", the 28 October 2026 results release, the error taxonomy in `error_taxonomy.md`, and references checked against their sources on 18 November.
This file is not rendered into the manuscript.
The current draft, `brief-communication.qmd`, still follows `outline-brief-communication.md`.
The two conditions are called "Galaxy" and "custom code", as fixed in `outline.md`.
"Galaxy-MCP" is the community MCP server named in the Galaxy 2026 update, "agentic-plugins" the Galaxy project's package that installs it with Galaxy skills in agent harnesses, and "the MCP server" or "the agent interface" (the server with its skills) the one built and benchmarked here, which its code names "galaxy-execute".
The results are for our server, not for Galaxy-MCP, so the paper never writes "Galaxy-MCP" for it.
Every number below was recomputed from `data/site/` (the 28 October release) or read from a table listed under "Where each number comes from"; each pair of numbers is Galaxy first, then custom code.
The slides were made from an earlier scoring snapshot and, for IWC, from the shorter workflow tasks; "Slides against the frozen release" lists each slide number and the number the paper uses instead.
All numbers stay provisional until one results release is frozen.
The 17 November revision of this file (seven paragraphs, one of them for a blinded inspection study) was never committed; its wording rules are kept in the claim table, and the inspection study moves to "Work before submission".

Working title (the authors', 18 November): "Engineering trustworthy AI agents for computational cancer research".
"Trustworthy" and "cancer" are the two words a reviewer will test; "Title" under "Format and word budget" says what each needs.

## The argument

Researchers use AI agents to analyse more data faster, but each analysis yields more code, logs and files than a person can review, so trust in the answers lags behind their volume.
Trusting an agent's answer means trusting two things: the plan its knowledge produces, and the execution that turns the plan into installed software, chosen parameters, organized outputs and an extracted answer.
Benchmarks exercise both but report a single score, which tells a researcher neither where an agent is strong nor when its answer needs a check.
Galaxy, a workbench built for people, already standardizes the execution side: curated tools, compute, and a history that records every step in one inspectable form.
We engineered an MCP server and skills through which agents work in Galaxy, so that the agent plans and interprets while Galaxy executes and records, and benchmarked four models with and without it on 160 tasks in 3,780 runs.
The results answer five questions, one paragraph each:

1. Does working through Galaxy cost accuracy (P4)? Scores were close on BixBench and CompBioBench and higher on the multi-step analyses, with wide uncertainty.
2. Does a workbench help on long analyses (P5)? On one of ten, multiplex tissue imaging, Galaxy supplied software that agents writing their own code did not manage to install and run; on the other nine the conditions were close.
3. How much do answers vary between attempts, and what could a check recover (P6)? A majority of three recovered more custom-code failures on two benchmarks, and at least one of three attempts was correct in most failing groups, which only a check can exploit.
4. What do the standard records show about errors (P7)? Interface errors that successful runs absorbed and that engineering can remove, and failure causes that recur across models.
5. What does it cost (P8)? More tokens in Galaxy; successive interface batches recorded lower ratios, from 5.48 to 1.53 times custom code on BixBench.

Equivalence was not tested: no margin was prespecified, and the multi-step interval spans −6.1 to 27.1 points.
Whether a person finds a wrong answer faster or more reliably with a Galaxy history than with custom code's scripts and logs was not measured.
Without that test the paper can say that every Galaxy run leaves a standard record and that the records made the analyses in P6 and P7 possible, but not that they make human checking better.

## What this revision changes

| Source | Change | Where |
|---|---|---|
| Authors' storyline, 18 November | New title; three introduction paragraphs (agents and trust; plan versus execution and the limits of a single score; Galaxy and the engineered MCP server); five results paragraphs, one per question; a closing paragraph in the authors' words | Paragraph outline |
| Authors' decision, 18 November | The IWC results stay the ten multi-step tasks, although the slides show the shorter workflow tasks; those slide panels are redrawn, and the workflow tasks stay in the Supplementary Information | P4, P5, display items |
| Slides | Each slide is mapped to a paragraph and a panel; where a slide number differs from the 28 October release, the release number is used | Display items, "Slides against the frozen release" |
| Slides | The imaging task becomes the example of P5, bix-52-q7 the example of P6 and the token series the core of P8; the rule-violation audit enters P7 and Methods once its data are in the repository | P5–P8, Work before submission |
| References | 44 references checked against Crossref, PubMed, arXiv, bioRxiv or the publisher (most on 18 November, six in October), 15 of them checked a second time; every introduction claim and every external comparison carries one | Paragraph outline, "References checked for this outline" |
| 17 November revision | The inspection-study paragraph leaves the main text; the study is recommended before submission as the only test of whether the record helps people find mistakes | Argument, claim table, Work before submission |
| Data check, 18 November | BixBench token ratios per model now come from the release (`bixbench_tokens_by_model.csv`): DeepSeek V4 Pro 3.30, not the 3.67 of the 12 October token pages, and pooled 4.07, not 4.23 | P8, token tables |
| Authors' request, 18 November | P1 to P9 rewritten for readability, numbers unchanged: each number names its condition (Galaxy or custom code), benchmark and denominator; elliptical lists and three-idea sentences split; each reference sits beside the claim it supports; the 1,251 lookups are stated for all Galaxy runs, not only successful ones; "successful" defined as ending with a correct answer; the P8 title no longer credits the token reduction to engineering alone | Paragraph outline, "Words and panels" |
| Authors' description of the server, 18 November | Why the server was built (round trips and long replies, measured in the July batch), its five design principles and nine tools, and the difference from Galaxy-MCP, each checked against the code where possible; the final server's features are kept apart from the version the main runs used; wording rules for "subset", "no polling" and contributions back to Galaxy-MCP | P3, P8, "The MCP server and how it differs from Galaxy-MCP", claim table, Fig. 1a, Work before submission |

## Paragraph outline

Nine paragraphs: three on the problem and the method, five on the results (one per question), one closing.
Each block has a title stating its one message and two or three bullets; the drafting label that opens a bullet (such as "Evidence:") is not text.
Reference keys in square brackets point to "References checked for this outline"; keys in bold are the core set for the main text.
The titles are drafting labels and come out before submission.
The bullets carry more detail than the paper can hold; "Format and word budget" says what moves to Methods or the Supplementary Information.

### Abstract

- Affirm, then turn: agents can accelerate computational research, but an answer is hard to trust without seeing how it was produced.
- What we did: an interface through which agents plan analyses that Galaxy executes and records.
- Result and cost: close scores on two benchmarks, higher but uncertain on multi-step analyses, more tokens, and a standard record of every run.

Draft, 70 words (the limit):

> AI agents can accelerate computational research, but their answers are hard to trust without seeing how each was produced. We engineered an interface through which agents plan analyses that the Galaxy workbench executes and records. In 3,780 runs on three benchmarks, agents using Galaxy scored close to agents writing their own code, higher but uncertain on multi-step analyses, at higher token cost, and left an inspectable record of every run.

If the inspection study is run, its result replaces "and left an inspectable record of every run" and the multi-step clause is shortened.

### P1. Agents accelerate computational research, but reviewing what they produce limits trust in their answers

- Affirm: AI agents now plan and run computational biology analyses, from single questions to whole studies [**gao2024**; **ghareeb2026**], and an autonomous agent has been validated for clinical decision-making in oncology [**ferber2025**].
  Researchers are adopting AI quickly: 84% of the 2,430 researchers in Wiley's 2025 survey used it, against 57% in 2024 [wiley2025].
- Turn: Trust has not kept pace: in the same survey, concern about inaccuracies rose from 51% to 64%, and AI can lead scientists to "produce more but understand less" [**messeri2024**; wiley2025].
  One reason is volume: an agent's analysis yields more code, logs and files than a person can review, and checking AI output can use up the time the AI saved [stackoverflow2025].
  In one study, experienced developers were 19% slower with AI tools while believing they were 20% faster [**becker2025**].
- Shift: Asking agents to organize their outputs helps only in part: each researcher asks for a different structure and level of detail, so no shared format lets others read the result.
  What is missing is a standard record of each analysis, as reproducible research requires: every result traced to how it was produced, with its software versions and intermediate results kept [**sandve2013**; gruning2018].

### P2. Trusting an analysis means trusting both the plan and its execution, and a single benchmark score shows neither

- Affirm: An agent's knowledge produces a plan, and execution turns the plan into installed software, chosen parameters, organized files and an extracted answer, for example through code the agent writes and runs itself [wang2024codeact].
  When each agent sets up its own environment, every one of these steps can be done in many ways, which makes the result harder to understand, evaluate and share.
  Execution can fail on its own: even when a model is given the plan and the knowledge it needs, it makes more mistakes as the task gets longer [**sinha2026**].
- Turn: Benchmarks such as BixBench and CompBioBench test planning and execution together, on analyses with accepted answers [**bixbench2025**; **compbiobench**], but rank agents by a single accuracy score.
  A single score cannot show whether a failure came from the plan or from its execution, how answers vary between attempts, or what each answer costs [**kapoor2025agents**; **yao2025tau**].
- Shift: Before applying agents to important analyses, researchers need to know where an agent is strong, where it fails, and when its answer needs a check.

### P3. Galaxy, a workbench built for people, can be engineered to work with agents

- Affirm: Galaxy offers thousands of curated tools and compute for large analyses, and records every step in a history (tool, version, parameters, inputs and outputs), so analyses can be inspected, shared and turned into workflows, such as the peer-reviewed workflows of the Intergalactic Workflow Commission (IWC) [**goecks2010**; galaxy2024; **galaxy2026**; iwc].
- Turn: But Galaxy was built for people.
  Galaxy-MCP, a community server for the Model Context Protocol (MCP) [mcp], exposes Galaxy's operations to AI clients; the Galaxy 2026 update names it as future work and does not evaluate agents that use it [**galaxy2026**].
  Exposing operations may not be enough, because how an agent's interface is designed changes what the agent achieves [**yang2024sweagent**].
- What we did and why: We therefore engineered our own MCP server and skills for running analyses in Galaxy, separate from Galaxy-MCP.
  We built it because agents working through the Galaxy API used far more tokens than agents writing their own code (5.48 times on BixBench in the last batch before the server), and their traces showed two causes: many more round trips to the model, such as polling jobs and resubmitting after guessing a tool's schema, and long API replies that stayed in the context (P8).
  Every step, whether it uses an installed Galaxy tool or the agent's own code packaged as a user-defined tool, follows one pattern: find the tool and read only the parameters it needs, submit the job once and wait for it, check the parameter values Galaxy resolved, and open the history.
  Four models (GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro, all in the Codex CLI) ran each task three times in Galaxy and three times with custom code, on BixBench-Verified-50 (50 questions), CompBioBench (100 questions) and ten multi-step analyses built from IWC workflows, which GPT-5.5 did not run: 160 tasks and 3,780 runs in all (Fig. 1a).
  We asked whether working through Galaxy keeps accuracy (Q1), helps on long analyses (Q2), and makes agents' variability (Q3), errors (Q4) and cost (Q5) visible enough to judge when an answer can be trusted.

### P4. Agents working through Galaxy scored at least as high as agents writing their own code (Q1)

- Evidence (Fig. 1b): On BixBench-Verified-50, 89.5% of Galaxy answers and 88.3% of custom-code answers were accepted (difference 1.2 points; 95% interval −1.5 to 4.2).
  On CompBioBench the official scores were 87.00% for Galaxy and 86.75% for custom code, with no interval, because the official grades of individual answers are not available for a paired comparison.
  On the multi-step analyses, Galaxy runs passed 67.5% of required results and custom-code runs 58.7% (8.8 points; −6.1 to 27.1).
- By model and against other reports: Galaxy scored at or above custom code for three of four models on BixBench, three of four on CompBioBench (one of them a tie) and all three on the multi-step analyses.
  Observed scores varied more across models than between conditions: on BixBench, Galaxy runs ranged from 83.3% (DeepSeek V4 Pro) to 93.3% (GPT-5.5).
  These scores are in line with other evaluations of current agents: CompBioBench's authors report 78% to 83% for four agent harnesses, including 83% for the Codex CLI, the harness used here, with GPT-5.4 [**compbiobench**].
- Shift: At the scale tested, working through the interface did not cost accuracy.
  No equivalence margin was set, so these comparisons establish neither equivalence nor an advantage for either condition.

### P5. On multi-step analyses, the workbench supplied software that agents writing their own code did not manage to install and run (Q2)

- Evidence: Each of the ten multi-step analyses runs from raw data to 8 to 12 required results, and the task text names no software.
  For each of the three models, Galaxy runs passed more required results than custom-code runs, by 1.9 to 15.6 points, but runs that passed every required result were rare in both conditions: 24.4% in Galaxy and 23.3% with custom code (1.1 points; −16.7 to 21.1).
- Example (Fig. 1c): The Galaxy advantage came from one task; with it left out, Galaxy and custom-code runs passed 65.4% and 64.3% of required results.
  That task is multiplex imaging of four tissue-microarray cores through an MCMICRO-style chain of illumination correction, stitching, core detection, deep-learning nuclear segmentation, quantification, phenotyping and spatial statistics [**schapiro2022**; creason2022].
  Its nine Galaxy runs (three models, three runs each) used tools already installed in Galaxy, took 6 to 21 hours, and passed 70 of 81 required results (nine per run); 6 of the 9 runs passed all nine.
  The nine custom-code runs passed 7 of 81 and none passed all nine: they ended after 10 to 38 minutes, having substituted their own methods, in some runs because a package such as the segmentation model would not install.
- Shift: A workbench therefore matters most where an analysis depends on software that is hard to install and run, which workflow systems manage for their users [wratten2021].
  On the other nine tasks the conditions were close, and long analyses were hard in both, as long tasks are for agents generally [**kwa2025**; **sinha2026**].
  The task pages trace the three Galaxy imaging runs that missed results to analytical mistakes, such as phenotyping without the log transform in two runs, which the history shows as the parameter "log: false" (slide 7).

### P6. Repeated attempts show that single answers vary, and that a check could recover most remaining failures (Q3)

- Majority of three: Counting a question as passed when at least two of a model's three attempts passed, a simple majority vote [**wang2023sc**], changed scores little.
  On BixBench it gave 90.0% in Galaxy and 90.5% with custom code, against 89.5% and 88.3% for a single attempt; on CompBioBench, scored here with the reconstructed answer key because official grades of individual answers are not available, 87.5% and 89.8%, against 86.6% and 88.3%; on the multi-step results, 69.0% and 58.1%, against 67.5% and 58.7%.
  The majority gained more for custom code (0.5 points for Galaxy and 2.2 for custom code on BixBench; 0.9 and 1.5 on CompBioBench) because custom-code failures were more often a single failed attempt, which the majority overrules: exactly two of three attempts passed on 9 Galaxy and 16 custom-code model–question pairs on BixBench, and on 31 and 43 on CompBioBench.
- At least one correct: At least one of three attempts passed on 93.0% (Galaxy) and 92.0% (custom code) of BixBench model–question pairs, 92.5% and 96.0% on CompBioBench, and 86.5% and 70.9% of multi-step required results.
  Of the 49 wrong BixBench answers that the audit does not attribute to the task or its scoring (P7), 34 came from a model that answered the same question correctly in another attempt in the same condition.
  This is an upper bound: recovering such answers needs a check that tells which attempt is right, as for repeated sampling generally [**brown2024**].
- Example and shift: bix-52-q7 asks how many methylation measurements a filter removes; 3 of 12 Galaxy runs were wrong, while all 12 custom-code runs were right (Fig. 2a,b).
  Two Galaxy runs reported 19,160 instead of 19,159 because they counted the header line of the filtered table, a mistake that each run's seven-item history shows step by step; the third reported 539, apparently the rows kept rather than those removed.
  Single answers therefore vary between attempts, as reported even at nominally deterministic settings [atil2024], and each needs a check; a standard record gives a person, or another agent, what that check requires.

### P7. Standard records map agents' errors: interface errors that runs absorbed, and failure causes shared across models (Q4)

- Absorbed: Among runs that ended with a correct answer and have an event log (1,587 in Galaxy, 1,610 with custom code), 87.6% of Galaxy runs and 72.6% of custom-code runs recorded at least one execution error along the way.
  In Galaxy most were requests the interface rejected, which a better interface could prevent: parameters in 55.6% of these runs, and interface or API requests such as tool lookups or identifiers in 46.6% (across all Galaxy runs, correct or not, 1,251 tool lookups in 545 runs came without a usable history).
  Custom-code runs more often met software that was not available (46.9% of these runs, against 20.9% in Galaxy) and compute limits (16.6%, against 6.4%).
  Galaxy errors could be typed by rule because the interface answers every call with one of a fixed set of statuses and Galaxy records each job's state; custom-code errors had to be typed from free-text shell output (Fig. 2c).
- Fatal: Of the 133 wrong BixBench answers (63 in Galaxy, 70 with custom code), the audit attributes 84 to the task or its scoring; independent audits have likewise found flawed tasks in agent benchmarks, BixBench-Verified-50 among them [**tu2026**; zhu2025abc].
  Of the remaining 49, it attributes 31 to missing validation of intermediate results (27 classified, 4 unresolved), 6 to the platform or harness and 5 to model knowledge; 7 await review.
  On the multi-step tasks, 253 of 783 required results failed in Galaxy and 320 of 783 with custom code, and the error analyses on the task pages name the same kinds of cause for all three models: in Galaxy, misleading tool defaults or labels and wrong parameters; with custom code, unavailable software and substituted methods.
- Shift: Because the Galaxy causes recur across models, fixing each once in the interface would serve every model.
  The records also showed agents breaking benchmark rules, such as searching the web for answers or reading other runs' files, as other evaluations report [**metr2025rh**; kapoor2026hal; zhong2025impossible]; counts follow once the audit data are deposited (see "Work before submission").

### P8. Galaxy costs more tokens, and the overhead fell as the interface was engineered (Q5)

- Cost: In the main runs (those scored in P4 to P7), Galaxy runs used 4.07 times as many tokens as custom-code runs on BixBench, 2.48 times on CompBioBench and 1.47 times on the multi-step analyses; on BixBench the ratio ranged by model from 2.81 (GPT-5.5) to 6.29 (GPT-5.6 Luna).
  On BixBench, token use did not signal whether a Galaxy answer was right: the median incorrect run used 1.85 million tokens and the median correct run 2.15 million, although a few incorrect runs used far more, so the mean was 9.0 million for incorrect runs against 4.1 million for correct ones.
- Engineering (Fig. 2d): The main runs did not use the later interface changes, which were run only on BixBench with GPT-5.6 Sol.
  Across successive BixBench batches, the ratio fell with GPT-5.5 from 5.48 (prompts and skills) to 2.81 (MCP execution), and with GPT-5.6 Sol from 3.45 (MCP execution) to 2.42 (compact replies) and 1.53 (longer waits), with 137 of 150 Galaxy answers accepted in the last batch.
  The MCP-execution stage replaced polling and resubmission with run calls that submit once and wait for the job; the compact-reply stage returned a short list of candidate tools, showed only the schema fields asked for with a fill-in template using the real parameter paths, and checked user-defined tool definitions before creating them; the last stage let run calls wait longer before returning ("The MCP server and how it differs from Galaxy-MCP").
  The CLI version, replicate coverage and scoring also changed between batches, so no reduction is credited to a single change; the earlier estimates of about 20 and 8 times have no deposited run records.
  Other MCP work reports similar overheads from tool definitions and intermediate results passing through the model, and large savings from reducing them [**anthropic2025codeexec**; luo2025mcpuniverse; gan2025ragmcp].
- Where the tokens go: Most Galaxy tokens went to re-reading context: in a July BixBench batch, before MCP execution, cached input made up 94.8% of Galaxy tokens, and Galaxy runs took 2.66 times as many agent turns as custom-code runs, each carrying 2.2 times as much cached context, which are the two causes the server was built to cut (P3).
  Waiting for Galaxy jobs still added turns when a job outlasted a run call's wait: in the GPT-5.6 Sol batches, longer waits cut the mean number of wait calls per replicate from 481 to 78.
  Agents should therefore be compared on cost as well as accuracy [**kapoor2025agents**].

### P9. Paired with Galaxy, agents' analyses become inspectable and open to oversight

- Summary: AI agents have the potential to automate and accelerate many aspects of computational cancer research.
  Here, agents working through Galaxy scored close to the same models writing their own code, and completed six of nine runs of an imaging analysis whose software the custom-code runs did not manage to install and run.
  Every Galaxy run left a standard record, and with these records and the scores the agents' variability, errors and cost could be measured.
- Limits: Four models (three on the multi-step tasks) in one agent harness; prompts and compute that differ between conditions; replicate diagnostics computed after the runs rather than planned; IWC reference results produced in Galaxy, which may favour the Galaxy condition; and no test yet of whether people check answers better with histories.
  [Once done:] the server, skills, prompts and histories are released with DOIs.
- Closing, in the authors' words: our results show that pairing AI agents with Galaxy enables accurate, verifiable and reproducible computational research, and Galaxy's curated software tools, scalable computing resources and auditable histories support trustworthy AI agents as well as human oversight [**natureed2026**; blau2024].
  Each word needs its own evidence: "accurate" rests on the close scores, "verifiable" on the history links (all 1,890 checked), and "reproducible" on rerunning a sample of histories without an agent, which is not done yet; see the claim table.

### Words and panels

Counted as whitespace-separated words in the bullets, excluding drafting labels and reference keys.

| Paragraph | Words in the bullets as written | Standard version (1,200 total) | Longer version (1,600 total) | Figure panel | Slide |
|---|---|---|---|---|---|
| P1 | 182 | 70 | 100 | | |
| P2 | 164 | 65 | 90 | | |
| P3 | 326 | 90 | 130 | 1a | 1 |
| P4 | 187 | 65 | 95 | 1b | 3, 4 |
| P5 | 278 | 80 | 120 | 1c | 7 |
| P6 | 325 | 80 | 120 | 2a, 2b | 5, 6 |
| P7 | 327 | 75 | 115 | 2c | 2 |
| P8 | 392 | 70 | 110 | 2d | 8 |
| P9 | 212 | 50 | 80 | | |
| **Total** | **2,393** | **645** | **960** | | |

## How each point is worded so that the results support it

Each row gives a point from the authors' storyline of 18 November, the wording the outline uses, and the evidence that carries it.
The rules set by the reviews of 17 November still apply: "broadly similar" or "close", never "no loss of accuracy"; official CompBioBench without an interval; both multi-step endpoints; execution errors stated with their denominators as events in successful runs; scripted counts are not validated classifications.

| Point as proposed | Wording the results support | Evidence |
|---|---|---|
| Using the MCP server and Galaxy does not diminish accuracy; "the MCP is doing a great work" | Scores through Galaxy were at least as high as with custom code; at the scale tested the interface did not cost accuracy; equivalence not tested | 89.5 versus 88.3 (−1.5 to 4.2); 87.00 versus 86.75 official; 67.5 versus 58.7 (−6.1 to 27.1); Galaxy at or above custom code for 3 of 4, 3 of 4 (one tie) and 3 of 3 models |
| Q1 is about "Galaxy-MCP" | The results are for our server; "Galaxy-MCP" names the community server, which was not benchmarked | Our server shares no code or operation names with Galaxy-MCP (17 November code reading) |
| Complex tasks are better performed with a structured workbench behind them, less prone to mistakes | On the multi-step analyses Galaxy passed more results for each model, but the difference came from the imaging task, where Galaxy supplied installed software; elsewhere the conditions were close; "less prone to mistakes" is not supported | Imaging task 70 of 81 versus 7 of 81 results; without it 65.4 versus 64.3; complete runs 24.4 versus 23.3; successful Galaxy runs recorded more execution errors (87.6% versus 72.6%); custom code passed more results on three of ten tasks (Table "Multi-step analyses by task") |
| Galaxy provides the execution environment, whereas custom code must set up its own | Holds for the imaging task, where custom-code runs substituted methods, in some runs because packages would not install; across benchmarks custom-code runs more often met software that was not available | Task-page causes C77 and C79; software not available in 46.9% versus 20.9% of successful runs; the custom-code agent had 64 GB of memory and internet access, the Galaxy agent 8 GB with jobs on usegalaxy.org |
| Custom code is more prone to execution mistakes, because a majority vote improves it more | Custom-code failures were more often isolated to one of three attempts, so a majority recovered more of them on BixBench and CompBioBench; not on the multi-step results; the counts do not establish that isolated failures are execution mistakes | Majority gain 0.5 versus 2.2 points (BixBench) and 0.9 versus 1.5 (CompBioBench); groups with exactly two passing 9 versus 16 and 31 versus 43; multi-step 69.0 versus 58.1 against 67.5 versus 58.7 |
| "Correct at least once" isolates the models' knowledge from execution randomness | At least one of three attempts was correct in most failing groups; this is an upper bound that only a check can realize; a correct sibling attempt shows variability, not that the failed attempt had the knowledge | 93.0 / 92.0, 92.5 / 96.0, 86.5 / 70.9 (output-wise for the multi-step tasks); 34 of 49 BixBench failures had a correct sibling |
| This shows the importance of human validation | A check of how each answer was produced could recover failures that a single run or a vote leaves; whether people make that check better with histories is untested | The P6 diagnostics; the bix-52-q7 histories; inspection study not run |
| Histories make the error analysis possible | Galaxy errors arrive as fixed interface statuses and job states, which allowed typing by rule; custom-code errors were typed from shell output; both conditions' event logs were used | `analysis/error_rules_galaxy.py`, `analysis/error_rules_shell.py`; the classifications await author review |
| Interface mistakes are corrected at run time | Successful runs absorbed many rejected requests; whether the next call fixed each one was not measured | 55.6% and 46.6% of successful Galaxy runs; events, not repair rates |
| Do different models hit the same challenges? | On the multi-step tasks the task pages name the same kinds of cause for all three models; per-model counts of execution errors are not computed yet | Page causes: tool defaults or labels and wrong parameters for Sol, Luna and DeepSeek in Galaxy; unavailable software for all three with custom code; DeepSeek V4 Pro accounts for 31 of the 49 traced BixBench failures |
| Galaxy uses more tokens; MCP engineering reduced them drastically, close to custom code | Main runs 4.07, 2.48 and 1.47 times custom code; successive BixBench batches recorded lower ratios, down to 1.53 with GPT-5.6 Sol; the main runs did not use the later optimizations; no reduction is credited to a single change | `bixbench_tokens_by_model.csv`, `token_costs.csv`, `token_optimization_ratios.csv`; CLI version, coverage and scoring also changed between batches |
| "From 20× to 1.5×" (slide 8) | "From 5.48 to 1.53 times in batches with run records"; the 20 and 8 are estimates without records | `data/token_optimization_rounds.csv`, source column |
| Token use is almost the same for correct and incorrect answers | Medians are close in Galaxy, means are not; in custom code incorrect runs used more | Galaxy median 2.15 versus 1.85 million, mean 4.12 versus 9.02; custom code median 0.46 versus 0.67, mean 1.09 versus 1.55 |
| Where most tokens go in Galaxy | Re-read context over more agent turns, measured in a July batch before MCP execution; wait calls in the later Sol batches | Cached input 94.8% of Galaxy tokens; 37.9 versus 14.2 turns per run; 74,600 versus 34,000 cached tokens per turn; wait calls 481 to 78 |
| "Trustworthy" (title) | Supported: every Galaxy run is linked to a standard record, and variability, errors and cost were measured; not tested: whether people judge answers better with that record | History links verified for 1,890 Galaxy runs; inspection study not run |
| "Computational cancer research" (title) | The benchmarks are general computational biology; few tasks are explicitly about cancer; present cancer research as the motivation or add cancer-specific evidence | Cancer or tumour terms in 2 of 50 BixBench questions (bix-37-q1, bix-37-q4) and 3 of 100 CompBioBench questions (among them lung-cancer-sc-q1); the imaging task analyses tissue-microarray cores without naming a disease |
| Accurate, verifiable and reproducible research (closing) | "Accurate": close scores; "verifiable": history links checked; "reproducible": only after archiving the histories and rerunning a sample without an agent | As in the rows above; histories and UDT code not yet archived |
| Workbench plus agent gives a standardized analysis | Every Galaxy run is recorded as a history of datasets and jobs in one format; custom code is not claimed to be uncheckable, since scripts and logs can preserve evidence | Custom-code event logs were used for the audit and the taxonomy |
| Reviewing agent outputs costs the time the agent saved (P1) | Supported only by external evidence; not measured here | becker2025, stackoverflow2025, wiley2025 |
| Agents working through the Galaxy API used far more tokens; the traces showed many round trips and long replies kept in context (why the server was built) | Supported for the last batch before the server: 5.48 times custom code on BixBench, with 2.66 times the agent turns and 2.2 times the cached context per turn; the earlier "about 20 times" has no run records | `token_optimization_ratios.csv`; July 6 batch in `s7_token_drivers/dataset/source_data.csv` |
| "Ours is basically a subset of galaxy-mcp" | "Covers a subset of Galaxy-MCP's operations and changes how they behave in an agent loop": run calls wait for the job, resolved parameters are compared, replies are short and full records go to files | Code reading, 17 and 18 November; Galaxy-MCP v1.9.0 to v1.12.0 ("The MCP server and how it differs from Galaxy-MCP") |
| "One call per job, so the agent doesn't poll or resubmit" | A run call submits once and waits for the job up to a time limit; a separate wait tool follows longer jobs without resubmitting; agents still made wait calls | `wait_for_galaxy_jobs` in the code; wait calls per replicate 481, then 78 (GPT-5.6 Sol batches) |
| Short replies, no repeats and records in files describe the benchmarked server | Only for the later BixBench batches: compact replies entered after the main runs, so P4 to P7 used the MCP-execution stage | Stage names in the token development series; the version used for each benchmark is not yet recorded |
| "We contribute what we learn back to galaxy-mcp as PRs" | Name only merged pull requests, by number, that carry a lesson from this server; the merged ones found on 18 November add a transport and display cards, not waiting or short replies | github.com/galaxyproject/galaxy-mcp pull requests #196, #206 (merged), #226, #227, #230, #233 (open), read 18 November |

## Numbers behind P4 to P8

### Accuracy (P4, P5; Fig. 1b)

| Benchmark | Score | Galaxy | Custom code | Difference, 95% interval | Runs per condition |
|---|---|---|---|---|---|
| BixBench-Verified-50 | Answers accepted | 89.5% | 88.3% | 1.2 (−1.5 to 4.2) | 600 |
| CompBioBench | Official points | 87.00% | 86.75% | 0.25, no paired interval | 1,200 (12 submissions) |
| CompBioBench, diagnostic | Reconstructed item matches | 86.6% | 88.3% | −1.7 (−3.8 to 0.5) | 1,200 |
| IWC multi-step | Required results passed, tasks weighted equally | 67.5% | 58.7% | 8.8 (−6.1 to 27.1) | 90 |
| IWC multi-step | Runs with every required result passed | 24.4% (22) | 23.3% (21) | 1.1 (−16.7 to 21.1) | 90 |
| IWC multi-step, exploratory | Required results passed, imaging task left out | 65.4% | 64.3% | 1.1 | 81 |

By model, Galaxy / custom code, in percent:

| Model | BixBench-Verified-50 | CompBioBench (official) | IWC multi-step (results passed) | IWC multi-step (complete runs) |
|---|---|---|---|---|
| GPT-5.5 | 93.3 / 92.0 | 85.7 / 86.3 | not run | not run |
| GPT-5.6 Sol | 92.7 / 89.3 | 92.3 / 91.0 | 89.9 / 88.0 | 53.3 / 60.0 |
| GPT-5.6 Luna | 88.7 / 89.3 | 84.7 / 84.7 | 49.5 / 33.9 | 6.7 / 6.7 |
| DeepSeek V4 Pro | 83.3 / 82.7 | 85.3 / 85.0 | 63.1 / 54.3 | 13.3 / 3.3 |

### Multi-step analyses by task (P5; Fig. 1c)

Required results passed, complete runs and mean minutes per run, Galaxy / custom code, three models and three replicates per condition.

| Task | Results passed, % | Complete runs, % | Minutes |
|---|---|---|---|
| 01 Genome profiling and HiFi assembly | 68.1 / 56.9 | 33.3 / 33.3 | 218 / 193 |
| 02 ATAC-seq peaks and normalized signal | 72.2 / 81.9 | 11.1 / 22.2 | 197 / 135 |
| 03 16S amplicon sequence variants and taxonomy | 59.7 / 90.3 | 11.1 / 55.6 | 499 / 94 |
| 04 Paired RNA-seq effects and donor robustness | 61.1 / 57.8 | 22.2 / 0 | 320 / 103 |
| 05 Single-cell populations and marker genes | 70.4 / 80.6 | 33.3 / 11.1 | 65 / 13 |
| 06 Replicate-supported CUT&RUN consensus | 73.6 / 69.4 | 44.4 / 33.3 | 457 / 166 |
| 07 Carbon-isotope incorporation in a metaproteome | 73.6 / 51.4 | 0 / 33.3 | 27 / 39 |
| 08 Small-variant differences among haploid yeast strains | 63.9 / 50.0 | 22.2 / 22.2 | 94 / 52 |
| 09 Multiplex tissue imaging and cell neighborhoods | 86.4 / 8.6 | 66.7 / 0 | 666 / 23 |
| 10 LC-MS features and ion relationships | 45.8 / 40.3 | 0 / 22.2 | 345 / 53 |

The imaging task run by run (slide 7): Galaxy, Sol 9, 9 and 9 of 9 results (10.7, 10.0 and 10.4 hours), Luna 9 (a trial run), 5 and 5 (11.0, 14.2 and 21.0 hours), DeepSeek 9, 9 and 6 (6.6, 10.1 and 6.0 hours); custom code, Sol 0, 3 and 4, Luna 0, 0 and 0, DeepSeek 0, 0 and 0 (10.4 to 37.9 minutes).
The task pages give the Galaxy failures as phenotyping without the log transform (DeepSeek run 3, Luna run 2), cores 3 and 4 delivered swapped (Luna run 2) and a spatial graph built on a PCA embedding instead of cell positions (Luna run 3); the custom-code failures as substituted illumination correction, stitching, core detection or segmentation, in some runs because a package would not install (C77, C79), and one run's illumination profiles written without the required suffix (C80).
Multi-step tokens: 1.47 times custom code; median wall time 233 versus 75 minutes, on the public usegalaxy.org server and with different resources, so not a measure of platform efficiency.

### Scoring three attempts (P6; Fig. 2a)

A group is the three attempts of one model on one question in one condition; on the multi-step tasks it is the three attempts of one model on one required result, averaged within task and then over ten equally weighted tasks.
"At least one attempt passed" needs the answer key to pick the attempt; on the multi-step tasks it can combine outputs from incompatible runs and is not a complete-analysis success rate.

| Benchmark | Single attempt | At least two passed | Answer vote accepted | Answer vote abstained | At least one passed (upper bound) | Groups with exactly two passing | Groups with exactly one passing |
|---|---|---|---|---|---|---|---|
| BixBench-Verified-50, 200 groups | 89.5 / 88.3 | 90.0 / 90.5 | 82.5 / 80.0 | 11.0 / 12.0 | 93.0 / 92.0 | 9 / 16 | 6 / 3 |
| CompBioBench, reconstructed key, 400 groups | 86.6 / 88.3 | 87.5 / 89.8 | 87.5 / 89.8 | 4.8 / 2.5 | 92.5 / 96.0 | 31 / 43 | 20 / 25 |
| IWC multi-step, 261 groups | 67.5 / 58.7 | 69.0 / 58.1 | not defined | not defined | 86.5 / 70.9, output-wise | 59 / 28 | 46 / 35 |

bix-52-q7 (P6, Fig. 2b): accepted answer 19,159; Galaxy runs wrong were GPT-5.6 Sol run 3 (19,160), GPT-5.6 Luna run 2 (19,160) and GPT-5.6 Luna run 3 (539); the two 19,160 histories each hold seven items and a filtered table of 19,159 measurements plus one header line, and the 19,159 is reproduced independently from the public data (`header_history_check.csv`); the correct Luna run 1 took a different route (13 items).
The 539 run's history has not been checked.

### Errors (P7; Fig. 2c)

Execution errors recorded in successful runs on the three paper benchmarks: runs with at least one, and their share of successful runs with an event log (1,587 Galaxy, 1,610 custom code).
These are events within successful runs, not rates of repairing an individual error and not causes of wrong answers; their frequencies depend on what each condition logs, on how many steps could fail, and on conditioning on success; categories overlap within a run.

| Subcategory | Galaxy | Custom code |
|---|---|---|
| Parameters rejected | 882 (55.6%) | 70 (4.3%) |
| Interface or API request rejected | 740 (46.6%) | 153 (9.5%) |
| Agent's own code failed | 625 (39.4%) | 208 (12.9%) |
| Data or file handling | 609 (38.4%) | 526 (32.7%) |
| Analysis tool failed | 332 (20.9%) | 70 (4.3%) |
| Software not available | 331 (20.9%) | 755 (46.9%) |
| Platform, network or sandbox | 226 (14.2%) | 244 (15.2%) |
| Compute limit reached | 102 (6.4%) | 268 (16.6%) |
| **Any execution error** | **1,391 (87.6%)** | **1,169 (72.6%)** |
| Any, without the interface's own parameter check | 1,323 (83.4%) | 1,169 (72.6%) |

Causes of the 133 wrong BixBench answers under the audit labels.

| Audit label | Galaxy (63) | Custom code (70) |
|---|---|---|
| Task or scoring ambiguity | 36 | 48 |
| Missing validation, classified | 14 | 13 |
| Missing validation label, audit unresolved | 1 | 3 |
| Platform or harness | 6 | 0 |
| Model knowledge | 1 | 4 |
| Awaiting review | 5 | 2 |

The 49 failures not attributed to the benchmark, by model (run-log trace, one reader, awaiting review): DeepSeek V4 Pro 18 Galaxy and 13 custom code, GPT-5.6 Luna 6 and 5, GPT-5.6 Sol 2 and 3, GPT-5.5 1 and 1.
Multi-step required results that failed: 253 of 783 (32.3%) versus 320 of 783 (40.9%); the scorer records only a symptom for 148 and 202 of them.
Multi-step causes named on the task pages, with the models named: in Galaxy, tool-form default or label misleading (all three), wrong parameter or threshold (all three), data-handling or scripting error (all three); with custom code, software or toolchain not available and method substituted (all three), output in the wrong format or under the wrong name (all three), wrong parameter or threshold (all three).

### Tokens (P8; Fig. 2d)

Token ratios count input plus output tokens, with cached input counted once; they are not cost ratios.

| Benchmark | Galaxy, millions | Custom code, millions | Ratio |
|---|---|---|---|
| BixBench-Verified-50 | 2,782.5 | 684.3 | 4.07 |
| CompBioBench (1,199 of 1,200 Galaxy runs recorded) | 12,923.3 | 5,216.5 | 2.48 |
| IWC multi-step | 1,642.1 | 1,115.8 | 1.47 |

BixBench by model (the October main runs, MCP execution stage): GPT-5.5 2.81, GPT-5.6 Sol 3.45, GPT-5.6 Luna 6.29, DeepSeek V4 Pro 3.30.

BixBench by outcome, in millions per run.

| Measure | Galaxy | Custom code |
|---|---|---|
| Correct runs, mean (median) | 4.12 (2.15) | 1.09 (0.46) |
| Incorrect runs, mean (median) | 9.02 (1.85) | 1.55 (0.67) |
| Ratio, correct runs only | 3.79 | |
| Share of tokens spent on correct runs | 79.6% | 84.2% |

Interface development series, all BixBench (slide 8):

| Stage | Model, replicates | Ratio | Galaxy accepted |
|---|---|---|---|
| Baseline | GPT-5.5, 1 | about 20, author estimate, no run records | |
| Prompts and skills | GPT-5.5, 1 | about 8, author estimate, no run records | |
| Prompts and skills (July 6 batch) | GPT-5.5, 3 | 5.48 | 139 of 150 |
| MCP execution (12 October snapshot) | GPT-5.5, 3 | 2.81 | 137 of 150, scored at the time |
| MCP execution (12 October snapshot) | GPT-5.6 Sol, 3 | 3.45 | 136 of 150, scored at the time |
| Compact replies, parameter templates, UDT checks | GPT-5.6 Sol, 1 | 2.42 | not reported |
| Plus longer waits | GPT-5.6 Sol, 3 | 1.53 | 137 of 150 published; 140 under the revised PhyKIT rule (sensitivity only) |

The three Sol ratios share one custom-code batch (35.51 million tokens per 50-task replicate).
From compact replies to longer waits, mean wait calls per replicate fell from 481 to 78 and model requests from 1,799 to 1,332.
In the July 6 batch cached input was 94.8% of Galaxy tokens and 88.8% of custom-code tokens; Galaxy runs took 37.9 against 14.2 agent turns (2.66 times), each carrying 74,600 against 34,000 cached tokens (2.2 times), with 1,851 against 154 platform or API commands and 788 against 164 skill reads; without skills the same batch used 502.8 million tokens and 126 of 150 answers were accepted, against 446.7 million and 139 with skills.
The CLI version, replicate coverage and scoring also changed between batches, so no single change is credited with a reduction and none with preserving accuracy.

### Slides against the frozen release

The slides were drawn from `Galaxy_benchmark/result_evaluation/figures/scored_runs.csv` (a scoring snapshot of 8 October 2026 in the authors' separate repository), from the IWC workflow tasks and from the token pages fetched on 12 October.
The 28 October release supersedes the snapshot; the paper uses the release.

| Slide | Slide shows | Where the slide number comes from | The paper uses |
|---|---|---|---|
| 1 Design | 4 models × 2 conditions × 3 benchmarks (IWC-WorkflowBench, 10 tasks) × 3 replicates = 3,840 runs | The design with the IWC workflow tasks | 4 models (3 on the multi-step tasks); BixBench-Verified-50, CompBioBench, IWC multi-step; 160 tasks, 3,780 runs |
| 2 Rule violations | About 25% of runs broke a rule; DeepSeek V4 Pro 74 of 108 major violations; web searches 437 runs, probed benchmark 232, listed other runs 139, viewed answers 59, local computation 38, copied answer 15 | Not found in either repository | Nothing until the audit table and its script are deposited |
| 3 Accuracy by benchmark | 87.7 / 87.2; 87.0 / 86.7; IWC 80.0 / 74.2 | 8 October snapshot (BixBench and CompBioBench reproduce exactly); the IWC values do not reproduce: the release gives 79.2 / 72.5 for the workflow tasks at ≥ 0.99 agreement | 89.5 / 88.3; 87.00 / 86.75; IWC multi-step 67.5 / 58.7 |
| 4 By model | BixBench 91/90, 91/89, 87/89, 82/81; CompBioBench 86/86, 92/91, 85/85, 85/84; IWC 70/63, 80/73, 73/73, 97/87 (Galaxy / custom code) | 8 October snapshot; IWC DeepSeek V4 Pro does not reproduce (release: 93/80) | The by-model table above, multi-step instead of IWC workflow tasks |
| 5 Consensus | BixBench 87.7/87.2, majority 88.0/89.5, correct once 91.5/91.0; CompBioBench 87.0/86.7, 87.25/89.0, 94.25/93.75; IWC 80.0/74.2, 80.0/72.5, 85.0/85.0 | 8 October snapshot, whose CompBioBench item scores are labelled "official leaderboard" (see Work before submission); IWC workflow tasks | The table "Scoring three attempts" |
| 6 bix-52-q7 | Wrong in 3 of 12 Galaxy runs: 19,160, 19,160, 539 | Release; reproduces | Same, adding that all 12 custom-code runs were correct |
| 7 Imaging task | Nine Galaxy runs, stage by stage, scores and hours | `multistep_runs.csv`; reproduces | Same, adding the nine custom-code runs |
| 8 Tokens | About 20, about 8, 5.48, 2.81, 6.29 (Luna), 3.67 (DeepSeek), 3.45, 2.42, 1.53 | `token_optimization_ratios.csv`; per-model points from the 12 October token pages | DeepSeek V4 Pro 3.30 from the release; title "from 5.5× to 1.5× in batches with run records" |

## External comparisons

| Our result | External result | Reference |
|---|---|---|
| CompBioBench 87.00% / 86.75% official, Codex CLI with four models | 78% to 83% for four agent harnesses, 83% for Codex CLI with GPT-5.4, from a bare environment | compbiobench (bioRxiv v2, 3 May 2026) |
| BixBench-Verified-50 89.5% / 88.3% | Original BixBench: frontier models reached 17% in the open-answer regime (a different, unverified question set) | bixbench2025 |
| 84 of 133 BixBench failures attributed to the task or its scoring | An automated audit matched 83.3% of expert-identified issues in BixBench-Verified-50; benchmark flaws can shift agent scores by up to 100% in relative terms | tu2026; zhu2025abc |
| Complete multi-step runs 24.4% / 23.3% | Agents' 50% time horizon about 50 minutes (Claude 3.7 Sonnet), doubling about every seven months; long-task failures come from execution even when the plan is given | kwa2025; sinha2026 |
| Majority of three: small gains | Self-consistency improved GSM8K accuracy by 17.9 points | wang2023sc |
| At least one of three correct: up to 19 points above a single run | Coverage grows with samples (15.9% to 56% on SWE-bench Lite with 250 samples), but without a verifier majority votes plateau | brown2024 |
| Attempts by the same model differ | Accuracy varied by up to 15% across runs at nominally deterministic settings; pass^8 under 25% in τ-bench retail | atil2024; yao2025tau |
| Interface engineering lowered the token ratio from 5.48 to 1.53 | Interface design added 10.7 points (64% relative) for SWE-agent; code execution with MCP cut one example from 150,000 to 2,000 tokens; retrieving only relevant tools cut prompt tokens by over half | yang2024sweagent; anthropic2025codeexec; gan2025ragmcp |
| Agents broke benchmark rules (counts pending) | o3 reward-hacked in 30.4% of RE-Bench runs; GPT-5 exploited tests in 76% of Oneoff-SWEbench tasks; agents searched Hugging Face for the benchmark instead of solving it | metr2025rh; zhong2025impossible; kapoor2026hal |

## References checked for this outline

Each was checked against the source named, on 18 November 2026 by a delegated literature search or, where the row says so, in October 2026; the 15 marked † were checked again against Crossref, arXiv or bioRxiv on 18 November.
"Abstract" means only the abstract was read.
Keys in bold in the paragraph outline are the core set for the main text (about 20, the journal's guideline); the rest can go to Methods or be dropped.
None is in `references.bib` yet; add each with the details below.

| Key | Reference | Checked against | Supports |
|---|---|---|---|
| gao2024 | Gao, S. et al. Empowering biomedical discovery with AI agents. *Cell* **187**, 6125–6151 (2024). doi:10.1016/j.cell.2024.09.022 | Crossref, PubMed 39486399 (checked 2 Oct 2026) | P1: agents in biomedical research |
| ghareeb2026 † | Ghareeb, A. E. et al. A multi-agent system for automating scientific discovery. *Nature* **655**, 497–505 (2026). doi:10.1038/s41586-026-10652-y | Crossref; PubMed 42156546 (abstract) | P1: Robin automates hypothesis generation and data analysis |
| gottweis2026 † | Gottweis, J. et al. Accelerating scientific discovery with Co-Scientist. *Nature* **655**, 487–496 (2026). doi:10.1038/s41586-026-10644-y | Crossref (abstract) | P1, optional: AML drug-repurposing candidates validated in vitro; the Nature editorial swaps this DOI with Robin's |
| ferber2025 † | Ferber, D. et al. Development and validation of an autonomous artificial intelligence agent for clinical decision-making in oncology. *Nat. Cancer* **6**, 1337–1349 (2025). doi:10.1038/s43018-025-00991-6 | Crossref (abstract) | P1: an oncology agent (clinical decision support, not data analysis) |
| biomni2026 | Huang, K. et al. Autonomous biomedical research with an artificial intelligence agent. *Science* **393**, eadz4351 (2026) | Crossref, PubMed (checked Oct 2026) | P1, optional |
| cellvoyager2026 | Alber, S. et al. CellVoyager: AI CompBio agent generates new insights by autonomously analyzing biological data. *Nat. Methods* **23**, 749–759 (2026) | Crossref (checked Oct 2026) | P1, optional |
| wiley2025 | Wiley. AI adoption jumps to 84% among researchers as expectations undergo significant 'reality check'. Press release, 7 Oct 2025 (ExplanAItions survey, 2,430 researchers) | Wiley newsroom page | P1: use 57% to 84%; concern about inaccuracies 51% to 64% |
| messeri2024 † | Messeri, L. & Crockett, M. J. Artificial intelligence and illusions of understanding in scientific research. *Nature* **627**, 49–58 (2024). doi:10.1038/s41586-024-07146-0 | Crossref; PubMed 38448693 (abstract) | P1: "produce more but understand less" |
| becker2025 | Becker, J., Rush, N., Barnes, E. & Rein, D. Measuring the impact of early-2025 AI on experienced open-source developer productivity. Preprint at arXiv:2507.09089 (2025) | arXiv (abstract) | P1: 19% slower with AI, believed 20% faster |
| stackoverflow2025 | Stack Overflow. 2025 Developer Survey: AI. survey.stackoverflow.co/2025/ai | The survey page | P1, optional: 46% distrust AI accuracy, 33% trust it; 66% frustrated by "almost right" answers |
| sandve2013 | Sandve, G. K., Nekrutenko, A., Taylor, J. & Hovig, E. Ten simple rules for reproducible computational research. *PLoS Comput. Biol.* **9**, e1003285 (2013) | Crossref; PubMed 24204232; full text | P1: keep track of how every result was produced, versions and intermediate results |
| gruning2018 | Grüning, B. et al. Practical computational reproducibility in the life sciences. *Cell Syst.* **6**, 631–635 (2018). doi:10.1016/j.cels.2018.03.014 | Crossref; PubMed 29953862 (abstract) | P1, optional |
| sinha2026 † | Sinha, A., Arun, A., Goel, S., Staab, S. & Geiping, J. The illusion of diminishing returns: measuring long horizon execution in LLMs. ICLR 2026; arXiv:2509.09677 | arXiv (abstract; HTML v3) | P2, P5: failures on longer tasks come from execution, not reasoning, when the plan is supplied |
| wang2024codeact | Wang, X. et al. Executable code actions elicit better LLM agents. ICML 2024; arXiv:2402.01030 | arXiv (abstract) | P2, optional: agents acting through code, the basis of the custom-code condition |
| bixbench2025 | Mitchener, L. et al. BixBench: a comprehensive benchmark for LLM-based agents in computational biology. Preprint at arXiv:2503.00096 (2025) | arXiv (checked Oct 2026) | P2, external comparison |
| compbiobench † | Nair, S. et al. Agentic systems are adept at solving well-scoped, verifiable problems in computational biology. Preprint at bioRxiv doi:10.64898/2026.04.06.716850 (2026) | bioRxiv API, v2 of 3 May 2026 | P2, P4: 78% to 83% for four harnesses |
| kapoor2025agents | Kapoor, S., Stroebl, B., Siegel, Z. S., Nadgir, N. & Narayanan, A. AI agents that matter. *Trans. Mach. Learn. Res.* (2025); arXiv:2407.01502 | arXiv (abstract); TMLR listing | P2, P8: accuracy-only evaluation; cost and accuracy optimized jointly |
| yao2025tau | Yao, S., Shinn, N., Razavi, P. & Narasimhan, K. τ-bench: a benchmark for tool-agent-user interaction in real-world domains. ICLR 2025; arXiv:2406.12045 | ICLR proceedings page; arXiv | P2, P6: pass^k; pass^8 under 25% in retail |
| goecks2010 | Goecks, J., Nekrutenko, A., Taylor, J. & The Galaxy Team. Galaxy: a comprehensive approach for supporting accessible, reproducible, and transparent computational research in the life sciences. *Genome Biol.* **11**, R86 (2010). doi:10.1186/gb-2010-11-8-r86 | Crossref (abstract) | P3: Galaxy tracks provenance |
| galaxy2024 | The Galaxy Community. The Galaxy platform for accessible, reproducible, and collaborative data analyses: 2024 update. *Nucleic Acids Res.* **52**, W83–W94 (2024). doi:10.1093/nar/gkae410 | Crossref (abstract) | P3, optional |
| galaxy2026 † | The Galaxy Community. Galaxy for accessible, reproducible, and collaborative data analyses: 2026 update. *Nucleic Acids Res.* **54**, W105–W116 (2026). doi:10.1093/nar/gkag469 | Europe PMC full text PMC13355071; Crossref | P3: IWC "open, peer-reviewed workflows"; Galaxy-MCP as future work (already in `references.bib` without pages) |
| iwc | Intergalactic Workflow Commission. About. iwc.galaxyproject.org/about (accessed 18 Nov 2026) | The page | P3: peer review, tests and daily testing of workflows; no journal paper on IWC exists |
| mcp | Model Context Protocol specification, version 2026-07-28 (in `references.bib`); Anthropic, Introducing the Model Context Protocol (25 Nov 2024) | The pages | P3 |
| yang2024sweagent | Yang, J. et al. SWE-agent: agent-computer interfaces enable automated software engineering. *Adv. Neural Inf. Process. Syst.* **37** (2024); arXiv:2405.15793 | NeurIPS proceedings page; arXiv HTML v3 | P3, P8: interface design changes agent performance (10.7 points, 64% relative) |
| schapiro2022 † | Schapiro, D. et al. MCMICRO: a scalable, modular image-processing pipeline for multiplexed tissue imaging. *Nat. Methods* **19**, 311–315 (2022). doi:10.1038/s41592-021-01308-y | Crossref (abstract) | P5: the imaging pipeline the task follows, shown on tissue and tumour images |
| creason2022 | Creason, A. L. et al. A web-based software resource for interactive analysis of multiplex tissue imaging datasets. Preprint at bioRxiv doi:10.1101/2022.08.18.504436 (v3, 2026) | bioRxiv API (not yet published in a journal) | P5, optional: Galaxy-ME, applied to normal and cancerous tissues; also the Galaxy Training Network TMA tutorial |
| wratten2021 | Wratten, L., Wilm, A. & Göke, J. Reproducible, scalable, and shareable analysis pipelines with bioinformatics workflow managers. *Nat. Methods* **18**, 1161–1168 (2021). doi:10.1038/s41592-021-01254-9 | Crossref; PubMed 34556866 (abstract) | P5, optional: workflow managers handle software installation and versions |
| kwa2025 | Kwa, T. et al. Measuring AI ability to complete long software tasks. NeurIPS 2025; arXiv:2503.14499 | arXiv (abstract) | P5: 50% time horizon about 50 minutes |
| wang2023sc | Wang, X. et al. Self-consistency improves chain of thought reasoning in language models. ICLR 2023; arXiv:2203.11171 | arXiv (abstract) | P6: majority voting |
| brown2024 † | Brown, B. et al. Large Language Monkeys: scaling inference compute with repeated sampling. Preprint at arXiv:2407.21787 (2024) | arXiv (abstract) | P6: coverage versus selection |
| atil2024 | Atil, B. et al. Non-determinism of "deterministic" LLM settings. Preprint at arXiv:2408.04667 (2024) | arXiv (abstract) | P6, optional: up to 15% accuracy variation across runs |
| tu2026 † | Tu, X. et al. Who guards the benchmarks? Automated auditing of LLM agent benchmarks. COLM 2026; arXiv:2604.24955 | arXiv (abstract) | P7: issues in BixBench-Verified-50 |
| zhu2025abc | Zhu, Y. et al. Establishing best practices in building rigorous agentic benchmarks. NeurIPS 2025 Datasets and Benchmarks; arXiv:2507.02825 | arXiv (abstract); venue from a proceedings listing, page not opened | P7, optional |
| metr2025rh | METR. Recent frontier models are reward hacking (5 Jun 2025). metr.org/blog/2025-06-05-recent-reward-hacking | The page | P7: reward hacking in 30.4% of RE-Bench runs |
| kapoor2026hal | Kapoor, S. et al. Holistic Agent Leaderboard: the missing infrastructure for AI agent evaluation. ICLR 2026; arXiv:2510.11977 | arXiv (abstract); venue from a proceedings listing | P7, optional: agents searched Hugging Face for the benchmark |
| zhong2025impossible † | Zhong, Z., Raghunathan, A. & Carlini, N. ImpossibleBench: measuring LLMs' propensity of exploiting test cases. Preprint at arXiv:2510.20270 (2025) | arXiv | P7, optional |
| anthropic2025codeexec | Anthropic. Code execution with MCP: building more efficient agents. Anthropic Engineering (4 Nov 2025). anthropic.com/engineering/code-execution-with-mcp | The page | P8: tool definitions and intermediate results inflate tokens; one example cut from 150,000 to 2,000 |
| luo2025mcpuniverse | Luo, Z. et al. MCP-Universe: benchmarking large language models with real-world Model Context Protocol servers. Preprint at arXiv:2508.14704 (2025) | arXiv (abstract) | P8, optional: input tokens grow rapidly with interaction steps |
| gan2025ragmcp | Gan, T. & Sun, Q. RAG-MCP: mitigating prompt bloat in LLM tool selection via retrieval-augmented generation. Preprint at arXiv:2505.03275 (2025) | arXiv (abstract) | P8, optional |
| natureed2026 † | Why AI cannot do good science without humans. *Nature* **653**, 650 (2026). doi:10.1038/d41586-026-01551-3 | Crossref; full text | P9: human oversight to catch errors |
| blau2024 † | Blau, W. et al. Protecting scientific integrity in an age of generative AI. *Proc. Natl Acad. Sci. USA* **121**, e2407886121 (2024). doi:10.1073/pnas.2407886121 | Crossref; Europe PMC full text | P9, optional: scientists accountable for AI-assisted inferences; disclosure of tools and settings |
| nmi2026 † | Multi-agent AI systems need transparency. *Nat. Mach. Intell.* **8**, 1 (2026). doi:10.1038/s42256-026-01183-2 | Crossref; full text | P9, optional: document workflows, model versions, prompts and human oversight |
| messeri2026 | Messeri, L. & Crockett, M. J. The uncritical adoption of AI in science is alarming — we urgently need guard rails. *Nature* **653**, 675–676 (2026) | Crossref (checked Oct 2026) | P1, optional |
| lu2026 † | Lu, C. et al. Towards end-to-end automation of AI research. *Nature* **651**, 914–919 (2026). doi:10.1038/s41586-026-10265-5 | Crossref (abstract) | Optional |

Not verified, so not to be cited: the percentages inside Baker (2016) and Bockting et al. (2023), which are behind paywalls; BixBench-Verified-50 leaderboard scores seen only in search snippets; a journal paper on the IWC (none exists).
Pages and volumes of the conference papers (ICLR, ICML, NeurIPS, COLM) were not confirmed; check them before the reference list is built.

## Display items

Two figures, as the format allows; each panel is redrawn from code with its `source_data.csv`, not copied from the slides.

| Figure | Panel | Shows | Supports | From slide |
|---|---|---|---|---|
| 1. Design, accuracy and the workbench on long analyses | a | The design (four models, three on the multi-step tasks; two conditions; three benchmarks; three replicates; 3,780 runs) and the division of labour: the agent plans, the MCP server and skills connect it to Galaxy, Galaxy executes and records, a person reads the history; the server's nine tools in three groups (find and set up a tool, run, check data) | P3 | 1, redrawn |
| 1 | b | Accuracy by benchmark and model, Galaxy and custom code, with the pooled differences and 95% intervals; CompBioBench official without an interval; multi-step results passed and complete runs | P4, P5 | 3 and 4, with release numbers and multi-step tasks |
| 1 | c | The imaging task run by run: stages passed, score out of 9 and hours, for the nine Galaxy and nine custom-code runs | P5 | 7, adding custom code |
| 2. Variability, record, errors and cost | a | Single attempt, at least two passed and at least one passed per benchmark and condition | P6 | 5, with release numbers |
| 2 | b | The bix-52-q7 history with the header line and the line count marked beside the accepted and reported answers | P6 | 6, adding the history |
| 2 | c | Errors recorded in successful runs and errors that prevented the answer, by subcategory and condition | P7 | New |
| 2 | d | Token ratio by interface stage and model, with the estimates of about 20 and 8 marked as unrecorded, and the main-run ratios by benchmark | P8 | 8, DeepSeek V4 Pro at 3.30 |

The Supplementary Information takes the rest: the rule-violation audit (slide 2), per-model accuracy with intervals, the multi-step analyses by task with the leave-one-task-out sensitivity, the ten shorter IWC workflow tasks (99.0% versus 95.3% mean agreement; 79.2% versus 72.5% of runs at ≥ 0.99; token ratio 0.96), the reconstructed CompBioBench comparison, raw against reviewed BixBench scoring, UDT use, the selected reruns and trial runs, the full execution-error tables and taxonomy, the run-log trace of the 49 BixBench failures, the answer-vote results, tokens by outcome, the token development series with its caveats, wall time, and the feature comparison with Galaxy-MCP.

## Format and word budget

A Brief Communication allows 1,200 words including abstract, references and figure legends, or 1,600 at the editor's discretion; legends count, so moving text into them saves nothing.

| Element | Journal limit | Standard version | Longer version, if 1,600 is granted |
|---|---|---|---|
| Abstract | 70 words, unreferenced | 70 | Same |
| Main text | No sections or subheadings | 9 paragraphs, about 645 | 9 paragraphs, about 960 |
| Figure legends | Counted | About 180 for 2 figures | About 250 |
| References | About 20 as a guideline; counted | 20, about 300 | 25, about 375 |
| **Total** | **1,200 (1,600)** | **About 1,195** | **About 1,655, so about 55 to cut** |
| Display items | 2 figures or tables, 3 at discretion | 2 figures, 3 and 4 panels | Same |
| Online Methods | Required, with subheadings; outside the count | Implementation, the interface's features against Galaxy-MCP, scoring, statistics, the audit and the rule-violation screen, disclosures | Same |

Nine paragraphs at about 70 words each is tight; the bullets as written run to 2,393 words.
To reach the standard version:

1. Merge P1 and P2 into one introduction paragraph of about 120 words, keeping the survey numbers and one sentence on plan versus execution (saves about 15 words and one paragraph break).
2. P3: the server's pattern in one clause; the design numbers to the Fig. 1a legend only if the legend is already counted at that length.
3. P4: the external comparison in one clause; the by-model sentence to the Supplementary Information.
4. P5: the imaging task in two sentences; the analytical-choice failures to the Supplementary Information.
5. P6: the answer vote and the 34 of 49 to the Supplementary Information.
6. P7: one sentence per group (absorbed, fatal); the rule-violation sentence to Methods.
7. P8: the development series in one sentence; the drivers to the Supplementary Information.
8. P9: the limits to one clause pointing to Methods.

Never cut: both multi-step endpoints, the sentence that the multi-step difference comes from one task, the upper-bound qualifier on "at least one passed", and the distinction between our server and Galaxy-MCP.

The journal lists software platforms and practical improvements to existing tools as Brief Communication material; novelty, usefulness, validation and broad applicability are required, not a biological discovery.
A paper that reads as a comparison of established tools may be redirected to the longer Analysis format, so keep the engineered interface and what its records reveal as the subject.

Title:

- "Engineering trustworthy AI agents for computational cancer research" (the authors').
  "Trustworthy" is a claim; the outline supports it as "agents whose every analysis leaves a standard record and whose variability, errors and cost were measured", and the inspection study would support it further.
  "Cancer research" will lead reviewers to expect cancer-specific evaluation; few tasks are explicitly about cancer (claim table), so either keep cancer research as the motivation in P1 and P9, which the bullets do, or report a cancer-specific subset.
- Alternative if a reviewer objects: "Engineering AI agents to work in the Galaxy workbench for inspectable computational biology".

## Which IWC results the paper reports

The repository holds two sets of ten IWC tasks; on 18 November the authors confirmed that the paper's third benchmark is the harder, multi-step set, although the slides show the workflow tasks.

| | IWC workflow tasks | IWC multi-step tasks |
|---|---|---|
| Task | Reproduce one IWC workflow of 2 to 27 tool steps | Carry a full analysis from raw data to 8–12 scored results; the task text names no software |
| Source file | `data/site/iwc/data/results.json` | `data/site/iwc/long-chain/data/results.json` |
| Runs | 240, four models | 180, three models (GPT-5.5 not run) |
| Galaxy versus custom code | 99.0% versus 95.3% mean output agreement; 79.2% versus 72.5% of runs at ≥ 0.99 | 67.5% versus 58.7% of required results passed; 24.4% versus 23.3% of runs with every result passed |
| Role in the paper | Supplementary Information | The third benchmark: abstract, P3 to P8 |

## The MCP server and how it differs from Galaxy-MCP

Source for P3, P8, Fig. 1a and the Methods section on implementation.
It combines the authors' description of 18 November with checks of the local copy of the server code (`Galaxy_benchmark/token_improvment/hf_batch/protocol/`, outside this repository) and of the public Galaxy-MCP repository, both on 18 November.
It describes the final version of the server; which features each benchmark's main runs had is still open (see "Work before submission").

### Why it was built

Agents working through the Galaxy API with prompts and skills used 5.48 times the tokens of custom code on BixBench (July 6 batch, the last before the server).
The authors' reading of the traces found two causes, and the same batch measures both (P8):

- many more model round trips (polling running jobs, retrying payloads after guessing the schema, re-checking jobs that had already finished): Galaxy runs took 2.66 times as many agent turns;
- long API replies (tool lists, full schemas, job details) that stay in the context and are resent with every later call: each Galaxy turn carried 2.2 times as much cached context.

### What it does

| Principle | What the server does | Checked in the code on 18 November |
|---|---|---|
| One call per job | Checks the inputs, submits once and waits for the job to finish, up to a time limit, then returns the outputs or the error; a separate wait tool follows jobs that outlast that limit without resubmitting | Yes: `run_galaxy_tool_and_wait` ("Submit and block; use this instead of BioBlend run_tool() plus polling"); `wait_for_galaxy_jobs` ("Block on existing jobs until terminal state without resubmission"); both waits take a time limit |
| Short replies | Tool search returns a short list of candidates; a tool schema shows only the fields and conditional branch the agent asked for, with a fill-in template that uses the real parameter paths; history listings and dataset previews are capped; a finished run returns the job state, check results, output IDs and small text outputs | Not checked line by line |
| No repeats | Outputs, unchanged results and schemas already shown in the session are shortened | Yes: unchanged repeat replies are abbreviated unless the agent asks to reread |
| Full records outside the conversation | The complete request, reply and job record go to a file, and the reply points to it; the agent reads only what it needs | Yes: each call writes its request and summary to an evidence directory; which of these files the scoring uses is not documented in this repository |
| Fewer failed submissions | Equivalent parameter formats are not flagged as mismatches; user-defined tool definitions are checked before the tool is created | Yes: numeric parameter values are compared as values; the user-defined tool's definition is validated before creation |

The nine tools, in three groups:

| Group | Tool | What it does |
|---|---|---|
| Find and set up a tool | `search_galaxy_tools` | Top matches among installed tools (current versions) by package, tool family, operation or metric |
| | `inspect_galaxy_tool` | The tool's live input schema, limited to the fields and branch the agent asks for |
| Run | `run_galaxy_tool_and_wait` | Check inputs, submit once, wait, return the outputs or the error |
| | `run_galaxy_udt_and_wait` | Create and run a user-defined tool (a command in a container), then wait |
| | `wait_for_galaxy_jobs` | Keep waiting on jobs already submitted, without resubmitting |
| | `stage_workspace_file` | Upload a local file and wait until it is ready |
| Check data | `inspect_galaxy_history` | Datasets in the history, filtered by name or type |
| | `peek_galaxy_dataset` | Preview and column information for one dataset |
| | `inspect_archive_inventory` | Files inside an archive |

In the local copy, eight tools are served by `galaxy-execute` and `wait_for_galaxy_jobs` by a separate wait server; a blocking variant serves six, without staging, peeking or waiting.
Not every benchmark exposed every tool: the multi-step and IWC workflow tasks had no user-defined-tool tool, and only CompBioBench had the dataset-peek tool (`error_taxonomy.md`, "Caveats").
By the stage names of the token development series (P8), run calls that wait were in place from the MCP-execution stage, which the main runs used; compact replies, parameter templates and user-defined-tool checks entered after the main runs (ratio 2.42), and longer waits last (1.53).
So the main runs did not have the short replies, and the paper must not describe the final server as the one behind P4 to P7.
When repeat shortening, record files and the parameter-equivalence rule entered is not recorded in this repository.

### Difference from Galaxy-MCP

| | Galaxy-MCP | Our server |
|---|---|---|
| Scope | General purpose, covering most of the Galaxy API (about 49 tools in the versions read on 17 November): histories, uploads, collections, tools, user-defined tools, jobs, workflows (including IWC) and pages | Finding, running and checking tools on the data in one history (nine tools) |
| Running a tool | `run_tool` returns as soon as the job is submitted, and the agent checks the status afterwards | Returns when the job has finished, with its outputs or error |
| Parameters | Dataset-versus-collection preflight only; no comparison of the parameters Galaxy resolved (v1.9.0 to v1.12.0) | Compares the parameters Galaxy resolved with those requested |
| Replies | Full API replies | Short replies, repeats shortened, full records saved to files |
| Code | BioBlend | BioBlend; imports nothing from Galaxy-MCP and shares no operation names with it |

How to say it in the paper:

- "Our server covers a subset of Galaxy-MCP's operations and changes how they behave in an agent loop", not "ours is a subset of Galaxy-MCP": the journal requires novelty, and a reviewer will read "subset" as no contribution.
- "A run call submits once and waits for the job", not "the agent never polls": agents still made wait calls for long jobs (481, then 78 per replicate in the GPT-5.6 Sol batches).
- Contributions back to Galaxy-MCP: the authors' note says lessons go back to Galaxy-MCP as pull requests.
  On 18 November the merged pull requests from accounts that appear to be the lab's add a Streamable HTTP transport (#196, merged 28 October) and MCP Apps cards for histories and datasets (#206, merged 18 November); open ones add a per-session history scope (#233), which may address the 1,251 tool lookups without a usable history in P7, extraction of a workflow from a history (#226) and checks before running user-defined tools (#227, #230).
  None of the merged ones carries waiting for jobs or short replies; cite only merged pull requests, by number, after the authors confirm the accounts.
- How the server relates to agentic-plugins, which installs Galaxy-MCP with Galaxy skills in agent harnesses, is still the authors' decision.

## Work before submission

### Required for submission

- [ ] Deposit the rule-violation audit behind slide 2: the run-level table, the rules, the prompt of the agent that flagged violations, and the human review, with a script in `analysis/` that writes the counts.
  State how runs that copied an answer (15) or viewed answers (59) were scored, and report the accuracy of every benchmark with flagged runs counted as wrong.
  Reconcile it with the earlier case review in `Galaxy_benchmark/individual_error_analysis.md` (28 September, older archive): answer retrieval attempted in 26 tasks, two Galaxy runs that copied answers from other runs through the shared Galaxy account, and 15 correct Galaxy CompBioBench answers computed locally.
- [ ] Redraw every slide used as a figure from the 28 October release (table "Slides against the frozen release"), with the multi-step tasks in place of the workflow tasks.
- [ ] Establish what the CompBioBench item scores in `Galaxy_benchmark/result_evaluation/figures/scored_runs.csv` are: they are labelled "official leaderboard" and give 1,044 and 1,040 of 1,200, one custom-code item fewer than the release's official 86.75 (1,041).
  If they are the official item grades, use them for P6 and for a paired interval on the official score, and drop the reconstructed key to a diagnostic.
- [ ] Count execution errors per model (extend `analysis/error_taxonomy.py` to group by model) to answer "do models hit the same challenges" for all three benchmarks, not only from the multi-step task pages.
- [ ] Check the bix-52-q7 history of the 539 run before Fig. 2b mentions it.
- [ ] Name the exact version (release or commit) of the server, skills and prompts benchmarked on each benchmark, which of the nine tools each benchmark exposed, and the Galaxy release on usegalaxy.org during the runs.
  Record the batch at which each feature in "The MCP server and how it differs from Galaxy-MCP" entered, so that Methods describes the server the main runs used and the later changes separately.
- [ ] Release the server, skills and prompts under an open licence with a DOI, and state how they relate to Galaxy-MCP and agentic-plugins; finish the feature comparison started on 17 November (Galaxy-MCP v1.9.0 to v1.12.0 submit and return without waiting or comparing resolved parameters; our server imports nothing from it) and pin it to the Galaxy-MCP version current at submission.
- [ ] List the pull requests to Galaxy-MCP that carry lessons from this server, confirm their authors, and cite only merged ones.
- [ ] Claim "reproducible" only if a sample of histories is rerun without an agent; archive the histories and each UDT's code with a DOI before claiming durable access.
- [ ] Freeze one results release and regenerate every number from it; integrate the multi-step tasks into `data/results_manifest.csv`, the manuscript, the figure build and the source-data inventories (the package still describes the 3,840-run design).
- [ ] Commit the verification scripts and tables (`analysis/verify_outline_claims.py`, `analysis/check_bixbench_header.py`, the error-taxonomy scripts, `data/outline_verification/`, `data/error_taxonomy/`).
- [ ] Review the audit labels used in P7 (7 unreviewed, 4 unresolved) and the rules that type execution errors; a second automated count is not an independent review.
- [ ] Add the core references to `references.bib`, each with the details checked above, and confirm conference pages and volumes.
- [ ] Decide the title's "cancer research" (claim table, "Title").
- [ ] Count the rendered reference list and legends, fit the total to 1,200 words, and send a presubmission enquiry asking the editor to confirm Brief Communication over Analysis.

### Recommended

- [ ] Run the blinded comparative inspection study designed on 17 November: reviewers who did not run the analyses receive either the Galaxy history or the preserved custom-code scripts, logs and outputs, without the answer key, for runs whose outcomes were established independently (correct analyses, natural failures with biological consequences and, where feasible, matched seeded mistakes); outcomes are wrong answers flagged, false alarms, time to a decision and the named cause.
  It is the only test of whether the record makes human checking better, which "trustworthy" and the closing sentence imply; freeze the protocol first and ask whether the institution requires ethics review.

### Disclosures in Methods

- [ ] Every replaced run and earlier recovery batch, the reason, and whether replacement depended on the outcome.
- [ ] The 16 GPT-5.6 Luna trial runs that count as run 1 in both conditions on eight multi-step tasks, including the imaging task.
- [ ] Uneven model coverage: GPT-5.5 did not run the multi-step tasks.
- [ ] Prompts that differ between conditions (707 against 366 median words on BixBench), and which skills belong to the interface rather than to the domain guidance both conditions received.
- [ ] Resources: on the multi-step tasks the Galaxy agent worked from a container with 8 GB of memory and ran its jobs on usegalaxy.org, and the custom-code agent had 64 GB and internet access.
- [ ] IWC references built by running the IWC workflows in Galaxy.
- [ ] Both BixBench scorings; the sign of the difference rests on one question, bix-45-q1.
- [ ] The rule-violation screen, its method (agent-assisted flagging and human review) and its effect on the scores.
- [ ] The AI tools used to prepare the manuscript and analyses, as `AGENTS.md` requires.

### Optional: would support further claims

- [ ] A second agent harness on a subset of tasks, to show that the server is not tied to Codex.
- [ ] GPT-5.5 on the multi-step tasks, so that all four models cover all three benchmarks.
- [ ] More multi-step tasks that need hard-to-install software, to test whether the imaging result generalizes.
- [ ] A broader failure audit: CompBioBench's 302 reconstructed-key mismatches and the multi-step causes the scorer records only as symptoms.
- [ ] A controlled interface comparison with model, CLI, tasks and scoring fixed, to credit individual changes with token reductions, and a rerun of the main benchmarks with the optimized interface.

## Where each number comes from

`analysis/verify_outline_claims.py` writes the tables in `data/outline_verification/` offline from the frozen exports and checks their fingerprints; on 18 November it was extended to write `bixbench_tokens_by_model.csv`, and every other table it writes was reproduced byte for byte.
`analysis/check_bixbench_header.py` reads the public bix-52-q7 histories over the network.
Neither script nor its tables is committed yet.
A script that reproduces a count does not validate the classification behind it.

| Numbers | Source |
|---|---|
| Tasks, runs and the 1,890 Galaxy history links | `data/outline_verification/verification.json`; `data/results_manifest.csv` still describes the 3,840-run design |
| Scores, intervals and per-model values | `data/accuracy_summary.csv`, `data/accuracy_by_model.csv` (`analysis/accuracy.py`); `data/outline_verification/performance.csv` |
| Multi-step by task, imaging runs and leave-one-task-out | `data/outline_verification/multistep_by_task.csv`, `multistep_runs.csv`, `multistep_leave_one_out.csv` |
| Imaging-task causes | `data/error_taxonomy/iwc_multistep_page_causes.csv`, rows C77 to C84, classified from the archived task pages; await author review |
| Replicate diagnostics | `data/outline_verification/replicate_diagnostics.csv`; BixBench and CompBioBench also in `s3_repeatability/dataset/source_data.csv` |
| bix-52-q7 answers and histories | `data/site/bixbench/data/results.json`; `data/outline_verification/header_history_check.csv` |
| Audit labels and the 34 of 49 | `data/outline_verification/audit_labels.csv`; `fig2_interface/dataset/bixbench_current_failures.csv` |
| Traced failures by model | `data/error_taxonomy/bixbench_agent_failures_traced.csv` |
| Execution errors in successful runs | `data/outline_verification/error_subcategories.csv`, `error_totals.csv`, `error_denominators.csv` (from `analysis/error_taxonomy.py`) |
| Multi-step failed results and causes | `data/error_taxonomy/iwc_multistep_reasons.csv`, `iwc_multistep_page_causes.csv`; `manuscript/error_taxonomy.md` |
| Lookups without usable history context | `data/outline_verification/history_lookup_errors.csv` |
| Token totals and ratios by benchmark | `data/outline_verification/token_costs.csv` |
| BixBench token ratios by model and by outcome | `data/outline_verification/bixbench_tokens_by_model.csv`, `bixbench_tokens_by_outcome.csv` |
| Token development series, wait calls, model requests | `data/token_optimization_ratios.csv`, `data/token_optimization_rounds.csv`, `fig2_interface/dataset/source_data.csv` |
| Token drivers, July batch | `figures/benchmark_results_summary/s7_token_drivers/dataset/source_data.csv` |
| IWC workflow tasks at ≥ 0.99 | `data/accuracy_summary.csv`, `strict_pct` |
| Slide numbers | `Galaxy_benchmark/result_evaluation/figures/scored_runs.csv` (outside this repository; recomputed on 18 November); `data/token_ratios_main_runs.csv`, `data/site_token_totals.csv` (12 October token pages); slide 2: no source found |
| Cancer terms in task text | Search of the question text in `data/site/` on 18 November; no script |
| External numbers | "References checked for this outline" |
| Server design, tools and the comparison with Galaxy-MCP | Authors' description, 18 November; local code copy `Galaxy_benchmark/token_improvment/hf_batch/protocol/` (`galaxy_execute_mcp.py`, `galaxy_wait_mcp.py`, `galaxy_execute_mcp_blocking.py`; outside this repository); github.com/galaxyproject/galaxy-mcp pull requests, read 18 November |
