"""Recompute the revised outline's claims without changing the existing paper package.

Run from the repository root with the project's Python environment:
    .venv/Scripts/python.exe analysis/verify_outline_claims.py

Outputs go to data/outline_verification/. Inputs are frozen published results and
the current audit/taxonomy tables; agreement with those tables is source
reconciliation, not independent adjudication of their scientific labels.
Task/cluster bootstrap intervals condition on the tested models. They are not
equivalence tests or uncertainty intervals over all possible models.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

import site_data as sd
from benchmark_records import BASE, KEY, ROOT, SOURCES, records

OUT = ROOT / "data/outline_verification"
DRAWS, SEED = 200_000, 20261028
G, C = sd.GALAXY, sd.CUSTOM
INPUTS: set[Path] = set()


def read_csv(path):
    INPUTS.add(path)
    return pd.read_csv(path)


def read_json(path):
    INPUTS.add(path)
    return json.loads(path.read_text(encoding="utf8"))


def save(name, frame):
    frame.to_csv(OUT / name, index=False, lineterminator="\n", float_format="%.12g")


def interval(task_differences, cluster_ids=None, rng=None):
    if rng is None:
        rng = np.random.default_rng(SEED)
    ids = task_differences.index if cluster_ids is None else cluster_ids
    units = task_differences.groupby(ids).agg(["sum", "size"])
    draws = rng.integers(len(units), size=(DRAWS, len(units)))
    boot = units["sum"].to_numpy()[draws].sum(1) / units["size"].to_numpy()[draws].sum(1)
    return np.quantile(boot, [.025, .975])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data, official, usage, _ = records()  # checks source hashes and exported summary totals
    INPUTS.update(sd.SITE / p for p in ["MANIFEST.csv", "bixbench/data/results.json",
        "compbiobench/data/paper_results.json", "compbiobench/data/public_token_usage.tsv",
        "iwc/data/results.json", "iwc/data/token_usage.tsv"])
    ms_json = read_json(sd.SITE / "iwc/long-chain/data/results.json")
    ms = sd.iwc_multistep_runs().rename(columns={"item": "task"})
    assert len(ms) == 180 and not ms_json["held_reruns"]
    ms["all_pass"] = ms.passed.eq(ms.denominator).astype(float)
    meta, outputs = [], []
    for item in ms_json["items"]:
        for r in item["runs"]:
            score = r["score"]
            assert score["passed"] == sum(o["passed"] for o in score["results"])
            assert score["denominator"] == len(score["results"])
            assert np.isclose(score["acc"], score["passed"] / score["denominator"])
            key = dict(task=item["id"], model=sd.LC_MODEL[r["model"]],
                       condition=sd.LC_CONDITION[r["condition"]], replicate=r["replicate"])
            assert r["tokens_input"] is not None and r["tokens_output"] is not None
            meta.append(dict(**key, minutes=r["minutes"], tokens=r["tokens_input"] + r["tokens_output"],
                             history=r.get("galaxy_history_url"), title=item["title"]))
            outputs.extend(dict(**key, result=o["name"], passed=int(o["passed"])) for o in score["results"])
    ms = ms.merge(pd.DataFrame(meta), on=KEY[1:], validate="one_to_one")
    save("multistep_runs.csv", ms)
    outputs = pd.DataFrame(outputs)
    primary = data[data.benchmark.isin(["BixBench", "CompBioBench"])]
    assert len(primary) + len(ms) == 3780
    assert primary.task.nunique() + ms.task.nunique() == 160
    assert primary.query("condition == @G").history.ne("").all()
    assert ms.query("condition == @G").history.notna().all()
    assert ms.query("condition == @G").history.ne("").all()

    metrics = []
    clusters = read_csv(SOURCES / "bixbench_task_clusters.csv").set_index("task_id").cluster
    rng = np.random.default_rng(SEED)
    # Match the released figure's draw order (four models, then pooled).
    for model in [*sd.MODELS, "Pooled"]:
        block = data.query("benchmark == 'BixBench'")
        if model != "Pooled":
            block = block[block.model == model]
        task = block.pivot_table(index="task", columns="condition", values="item_score") * 100
        lo, hi = interval(task[G] - task[C], clusters.loc[task.index], rng)
        metrics.append(dict(benchmark="BixBench", endpoint="reviewed acceptance", model=model,
            galaxy=task[G].mean(), custom_code=task[C].mean(), difference=task[G].mean()-task[C].mean(),
            lower_95=lo, upper_95=hi, runs_per_condition=len(block)//2,
            resampling_units=clusters.nunique(), interval_basis="paired dataset-cluster bootstrap"))
    means = official.groupby("condition").official_pct.mean()
    metrics.append(dict(benchmark="CompBioBench", endpoint="official points", model="Pooled",
        galaxy=means[G], custom_code=means[C], difference=means[G]-means[C], runs_per_condition=1200,
        interval_basis="no official item-level paired interval; 12 submissions per condition"))
    task = data.query("benchmark == 'CompBioBench'").pivot_table(index="task", columns="condition", values="item_score") * 100
    lo, hi = interval(task[G] - task[C])
    metrics.append(dict(benchmark="CompBioBench", endpoint="reconstructed key; diagnostic", model="Pooled",
        galaxy=task[G].mean(), custom_code=task[C].mean(), difference=task[G].mean()-task[C].mean(),
        lower_95=lo, upper_95=hi, runs_per_condition=1200, resampling_units=len(task),
        interval_basis="paired item bootstrap; official grades unavailable"))
    for endpoint in ["acc", "all_pass"]:
        task = ms.pivot_table(index="task", columns="condition", values=endpoint) * 100
        lo, hi = interval(task[G] - task[C])
        metrics.append(dict(benchmark="IWC multi-step", endpoint=endpoint, model="Pooled",
            galaxy=task[G].mean(), custom_code=task[C].mean(), difference=task[G].mean()-task[C].mean(),
            lower_95=lo, upper_95=hi, runs_per_condition=90, resampling_units=10,
            interval_basis="paired task bootstrap; equal task and model weights"))
    metrics = pd.DataFrame(metrics)
    save("performance.csv", metrics)
    save("multistep_by_task.csv", ms.groupby(["task", "title", "condition"])[["acc", "all_pass", "minutes"]].mean().reset_index())
    task_scores = ms.pivot_table(index="task", columns="condition", values="acc") * 100
    leave_one_out = []
    for omitted in task_scores.index:
        means = task_scores.drop(omitted).mean()
        leave_one_out.append(dict(omitted_task=omitted, galaxy=means[G], custom_code=means[C],
                                 difference=means[G]-means[C], status="exploratory sensitivity; no exclusion recommended"))
    save("multistep_leave_one_out.csv", pd.DataFrame(leave_one_out))
    # The other local branch archives the same release, not a new experiment.
    branch_check = {}
    try:
        ref = "iwc-multistep-snapshots"
        archived = subprocess.check_output(["git", "show", f"{ref}:data/iwc_long_chain/snapshots/2026-11-07/iwc/long-chain/data/results.json"], cwd=ROOT)
        assert json.loads(archived) == ms_json
        pooled = pd.read_csv(io.BytesIO(subprocess.check_output(["git", "show", f"{ref}:data/iwc_long_chain/derived/pooled.csv"], cwd=ROOT)))
        for metric in ["acc", "all_pass"]:
            their = pooled[(pooled.metric == metric) & pooled.models.eq(3)].iloc[0]
            ours = metrics[(metrics.benchmark == "IWC multi-step") & (metrics.endpoint == metric)].iloc[0]
            assert np.allclose([ours.galaxy, ours.custom_code, ours.difference, ours.lower_95, ours.upper_95],
                               np.array([their.galaxy, their.open_ended, their.difference, their.lower_95, their.upper_95])*100)
        branch_check = dict(ref=ref, commit=subprocess.check_output(["git", "rev-parse", ref], cwd=ROOT, text=True).strip(),
                            results_equal=True, intervals_equal=True)
    except subprocess.CalledProcessError:
        branch_check = {"available": False}

    summary = read_csv(ROOT / "data/error_taxonomy/run_summary.csv")
    sub = read_csv(ROOT / "data/error_taxonomy/execution_subcategories.csv")
    paper = ["BixBench-Verified-50", "CompBioBench", "IWC multi-step"]
    summary = summary[summary.benchmark.isin(paper)]
    assert summary.runs.sum() == 3780 and summary.runs_with_log.sum() == 3768
    # Reconcile the outcome denominator to the primary results, including missing logs.
    expected = pd.concat([primary.assign(correct=primary.item_score.eq(1),
        benchmark=primary.benchmark.replace({"BixBench": "BixBench-Verified-50"})),
        ms.assign(correct=ms.all_pass.eq(1))]).groupby(["benchmark", "condition", "correct"]).size()
    observed = summary.assign(correct=summary.outcome.eq("correct")).set_index(["benchmark", "condition", "correct"]).runs
    assert expected.equals(observed.reindex(expected.index).astype(int))
    totals = summary.groupby(["condition", "outcome"]).sum(numeric_only=True).reset_index()
    totals["share_with_error_pct"] = 100*totals.runs_with_error/totals.runs_with_log
    totals["share_without_resolution_check_pct"] = 100*totals.runs_with_error_without_resolution_check/totals.runs_with_log
    save("error_denominators.csv", summary)
    save("error_totals.csv", totals)
    rates = sub[sub.benchmark.isin(paper)].groupby(["condition", "outcome", "subcategory"])[["events", "runs_with_event", "runs_with_log"]].sum().reset_index()
    rates["share_pct"] = 100*rates.runs_with_event/rates.runs_with_log
    save("error_subcategories.csv", rates)
    events = read_csv(ROOT / "data/error_taxonomy/execution_errors.csv")
    save("history_lookup_errors.csv", events[events.benchmark.isin(paper) & events.error_type.eq("Tool lookup failed for lack of history context")].groupby("condition")[["events", "runs_with_event"]].sum().reset_index())

    audit = read_csv(BASE / "fig2_interface/dataset/bixbench_current_failures.csv").fillna("")
    wrong = primary.query("benchmark == 'BixBench' and item_score == 0")
    assert set(audit[KEY].itertuples(index=False, name=None)) == set(wrong[KEY].itertuples(index=False, name=None))
    save("audit_labels.csv", audit.groupby(["classification", "audit_status", "failure_category", "condition"]).size().rename("runs").reset_index())
    traced = read_csv(ROOT / "data/error_taxonomy/bixbench_agent_failures_traced.csv")
    nonbenchmark = audit[~audit.primary_cause.isin(["SPEC", "EVALUATOR"])]
    assert set(nonbenchmark[KEY[1:]].itertuples(index=False, name=None)) == set(traced[KEY[1:]].itertuples(index=False, name=None))
    assert nonbenchmark.other_replicates_correct.gt(0).sum() == traced.siblings_correct.gt(0).sum() == 34
    save("trace_crosswalk.csv", traced.groupby(["audit_label", "broad_category", "subcategory"]).size().rename("runs").reset_index())
    save("history_visibility.csv", traced.groupby(["condition", "visible_in_history"]).size().rename("runs").reset_index())

    repeat = []
    for (benchmark, condition), block in primary.groupby(["benchmark", "condition"]):
        counts = block.groupby(["task", "model"]).item_score.agg(["sum", "size"])
        assert counts["size"].eq(3).all()
        accepted = abstained = 0
        for _, group in block.groupby(["task", "model"]):
            strings = group.answer.fillna("").astype(str).str.strip().str.casefold()
            vc = strings.value_counts()
            winner = vc.index[0] if vc.iloc[0] >= 2 else ""
            if not winner:
                abstained += 1
            else:
                flags = group.loc[strings.eq(winner), "item_score"]
                assert flags.nunique() == 1
                accepted += int(flags.iloc[0] == 1)
        n = len(counts)
        repeat.append(dict(benchmark=benchmark, condition=condition, groups=n,
            weighting="one task/model group one vote", single_pct=100*counts["sum"].mean()/3,
            two_passed_pct=100*counts["sum"].ge(2).mean(), any_passed_pct=100*counts["sum"].gt(0).mean(),
            vote_accepted_pct=100*accepted/n, vote_abstained_pct=100*abstained/n,
            **{f"passed_{i}": int(counts["sum"].eq(i).sum()) for i in range(4)}))
    grouped = outputs.groupby(["task", "model", "condition", "result"]).passed.agg(["sum", "size"]).reset_index()
    assert grouped["size"].eq(3).all()
    grouped["single"] = grouped["sum"]/3
    grouped["two"] = grouped["sum"].ge(2).astype(float)
    grouped["any"] = grouped["sum"].gt(0).astype(float)
    for condition, block in grouped.groupby("condition"):
        means = block.groupby("task")[["single", "two", "any"]].mean().mean()*100
        repeat.append(dict(benchmark="IWC multi-step", condition=condition, groups=len(block),
            weighting="equal tasks; outputs/model groups averaged within task", single_pct=means["single"],
            two_passed_pct=means["two"], any_passed_pct=means["any"],
            **{f"passed_{i}": int(block["sum"].eq(i).sum()) for i in range(4)}))
    save("replicate_diagnostics.csv", pd.DataFrame(repeat))

    bix_json = read_json(sd.SITE / "bixbench/data/results.json")
    token_rows = []
    for item in bix_json["items"]:
        for exp, conditions in item["results"].items():
            if bix_json["experiments"][exp].get("superseded"):
                continue
            for condition, runs in conditions.items():
                for r in runs:
                    token_rows.append(dict(condition=sd.BIX_CONDITION[condition], correct=r["status"] == "pass",
                        model=sd.BIX_MODEL[bix_json["experiments"][exp]["configuration"]["model"]],
                        tokens=r["usage"]["input_tokens"]+r["usage"]["output_tokens"]))
    tokens = pd.DataFrame(token_rows)
    by_outcome = tokens.groupby(["condition", "correct"]).tokens.agg(["count", "sum", "mean", "median"]).reset_index()
    save("bixbench_tokens_by_outcome.csv", by_outcome)
    # Per-model ratios from the frozen release; the 12 October token pages behind
    # data/token_ratios_main_runs.csv predate the DeepSeek V4 Pro rerun.
    by_model = tokens.pivot_table(index="model", columns="condition", values="tokens", aggfunc="sum")
    by_model["galaxy_custom_ratio"] = by_model[G]/by_model[C]
    save("bixbench_tokens_by_model.csv", by_model.reset_index())
    costs = usage.groupby(["benchmark", "condition"])[["assigned", "observed", "total_tokens"]].sum().reset_index()
    extra = ms.groupby("condition").agg(assigned=("tokens", "size"), observed=("tokens", "count"),
        total_tokens=("tokens", "sum"), median_minutes=("minutes", "median")).reset_index().assign(benchmark="IWC multi-step")
    costs = pd.concat([costs, extra], ignore_index=True)
    ratios = costs.pivot(index="benchmark", columns="condition", values="total_tokens")
    costs["galaxy_custom_ratio"] = costs.benchmark.map(ratios[G]/ratios[C])
    save("token_costs.csv", costs)
    trials = ms.groupby(["condition", "trial_run"])[["acc", "all_pass"]].agg(["count", "mean"])
    trials.columns = ["_".join(c) for c in trials.columns]
    save("trial_run_descriptive.csv", trials.reset_index())

    # Ground-truth spot checks use raw archived output tables and genomic sequence.
    ann = read_json(SOURCES / "hg38_gencode_v49.json")
    seq = read_json(SOURCES / "hg38_promoter_sequence.json")
    tx, = [t for t in ann["wgEncodeGencodeCompV49"] if t["name"].split(".")[0] == "ENST00000269305"]
    assert tx["strand"] == "-" and tx["chrom"] == seq["chrom"] == "chr17"
    start, end = tx["txEnd"]-99, tx["txEnd"]+500
    assert (seq["start"]+1, seq["end"]) == (start, end)
    dna = seq["dna"].upper()
    gc = dna.count("G")+dna.count("C")
    reference = read_json(sd.SITE / "compbiobench/data/paper_results.json")["items"]["compute-gccontent-promoter-q1"]["reference"]
    assert reference == f"17;{start};{end};-;{len(dna)};{gc};{gc/len(dna):.2f}"
    fields = ["gene", "base_mean", "log2_fold_change", "se", "wald_stat", "p", "adjusted_p"]
    significant = []
    for name in ["run", "reference"]:
        path = SOURCES / f"wf002_{name}_deseq2.tsv"
        INPUTS.add(path)
        table = pd.read_csv(path, sep="\t", names=fields)
        significant.append(set(table.loc[table.adjusted_p < .05, "gene"]))
    phykit = next(i for i in bix_json["items"] if i["item_id"] == "bix-45-q1")
    key = list(map(float, phykit["accepted_answers"]))
    pk = primary[primary.task.eq("bix-45-q1")]
    recomputed = pk.answer.map(lambda a: any(abs(float(a)-v) <= .05*v for v in key))
    assert recomputed.eq(pk.status.eq("pass")).all()
    evidence = dict(cohort_runs=3780, tasks=160, galaxy_histories=1890, multistep_trials=int(ms.trial_run.sum()),
        multistep_complete_runs=ms.groupby("condition").all_pass.sum().astype(int).to_dict(),
        source_reconciliation="frozen result exports and audit tables; labels not independently adjudicated",
        branch_crosscheck=branch_check,
        independent_spot_checks=dict(promoter_bases=len(dna), promoter_gc_bases=gc,
            promoter_fraction=gc/len(dna), run_significant_genes=len(significant[0]),
            reference_significant_genes=len(significant[1]), shared_significant_genes=len(significant[0]&significant[1]),
            phykit_answers_regraded=len(pk)),
        bootstrap=dict(draws=DRAWS, seed=SEED, paired=True),
        tool="Codex", model="GPT-6 (session identity; exact backend variant not exposed)")
    (OUT / "verification.json").write_text(json.dumps(evidence, indent=2)+"\n", encoding="utf8")
    INPUTS.add(Path(__file__).resolve())
    save("inputs.csv", pd.DataFrame([dict(path=p.relative_to(ROOT).as_posix(),
        hash_policy="LF-normalized bytes", sha256=hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest())
        for p in sorted(INPUTS)]))
    print(metrics[metrics.model.eq("Pooled")].to_string(index=False))
    print("Verified cohort, scores, paired intervals, error denominators, audit crosswalk, replicate diagnostics,")
    print("token use and three ground-truth spot checks. Outputs: data/outline_verification/")


if __name__ == "__main__":
    main()
