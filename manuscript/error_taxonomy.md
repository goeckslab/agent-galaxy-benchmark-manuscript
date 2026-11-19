# Error taxonomy: what went wrong when agents ran the analyses

Side document for the authors, written on 17 November 2026 from the 28 October 2026 results release and the run event logs.
It is not rendered into the manuscript.
It maps the mistakes agents made in two broad categories:

- **Knowledge:** the agent chose the wrong analysis (concept, method, parameter, or what the question asked).
- **Execution environment:** the analysis chosen was appropriate, but carrying it out or delivering it went wrong.

Each category splits into subcategories built from the errors actually observed, and every error belongs to one of two groups:

- **Recorded in successful runs:** the error occurred and the run still ended with a correct answer.
  The logs do not show that the agent repaired a given error, or that the next call fixed it.
- **Prevented the correct answer:** the error is why the run's answer, or one of its results, was wrong.

The two conditions are "Galaxy" and "custom code", as in the paper.
Counts come from the scripts and tables listed under "Sources and how to reproduce"; the classifications of individual failures await author review.

## Summary

### At a glance

| Measure | Galaxy | Custom code |
|---|---|---|
| Runs with an event log | 1,998 | 2,010 |
| Runs that ended correct | 1,682 | 1,697 |
| Correct runs with at least one recorded execution error | 1,486 (88.3%) | 1,248 (73.5%) |
| Execution errors in those correct runs | 11,651 (6.9 per correct run) | 4,088 (2.4 per correct run) |
| Shell commands that failed with a real error | 3,436 of 70,619 (4.9%) | 5,772 of 67,542 (8.5%) |
| Galaxy interface calls that failed | 12,585 of 79,845 (15.8%) | not applicable |
| BixBench wrong answers traced to a cause (run-log trace, one reader, awaiting review) | 63 | 70 |
| ... knowledge | 12 | 15 |
| ... execution environment | 12 | 6 |
| ... task or scoring ambiguity (the benchmark, not the agent) | 36 | 48 |
| ... unclear | 3 | 1 |
| IWC multi-step results that failed | 253 of 783 (32.3%) | 320 of 783 (40.9%) |

### Map of errors by category and subcategory

Recorded in successful runs: correct runs with at least one error of the subcategory, and their share of correct runs.
Prevented: BixBench runs whose wrong answer the subcategory explains, and IWC multi-step runs the task pages name for it (a run can be named for more than one failed result).
A dash means the source cannot show that kind of error.

| Category | Subcategory | Recorded in successful runs, Galaxy | Recorded in successful runs, custom code | Prevented, BixBench, Galaxy | Prevented, BixBench, custom code | Prevented, IWC multi-step, Galaxy | Prevented, IWC multi-step, custom code |
|---|---|---|---|---|---|---|---|
| Knowledge | Wrong parameter or threshold | – | – | 6 | 4 | 30 | 6 |
| Knowledge | Wrong biological or statistical concept | – | – | 3 | 7 | 0 | 0 |
| Knowledge | Wrong method for the question | – | – | 2 | 3 | 5 | 3 |
| Knowledge | Task or question misread | – | – | 1 | 0 | 7 | 3 |
| Knowledge | Step omitted or added | – | – | 0 | 1 | 5 | 4 |
| Execution environment | Software not available | 384 (22.8%) | 815 (48.0%) | 0 | 0 | 14 | 4 |
| Execution environment | Specified tool replaced by the agent's own code | – | – | 0 | 0 | 0 | 17 |
| Execution environment | Tool version or implementation differs from the reference | – | – | 2 | 3 | 0 | 4 |
| Execution environment | Interface or API request rejected | 787 (46.8%) | 160 (9.4%) | 0 | 0 | 0 | 0 |
| Execution environment | Parameters rejected | 968 (57.6%) | 72 (4.2%) | 0 | 0 | 0 | 0 |
| Execution environment | Galaxy tool default or label misleading | – | – | 0 | – | 11 | – |
| Execution environment | Agent's own code failed | 641 (38.1%) | 238 (14.0%) | 0 | 0 | 0 | 0 |
| Execution environment | Data or file handling | 641 (38.1%) | 554 (32.6%) | 6 | 3 | 12 | 1 |
| Execution environment | Analysis tool failed | 391 (23.2%) | 76 (4.5%) | 0 | 0 | 3 | 0 |
| Execution environment | Compute limit reached | 107 (6.4%) | 289 (17.0%) | 0 | 0 | 0 | 0 |
| Execution environment | Platform, network or sandbox | 246 (14.6%) | 275 (16.2%) | 0 | 0 | 0 | 0 |
| Execution environment | Output not delivered as required | – | – | 0 | 0 | 8 | 11 |
| Execution environment | Result accepted without a check | – | – | 1 | 0 | 0 | 0 |
| Execution environment | No answer returned | – | – | 3 | 0 | 0 | 0 |
| Not the agent | Task or scoring ambiguity | – | – | 36 | 48 | 0 | 0 |
| Not the agent | Permitted variation | – | – | 0 | 0 | 1 | 0 |
| Unclear | No agent mistake identified | – | – | 3 | 1 | 0 | 0 |

### What the map shows

1. **Successful runs often contained recorded execution errors.**
   88.3% of correct Galaxy runs and 73.5% of correct custom-code runs contained at least one recorded execution error.
   These are shares of successful runs, not rates of repairing an individual error.
   Excluding the interface's own pre-submission parameter check, the Galaxy share is 83.9% (1,412 runs).
   The paper restricts these counts to its three benchmarks, which gives 87.6% versus 72.6% (`data/outline_verification/`).
