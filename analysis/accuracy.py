#!/usr/bin/env python3
"""Accuracy of each model, and of all models together, on each benchmark in each condition.

Reads the committed results-website data in data/site/ through analysis/site_data.py and
writes data/accuracy_by_model.csv, one row per benchmark, model and condition, plus an
"All models" row per benchmark and condition.

Accuracy, in percent, follows the website's definition for each benchmark:

- BixBench-Verified-50: runs whose reviewed `status` is pass, out of all planned runs
  (3 replicates x 50 items per model and condition).
- CompBioBench: the mean of the three per-replicate official scores (each out of 100).
- IWC: the mean of `acc` over runs (3 replicates x 10 items).
- IWC multi-step: the mean of `acc` (the share of a task's required results that pass)
  over the scored runs of each task, then over tasks, as the website averages it.

Each model's three replicates are also summarised separately (rep1-rep3, their standard
deviation, minimum and maximum). For IWC and IWC multi-step a stricter all-or-nothing rate
is given too: IWC runs with `acc` >= 0.99, the threshold earlier drafts used, and
multi-step runs in which every required result passed.

"All models" is the unweighted mean of the model accuracies; because every model has the
same number of runs on a benchmark, it equals the accuracy of all runs pooled (checked
below). Only models run in both conditions are included: GPT-6 Astra has CompBioBench
custom-code runs only. The IWC multi-step tasks were run with three models, not four.

It also writes data/accuracy_summary.csv, one row per benchmark aggregating across models:
all-models accuracy in each condition, the Galaxy minus custom-code difference, how many
models score higher in each condition, and the range of model accuracies and differences.

The script stops if a cross-check against the website's own summaries fails.

Usage: python analysis/accuracy.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_data as sd  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data" / "accuracy_by_model.csv"
SUMMARY = OUT.with_name("accuracy_summary.csv")
ALL = "All models"


def per_replicate(runs: pd.DataFrame, value: str) -> pd.DataFrame:
    """Mean of `value` per model, condition and replicate, in percent."""
    return (runs.groupby(["benchmark", "model", "condition", "replicate"])[value].mean() * 100).rename("acc").reset_index()


def site_mean(runs: pd.DataFrame, value: str) -> pd.Series:
    """Mean over runs of each item, then over items, in percent (the website's averaging)."""
    by_item = runs.groupby(["benchmark", "model", "condition", "item"])[value].mean()
    return (by_item.groupby(["benchmark", "model", "condition"]).mean() * 100).rename("accuracy_pct")


def summarise(reps: pd.DataFrame, means: pd.Series, n_runs: pd.Series, definition: str,
              strict: pd.Series | None = None) -> pd.DataFrame:
    wide = reps.pivot_table(index=["benchmark", "model", "condition"], columns="replicate", values="acc")
    wide.columns = [f"rep{c}" for c in wide.columns]
    stats = reps.groupby(["benchmark", "model", "condition"])["acc"].agg(
        rep_sd=lambda s: s.std(ddof=1), rep_min="min", rep_max="max", n_replicates="count")
    out = pd.concat([means, n_runs.rename("n_runs"), wide, stats], axis=1)
    out["strict_pct"] = strict if strict is not None else np.nan
    out["definition"] = definition
    return out.reset_index()


def summarise_across_models(table: pd.DataFrame) -> pd.DataFrame:
    """One row per benchmark: all-models accuracy in each condition and how the models compare.

    Differences are Galaxy minus custom code, in percentage points, computed per model from
    unrounded accuracies; a model counts as tied when its two accuracies are equal.
    """
    rows = []
    for b in sd.BENCHMARKS:
        t = table[table.benchmark == b].set_index(["model", "condition"])
        models = t.drop(index=ALL, level="model")
        g = models.xs(sd.GALAXY, level="condition").accuracy_pct
        c = models.xs(sd.CUSTOM, level="condition").accuracy_pct
        if set(g.index) != set(c.index):
            raise SystemExit(f"{b}: models differ between conditions")
        diff = (g - c[g.index]).astype(float)
        tied = np.isclose(diff, 0)
        ag, ac = t.loc[(ALL, sd.GALAXY)], t.loc[(ALL, sd.CUSTOM)]
        rows.append(dict(
            benchmark=b, n_models=len(g), n_runs_per_condition=ag.n_runs,
            galaxy_pct=ag.accuracy_pct, custom_code_pct=ac.accuracy_pct,
            diff_pp=ag.accuracy_pct - ac.accuracy_pct,
            models_galaxy_higher=int(((diff > 0) & ~tied).sum()), models_tied=int(tied.sum()),
            models_custom_code_higher=int(((diff < 0) & ~tied).sum()),
            model_diff_min_pp=diff.min(), model_diff_max_pp=diff.max(),
            galaxy_model_min=g.min(), galaxy_model_max=g.max(),
            custom_code_model_min=c.min(), custom_code_model_max=c.max(),
            galaxy_strict_pct=ag.strict_pct, custom_code_strict_pct=ac.strict_pct,
            definition=ag.definition))
    out = pd.DataFrame(rows)
    num = out.select_dtypes("number").columns
    out[num] = out[num].round(2)
    return out


def main() -> None:
    parts = []

    # BixBench-Verified-50
    bix = sd.bixbench_runs()
    if bix.correct.isna().any():
        raise SystemExit("BixBench has runs without a pass/fail status; decide how to report them first.")
    bix_reps = per_replicate(bix, "correct")
    bix_mean = (bix.groupby(["benchmark", "model", "condition"]).correct.mean() * 100).rename("accuracy_pct")
    site = sd.bixbench_site_summary().set_index(["model", "condition"])
    for (b, m, c), v in bix_mean.items():
        s = site.loc[(m, c)]
        if round(v, 1) != s.accuracy_pct or (bix[(bix.model == m) & (bix.condition == c)].correct.sum() != s.passed):
            raise SystemExit(f"BixBench {m} {c}: computed {v:.1f}% differs from the website's {s.accuracy_pct}%")
        for r, n in s.replicate_pass.items():
            got = bix[(bix.model == m) & (bix.condition == c) & (bix.replicate == r)].correct.sum()
            if got != n:
                raise SystemExit(f"BixBench {m} {c} replicate {r}: {got} passes, website says {n}")
    parts.append(summarise(bix_reps, bix_mean, bix.groupby(["benchmark", "model", "condition"]).size(),
                           "runs with reviewed status pass / planned runs"))

    # CompBioBench
    cbb = sd.compbiobench_replicates()
    if cbb.has_predicted_only.any() or cbb.official_score.isna().any():
        raise SystemExit("CompBioBench has replicates without an official score; decide how to report them first.")
    paired = cbb.groupby("model").condition.nunique()
    cbb = cbb[cbb.model.isin(paired[paired == 2].index)]
    cbb_reps = cbb.rename(columns={"official_score": "acc"})[["benchmark", "model", "condition", "replicate", "acc"]]
    cbb_mean = cbb_reps.groupby(["benchmark", "model", "condition"]).acc.mean().rename("accuracy_pct")
    items = sd.compbiobench_item_runs()
    match = (items[items.model.isin(cbb.model)].assign(m=lambda d: d.status.eq("match"))
             .groupby(["model", "condition", "replicate"]).m.sum())
    cbb_check = cbb.set_index(["model", "condition", "replicate"]).official_score.to_frame().join(match.rename("item_matches"))
    parts.append(summarise(cbb_reps, cbb_mean, cbb.groupby(["benchmark", "model", "condition"]).size() * 100,
                           "mean of per-replicate official scores (out of 100)"))

    # IWC workflow generation
    iwc = sd.iwc_runs()
    if iwc.acc.isna().any():
        raise SystemExit("IWC has runs without acc; they must stay out of the mean, not count as zero. Check them first.")
    iwc_strict = site_mean(iwc.assign(ok=(iwc.acc >= 0.99).astype(float)), "ok")
    parts.append(summarise(per_replicate(iwc, "acc"), site_mean(iwc, "acc"),
                           iwc.groupby(["benchmark", "model", "condition"]).size(),
                           "mean acc over runs of each item, then over items", iwc_strict))

    # IWC multi-step tasks
    lc = sd.iwc_multistep_runs()
    lc_strict = site_mean(lc.assign(ok=(lc.passed == lc.denominator).astype(float)), "ok")
    parts.append(summarise(per_replicate(lc, "acc"), site_mean(lc, "acc"),
                           lc.groupby(["benchmark", "model", "condition"]).size(),
                           "mean acc (passed results / required results) over scored runs of each task, then over tasks",
                           lc_strict))

    table = pd.concat(parts, ignore_index=True)

    # All models: unweighted mean of model accuracies; check it equals the pooled-run accuracy.
    pooled_runs = {"BixBench-Verified-50": bix.assign(v=bix.correct), "IWC": iwc.assign(v=iwc.acc),
                   "IWC multi-step": lc.assign(v=lc.acc)}
    rows = []
    for (b, c), g in table.groupby(["benchmark", "condition"], sort=False):
        if g.n_runs.nunique() != 1:
            raise SystemExit(f"{b} {c}: models have different numbers of runs; the All-models mean needs weighting")
        acc = g.accuracy_pct.mean()
        if b in pooled_runs:
            r = pooled_runs[b]
            pooled = r[r.condition == c].v.mean() * 100
            if not np.isclose(acc, pooled):
                raise SystemExit(f"{b} {c}: mean of models {acc:.3f} differs from pooled runs {pooled:.3f}")
        rows.append(dict(benchmark=b, model=ALL, condition=c, accuracy_pct=acc, n_runs=g.n_runs.sum(),
                         n_models=len(g), model_min=g.accuracy_pct.min(), model_max=g.accuracy_pct.max(),
                         strict_pct=g.strict_pct.mean(), definition=g.definition.iloc[0]))
    table = pd.concat([table, pd.DataFrame(rows)], ignore_index=True)

    order = {"benchmark": sd.BENCHMARKS, "model": sd.MODELS + [ALL], "condition": sd.CONDITIONS}
    for col, levels in order.items():
        table[col] = pd.Categorical(table[col], levels, ordered=True)
    table = table.sort_values(list(order)).reset_index(drop=True)
    cols = ["benchmark", "model", "condition", "accuracy_pct", "n_runs", "n_replicates", "rep1", "rep2", "rep3",
            "rep_sd", "rep_min", "rep_max", "n_models", "model_min", "model_max", "strict_pct", "definition"]
    table = table[cols]
    summary = summarise_across_models(table)
    num = table.select_dtypes("number").columns
    table[num] = table[num].round(2)
    table.to_csv(OUT, index=False)
    print(f"Wrote {OUT.relative_to(OUT.parents[1])} ({len(table)} rows)")
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {SUMMARY.relative_to(SUMMARY.parents[1])} ({len(summary)} rows)\n")
    print(summary.drop(columns="definition").to_string(index=False))

    print("\nCross-check: BixBench accuracy and per-replicate pass counts match the website's experiment summaries.")
    print("Cross-check: All-models accuracy equals pooled-run accuracy on BixBench, IWC and IWC multi-step.")
    print("\nCompBioBench official score vs. per-item 'match' count, by replicate (information only):")
    print(cbb_check.assign(diff=lambda d: d.official_score - d.item_matches).to_string())


if __name__ == "__main__":
    main()
