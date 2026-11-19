#!/usr/bin/env python3
"""Count the execution errors agents met and recovered from, by condition, category and subcategory.

Every failed shell command and every failed Galaxy interface call in the run event logs is given an
error type by the ordered rules in `error_rules_shell.py` and `error_rules_galaxy.py`. Each error type
belongs to one subcategory of the broad category "Execution environment" (table `SUBCATEGORY` below).
An error in a run that ended with a correct answer counts as recovered.

Runs covered: the 4,020 runs of `traces/codex_events/index.csv` (3,840 primary runs and the 180 IWC
multi-step runs); 4,008 have an event log. A run is correct when BixBench marks it pass, CompBioBench's
reconstructed key marks it a match, its IWC workflow-output agreement is at least 0.99, or, for an IWC
multi-step run, every required result passes.

The event logs are private (Hugging Face dataset goeckslab/galaxy-agent-benchmark-run-traces) and are
read from the git-ignored cache `traces/codex_events/`, filled by `count_trace_code.py` on the branch
`aacr-2027-abstract` (dataset revision 1a95f25d6a5fc65890f6e9f0a97224a1a40267af). No trace text is
written out; the outputs hold counts only.

Writes, in data/error_taxonomy/:
  execution_errors.csv   one row per benchmark x condition x outcome x source x error type:
                         events and runs with at least one event (zero rows included)
  execution_subcategories.csv
                         one row per benchmark (and "All") x condition x outcome x subcategory: events,
                         runs with at least one event (each run counted once), runs with a log
  run_summary.csv        one row per benchmark x condition x outcome: runs, runs with a log, shell
                         commands, Galaxy interface calls, runs with at least one execution error, errors

Usage (from the repository root):
    python analysis/error_taxonomy.py
"""
import gzip
import hashlib
import json
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
import error_rules_galaxy as G  # noqa: E402
import error_rules_shell as SH  # noqa: E402

CACHE = ROOT / "traces/codex_events"
OUT = ROOT / "data/error_taxonomy"

MODEL_NAMES = {"gpt-5.5": "GPT-5.5", "gpt-5.6-sol": "GPT-5.6 Sol", "gpt-5.6-luna": "GPT-5.6 Luna",
               "deepseek-v4-pro": "DeepSeek V4 Pro"}

# Subcategory of every error type. All are in the broad category "Execution environment".
SUBCATEGORY = {
    # Software not available
    "Program not installed": "Software not available",
    "Package or module missing": "Software not available",
    "Package installation failed": "Software not available",
    "Program crashed": "Software not available",
    "Missing software dependency in job": "Software not available",
    # Requests to a tool, the Galaxy interface or a library made incorrectly
    "Tool lookup failed for lack of history context": "Interface or API request rejected",
    "Tool ID not found": "Interface or API request rejected",
    "Interface rejected the call arguments": "Interface or API request rejected",
    "Archive inspection rejected": "Interface or API request rejected",
    "Dataset, history or job ID problem": "Interface or API request rejected",
    "Galaxy API request failed": "Interface or API request rejected",
    "Wrong use of a library or API": "Interface or API request rejected",
    # Parameters rejected
    "Parameter rejected: nested-key structure": "Parameters rejected",
    "Parameter rejected: value or datatype": "Parameters rejected",
    "Parameters did not resolve as requested (not submitted)": "Parameters rejected",
    "Wrong command-line arguments to a program": "Parameters rejected",
    # The agent's own code, including user-defined tools (UDTs) run in Galaxy
    "Syntax error in the agent's own code": "Agent's own code failed",
    "The agent's own check failed": "Agent's own code failed",
    "Other runtime error": "Agent's own code failed",
    "No error message captured": "Agent's own code failed",
    "UDT definition rejected": "Agent's own code failed",
    "UDT script runtime error with diagnostic": "Agent's own code failed",
    "UDT job failed before its command ran": "Agent's own code failed",
    # Files and data
    "File or path not found": "Data or file handling",
    "Data did not match what the code expected": "Data or file handling",
    "Input format, compression or index problem": "Data or file handling",
    "Upload or staging failed": "Data or file handling",
    "Output dataset failed metadata": "Data or file handling",
    # An installed analysis tool failed
    "Bioinformatics tool reported a failure": "Analysis tool failed",
    "Tool runtime error with diagnostic": "Analysis tool failed",
    "Job failed before execution or without diagnostic": "Analysis tool failed",
    # Compute limits
    "Time limit reached or command interrupted": "Compute limit reached",
    "Out of memory or killed": "Compute limit reached",
    "Job hit memory, disk or time limit": "Compute limit reached",
    # Platform, network and sandbox
    "Network or remote resource failure": "Platform, network or sandbox",
    "Permission or sandbox restriction": "Platform, network or sandbox",
    "Server, transport or rate-limit problem": "Platform, network or sandbox",
    "MCP call failed or timed out": "Platform, network or sandbox",
    "Output collection lookup failed after the job": "Platform, network or sandbox",
    "Job paused": "Platform, network or sandbox",
    "Job deleted or cancelled": "Platform, network or sandbox",
    "Other": "Platform, network or sandbox",
}
SUBCATEGORY_ORDER = ["Software not available", "Interface or API request rejected", "Parameters rejected",
                     "Agent's own code failed", "Data or file handling", "Analysis tool failed",
                     "Compute limit reached", "Platform, network or sandbox"]