2. **The recorded errors differ by condition.**
   Custom-code runs more often met software not available, a category that includes basic utilities, failed installs and crashes (48.0% of correct runs), and compute limits (17.0%).
   Galaxy runs met those less often (22.8% and 6.4%) and instead had requests rejected by the interface: parameters (57.6%) and tool lookups or IDs (46.8%).
   Rejected requests come from the interface and are candidates for engineering; whether the next call fixed each one was not measured.
3. **In the run-log trace, analytical choices account for at least as many wrong answers as execution slips.**
   Of the 49 BixBench wrong answers the audit did not attribute to the benchmark, the trace (one reader, awaiting review) assigns 27 to knowledge or analytical choice, 18 to execution and 4 to unclear causes.
   In 17 of the 27, another run of the same model on the same question was correct; this shows variability between attempts, not that the failed attempt had the knowledge.
4. **Execution failures that prevented the answer are of several kinds; in Galaxy, 7 of 12 were visible in the history.**
   Galaxy's 12 on BixBench are six data-handling slips, such as a header row counted as data, three runs that returned no answer, two tool substitutions and one result accepted without a check; 7 of the 12 were visible in the history on retrospective reading.
   Custom code's 6 are data-handling slips and installed tool versions that differ from the reference (BUSCO 5.7.1 in both bix-55-q1 failures).
5. **Most BixBench wrong answers are the benchmark's.**
   84 of 133 come from an under-specified task or a scoring rule (36 Galaxy, 48 custom code), according to the audit.
6. **On multi-step analyses, the causes named differ by condition, but most failures have no recorded cause.**
   Custom code failed 320 required results against 253 for Galaxy.
   The task pages name causes for only some runs: custom-code runs replaced specified tools with their own code (17 runs named) or did not deliver outputs in the required form (11), and Galaxy runs were misled by tool defaults or labels (11) or needed steps no Galaxy tool performs (14).
   The scorer records only a symptom for 148 Galaxy and 202 custom-code failures, so the named causes do not explain the difference between conditions.

## Details

### How each group was measured

**Errors recorded in successful runs** come from the event logs of 4,008 runs.
Every shell command that exited with an error and every Galaxy interface call that failed was given an error type by ordered, deterministic rules (`analysis/error_rules_shell.py`, `analysis/error_rules_galaxy.py`).
Each error type belongs to one subcategory of the execution-environment category (`SUBCATEGORY` in `analysis/error_taxonomy.py`).
An error counts as recorded in a successful run when its run ended correct: BixBench pass, CompBioBench reconstructed-key match, IWC workflow-output agreement of at least 0.99, or every required result passing on the IWC multi-step tasks.
Knowledge errors leave no failed command, so the logs cannot count them in successful runs.

**Errors that prevented the correct answer** come from three sources:

- BixBench: all 133 incorrect runs.
  The 84 the audit attributes to the task or its scoring are kept as such.
  The other 49 were traced individually: each run's event log was read against the question, the accepted answer and the passing runs of the same model and condition (`data/error_taxonomy/bixbench_agent_failures_traced.csv`).
- IWC multi-step tasks: the scorer's recorded reason for each of the 573 failed results (`analysis/iwc_failed_results.py`), and the 92 cause statements in the error analyses on the ten task pages (`data/error_taxonomy/iwc_multistep_page_causes.csv`).
- IWC workflow tasks: the published explanation of each of the 98 scores below 1 (`data/error_taxonomy/iwc_workflow_explanations.csv`).

CompBioBench has no failure-cause audit, so its 302 reconstructed-key mismatches (161 Galaxy, 141 custom code) appear only in the execution-error counts from the event logs; 301 of them have event logs, as one Galaxy log is missing.

### Execution errors recorded in the event logs

Execution errors by subcategory, in correct and incorrect runs, all benchmarks pooled.
Each cell gives runs with at least one error of the subcategory and their share of runs.

| Subcategory | Galaxy, correct (1,682) | Galaxy, incorrect (316) | Custom code, correct (1,697) | Custom code, incorrect (313) |
|---|---|---|---|---|
| Software not available | 384 (22.8%) | 117 (37.0%) | 815 (48.0%) | 200 (63.9%) |
| Interface or API request rejected | 787 (46.8%) | 194 (61.4%) | 160 (9.4%) | 65 (20.8%) |
| Parameters rejected | 968 (57.6%) | 187 (59.2%) | 72 (4.2%) | 26 (8.3%) |
| Agent's own code failed | 641 (38.1%) | 109 (34.5%) | 238 (14.0%) | 102 (32.6%) |
| Data or file handling | 641 (38.1%) | 157 (49.7%) | 554 (32.6%) | 190 (60.7%) |
| Analysis tool failed | 391 (23.2%) | 129 (40.8%) | 76 (4.5%) | 16 (5.1%) |
| Compute limit reached | 107 (6.4%) | 38 (12.0%) | 289 (17.0%) | 101 (32.3%) |
| Platform, network or sandbox | 246 (14.6%) | 106 (33.5%) | 275 (16.2%) | 70 (22.4%) |

Errors in incorrect runs are listed for comparison only; the logs do not say which of them, if any, caused the wrong answer.
Incorrect runs are also about twice as long, so they meet more errors of every kind.

The tables below give each error type: events and runs with at least one event.
"Where" says whether the error came from a shell command or a Galaxy interface call; custom-code runs make no Galaxy calls.

