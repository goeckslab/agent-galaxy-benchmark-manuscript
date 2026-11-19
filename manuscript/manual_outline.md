# Engineering trustworthy AI agents for computational research

## Abstract

- Agents can accelerate computational research, but an answer is hard to trust without seeing and understanding how it was produced.
- An MCP interface connects an agent's analysis plan to the Galaxy workbench, where the plan is executed and recorded.
- Accuracy is kept when Galaxy executes the model's plan; token usage is slightly higher, but a standard record is kept for every run.

## P1. Agents accelerate computational research, but reviewing what they produce limits trust in their answers

- Researchers are adopting AI agents quickly, as agents have proven able to plan and execute computational analyses.
- Trust has not kept pace: to some extent, the greater volume of output overwhelms people's capacity to understand it.
- Agents can be set up to organize their outputs. However, the lack of a standard for how they do this is a challenge for reproducibility and interpretability.

## P2. Trusting an analysis means trusting both the plan and its execution, and a single benchmark score shows neither

- An agent's knowledge produces a plan, but the environment to execute it must be built entirely at run time for the plan to be viable. As the analysis grows longer, the chance of errors grows proportionally.
- Benchmarks test planning and execution together, but the traces that models generate while executing the tasks are rarely analyzed rigorously.
- Understanding where an agent is strong, where it fails, and when to check its answer is fundamental to building trust.

## P3. Galaxy, a workbench built for humans, can be engineered to work with agents

- Galaxy, a workbench used worldwide, offers thousands of curated tools, compute for large analyses, and histories.
- Galaxy was built for humans executing analyses. A Model Context Protocol (MCP) server exposes Galaxy's operations to AI agent clients; however, how an agent's interface is designed changes what the agent achieves.
- We engineered an MCP server and skills and evaluated them on three benchmarks. Four models ran each task three times in each of two execution environments: custom code and Galaxy. We ask whether combining agents with Galaxy keeps accuracy, helps on long analyses, and makes the agents' variability and errors visible enough to judge when an answer can be trusted.

## P4. Agents working through Galaxy scored at least as high as agents writing their own code

- Galaxy versus custom code: BixBench-Verified-50, 89.5% versus 88.3% of answers accepted (difference 1.2 points, 95% interval −1.5 to 4.2); CompBioBench, 87.00 versus 86.75 official points, with no paired interval because item-level official grades are not available; multi-step analyses, 67.5% versus 58.7% of required results passed (8.8 points, −6.1 to 27.1).
- By model: Galaxy scored at or above custom code for three of four models on BixBench and on CompBioBench, and for all three on the multi-step analyses; scores varied more across models (BixBench 83.3% to 93.3%) than between conditions.
- Working through Galaxy did not cost accuracy, and it brought Galaxy's important features into the analysis.

## P5. On multi-step analyses, the workbench supplied software that agents writing their own code did not manage to install and run

- Galaxy runs passed more required results for each of the three models, but complete runs were rare in both conditions: 24.4% versus 23.3% (1.1 points, −16.7 to 21.1).
- On one task, multiplex tissue imaging, Galaxy runs passed 70 of 81 results and completed 6 of 9 runs with installed tools, over 6 to 21 hours; custom-code runs passed 7 of 81, completed none and stopped after 10 to 38 minutes, having substituted their own methods, in some runs because a package such as the segmentation model would not install.
- The workbench matters most where an analysis depends on software that is hard to install and run.

## P6. Repeated attempts show that single answers vary, and that a check could recover most remaining failures

- The consensus (at least two of three runs correct) recovered more for custom code than for Galaxy (Galaxy 0.5 versus custom code 2.2 points on BixBench; 0.9 versus 1.5 on CompBioBench), because custom-code failures were more often isolated to one attempt (groups with exactly two of three passing: 9 versus 16 on BixBench and 31 versus 43 on CompBioBench). This did not hold on the multi-step results (69.0% versus 58.1%).
- At least one correct run increases accuracy equally in Galaxy and custom code, confirming that agents' problems are most often related to the execution step rather than to a knowledge limitation. It also shows the randomness of agents' execution.
- Answers therefore need a check, and a standard record is what lets a person, or another agent, make it.

## P7. Standard records map agents' errors: interface errors that runs absorbed, and failure causes shared across models

- Among successful runs with event logs, 6% contained at least one recorded execution error.
- In Galaxy, these were mostly requests that the interface rejected (parameters and tool lookups), which a better interface can prevent; custom-code runs more often met software that was not available and compute limits.
- Because causes recur across models, fixing them once in the interface serves every model.

## P8. Galaxy costs more tokens, and engineering the interface lowered the overhead

- In the main runs, Galaxy used 4.07, 2.48 and 1.47 times the tokens of custom code on BixBench, CompBioBench and the multi-step analyses. Token use did not signal whether an answer was right: a typical incorrect Galaxy run used about as many tokens as a correct one (median 1.85 versus 2.15 million), although a few failing runs used far more (mean 9.0 versus 4.1 million).
- In successive BixBench batches, the ratio fell from 5.48 (prompts and skills, GPT-5.5) to 2.81 (MCP execution), and for GPT-5.6 Sol from 3.45 to 2.42 (compact replies) and 1.53 (longer waits), without affecting accuracy (137 of 150 answers accepted).
- Reducing token usage is important so that bringing Galaxy's features into the task-execution pipeline is not penalized.

## P9. Paired with Galaxy, agents' analyses become inspectable and open to oversight

- AI agents have the potential to automate and accelerate many aspects of computational cancer research; through Galaxy they kept accuracy close to custom code, completed analyses whose software they could not install themselves, and left a standard record of every run, which made their variability and errors identifiable.
- Our results show that pairing AI agents with Galaxy enables accurate, verifiable and reproducible computational research, and Galaxy's curated software tools, scalable computing resources and auditable histories support trustworthy AI agents as well as human oversight.
