#!/usr/bin/env python3
"""Estimate how much consensus across replicate runs would change accuracy.

Usage:
    python analysis/replicate_consensus.py

Reads data/run_scores.csv (one score per run) and data/bixbench_failure_causes.csv
(one cause per incorrect BixBench-Verified-50 run) and writes two tables:

- data/replicate_consensus.csv: for each benchmark and condition, accuracy of a
  single run, of a majority vote over the 3 replicates of each task and model,
  of at least 1 correct replicate (the ceiling a validation step that picks the
  correct run could reach), and of a majority vote over all 12 runs of a task
  (4 models x 3 replicates); plus how often replicates agree, and where the
  incorrect runs fall.
- data/bixbench_causes_by_agreement.csv: incorrect BixBench-Verified-50 runs by
  primary cause and by how many of the other replicates were correct.

Only benchmarks scored correct or incorrect are analysed (BixBench-Verified-50
and CompBioBench); IWC scores are continuous.

Votes are computed from correctness, not from the answers themselves. A majority
vote counts as correct when a strict majority of runs is correct, which assumes
correct answers agree with each other. Ties and splits without a correct
majority count as incorrect, so the 12-run vote is a conservative estimate.
"""
import argparse
import sys

import pandas as pd

BINARY_BENCHMARKS = ["BixBench-Verified-50", "CompBioBench"]
RUN_KEYS = ["benchmark", "task_id", "model", "track", "replicate"]
N_REPLICATES = 3


def replicate_groups(scores: pd.DataFrame) -> pd.DataFrame:
    """One row per benchmark, condition, model and task, with the number of correct replicates."""
    groups = (
        scores.groupby(["benchmark", "track", "model", "task_id"])
        .agg(n_runs=("correct", "size"), n_correct=("correct", "sum"))
        .reset_index()
    )
    bad = groups[groups.n_runs != N_REPLICATES]
    if not bad.empty:
        sys.exit(f"Expected {N_REPLICATES} replicates per group; found:\n{bad.head()}")
    return groups


def consensus_table(scores: pd.DataFrame, groups: pd.DataFrame) -> pd.DataFrame:
    tasks = scores.groupby(["benchmark", "track", "task_id"]).correct.agg(["size", "sum"]).reset_index()
    wrong = scores[~scores.correct].merge(groups, on=["benchmark", "track", "model", "task_id"])
    rows = []
    for (benchmark, track), g in groups.groupby(["benchmark", "track"]):
        runs = scores[(scores.benchmark == benchmark) & (scores.track == track)]
        t = tasks[(tasks.benchmark == benchmark) & (tasks.track == track)]
        w = wrong[(wrong.benchmark == benchmark) & (wrong.track == track)]
        k = g.n_correct
        rows.append({
            "benchmark": benchmark,
            "track": track,
            "runs": len(runs),
            "replicate_groups": len(g),
            "tasks": len(t),
            "single_run_accuracy": runs.correct.mean(),
            "majority_of_3_accuracy": (k >= 2).mean(),
            "any_of_3_accuracy": (k >= 1).mean(),
            "majority_of_12_accuracy": (t["sum"] > t["size"] / 2).mean(),
            "groups_3_of_3": (k == 3).mean(),
            "groups_2_of_3": (k == 2).mean(),
            "groups_1_of_3": (k == 1).mean(),
            "groups_0_of_3": (k == 0).mean(),
            "incorrect_runs": len(w),
            "incorrect_in_all_wrong_groups": int((w.n_correct == 0).sum()),
            "incorrect_in_majority_correct_groups": int((w.n_correct >= 2).sum()),
        })
    return pd.DataFrame(rows)


def causes_by_agreement(causes: pd.DataFrame, scores: pd.DataFrame, groups: pd.DataFrame) -> pd.DataFrame:
    bix = scores[scores.benchmark == "BixBench-Verified-50"]
    wrong = bix.loc[~bix.correct, RUN_KEYS]
    merged = wrong.merge(causes, on=RUN_KEYS, how="outer", indicator=True)
    if (merged._merge != "both").any():
        sys.exit("Incorrect BixBench runs and failure-cause rows do not match one to one.")
    merged = merged.merge(groups, on=["benchmark", "track", "model", "task_id"])
    return (
        merged.groupby(["track", "primary_cause", "n_correct"])
        .size()
        .rename("incorrect_runs")
        .reset_index()
        .rename(columns={"n_correct": "correct_replicates_in_group"})
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scores", default="data/run_scores.csv")
    p.add_argument("--causes", default="data/bixbench_failure_causes.csv")
    p.add_argument("--out-consensus", default="data/replicate_consensus.csv")
    p.add_argument("--out-causes", default="data/bixbench_causes_by_agreement.csv")
    args = p.parse_args()

    scores = pd.read_csv(args.scores)
    scores = scores[scores.benchmark.isin(BINARY_BENCHMARKS)].copy()
    if not scores.score.isin([0, 1]).all():
        sys.exit("Expected scores of 0 or 1 for BixBench-Verified-50 and CompBioBench.")
    scores["correct"] = scores.score == 1

    groups = replicate_groups(scores)
    consensus = consensus_table(scores, groups)
    causes = pd.read_csv(args.causes)
    by_cause = causes_by_agreement(causes, scores, groups)

    consensus.round(4).to_csv(args.out_consensus, index=False)
    by_cause.to_csv(args.out_causes, index=False)

    with pd.option_context("display.width", 200, "display.max_columns", None):
        print(consensus.round(3).to_string(index=False))
        print()
        print(by_cause.pivot_table(index="primary_cause", columns="correct_replicates_in_group",
                                   values="incorrect_runs", aggfunc="sum", fill_value=0))
    rigor = (causes.primary_cause == "RIGOR") | (causes.secondary_cause == "RIGOR")
    print(f"\nIncorrect BixBench runs with RIGOR as primary or secondary cause: {rigor.sum()} of {len(causes)}")
    print(f"\nWrote {args.out_consensus} and {args.out_causes}")


if __name__ == "__main__":
    main()