#### Software not available

| Error type | Where | Galaxy, correct runs | Galaxy, incorrect runs | Custom code, correct runs | Custom code, incorrect runs |
|---|---|---|---|---|---|
| Program not installed | shell | 357 / 274 | 181 / 99 | 635 / 522 | 269 / 158 |
| Package or module missing | shell | 92 / 66 | 47 / 22 | 487 / 327 | 134 / 68 |
| Package installation failed | shell | 12 / 10 | 0 / 0 | 101 / 79 | 58 / 39 |
| Program crashed | shell | 1 / 1 | 1 / 1 | 125 / 56 | 34 / 16 |
| Missing software dependency in job | Galaxy call | 104 / 75 | 13 / 9 | – | – |

- The missing programs are mostly basic utilities, not bioinformatics tools: `rg`, `file`, `python3`, `python` and `free` with custom code, and `file`, `python3`, `python` and `xxd` in Galaxy runs.
- "Package installation failed" undercounts failed installs, because a visible cause takes precedence (permission, network, missing program).
  Counting every failed installation or build command, custom code had 441 in 270 runs and Galaxy 47 in 28 runs.
- "Program crashed" with custom code is mostly TensorFlow and similar libraries aborting on an unsupported CPU instruction, in CompBioBench.
- "Missing software dependency in job" is mostly a user-defined tool (UDT) container lacking a package (99 of 117).

#### Interface or API request rejected

| Error type | Where | Galaxy, correct runs | Galaxy, incorrect runs | Custom code, correct runs | Custom code, incorrect runs |
|---|---|---|---|---|---|
| Tool lookup failed for lack of history context | Galaxy call | 991 / 461 | 310 / 106 | – | – |
| Wrong use of a library or API | shell | 254 / 202 | 55 / 33 | 240 / 160 | 127 / 65 |
| Tool ID not found | Galaxy call | 326 / 154 | 151 / 53 | – | – |
| Dataset, history or job ID problem | Galaxy call | 236 / 150 | 76 / 42 | – | – |
| Galaxy API request failed | shell | 225 / 134 | 64 / 34 | 0 / 0 | 0 / 0 |
| Archive inspection rejected | Galaxy call | 166 / 94 | 77 / 41 | – | – |
| Interface rejected the call arguments | Galaxy call | 95 / 64 | 79 / 27 | – | – |

- Asking for a tool's schema without usable history context, either no history named or one the interface could not use, is the most common single agent mistake in Galaxy after the parameter check: 1,301 calls in 567 runs, 1,158 of them with no history given at all.
- "Galaxy API request failed" is Galaxy agents driving Galaxy directly with bioblend or HTTP, outside the interface.

#### Parameters rejected

| Error type | Where | Galaxy, correct runs | Galaxy, incorrect runs | Custom code, correct runs | Custom code, incorrect runs |
|---|---|---|---|---|---|
| Parameters did not resolve as requested (not submitted) | Galaxy call | 2,907 / 878 | 630 / 147 | – | – |
| Parameter rejected: value or datatype | Galaxy call | 717 / 316 | 319 / 101 | – | – |
| Parameter rejected: nested-key structure | Galaxy call | 159 / 135 | 27 / 20 | – | – |
| Wrong command-line arguments to a program | shell | 14 / 7 | 25 / 8 | 74 / 72 | 31 / 26 |

- "Parameters did not resolve as requested" is the interface's own check: it compares the parameters the agent asked for with those Galaxy resolved, and does not submit the job when they differ.
  It is the largest single error type (3,537 calls) and is reported with and without it throughout.
  1,794 of these had values changed; 1,743 had only requested keys missing from the resolved state, some of which may be false alarms of the check (flat legacy keys, inactive conditional branches).
- When the check let a job run with changed or dropped parameters, it is counted as a warning, not an error: 967 calls.
  These jobs ran with parameters other than those requested, which may matter scientifically.

#### Agent's own code failed

| Error type | Where | Galaxy, correct runs | Galaxy, incorrect runs | Custom code, correct runs | Custom code, incorrect runs |
|---|---|---|---|---|---|
| UDT job failed before its command ran | Galaxy call | 933 / 244 | 195 / 40 | – | – |
| UDT script runtime error with diagnostic | Galaxy call | 492 / 280 | 155 / 50 | – | – |
| No error message captured | shell | 160 / 134 | 27 / 19 | 114 / 81 | 71 / 48 |
| UDT definition rejected | Galaxy call | 304 / 121 | 27 / 19 | – | – |
| Syntax error in the agent's own code | shell | 45 / 37 | 17 / 12 | 113 / 100 | 45 / 38 |
| Other runtime error | shell | 36 / 31 | 18 / 11 | 77 / 62 | 47 / 30 |
| The agent's own check failed | shell | 3 / 3 | 0 / 0 | 38 / 26 | 15 / 11 |

- UDTs are the agent's own code run as a Galaxy job, so their failures are the Galaxy counterpart of a failed script.
- "UDT job failed before its command ran" gives no diagnostic (1,103 of its 1,128 events are in CompBioBench); the cause cannot be read from the logs.

#### Data or file handling