# Inputs exactly as the rules were written and checked on: commands cut at 600 characters, outputs over
# 1,000 characters kept as the first 300 and last 700; Galaxy results with strings over 4,000 characters
# kept as the first and last 2,000, lists cut at six items, and unparsed text cut at 1,500 characters.
CMD_CHARS, OUT_HEAD, OUT_TAIL, OUT_MAX = 600, 300, 700, 1000
MAXSTR, MAXLIST = 4000, 6


def cache_file(events_path: str) -> pathlib.Path:
    return CACHE / (hashlib.sha1(events_path.encode()).hexdigest() + ".jsonl.gz")


def prune(o, depth=0):
    if isinstance(o, str):
        return o if len(o) <= MAXSTR else o[:MAXSTR // 2] + " ...<cut>... " + o[-MAXSTR // 2:]
    if isinstance(o, list):
        out = [prune(x, depth + 1) for x in o[:MAXLIST]]
        if len(o) > MAXLIST:
            out.append("<%d more>" % (len(o) - MAXLIST))
        return out
    if isinstance(o, dict):
        if depth > 8:
            return "<deep>"
        return {k: prune(v, depth + 1) for k, v in o.items()}
    return o


def mcp_text(item: dict) -> str:
    res = item.get("result")
    if isinstance(res, dict):
        c = res.get("content")
        if isinstance(c, list) and c and isinstance(c[0], dict):
            return str(c[0].get("text", ""))
    return ""


def outcomes(idx: pd.DataFrame) -> pd.Series:
    """Whether each run ended correct, by its benchmark's criterion."""
    sc = pd.read_csv(ROOT / "figures/benchmark_results_summary/fig1_performance/dataset/item_scores.csv")
    sc["benchmark"] = sc.benchmark.replace({"BixBench": "BixBench-Verified-50"})
    sc["correct"] = [(st == "pass") if b == "BixBench-Verified-50" else (st == "match") if b == "CompBioBench"
                     else float(s) >= 0.99 for b, st, s in zip(sc.benchmark, sc.status, sc.item_score)]
    d = json.loads((ROOT / "data/site/iwc/long-chain/data/results.json").read_text(encoding="utf-8"))
    ms = pd.DataFrame([{"benchmark": "IWC multi-step", "task": it["id"], "model": d["models"][r["model"]],
                        "condition": "Galaxy" if r["condition"] == "galaxy" else "custom code",
                        "replicate": r["replicate"], "correct": r["score"]["passed"] == r["score"]["denominator"]}
                       for it in d["items"] for r in it["runs"]])
    keys = ["benchmark", "task", "model", "condition", "replicate"]
    allc = pd.concat([sc[keys + ["correct"]], ms], ignore_index=True)
    out = idx.merge(allc, on=keys, how="left", validate="one_to_one")
    if out.correct.isna().any():
        sys.exit(f"{out.correct.isna().sum()} runs without an outcome")
    return out.correct.astype(bool)


def read_run(events_path: str):
    """Return (shell commands, Galaxy calls, list of (source, error type))."""
    n_cmd = n_call = 0
    found = []
    with gzip.open(cache_file(events_path), "rt", encoding="utf8", errors="replace") as fh:
        for line in fh:
            if '"item.completed"' not in line:
                continue
            if '"command_execution"' in line:
                try:
                    it = json.loads(line)["item"]
                except (ValueError, KeyError):
                    continue
                if it.get("type") != "command_execution":
                    continue
                n_cmd += 1
                code = it.get("exit_code")
                if code in (0, None) and it.get("status") != "failed":
                    continue
                out = it.get("aggregated_output") or ""
                if len(out) > OUT_MAX:
                    out = out[:OUT_HEAD] + " ... " + out[-OUT_TAIL:]
                found.append(("shell", SH.classify_shell((it.get("command") or "")[:CMD_CHARS], out, code)))
            elif '"mcp_tool_call"' in line:
                try:
                    it = json.loads(line)["item"]
                except (ValueError, KeyError):
                    continue
                if it.get("type") != "mcp_tool_call":
                    continue
                n_call += 1
                txt = mcp_text(it)
                try:
                    parsed, raw = json.loads(txt), ""
                except ValueError:
                    parsed, raw = None, txt[:1500]
                label = G.classify_mcp(it.get("tool"), it.get("status"), prune(parsed) if parsed is not None else None,
                                       it.get("error"), raw)
                if label is not None:
                    found.append(("galaxy", label))
    return n_cmd, n_call, found


def severity(source: str, label: str) -> str:
    if source == "shell":
        return "not an error" if label == "Not an error" else "error"
    return {"error": "error", "warning": "warning", "out_of_scope": "out of scope"}[G.MCP_SEVERITY[label]]


def main() -> None:
    idx = pd.read_csv(CACHE / "index.csv")
    idx["model"] = idx.model.replace(MODEL_NAMES)
    idx["correct"] = outcomes(idx)
    idx["outcome"] = idx.correct.map({True: "correct", False: "incorrect"})
    idx["has_log"] = [isinstance(p, str) and cache_file(p).exists() for p in idx.events_path]

    events, per_run = [], []
    for i, r in idx[idx.has_log].iterrows():
        n_cmd, n_call, found = read_run(r.events_path)
        per_run.append((i, n_cmd, n_call))
        events += [(i, src, lab) for src, lab in found]
    ev = pd.DataFrame(events, columns=["run", "source", "error_type"])
    ev["severity"] = [severity(s, l) for s, l in zip(ev.source, ev.error_type)]
    ev = ev.join(idx[["benchmark", "condition", "outcome"]], on="run")
    missing = set(ev.loc[ev.severity == "error", "error_type"]) - set(SUBCATEGORY)
    if missing:
        sys.exit(f"error types without a subcategory: {sorted(missing)}")

    # Every error type, with its category and subcategory, by benchmark, condition and outcome
    types = ([("shell", l) for l, _ in SH.SHELL_LABELS] + [("galaxy", l) for l, _ in G.MCP_LABELS])
    grid = pd.DataFrame([(b, c, o, s, l) for b in sorted(idx.benchmark.unique()) for c in ["Galaxy", "custom code"]
                         for o in ["correct", "incorrect"] for s, l in types
                         if not (s == "galaxy" and c == "custom code")],
                        columns=["benchmark", "condition", "outcome", "source", "error_type"])
    cnt = (ev.groupby(["benchmark", "condition", "outcome", "source", "error_type"])
           .agg(events=("run", "size"), runs_with_event=("run", "nunique")).reset_index())
    tab = grid.merge(cnt, how="left").fillna({"events": 0, "runs_with_event": 0})
    tab[["events", "runs_with_event"]] = tab[["events", "runs_with_event"]].astype(int)
    tab["severity"] = [severity(s, l) for s, l in zip(tab.source, tab.error_type)]
    tab["category"] = ["Execution environment" if v == "error" else "" for v in tab.severity]
    tab["subcategory"] = [SUBCATEGORY.get(l, "") if v == "error" else "" for l, v in zip(tab.error_type, tab.severity)]
    tab["galaxy_stage"] = [G.MCP_STAGE.get(l, "") if s == "galaxy" else "" for s, l in zip(tab.source, tab.error_type)]
    tab = tab[["benchmark", "condition", "outcome", "source", "severity", "category", "subcategory", "galaxy_stage",
               "error_type", "events", "runs_with_event"]]

    # Runs, commands, calls and runs with at least one execution error
    pr = pd.DataFrame(per_run, columns=["run", "shell_commands", "galaxy_calls"]).set_index("run")
    runs = idx.join(pr)
    err = ev[ev.severity == "error"]
    runs["errors"] = err.groupby("run").size().reindex(runs.index, fill_value=0)
    runs["errors_without_resolution_check"] = (err[err.error_type != "Parameters did not resolve as requested (not submitted)"]
                                               .groupby("run").size().reindex(runs.index, fill_value=0))
    summ = (runs.groupby(["benchmark", "condition", "outcome"])
            .agg(runs=("task", "size"), runs_with_log=("has_log", "sum"),
                 shell_commands=("shell_commands", "sum"), galaxy_calls=("galaxy_calls", "sum"),
                 runs_with_error=("errors", lambda s: int((s > 0).sum())), errors=("errors", "sum"),
                 runs_with_error_without_resolution_check=("errors_without_resolution_check", lambda s: int((s > 0).sum())),
                 errors_without_resolution_check=("errors_without_resolution_check", "sum"))
            .reset_index())
    for c in ["runs_with_log", "shell_commands", "galaxy_calls", "errors", "errors_without_resolution_check"]:
        summ[c] = summ[c].astype(int)

    # Subcategories, counting each run once, per benchmark and pooled over benchmarks
    err = err.assign(subcategory=err.error_type.map(SUBCATEGORY))
    logged = runs[runs.has_log]
    parts = []
    for scope, by in (("per benchmark", ["benchmark", "condition", "outcome"]), ("all benchmarks", ["condition", "outcome"])):
        den = logged.groupby(by).size().rename("runs_with_log").reset_index()
        rows = [(*k, sub) for k in den[by].itertuples(index=False) for sub in SUBCATEGORY_ORDER]
        g = pd.DataFrame(rows, columns=by + ["subcategory"])
        e = (err.groupby(by + ["subcategory"]).agg(events=("run", "size"), runs_with_event=("run", "nunique"))
             .reset_index())
        g = g.merge(e, how="left").merge(den).fillna({"events": 0, "runs_with_event": 0})
        if "benchmark" not in by:
            g.insert(0, "benchmark", "All")
        parts.append(g)
    sub = pd.concat(parts, ignore_index=True)
    sub["category"] = "Execution environment"
    sub[["events", "runs_with_event"]] = sub[["events", "runs_with_event"]].astype(int)
    sub["share_of_runs_pct"] = (100 * sub.runs_with_event / sub.runs_with_log).round(2)
    sub = sub[["benchmark", "condition", "outcome", "category", "subcategory", "events", "runs_with_event",
               "runs_with_log", "share_of_runs_pct"]]

    OUT.mkdir(parents=True, exist_ok=True)
    tab.to_csv(OUT / "execution_errors.csv", index=False, lineterminator="\n")
    sub.to_csv(OUT / "execution_subcategories.csv", index=False, lineterminator="\n")
    summ.to_csv(OUT / "run_summary.csv", index=False, lineterminator="\n")
    print(f"{len(ev)} flagged events in {idx.has_log.sum()} runs with a log; "
          f"{len(err)} execution errors ({(err.source == 'shell').sum()} shell, {(err.source == 'galaxy').sum()} Galaxy)")
    print(summ.groupby(["condition", "outcome"])[["runs_with_log", "runs_with_error", "errors"]].sum().to_string())


if __name__ == "__main__":
    main()
