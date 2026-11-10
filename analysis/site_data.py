"""Load the committed results-website data in data/site/ as tidy tables.

Each loader applies the rules in data/site/data/README.md, the website's documentation
of its own exports:

- BixBench: pass/fail comes from `status`, not the historical `raw_status`, and
  experiments with `superseded` metadata are left out.
- CompBioBench: accuracy is the per-replicate `official_score` (out of 100).
  Replicate-level match counts are not exported, so the per-item `status` is loaded
  separately and used only as a cross-check.
- IWC (workflow generation): accuracy is `acc`; `acc_status` and nulls are kept.
- IWC multi-step tasks: runs in `held_reruns` and runs without a score are dropped;
  accuracy is the official `score.acc` (passed / denominator).

A missing score is never treated as zero: it stays NaN and is excluded from means.

Model names and condition names are normalised to the ones the paper uses
(see CONTRIBUTING.md): conditions are "Galaxy" and "custom code".
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

SITE = Path(__file__).resolve().parents[1] / "data" / "site"

GALAXY, CUSTOM = "Galaxy", "custom code"
CONDITIONS = [GALAXY, CUSTOM]
MODELS = ["GPT-5.5", "GPT-5.6 Sol", "GPT-5.6 Luna", "DeepSeek V4 Pro"]
BENCHMARKS = ["BixBench-Verified-50", "CompBioBench", "IWC", "IWC multi-step"]

# Each benchmark names models and conditions in its own way.
BIX_MODEL = {"gpt-5.5": "GPT-5.5", "gpt-5.6-sol": "GPT-5.6 Sol", "gpt-5.6-luna": "GPT-5.6 Luna",
             "deepseek-v4-pro": "DeepSeek V4 Pro"}
BIX_CONDITION = {"galaxy_strict_skills": GALAXY, "anycode_nongalaxy_skills": CUSTOM}
CBB_MODEL = {"gpt55": "GPT-5.5", "sol": "GPT-5.6 Sol", "luna": "GPT-5.6 Luna", "deepseek": "DeepSeek V4 Pro",
             "astra": "GPT-6 Astra"}
CBB_CONDITION = {"galaxy": GALAXY, "anycode": CUSTOM}
IWC_MODEL = {"gpt-5.5": "GPT-5.5", "gpt-5.6-sol": "GPT-5.6 Sol", "gpt-5.6-luna": "GPT-5.6 Luna",
             "deepseek-v4-pro": "DeepSeek V4 Pro"}
IWC_CONDITION = {"galaxy_tools": GALAXY, "any_code_no_galaxy_tools": CUSTOM}
LC_MODEL = {"sol": "GPT-5.6 Sol", "luna": "GPT-5.6 Luna", "ds": "DeepSeek V4 Pro"}
LC_CONDITION = {"galaxy": GALAXY, "open": CUSTOM}


def _load(path: str) -> dict:
    return json.loads((SITE / path).read_text())


def _map(value: str, table: dict, what: str) -> str:
    if value not in table:
        raise KeyError(f"Unknown {what} {value!r}; add it to the mapping in analysis/site_data.py")
    return table[value]


def bixbench_runs() -> pd.DataFrame:
    """One row per BixBench run: experiment, model, condition, replicate, item, status, correct."""
    data = _load("bixbench/data/results.json")
    current = {k: e for k, e in data["experiments"].items() if not e.get("superseded")}
    rows = []
    for item in data["items"]:
        for exp_id, conds in item["results"].items():
            if exp_id not in current:
                continue
            model = _map(current[exp_id]["configuration"]["model"], BIX_MODEL, "BixBench model")
            for cond_id, runs in conds.items():
                for run in runs:
                    status = run.get("status")
                    rows.append(dict(benchmark="BixBench-Verified-50", experiment=exp_id, model=model,
                                     condition=_map(cond_id, BIX_CONDITION, "BixBench condition"),
                                     replicate=int(run["replicate"]), item=item["item_id"], status=status,
                                     # pass counts as correct; fail and invalid count as incorrect, as on the
                                     # website; a missing run has no score.
                                     correct={"pass": 1.0, "fail": 0.0, "invalid": 0.0}.get(status)))
    return pd.DataFrame(rows)


def bixbench_site_summary() -> pd.DataFrame:
    """The website's own per-experiment counts and accuracy (percent), for cross-checks."""
    data = _load("bixbench/data/results.json")
    rows = []
    for exp_id, e in data["experiments"].items():
        if e.get("superseded"):
            continue
        for cond_id, c in e["conditions"].items():
            rows.append(dict(model=_map(e["configuration"]["model"], BIX_MODEL, "BixBench model"),
                             condition=_map(cond_id, BIX_CONDITION, "BixBench condition"),
                             planned=c["planned"], passed=c["pass"], accuracy_pct=c["accuracy"],
                             replicate_pass={int(r): v["pass"] for r, v in c["replicates"].items()}))
    return pd.DataFrame(rows)


