"""Read and check the frozen, paired October score and execution records.

The website exports are read, and models and conditions named, through analysis/site_data.py, the shared
loader for data/site/; this module adds the per-run fields the figure package needs (answers, histories,
routes, batches, token usage and workflow metadata) and checks them against the exports' own summaries.
"""
from hashlib import sha256
import csv
from pathlib import Path

import pandas as pd

import site_data as sd

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "figures/benchmark_results_summary"
SOURCES = BASE / "sources"
SITE = sd.SITE
URL = "https://goeckslab.github.io/galaxy-agent-benchmark/"
MODELS = sd.MODELS
load_site = sd._load


def _bix_experiments():
    """Current (not superseded) BixBench experiments, keyed by experiment id, in the paper's model order."""
    exps = load_site("bixbench/data/results.json")["experiments"]
    current = {k: sd.BIX_MODEL[e["configuration"]["model"]] for k, e in exps.items() if not e.get("superseded")}
    assert sorted(current.values(), key=MODELS.index) == MODELS, current
    return dict(sorted(current.items(), key=lambda kv: MODELS.index(kv[1])))


BIX = _bix_experiments()
COMP = {k: v for k, v in sd.CBB_MODEL.items() if v in MODELS}  # GPT-6 Astra has custom-code runs only
IWC = dict(sd.IWC_MODEL)
KEY = ["benchmark", "task", "model", "condition", "replicate"]
FIGS = ["fig1_performance", "fig2_interface", "s1_execution", "s2_reruns", "s3_repeatability",
        "s4_iwc_outputs", "s5_request_failures", "s6_token_usage", "s7_token_drivers"]


def save(frame, figure, filename="source_data.csv"):
    directory = BASE / figure / "dataset"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    contents = frame.to_csv(index=False, lineterminator="\n", float_format="%.12g").encode("utf8")
    if not path.exists() or path.read_bytes() != contents:
        path.write_bytes(contents)