| Error type | Where | Galaxy, correct runs | Galaxy, incorrect runs | Custom code, correct runs | Custom code, incorrect runs |
|---|---|---|---|---|---|
| Data did not match what the code expected | shell | 472 / 272 | 182 / 78 | 698 / 407 | 296 / 142 |
| File or path not found | shell | 421 / 340 | 112 / 86 | 336 / 247 | 194 / 99 |
| Input format, compression or index problem | Galaxy call | 135 / 81 | 55 / 20 | – | – |
| Upload or staging failed | Galaxy call | 100 / 61 | 31 / 14 | – | – |
| Output dataset failed metadata | Galaxy call | 47 / 18 | 31 / 7 | – | – |

- 362 of the 533 Galaxy "File or path not found" events, and 136 of 530 with custom code, are attempts to read skill files that do not exist.

#### Analysis tool failed

| Error type | Where | Galaxy, correct runs | Galaxy, incorrect runs | Custom code, correct runs | Custom code, incorrect runs |
|---|---|---|---|---|---|
| Tool runtime error with diagnostic | Galaxy call | 887 / 333 | 494 / 118 | – | – |
| Job failed before execution or without diagnostic | Galaxy call | 167 / 86 | 241 / 26 | – | – |
| Bioinformatics tool reported a failure | shell | 5 / 3 | 0 / 0 | 95 / 76 | 20 / 16 |

- With custom code, a tool's own file or format error counts under the generic label, so "Bioinformatics tool reported a failure" is a residual category.
- 241 of the 408 Galaxy jobs that failed without a diagnostic are in incorrect IWC multi-step runs.

#### Compute limit reached

| Error type | Where | Galaxy, correct runs | Galaxy, incorrect runs | Custom code, correct runs | Custom code, incorrect runs |
|---|---|---|---|---|---|
| Time limit reached or command interrupted | shell | 97 / 64 | 54 / 28 | 484 / 267 | 206 / 88 |
| Job hit memory, disk or time limit | Galaxy call | 114 / 46 | 12 / 7 | – | – |
| Out of memory or killed | shell | 6 / 4 | 6 / 4 | 45 / 32 | 41 / 18 |

- Exit codes cannot separate a time limit from a cancellation or a harness kill, or an out-of-memory kill from another kill.

#### Platform, network or sandbox

| Error type | Where | Galaxy, correct runs | Galaxy, incorrect runs | Custom code, correct runs | Custom code, incorrect runs |
|---|---|---|---|---|---|
| Network or remote resource failure | shell | 260 / 122 | 113 / 39 | 260 / 155 | 57 / 40 |
| Output collection lookup failed after the job | Galaxy call | 123 / 29 | 459 / 40 | – | – |
| Permission or sandbox restriction | shell | 46 / 38 | 28 / 20 | 166 / 130 | 39 / 32 |
| MCP call failed or timed out | Galaxy call | 52 / 26 | 39 / 16 | – | – |
| Server, transport or rate-limit problem | Galaxy call | 77 / 49 | 13 / 8 | – | – |
| Job deleted or cancelled | Galaxy call | 11 / 10 | 2 / 2 | – | – |
| Job paused | Galaxy call | 1 / 1 | 4 / 3 | – | – |
| Other | Galaxy call | 1 / 1 | 0 / 0 | – | – |

- "Output collection lookup failed after the job" is an interface fault: the job finished, but the interface could not find its output collection by its short identifier.
  562 of the 582 events are in IWC multi-step runs, and 459 of the 582 are in 40 incorrect runs.
- Permission failures with custom code are mostly apt-get blocked by the sandbox and refused user-level pip installs.

#### Not counted as errors

| Kind | Galaxy, correct runs | Galaxy, incorrect runs | Custom code, correct runs | Custom code, incorrect runs |
|---|---|---|---|---|
| Shell command exited non-zero without failing (grep with no match, a probe, a closed pipe) | 170 | 80 | 204 | 100 |
| Warning: job ran with parameters that differ from the request | 713 | 254 | – | – |
| Warning: job ran on inputs that differ from the request | 114 | 50 | – | – |
| Warning: dataset inspected before it was ready | 201 | 74 | – | – |
| Warning: dataset outside the stated history | 15 | 8 | – | – |
| Call to another connector (out of scope) | 59 | 24 | – | – |

Errors the IWC multi-step task pages describe as recovered, both in Galaxy runs:

- Task 1: the assembler reported success with empty outputs when the genome size was written in a form it rejects; every Galaxy run (9) met this once and most recovered.
- Task 9: one version of the neighbourhood tool failed with a shared-storage error, and the runs recovered with another version.

### Errors that prevented the correct answer

#### BixBench

All 133 incorrect runs, by category.

| Category | Galaxy (63) | Custom code (70) |
|---|---|---|
| Task or scoring ambiguity, from the audit | 36 | 48 |
| Knowledge | 12 | 15 |
| Execution environment | 12 | 6 |
| Unclear | 3 | 1 |

In 17 of the 27 knowledge errors (8 of 12 Galaxy, 9 of 15 custom code), another run of the same model on the same question was correct.
Every execution-environment error except one (bix-43-q2, DeepSeek V4 Pro, Galaxy run 3) had at least one correct sibling run.
For Galaxy runs, the mistake can be seen by opening the history in 13 of the 27 (7 of 12 execution errors, 6 of 12 knowledge errors).

The trace and the earlier audit label many of the same runs differently.
The audit labelled 31 of them "missing validation"; the trace places 19 of those 31 (9 Galaxy, 10 custom code) in its knowledge category: 5 wrong concepts and 14 other analytical choices, such as a design over all 30 samples or a non-default enrichment background.
The two schemes classify different things: a missed validation step can coexist with a wrong analytical choice, so neither label set is shown to be the correct one until an independent rater reviews them.