def compbiobench_replicates() -> pd.DataFrame:
    """One row per CompBioBench model, condition and replicate with its official score (0-100)."""
    data = _load("compbiobench/data/paper_results.json")
    rows = []
    for m in data["models"]:
        for cond_id, c in m["conditions"].items():
            for i, rep in enumerate(c.get("replicates", []), start=1):
                rows.append(dict(benchmark="CompBioBench", model=_map(m["id"], CBB_MODEL, "CompBioBench model"),
                                 condition=_map(cond_id, CBB_CONDITION, "CompBioBench condition"), replicate=i,
                                 official_score=rep.get("official_score"),
                                 has_predicted_only="official_score" not in rep and "predicted_score" in rep))
    return pd.DataFrame(rows)


def compbiobench_item_runs() -> pd.DataFrame:
    """One row per CompBioBench item run with its match status; for cross-checks only."""
    data = _load("compbiobench/data/paper_results.json")
    rows = []
    for qid, item in data["items"].items():
        for model_id, conds in item["runs"].items():
            for cond_id, runs in conds.items():
                for run in runs:
                    rows.append(dict(model=_map(model_id, CBB_MODEL, "CompBioBench model"),
                                     condition=_map(cond_id, CBB_CONDITION, "CompBioBench condition"),
                                     replicate=int(str(run.get("replicate_id", "r0")).lstrip("r") or 0),
                                     item=qid, status=run.get("status")))
    return pd.DataFrame(rows)


def iwc_runs() -> pd.DataFrame:
    """One row per IWC workflow-generation run with `acc` (NaN when unscored) and `acc_status`."""
    data = _load("iwc/data/results.json")
    rows = []
    for item in data["items"]:
        for model_id, conds in item["results"].items():
            for cond_id, runs in conds.items():
                for run in runs:
                    rows.append(dict(benchmark="IWC", model=_map(model_id, IWC_MODEL, "IWC model"),
                                     condition=_map(cond_id, IWC_CONDITION, "IWC condition"),
                                     replicate=int(run["replicate"]), item=item["id"], acc=run.get("acc"),
                                     acc_status=run.get("acc_status")))
    df = pd.DataFrame(rows)
    df["acc"] = pd.to_numeric(df["acc"])
    return df


def iwc_multistep_runs() -> pd.DataFrame:
    """One row per scored IWC multi-step run with the official `acc` and whether every result passed."""
    data = _load("iwc/long-chain/data/results.json")
    held = {(h.get("task"), h.get("model"), h.get("condition"), h.get("replicate")) for h in data["held_reruns"]
            if isinstance(h, dict)}
    rows = []
    for item in data["items"]:
        for run in item["runs"]:
            key = (item["task"], run["model"], run["condition"], run["replicate"])
            score = run.get("score") or {}
            if run.get("status") != "scored" or key in held or score.get("acc") is None:
                continue
            rows.append(dict(benchmark="IWC multi-step", model=_map(run["model"], LC_MODEL, "multi-step model"),
                             condition=_map(run["condition"], LC_CONDITION, "multi-step condition"),
                             replicate=int(run["replicate"]), item=item["id"], acc=float(score["acc"]),
                             passed=score.get("passed"), denominator=score.get("denominator"),
                             trial_run=bool(run.get("trial_run"))))
    if data["held_reruns"] and not all(isinstance(h, dict) for h in data["held_reruns"]):
        raise ValueError("held_reruns has entries this loader cannot match; update iwc_multistep_runs()")
    return pd.DataFrame(rows)
