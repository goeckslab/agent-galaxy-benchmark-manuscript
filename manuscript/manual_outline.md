# Engineering inspectable AI agents for computational research with Galaxy

## Abstract

- AI agents can accelerate research, but trusting an answer requires seeing how it was produced.
- Through our interface, agents choose tools and parameters; Galaxy executes and records each job.
- On three benchmarks (3,780 runs), agents working in Galaxy scored close to agents writing custom code and every Galaxy run had a history link

## P1. Agents now run computational analyses, but a benchmark score shows whether an answer passed, not how it was produced

- AI agents now plan and execute computational biology analyses, from single questions to whole studies, and researchers are adopting AI faster than they trust it. Allowing agents to execute a plan means building the environment at run time: installing software, choosing parameters and organizing files, each of which can be done in many ways, and even when given the plan, models make more mistakes as tasks get longer.
- Benchmarks such as BixBench and CompBioBench rank agents by a single accuracy score. A score tells whether an answer passed, but not at which step an analysis went wrong, whether the plan or its execution was at fault, and how answers vary between attempts.
- An execution record lets a researcher investigate how an answer was produced: which software ran, with which version and parameters, on which intermediate results. Agents can be asked to keep such records, but each researcher asks for a different structure and level of detail, so the records are not standard.

## P2. Galaxy, a workbench built for humans, can be engineered to work with agents

- Galaxy, a workbench used worldwide, offers thousands of curated tools, compute for large analyses, and histories that record each job's tool, version, parameters, inputs and outputs. Researchers with access to the history can inspect intermediate results, rerun a step with revised parameters, or continue the analysis in Galaxy after the agent session ends.
- Galaxy-MCP, a community server for the Model Context Protocol (MCP), exposes Galaxy's operations to AI clients, but the Galaxy 2026 update lists it as future work without evaluating agents, and how an agent's interface is designed changes what the agent achieves. 
- We engineered our own MCP server and skills, separate from Galaxy-MCP, to divide the work: the agent selects tools and parameters and interprets outputs, while Galaxy executes and records the jobs. Where enabled, user-defined tools (UDTs) let the agent package custom code as a recorded Galaxy job.
- Four models (three on the multi-step tasks) ran each task three times in Galaxy and three times with custom code, on BixBench-Verified-50, CompBioBench and ten multi-step analyses built from the peer-reviewed workflows of the Intergalactic Workflow Commission (IWC). We ask whether working through Galaxy keeps accuracy, helps on long analyses, and makes the agents' variability, errors and cost visible enough to judge when an answer can be trusted.

## P3. On two benchmarks, agents working through Galaxy scored close to agents writing their own code

- On BixBench-Verified-50, 89.5% of Galaxy answers and 88.3% of custom-code answers were accepted (difference 1.2 points, 95% interval −1.5 to 4.2). On CompBioBench, the official scores were 87.00% for Galaxy and 86.75% for custom code, with no paired interval because item-level official grades are not available.
- By model, Galaxy scored at or above custom code for three of four models on BixBench and on CompBioBench, and scores varied more across models than between conditions (Galaxy on BixBench ranged from 83.3% for DeepSeek V4 Pro to 93.3% for GPT-5.5). These scores are in line with the 78% to 83% that CompBioBench's authors report for four agent harnesses.
- Observed scores were close on both question benchmarks. Galaxy usage did not had impact on model's accuracy.

## P4. On multi-step analyses, the estimate favoured Galaxy, and one imaging task accounted for most of the observed gap

- Each of the ten multi-step tasks asked agents to produce 8–12 required results from raw data using software of their choice. On average, Galaxy runs passed 67.5% of required results and custom-code runs 58.7% (8.8 points, 95% interval −6.1 to 27.1), and Galaxy runs passed more for each of the three models (by 1.9 to 15.6 points). Complete runs were rare in both conditions: 24.4% of Galaxy runs and 23.3% of custom-code runs passed every required result (1.1 points, −16.7 to 21.1).
- The multiplex tissue imaging task accounted for most of the gap in required results. On that task, the nine Galaxy runs (three per model) used tools installed in Galaxy, which also hosted the jobs and intermediate datasets; they took 6 to 21 hours and passed 70 of 81 results (nine per run), and 6 of the 9 runs passed all nine. The nine custom-code runs passed 7 of 81, none passed all nine, and they stopped after 10 to 38 minutes, having substituted their own methods, in some runs because a package such as the segmentation model would not install.
- The imaging task is the concrete case for installed tools: Galaxy supplied the pipeline's software, as workflow systems do for their users, whereas the custom-code runs tried to replace it.

## P5. Every Galaxy run had a history link, and on one question the histories showed how wrong answers arose

- All 1,890 Galaxy runs have a link to their Galaxy history.
- On bix-52-q7, 3 of 12 Galaxy runs were wrong while all 12 custom-code runs were right. Two of the wrong runs answered 19,160 removed rows instead of 19,159. Their seven-item histories show the error step by step: the filtered table kept its header line, and the line count included it. Applying the question's methylation thresholds to the original data independently gives 19,159.
- Reading the history located the error at one step, which the score alone could not show. Both models with wrong runs also answered correctly in another attempt.