##### Galaxy (27 runs)

| Category | Subcategory | Question, model, run | Answer (accepted) | What went wrong | In history | Other runs correct |
|---|---|---|---|---|---|---|
| Knowledge | Question misread | bix-52-q7, GPT-5.6 Luna, 3 | 539 (19,159) | Counted the 19,159 rows correctly but treated them as retained and reported the complement (19,698 minus 19,159). | no | 1 of 2 |
| Knowledge | Wrong biological or statistical concept | bix-14-q1, DeepSeek V4 Pro, 1 | 0.638 (0.7–0.8) | Counted splice-region variants as coding, following a script found on the web: 30 of 47, not 30 of 41. | no | 1 of 2 |
| Knowledge | Wrong biological or statistical concept | bix-14-q1, DeepSeek V4 Pro, 2 | 0.638 (0.7–0.8) | The Galaxy filter's coding terms included splice-region variants, so the denominator was 47 instead of 41. | yes | 1 of 2 |
| Knowledge | Wrong biological or statistical concept | bix-16-q1, DeepSeek V4 Pro, 3 | CCND1 (CDKN1A) | Correlated with raw CRISPR gene-effect scores without flipping the sign to essentiality. | yes | 1 of 2 |
| Knowledge | Wrong method for the question | bix-24-q2, GPT-5.6 Luna, 3 | upregulation (downregulation) | Chose edgeR on all 30 samples and judged direction by term counts in one contrast. | no | 2 of 2 |
| Knowledge | Wrong method for the question | bix-43-q4, GPT-5.5, 1 | 9/49 (8/49) | Fitted DESeq2 on all 30 samples instead of the six in the contrast. | no | 2 of 2 |
| Knowledge | Wrong parameter or threshold | bix-30-q3, DeepSeek V4 Pro, 1 | 1:0 (0:0) | Tuned the test to reproduce the source paper and kept an equal-variance t-test; Welch gives 0:0. | no | 1 of 2 |
| Knowledge | Wrong parameter or threshold | bix-30-q3, DeepSeek V4 Pro, 3 | 1:0 (0:0) | The Galaxy tool reported Welch and Student p-values; after checking the paper the agent reported Student's. | no | 1 of 2 |
| Knowledge | Wrong parameter or threshold | bix-32-q2, DeepSeek V4 Pro, 1 | 2 (0) | Switched the enrichment correction to pathways with hits after a stricter pass found nothing. | yes | 0 of 2 |
| Knowledge | Wrong parameter or threshold | bix-32-q2, DeepSeek V4 Pro, 2 | 2 (0) | Restricted the enrichment correction to pathways with hits; the default gives 0. | yes | 0 of 2 |
| Knowledge | Wrong parameter or threshold | bix-32-q2, DeepSeek V4 Pro, 3 | 2 (0) | Same restriction of the correction scope, admitting two pathways. | yes | 0 of 2 |
| Knowledge | Wrong parameter or threshold | bix-43-q2, DeepSeek V4 Pro, 1 | 7.17 (5.81 or 5.84) | Gave the enrichment a custom 19,074-gene background instead of the default. | yes | 0 of 2 |
| Execution environment | Data or file handling: header row counted as data | bix-52-q7, GPT-5.6 Luna, 2 | 19,160 (19,159) | The filtered table kept its header line and the line count was reported without subtracting it. | yes | 1 of 2 |
| Execution environment | Data or file handling: header row counted as data | bix-52-q7, GPT-5.6 Sol, 3 | 19,160 (19,159) | Same: header line counted as a removed row. | yes | 2 of 2 |
| Execution environment | Data or file handling | bix-14-q1, GPT-5.6 Luna, 2 | 0 (0.7–0.8) | Converted and filtered one of the 19 carrier workbooks instead of all of them. | yes | 2 of 2 |
| Execution environment | Data or file handling | bix-16-q1, DeepSeek V4 Pro, 1 | COX17 (CDKN1A) | Its own Galaxy tool read each gene's values one column off; the weak top correlation went unquestioned. | no | 1 of 2 |
| Execution environment | Data or file handling | bix-16-q1, GPT-5.6 Luna, 2 | USP54 (CDKN1A) | Sorted the correct correlation table with `sort -n`, which misreads scientific notation. | no | 2 of 2 |
| Execution environment | Data or file handling | bix-52-q2, GPT-5.6 Luna, 3 | 9.5e-08 (1.03–1.23e-07) | The expression used to drop the header also dropped chromosomes W and Z. | yes | 2 of 2 |
| Execution environment | Tool version or implementation differs | bix-31-q2, DeepSeek V4 Pro, 2 | −0.081 (−0.07 to −0.05) | Its pydeseq2 UDT jobs never ran, so it used Galaxy's R DESeq2 wrapper; the question requires pydeseq2. | yes | 1 of 2 |
| Execution environment | Tool version or implementation differs | bix-31-q2, DeepSeek V4 Pro, 3 | −0.083 (−0.07 to −0.05) | Same fallback from pydeseq2 to R DESeq2. | yes | 1 of 2 |
| Execution environment | Result accepted without a check | bix-28-q3, GPT-5.6 Sol, 1 | 146.3 (−30.46) | Reported the PhyKIT wrapper's single value without reconciling it with the per-taxon scores it already had. | yes | 2 of 2 |
| Execution environment | No answer returned | bix-27-q5, DeepSeek V4 Pro, 1 | none (55–56) | Ran no analysis job; the run ended after web searches with no answer. | no | 2 of 2 |
| Execution environment | No answer returned | bix-43-q2, DeepSeek V4 Pro, 3 | none (5.81 or 5.84) | Ran no analysis; after web searches, including the benchmark's dataset page, the run ended with no answer. | no | 0 of 2 |
| Execution environment | No answer returned | bix-46-q4, DeepSeek V4 Pro, 2 | none (−4.10) | Its Galaxy DESeq2 output already held −4.099; the run ended after web searches with no answer. | no | 2 of 2 |
| Unclear | No agent mistake identified | bix-26-q5, DeepSeek V4 Pro, 1 | 1 (3) | Default enrichment gave one pathway; no run of any model reached 3. | not checked | 0 of 2 |
| Unclear | No agent mistake identified | bix-26-q5, DeepSeek V4 Pro, 3 | 1 (3) | Same route and answer as run 1. | not checked | 0 of 2 |
| Unclear | No agent mistake identified | bix-54-q7, DeepSeek V4 Pro, 1 | 180,771 (184,000–185,000) | Fitted only the mixture rows; the question does not settle which rows to use. | not checked | 0 of 2 |