def verify_site():
    with (SITE / "MANIFEST.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            body = (SITE / row["path"]).read_bytes()
            # Windows Git checkouts may convert LF to CRLF. Accept only exact published bytes after reversal.
            if sha256(body).hexdigest() != row["sha256"]:
                body = body.replace(b"\r\n", b"\n")
            assert len(body) == int(row["bytes"]) and sha256(body).hexdigest() == row["sha256"], row["path"]


def records():
    verify_site()
    bix = load_site("bixbench/data/results.json")
    comp = load_site("compbiobench/data/paper_results.json")
    iwc = load_site("iwc/data/results.json")
    rows, official, usage, workflows = [], [], [], []
    def add(bench, task, model, condition, rep, group, status, score, route, history, answer, locator,
            raw_status="", batch=""):
        rows.append(dict(benchmark=bench, task=task, model=model, condition=condition, replicate=rep,
                         task_group=group, status=status, item_score=score, route=route, history=history or "",
                         answer=answer, locator=locator, item_url=f"{URL}{bench.lower()}/{task}/index.html",
                         raw_status=raw_status, batch=batch))

    for item in bix["items"]:
        task = item["item_id"]
        for m, label in BIX.items():
            assert not bix["experiments"][m].get("superseded")
            for t, runs in item["results"][m].items():
                cond = sd.BIX_CONDITION[t]
                for r in runs:
                    assert r["status"] in ("pass","fail")
                    route = r.get("udt_mode") or "no_udt_recorded"
                    add("BixBench", task, label, cond, r["replicate"], item["category"], r["status"],
                        int(r["status"] == "pass"), route if cond == "Galaxy" else "", r.get("history_url"),
                        r["answer"], f"items[item_id={task}].results.{m}.{t}[replicate={r['replicate']}]",
                        raw_status=r["raw_status"], batch=bix_batch(r.get("source_run") or ""))
    for m, label in BIX.items():
        for t, condition in bix["experiments"][m]["conditions"].items():
            cond = sd.BIX_CONDITION[t]
            for rep, v in condition["replicates"].items():
                observed = [r for r in rows if r["model"] == label and r["condition"] == cond and r["replicate"] == int(rep)]
                assert len(observed) == v["planned"] == 50 and sum(r["item_score"] for r in observed) == v["pass"]
                u = v["usage"]
                raw = [r["usage"] for i in bix["items"] for r in i["results"][m][t] if r["replicate"] == int(rep)]
                assert sum(r["input_tokens"] + r["output_tokens"] for r in raw) == u["total_tokens"]
                usage.append(dict(benchmark="BixBench", model=label, condition=cond, replicate=int(rep),
                                  assigned=v["planned"], observed=len(raw), **{k:u[k] for k in TOKEN_FIELDS}))
            if cond == "Galaxy":
                for mode in ("udt_only","udt_and_standard"):
                    assert sum(r["route"] == mode for r in rows if r["model"] == label and r["condition"] == cond) == condition["udt_usage"][mode]

    for task, item in comp["items"].items():
        for m, label in COMP.items():
            for t, runs in item["runs"][m].items():
                cond = sd.CBB_CONDITION[t]
                for r in runs:
                    assert r["status"] in ("match", "different")
                    add("CompBioBench", task, label, cond, int(r["replicate_id"][1:]), item["domain"], r["status"],
                        int(r["status"] == "match"), r.get("udt_mode",""), r.get("history_url"), r["answer"],
                        f"items.{task}.runs.{m}.{t}[replicate_id={r['replicate_id']}]",
                        batch="adopted rerun" if r.get("replicate_note","").startswith("Rerun") else "original")
    for m in comp["models"]:
        if m["id"] not in COMP:
            continue
        for t, v in m["conditions"].items():
            for r in v["replicates"]:
                assert r["answered"] == 100 and r["official_score"] is not None
                official.append(dict(model=COMP[m["id"]], condition=sd.CBB_CONDITION[t],
                                     replicate=int(r["id"][1:]), official_pct=r["official_score"], answered=r["answered"]))

    for i in iwc["items"]:
        for m, label in IWC.items():
            for t, runs in i["results"][m].items():
                cond = sd.IWC_CONDITION[t]
                for r in runs:
                    assert r["acc_status"] == "scored" and 0 <= r["acc"] <= 1
                    hist = (r.get("galaxy_history") or {}).get("url", "")
                    add("IWC", i["id"], label, cond, r["replicate"], i["name"], r["acc_status"], r["acc"],
                        "", hist, "", f"items[id={i['id']}].results.{m}.{t}[replicate={r['replicate']}]",
                        batch="replacement" if r.get("source_run") else "original")
        workflows.append(dict(task=i["id"], workflow=i["iwc_workflow_name"], tools=i["tool_steps"],
                              unique_tools=i["unique_tools"], evaluator=i["evaluator"]["type"],
                              reference_url=i["ground_truth_history"]["url"], workflow_url=i["iwc_url"]))

    for bench, path, mapping, runs, obs in [
        ("CompBioBench", "compbiobench/data/public_token_usage.tsv", {**COMP, "deepseek-v4-pro-0813": MODELS[-1]}, "items_total", "items_with_usage"),
        ("IWC", "iwc/data/token_usage.tsv", IWC, "runs_total", "runs_with_usage")]:
        for r in csv.DictReader((SITE / path).open(encoding="utf8"), delimiter="\t"):
            if r["model_id"] in mapping:
                usage.append(dict(benchmark=bench, model=mapping[r["model_id"]],
                                  condition={**sd.CBB_CONDITION, **sd.IWC_CONDITION}[r["condition"]],
                                  replicate=int(r["replicate_id"][1:]), assigned=int(r[runs]), observed=int(r[obs]),
                                  **{k:int(r[k]) for k in TOKEN_FIELDS}))
    df, off, tokens = pd.DataFrame(rows), pd.DataFrame(official), pd.DataFrame(usage)
    assert len(df) == 3840 and not df.duplicated(KEY).any()
    assert df.groupby(KEY[:-1]).replicate.apply(lambda s: set(s) == {1,2,3}).all()
    assert df.groupby("benchmark").task.nunique().to_dict() == {"BixBench":50,"CompBioBench":100,"IWC":10}
    assert len(off) == 24 and len(tokens) == 72
    assert (tokens.input_tokens + tokens.output_tokens == tokens.total_tokens).all()
    assert (tokens.cached_input_tokens <= tokens.input_tokens).all()
    return df, off, tokens, pd.DataFrame(workflows)


TOKEN_FIELDS = ["input_tokens", "cached_input_tokens", "output_tokens", "total_tokens"]


def bix_batch(source_run):
    """Classify a BixBench run's local source directory into the execution batch that produced it."""
    if "integrity_reruns_20261023" in source_run:
        return "October integrity rerun"
    if "recovery" in source_run or "second_rerun" in source_run:
        return "recovery or repeat run"
    return "primary batch"