## P6. Answers varied between attempts, and recovering the right one needs a check of how it was produced

- With the answer key, at least one of a model's three attempts passed on 93.0% (Galaxy) and 92.0% (custom code) of BixBench model–question pairs, 92.5% and 96.0% on CompBioBench, and 86.5% and 70.9% of multi-step required results; 34 of the 49 BixBench had a correct attempt by the same model in the same condition. 
- Counting a question as passed when at least two attempts passed changed scores by at most 2.2 points, and gained more for custom code on BixBench and CompBioBench. Both measures need the key to pick the right attempt, so they show how much single answers vary.
- Without the key, an agent could take the answer that at least two of its attempts gave. On BixBench, this vote accepted 82.5% of Galaxy and 80.0% of custom-code model–question pairs, below single attempts (89.5% and 88.3%), because 11.0% and 12.0% of pairs had no shared answer and counted as not accepted. Recovering the right attempt needs a check that tells which answer is right.

## P7. Standard records map agents' errors and make agents virtual users of the interface

- Among successful runs with event logs, 87.6% of Galaxy runs (1,391 of 1,587) and 72.6% of custom-code runs (1,169 of 1,610) recorded at least one execution error. In Galaxy, the most frequent were parameters that the interface rejected (55.6% of these runs), which a better interface can prevent; custom-code runs more often met software that was not available (46.9%, against 20.9% in Galaxy). Galaxy errors could be typed by rule because the interface answers every call with one of a fixed set of statuses; custom-code errors had to be read from free-text shell output.
- Of the 133 wrong BixBench answers (63 Galaxy, 70 custom code), the audit attributes 84 to the task or its scoring, as independent audits have found flawed tasks in agent benchmarks, BixBench-Verified-50 among them. Of the other 49, it classifies 27 as missing validation of intermediate results, 6 as platform or harness and 5 as model knowledge; 4 more carry the missing-validation label but remain unresolved, and 7 await review. On the multi-step tasks, 253 of 783 required results failed in Galaxy and 320 of 783 with custom code, and the task pages name the same kinds of cause for all three models: misleading tool defaults or labels and wrong parameters in Galaxy, and unavailable software and substituted methods with custom code.
- Agents working through Galaxy act as virtual users: recurring rejected requests and retries, each recorded with its status, give developers concrete problems to investigate.

## P8. Token use was higher with Galaxy and lower in successive interface development batches

- In the main runs, Galaxy runs used 4.07 times as many tokens as custom-code runs on BixBench, 2.48 times on CompBioBench and 1.47 times on the multi-step analyses, and agents should be compared on cost as well as accuracy. On BixBench, token use did not signal whether a Galaxy answer was right: the median incorrect run used 1.85 million tokens and the median correct run 2.15 million, although a few incorrect runs used far more (mean 9.0 against 4.1 million).
- Development batches on BixBench followed the virtual-user cycle: examine the traces, revise the interface, measure again.
- Across batches, the observed Galaxy-to-custom-code token ratio was lowering as we better engineered the interface: with GPT-5.5, 5.48 (prompts and skills) and then 2.81 (MCP execution); with GPT-5.6 Sol, 3.45, then 2.42 (compact replies) and 1.53 (longer waits). Galaxy accuracy was held, the number of tasks accepted was of 136 to 139 of 150 answers correct. The main runs did not use the later changes, which were tested on BixBench only, and reducing this overhead matters so that the cost of Galaxy's features does not outweigh their benefits.

## P9. The histories that make analyses inspectable can also expose earlier answers to later benchmark runs

- Some agents broke the rules set for the benchmarks: they read earlier answers or execution traces for the same question, including the project's public results pages and other runs' published Galaxy histories, copied a published answer, or searched the web for the question text. Evaluations of other agents report the same behaviour.
- A review found 68 BixBench and CompBioBench runs with confirmed or possible exposure, and we reran them under a stricter block (Methods); the pooled official CompBioBench scores were unchanged (87.00% and 86.75%).
- The same records made the breaches detectable. Benchmarks for agents need runs isolated from published results, and agents' answers need oversight that reads how each was produced.

## P10. Paired with Galaxy, agents' analyses become inspectable

- AI agents have the potential to automate and accelerate many aspects of computational research, including cancer research. Through Galaxy, they scored close to agents writing their own code on BixBench and CompBioBench. Every Galaxy run had a history link.
- Limits: four models in one agent harness (three on the multi-step tasks). 
- No direct test yet of whether people review answers better with histories or whether the benchmarked analyses replay end to end from their histories. 
- The records also suggest how to build in rigor: disagreement between answers or methods could trigger inspection, and checks on intermediate outputs could run before an answer is reported.
- Pairing AI agents with Galaxy makes their analyses inspectable: Galaxy's curated tools, scalable compute and histories keep each answer next to the jobs that produced it, open to human oversight. 
- For tool developers, agents can serve as virtual users: examining their traces, revising the interface and measuring again turns benchmarking into usability testing.