##### Custom code (22 runs)

| Category | Subcategory | Question, model, run | Answer (accepted) | What went wrong | Other runs correct |
|---|---|---|---|---|---|
| Knowledge | Step added the task did not ask for | bix-12-q4, GPT-5.6 Luna, 1 | 1,162 (6,948) | Kept only alignments with all four species; its own calculation on all alignments had given 6,948. | 2 of 2 |
| Knowledge | Wrong biological or statistical concept | bix-12-q6, GPT-5.6 Luna, 1 | 6,397 (6,748) | Treated gaps as character states when counting parsimony-informative sites. | 2 of 2 |
| Knowledge | Wrong biological or statistical concept | bix-14-q1, DeepSeek V4 Pro, 1 | 0.638 (0.7–0.8) | Counted splice-region variants as coding, following a script found on the web. | 0 of 2 |
| Knowledge | Wrong biological or statistical concept | bix-14-q1, DeepSeek V4 Pro, 2 | 0.638 (0.7–0.8) | Computed both 30/41 and 30/47 and chose the version counting splice-region variants. | 0 of 2 |
| Knowledge | Wrong biological or statistical concept | bix-14-q1, DeepSeek V4 Pro, 3 | 0.638 (0.7–0.8) | Same definition, taken from a third-party tool found on the web. | 0 of 2 |
| Knowledge | Wrong biological or statistical concept | bix-16-q1, DeepSeek V4 Pro, 1 | CCND1 (CDKN1A) | Correlated with raw gene-effect scores without inverting them. | 1 of 2 |
| Knowledge | Wrong biological or statistical concept | bix-16-q1, DeepSeek V4 Pro, 2 | CCND1 (CDKN1A) | Same sign error. | 1 of 2 |
| Knowledge | Wrong biological or statistical concept | bix-16-q1, GPT-5.6 Luna, 3 | CCND1 (CDKN1A) | Same sign error. | 2 of 2 |
| Knowledge | Wrong method for the question | bix-24-q2, GPT-5.6 Sol, 1 | upregulation (downregulation) | Preferred a ten-group model on all 30 samples over its own two-group fit, which pointed the right way. | 2 of 2 |
| Knowledge | Wrong method for the question | bix-43-q4, DeepSeek V4 Pro, 1 | 9/49 (8/49) | Fitted PyDESeq2 on all 30 samples instead of the two groups compared. | 2 of 2 |
| Knowledge | Wrong method for the question | bix-43-q4, GPT-5.6 Sol, 3 | 9/49 (8/49) | Same ten-group design. | 2 of 2 |
| Knowledge | Wrong parameter or threshold | bix-32-q2, DeepSeek V4 Pro, 1 | 2 (0) | Used all annotated genes as the enrichment background instead of measured genes. | 0 of 2 |
| Knowledge | Wrong parameter or threshold | bix-32-q2, DeepSeek V4 Pro, 2 | 2 (0) | Same background. | 0 of 2 |
| Knowledge | Wrong parameter or threshold | bix-32-q2, DeepSeek V4 Pro, 3 | 2 (0) | Same background, hand-coded. | 0 of 2 |
| Knowledge | Wrong parameter or threshold | bix-43-q2, GPT-5.5, 2 | 6.13 (5.81 or 5.84) | Supplied a custom background to the enrichment call. | 1 of 2 |
| Execution environment | Data or file handling | bix-16-q4, DeepSeek V4 Pro, 2 | 6.9% (20–25%) | Paired gene columns by position across two files with different column orders. | 2 of 2 |
| Execution environment | Data or file handling | bix-27-q5, DeepSeek V4 Pro, 2 | 56.47% (55–56%) | Kept 44 columns with repeated sample IDs; its own check without them gave 55.97%. | 2 of 2 |
| Execution environment | Data or file handling | bix-27-q5, GPT-5.6 Luna, 3 | 56.47% (55–56%) | Kept the columns with repeated sample IDs. | 2 of 2 |
| Execution environment | Tool version or implementation differs | bix-31-q2, DeepSeek V4 Pro, 3 | −0.048 (−0.07 to −0.05) | After repeated out-of-memory kills, ran a hand-modified low-memory PyDESeq2 pipeline. | 2 of 2 |
| Execution environment | Tool version or implementation differs | bix-55-q1, GPT-5.6 Luna, 3 | 100 (101) | Installed BUSCO 5.7.1; passing runs used 5.5.0 or 5.8.3. | 2 of 2 |
| Execution environment | Tool version or implementation differs | bix-55-q1, GPT-5.6 Sol, 1 | 100 (101) | Installed BUSCO 5.7.1; passing runs used 5.5.0 or 5.8.3. | 2 of 2 |
| Unclear | No agent mistake identified | bix-26-q5, DeepSeek V4 Pro, 3 | 1 (3) | Applied the stated thresholds and got 1; no run of any model reached 3. | 0 of 2 |

#### IWC multi-step tasks

Failed results by the scorer's primary reason, first match in this order.

| Primary reason | Galaxy | Custom code |
|---|---|---|
| Required file missing | 12 | 1 |
| Output format or naming | 17 | 9 |
| Other output instruction not followed | 22 | 2 |
| Required content missing or unreadable | 32 | 90 |
| Stated method or setting not followed | 22 | 16 |
| Content below the pass mark | 147 | 196 |
| Only a per-sample, check or gene-list minimum missed | 1 | 6 |
| **Failed results** | **253** | **320** |

The scorer records symptoms, not causes: 148 Galaxy and 202 custom-code failures carry only "content below the pass mark" or a minimum missed.
The causes come from the task pages' error analyses (92 statements, 89 of them for errors that prevented a correct result; the table counts only those 89):

| Category | Subcategory | Galaxy runs named | Custom-code runs named | Example |
|---|---|---|---|---|
| Knowledge | Wrong parameter or threshold | 30 | 6 | Task 6: a quality cutoff that trimmed 5′ ends; the task asks for 3′ trimming only (custom code). |
| Knowledge | Task or question misread | 7 | 3 | Task 2: delivered peak windows already merged (Galaxy). |
| Knowledge | Wrong method for the question | 5 | 3 | Task 5: Leiden clustering in place of the required Louvain (custom code). |
| Knowledge | Step omitted or added | 5 | 4 | Task 9: phenotyping without the log transform (Galaxy). |
| Execution environment | Software not available | 14 | 4 | Task 9: other segmentation methods, in some cases because a package would not install (custom code). |
| Execution environment | Specified tool replaced by the agent's own code | 0 | 17 | Task 7: never installed the mass-spectrometry tools and wrote its own search and isotope fitting. |
| Execution environment | Tool version or implementation differs | 0 | 4 | Task 2: older trimming tool whose reports lack current fields. |
| Execution environment | Galaxy tool default or label misleading | 11 | – | Task 5: the older variable-gene tool pre-fills the top 2,000 genes, overriding the requested cutoffs. |
| Execution environment | Analysis tool failed | 3 | 0 | Task 3: paired filtering jobs failed and the agent switched denoising method. |
| Execution environment | Data or file handling | 12 | 1 | Task 4: a header line written with text tools displaced the top-ranked gene. |
| Execution environment | Output not delivered as required | 8 | 11 | Task 3: files named fwd.rds and rev.rds instead of forward.rds and reverse.rds (Galaxy). |
| Not the agent | Permitted variation | 1 | 0 | Task 5: the PCA solver was left to the tool. |

"Software not available" in Galaxy means a step that no tool on usegalaxy.org performs, which Galaxy agents may not compute locally.
"Specified tool replaced by the agent's own code" is kept apart because the pages give a reason only for some of these runs.

#### IWC workflow tasks

Of the 98 scores below 1, 40 are at or above 0.99 agreement (18 Galaxy, 22 custom code).

| Category | Galaxy | Custom code |
|---|---|---|
| Knowledge | 21 | 16 |
| Execution environment | 2 | 14 |
| Not an error (precision or permitted variation) | 13 | 9 |
| Unclear | 7 | 16 |
| **Scores below 1** | **43** | **55** |

| Category | Subcategory | Published explanation | Galaxy runs | Custom-code runs | At or above 0.99 (Galaxy / custom code) |
|---|---|---|---|---|---|
| Knowledge | Step omitted or added | Missing chimera removal | 0 | 1 | 0 / 0 |
| Knowledge | Task or question misread | Invalid multiple-testing correction | 0 | 1 | 0 / 0 |
| Knowledge | Wrong method for the question | Generic negative-binomial model | 0 | 1 | 0 / 0 |
| Knowledge | Wrong parameter or threshold | Adapter-detection setting | 4 | 1 | 4 / 1 |
| Knowledge | Wrong parameter or threshold | Over-aggressive read filtering | 8 | 5 | 0 / 0 |
| Knowledge | Wrong parameter or threshold | Over-permissive peptide validation | 9 | 6 | 0 / 0 |
| Knowledge | Wrong parameter or threshold | Over-restrictive peptide validation | 0 | 1 | 0 / 0 |
| Execution environment | Output not delivered as required | Sample identifiers | 0 | 2 | 0 / 0 |
| Execution environment | Tool version or implementation differs | DESeq2 implementation difference | 0 | 4 | 0 / 4 |
| Execution environment | Tool version or implementation differs | PyDESeq2 implementation variation | 0 | 7 | 0 / 7 |
| Execution environment | Tool version or implementation differs | edgeR fitting variation | 2 | 1 | 1 / 1 |
| Not an error | Numerical precision | Floating-point precision | 4 | 0 | 4 / 0 |
| Not an error | Permitted variation | Borderline pair classification | 2 | 1 | 2 / 1 |
| Not an error | Permitted variation | DESeq2 normalization choice | 0 | 1 | 0 / 0 |
| Not an error | Permitted variation | Differential-expression method | 1 | 0 | 1 / 0 |
| Not an error | Permitted variation | Extra summit splitting | 0 | 1 | 0 / 0 |
| Not an error | Permitted variation | Minor peak-boundary differences | 5 | 4 | 5 / 4 |
| Not an error | Permitted variation | Peak-boundary variation | 1 | 2 | 1 / 2 |
| Unclear | Cause not stated | Additional peptide–protein pairs | 1 | 2 | 0 / 0 |
| Unclear | Cause not stated | Denoising decision boundary | 0 | 1 | 0 / 0 |
| Unclear | Cause not stated | Different ASV set after denoising | 1 | 0 | 0 / 0 |
| Unclear | Cause not stated | Peptide-pair substitution | 0 | 1 | 0 / 0 |
| Unclear | Cause not stated | Sequence differences from the reference | 5 | 11 | 0 / 2 |
| Unclear | Cause not stated | Unmatched mitochondrial sequence | 0 | 1 | 0 / 0 |

Eleven of the 12 custom-code implementation differences score at or above 0.999.
One identical score (0.982332, five extra peptide pairs) recurs in nine runs across both conditions under two labels, which points to one shared difference rather than nine agent errors.

### Behaviour outside the taxonomy

These do not explain a wrong answer by themselves but bear on benchmark integrity.

- In bix-14-q1, DeepSeek V4 Pro searched the web for the question text in both conditions and adopted a definition from a third-party script (four runs).
- In bix-43-q2, a DeepSeek V4 Pro Galaxy run opened the benchmark's dataset page on Hugging Face before ending without an answer.
- In bix-30-q3, DeepSeek V4 Pro downloaded the source paper's supplementary tables and tuned its test until it reproduced the paper's result.
- All three runs that returned no answer ended after a burst of web searches.

### Caveats

- **One classifier, no second rater.** The rules were checked by reading 15 or more random events per error type; the traced failures were classified by one reader each and spot-checked.
  Every classification needs author review before it enters the paper.
- **Truncated inputs.** The rules saw commands cut at 600 characters, outputs over 1,000 characters kept as their first 300 and last 700, and long Galaxy messages kept as their ends; 779 shell failures had no output at all.
- **Run length.** Incorrect runs are about twice as long as correct ones (58–64 against 28–31 shell commands per run), so they meet more errors of every kind.
- **Galaxy calls are not shell commands.** A rejected Galaxy request costs one call and is answered at once, so per-call failure rates are not comparable with per-command rates.
- **Counts depend on the benchmark's interface.** IWC and the multi-step tasks had no UDT tool, and only CompBioBench had the dataset-peek tool, so differences in those error types between benchmarks reflect the interface.
- **IWC references were built in Galaxy.** Implementation differences lower a custom-code score even when the analysis is sound, which inflates custom code's implementation and own-code counts.
- **IWC page narratives are selective.** Custom-code problems appear mainly under "What Galaxy added", and run counts are given only sometimes, so the runs named are not error rates.
- **The BixBench audit labels predate the reruns.** Six of the seven "unreviewed" runs give the same answers the audit labels as task ambiguity in other runs and may belong there; they are kept as traced here.
- **The three "no answer" runs** ended with a normal turn completion; the logs do not show whether the harness or the model ended them.
- **CompBioBench** has no cause audit, so its wrong answers cannot be split into knowledge and execution.

## Sources and how to reproduce

| File | Contents | Written by |
|---|---|---|
| `data/error_taxonomy/execution_errors.csv` | Every error type by benchmark, condition, outcome and source, with category and subcategory | `analysis/error_taxonomy.py` |
| `data/error_taxonomy/execution_subcategories.csv` | Subcategories, each run counted once, per benchmark and pooled | `analysis/error_taxonomy.py` |
| `data/error_taxonomy/run_summary.csv` | Runs, commands, Galaxy calls and runs with an error, by benchmark, condition and outcome | `analysis/error_taxonomy.py` |
| `data/error_taxonomy/iwc_multistep_reasons.csv`, `iwc_multistep_reason_counts.csv` | Each failed IWC multi-step result with its scorer reasons and primary reason | `analysis/iwc_failed_results.py` |
| `data/error_taxonomy/bixbench_agent_failures_traced.csv` | The 49 BixBench failures not attributed to the benchmark, traced in the event logs | Classified by reading each run's log |
| `data/error_taxonomy/iwc_multistep_page_causes.csv` | The 92 cause statements on the IWC multi-step task pages, classified | Classified from the archived task pages |
| `data/error_taxonomy/iwc_workflow_explanations.csv` | The 24 published IWC workflow explanations, classified | Classified from the archived explanation page |

```sh
python analysis/error_taxonomy.py         # needs the cached event logs in traces/codex_events/
python analysis/iwc_failed_results.py     # reads data/site only
```

The event logs are private and are read from the git-ignored cache that `count_trace_code.py` fills (branch `aacr-2027-abstract`, dataset revision `1a95f25d6a5fc65890f6e9f0a97224a1a40267af`); the outputs hold counts and paraphrases only.
The BixBench audit labels are from `figures/benchmark_results_summary/fig2_interface/dataset/bixbench_current_failures.csv`.

The rules, the traced classifications and this document were prepared with Claude Code (Claude Fable 5.2 subagents for the classification; Claude Opus 5.5 for the checks and the text).
