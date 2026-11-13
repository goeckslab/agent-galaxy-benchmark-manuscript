"""Build the Brief Communication source tables and, by default, its nine figures."""
import argparse
import json
import os
import re
import subprocess
import sys

from lxml import html
import numpy as np
import pandas as pd

from benchmark_records import BASE, FIGS, KEY, MODELS, ROOT, SOURCES, load_site, records, save
from check_workflow_output import compare
from extract_rerun_report import PDF as REPORT_PDF, parse as extract_report
from site_data import CUSTOM as C, GALAXY as G
from summary_provenance import figure_inputs, verify
from token_usage import main_run_ratios
BENCH = ["BixBench", "CompBioBench", "IWC"]
F1, F2, S1, S2, S3, S4, S5, S6, S7 = FIGS
DRAWS = 200_000  # 20,000 draws left about ±0.1-point Monte Carlo jitter in the ten-cluster IWC bounds


def performance(d, official):
    rows = []
    rng = np.random.default_rng(20261028)
    clusters = pd.read_csv(SOURCES/"bixbench_task_clusters.csv").set_index("task_id").cluster
    for benchmark in BENCH:
        data = d[d.benchmark == benchmark]
        for model in [*MODELS, "Pooled"]:
            block = data if model == "Pooled" else data[data.model == model]
            lo, hi = np.nan, np.nan
            if benchmark == "CompBioBench":
                scored = official if model == "Pooled" else official[official.model == model]
                means = scored.groupby("condition").official_pct.mean()
                unit = "mean official submission score (% of 100 available points)"
            else:
                task = block.pivot_table(index="task", columns="condition", values="item_score").sort_index() * 100
                diffs = task[G] - task[C]
                ids = clusters.loc[task.index] if benchmark == "BixBench" else task.index
                units = diffs.groupby(ids).agg(["sum","size"])
                draws = rng.integers(len(units), size=(DRAWS,len(units)))
                ci = units["sum"].to_numpy()[draws].sum(axis=1) / units["size"].to_numpy()[draws].sum(axis=1)
                lo, hi = np.quantile(ci, [.025,.975])
                means = task.mean()
                unit = "reviewed acceptance (%)" if benchmark == "BixBench" else "mean workflow-output agreement (%)"
            rows.append(dict(benchmark=benchmark, model=model, tasks=block.task.nunique(), runs_per_condition=len(block)//2,
                             endpoint=unit, galaxy=means[G], custom_code=means[C], difference=means[G]-means[C],
                             lower_95=lo, upper_95=hi, model_count=block.model.nunique(),
                             replicates_per_task_model=block.replicate.nunique(), policies=block.condition.nunique(),
                             resampling_units=len(units) if benchmark != "CompBioBench" else None,
                             official_submissions_per_condition=len(scored)//2 if benchmark=="CompBioBench" else None))
    match_accuracy_table(pd.DataFrame(rows))
    save(pd.DataFrame(rows), F1)
    save(d.drop(columns=["answer","history","route","raw_status"]), F1, "item_scores.csv")
    save(official, F1, "official_submissions.csv")


def match_accuracy_table(perf):
    """Stop unless every point estimate equals data/accuracy_by_model.csv (analysis/accuracy.py), the
    reference per-model accuracy table; it is rounded to 0.01, so agreement means within 0.005 points."""
    ref = pd.read_csv(ROOT/"data/accuracy_by_model.csv")
    ref = ref.assign(benchmark=ref.benchmark.replace({"BixBench-Verified-50": "BixBench"}),
                     model=ref.model.replace({"All models": "Pooled"}))
    ref = ref.pivot_table(index=["benchmark","model"], columns="condition", values="accuracy_pct")
    for r in perf.itertuples():
        for cond, ours in [(G, r.galaxy), (C, r.custom_code)]:
            theirs = ref.loc[(r.benchmark, r.model), cond]
            assert abs(ours - theirs) <= 0.005 + 1e-9, f"{r.benchmark} {r.model} {cond}: {ours} vs accuracy.py {theirs}"


def question_index():
    rows = []
    for i in load_site("bixbench/data/results.json")["items"]:
        rows.append(["BixBench",i["item_id"],i["question"],"reviewed acceptance",json.dumps(i["accepted_answers"]), ""])
    for k,i in load_site("compbiobench/data/paper_results.json")["items"].items():
        rows.append(["CompBioBench",k,i["question"],"evidence-based item reference",i["reference"],""])
    for i in load_site("iwc/data/results.json")["items"]:
        rows.append(["IWC",i["id"],i["query"],i["evaluator"]["type"],i["evaluator"]["description"],i["ground_truth_history"]["url"]])
    table=pd.DataFrame(rows,columns=["benchmark","task","question","reference_type","published_reference","curated_history"])
    pages=pd.read_csv(SOURCES/"web_pages.csv")
    table=table.merge(pages[pages.benchmark.isin(BENCH)][["benchmark","item","url","sha256"]].rename(columns={"item":"task"}),
                      on=["benchmark","task"],validate="one_to_one")
    assert len(table)==160
    save(table,F1,"question_index.csv")


def repeatability(d):
    data = d.copy()
    data["pass_flag"] = data.item_score >= .99
    groups = data.groupby(KEY[:-1]).pass_flag.agg(["sum","size"]).reset_index()
    save(groups, S3, "replicate_groups.csv")
    summaries = []
    for (bench, cond), grp in groups.groupby(["benchmark","condition"]):
        k = grp["sum"]
        summaries.append(dict(benchmark=bench, condition=cond, groups=len(k), single=k.mean()/3,
                              majority=(k>=2).mean(), any_correct=(k>0).mean(), all_wrong=(k==0).sum(),
                              split=((k>0)&(k<3)).sum(), zero=(k==0).sum(), one=(k==1).sum(),
                              two=(k==2).sum(), three=(k==3).sum()))
    summaries = pd.DataFrame(summaries)
    summaries["runs_per_condition"] = 3 * summaries.groups
    per_task = data.groupby(["benchmark","task","task_group","condition"]).pass_flag.agg(["sum","size"]).reset_index()
    per_task["below_criterion"] = per_task["size"] - per_task["sum"]
    save(per_task, S3, "task_outcomes.csv")
    task_votes = data.groupby(["benchmark","task","condition"]).pass_flag.sum().rename("runs_meeting_criterion").reset_index()
    task_votes["strict_majority_of_12"] = task_votes.runs_meeting_criterion > 6
    task_votes["tie"] = task_votes.runs_meeting_criterion == 6
    save(task_votes,S3,"across_model_votes.csv")
    votes = []
    for key, grp in data[data.benchmark!="IWC"].groupby(KEY[:-1]):
        # Conservative identity rule: no semantic collapsing or tie-breaking by ground truth.
        normalized = grp.answer.fillna("").astype(str).str.strip().str.casefold()
        counts = normalized.value_counts()
        winner = counts.index[0] if counts.iloc[0] >= 2 else ""
        statuses = set(grp.loc[normalized==winner,"pass_flag"]) if winner else set()
        votes.append(dict(zip(KEY[:-1],key),distinct_strings=len(counts),selected=bool(winner),
                          selected_meets_criterion=next(iter(statuses)) if len(statuses)==1 else None))
    votes = pd.DataFrame(votes)
    save(votes, S3, "answer_string_votes.csv")
    # Voting sees only the answer strings. Use the reference afterwards to evaluate the selection.
    outcomes = votes.assign(vote_correct=votes.selected_meets_criterion.eq(True),
                            vote_incorrect=votes.selected_meets_criterion.eq(False),
                            vote_abstained=~votes.selected,
                            vote_ungraded=votes.selected & votes.selected_meets_criterion.isna())
    vote_counts = outcomes.groupby(["benchmark", "condition"])[
        ["vote_correct", "vote_incorrect", "vote_abstained", "vote_ungraded"]
    ].sum()
    summaries = summaries.merge(vote_counts, on=["benchmark", "condition"], how="left", validate="one_to_one")
    for field in ("single", "majority", "any_correct"):
        summaries[field + "_pct"] = 100 * summaries[field]
    for field in ("vote_correct", "vote_incorrect", "vote_abstained"):
        summaries[field + "_pct"] = 100 * summaries[field] / summaries.groups
    audit=pd.read_csv(SOURCES/"bixbench_failure_causes.csv")
    flagged=set(audit.loc[audit.primary_cause.isin(["SPEC","EVALUATOR"]),"task_id"])
    bix=data[data.benchmark=="BixBench"]
    iwc=data[data.benchmark=="IWC"]
    raw=bix.assign(item_score=bix.raw_status.eq("pass").astype(int))
    old_key=bix.assign(item_score=np.where(bix.task=="bix-45-q1",raw.item_score,bix.item_score))
    subsets=[("Historical primary specification/scorer flag",bix[~bix.task.isin(flagged)]),
             ("Pre-review grades (raw_status) for all questions",raw),
             ("bix-45-q1 graded by its pre-October status (raw_status)",old_key),
             ("Exclude bix-45-q1 (answer key revised in October)",bix[bix.task!="bix-45-q1"])]
    subsets.extend((f"Leave out {task}",iwc[iwc.task!=task]) for task in sorted(iwc.task.unique()))
    sensitivity=[]
    for rule,sub in subsets:
        mean=sub.groupby("condition").item_score.mean()
        sensitivity.append(dict(benchmark=sub.benchmark.iloc[0],selection=rule,tasks_retained=sub.task.nunique(),
                                runs_per_condition=len(sub)//2,galaxy=mean[G],custom_code=mean[C],difference=mean[G]-mean[C]))
    save(pd.DataFrame(sensitivity),S3,"sensitivity.csv")
    return summaries


def audit_report(d, off):
    report = pd.read_csv(BASE/S2/"dataset/report_runs.csv", keep_default_na=False)
    effects = pd.read_csv(BASE/S2/"dataset/report_effects.csv")
    checked = report.merge(d, on=KEY, validate="one_to_one", how="left", indicator=True)
    assert checked._merge.eq("both").all()
    for r in checked.itertuples():
        if r.benchmark == "IWC":
            value = float(re.search(r"([\d.]+)%", r.replacement_cell)[1])
            assert abs(value - r.item_score*100) <= .005
        else:
            cell = re.sub(r"\s+", "", r.replacement_cell)
            if r.benchmark == "BixBench":
                verdict = "PASS" if r.status == "pass" else "FAIL"
                assert cell.endswith(verdict)
                cell = cell.removesuffix(verdict)
            assert cell == re.sub(r"\s+", "", str(r.answer)), (r.task, r.model)
    for r in effects.itertuples():
        block = d[(d.benchmark==r.benchmark)&(d.model==r.model)&(d.condition==r.condition)]
        selected = checked[(checked.benchmark==r.benchmark)&(checked.model==r.model)&(checked.condition==r.condition)]
        if r.benchmark == "CompBioBench":
            selected = selected[selected.replicate == r.replicate]
            value = off.loc[(off.model==r.model)&(off.condition==r.condition)&(off.replicate==r.replicate),"official_pct"].item()
            assert r.changed_strings == selected.report_changed.sum()
        else:
            value = block.item_score.mean()*100
        assert len(selected) == r.reruns and abs(value-r.after_pct) <= .00501, r
    assert len(report)==77 and checked.loc[checked.benchmark=="CompBioBench","report_changed"].sum()==22
    selection = report.groupby(["benchmark","reason_class","condition"]).size().rename("selected").reset_index()
    comp_effects = effects[effects.benchmark == "CompBioBench"]
    effects["changed_answer_pct"] = 100 * comp_effects.changed_strings / comp_effects.reruns
    save(pd.concat([effects.assign(panel="release_scores"),selection.assign(panel="selection")], ignore_index=True), S2)
    save(checked[KEY+["page","status","item_score","locator","item_url"]], S2, "verified_replacements.csv")
    return report


def independent_checks(d):
    # Compute the promoter interval from a separately hosted transcript model.
    ann = json.loads((SOURCES/"hg38_gencode_v49.json").read_bytes())
    seq = json.loads((SOURCES/"hg38_promoter_sequence.json").read_bytes())
    tx, = [t for t in ann["wgEncodeGencodeCompV49"] if t["name"].split(".")[0]=="ENST00000269305"]
    assert tx["strand"]=="-" and tx["chrom"]==seq["chrom"]=="chr17"
    tss = tx["txEnd"]
    start, end = tss-100+1, tss+500
    assert (seq["start"]+1,seq["end"])==(start,end)
    dna = seq["dna"].upper()
    gc = dna.count("G")+dna.count("C")
    key = f"17;{start};{end};-;{len(dna)};{gc};{gc/len(dna):.2f}"
    task = "compute-gccontent-promoter-q1"
    item = load_site("compbiobench/data/paper_results.json")["items"][task]
    assert len(dna)==end-start+1 and item["reference"]==key
    answers = d.loc[(d.benchmark == "CompBioBench") & (d.task == task), "answer"]
    promoter = dict(benchmark="CompBioBench", task=task, transcript=tx["name"], strand=tx["strand"],
                    chromosome=seq["chrom"], interval_start=start, interval_end=end, bases=len(dna),
                    gc_bases=gc, gc_fraction=gc/len(dna), reported_fraction=round(gc/len(dna), 2),
                    answers_checked=len(answers), answers_matching=int(answers.eq(key).sum()))
    report = pd.read_csv(BASE/S2/"dataset/report_runs.csv")
    for r in report[report.task=="compute-gccontent-promoter-q1"].itertuples():
        assert re.sub(r"\s+","",r.replacement_cell) == key
    # Evaluate the version-sensitive BixBench item independently of the site's status column.
    item, = [i for i in load_site("bixbench/data/results.json")["items"] if i["item_id"]=="bix-45-q1"]
    accepted = list(map(float,item["accepted_answers"]))
    grades = d[d.task=="bix-45-q1"].copy()
    grades["numeric_rule_pass"] = grades.answer.map(lambda a:any(abs(float(a)-v)<=.05*v for v in accepted))
    assert grades.numeric_rule_pass.eq(grades.status=="pass").all()
    save(grades[KEY+["answer","status","numeric_rule_pass"]], S2, "phykit_regrading.csv")
    return promoter


def routes_and_causes(d, report):
    galaxy = d[d.condition==G].copy()
    galaxy["has_history"] = galaxy.history.ne("")
    save(galaxy[KEY+["route","history","item_url"]], S1, "run_histories.csv")
    routes = galaxy[galaxy.benchmark!="IWC"].groupby(["benchmark","model","route"]).size().rename("runs").reset_index()
    routes["model_runs"] = routes.groupby(["benchmark","model"]).runs.transform("sum")
    routes["fraction"] = routes.runs / routes.model_runs
    routes["runs_pct"] = 100 * routes.fraction
    # Verify the per-question route ledger against the separately published history-derived TSV.
    table = pd.read_csv(ROOT/"data/site/compbiobench/data/public_udt_usage.tsv",sep="\t")
    expected = galaxy[galaxy.benchmark=="CompBioBench"][["task","history","route"]]
    found = expected.merge(table, left_on=["task","history"],right_on=["question_id","history_url"], how="left",validate="one_to_one")
    assert len(found)==1200 and found.route.eq(found.udt_mode).all()
    check = pd.DataFrame([compare()])
    design = d.groupby("benchmark").agg(tasks=("task", "nunique"), models=("model", "nunique"),
                                        policies=("condition", "nunique"), replicates=("replicate", "nunique"),
                                        runs=("task", "size")).reset_index()
    save(pd.concat([design.assign(panel="design"), routes.assign(panel="routes"),
                    check.assign(panel="history")], ignore_index=True), S1)
    audit = pd.read_csv(SOURCES/"bixbench_failure_causes.csv").rename(columns={"track":"condition","task_id":"task"})
    audit["benchmark"] = "BixBench"
    fails = d[(d.benchmark=="BixBench")&(d.status=="fail")][KEY].merge(audit,on=KEY,how="left",validate="one_to_one")
    fails = fails.merge(report[KEY].assign(replaced=True),on=KEY,how="left",validate="one_to_one")
    fails["classification"] = fails.primary_cause.fillna("UNREVIEWED")
    fails.loc[fails.replaced==True,"classification"] = "UNREVIEWED"
    fails.loc[fails.classification=="UNREVIEWED",["primary_cause","secondary_cause","confidence","cause_source"]]=""
    # Retrospective groups of primary audit labels, kept separate by who can act on them:
    # the benchmark (task or scoring), the agent (validation, knowledge) or the software.
    audit_groups = {
        "SPEC": "Task or scoring ambiguity",
        "EVALUATOR": "Task or scoring ambiguity",
        "RIGOR": "Missing validation",
        "PLATFORM": "Platform or harness",
        "HARNESS": "Platform or harness",
        "KNOWLEDGE": "Model knowledge",
    }
    assert set(fails.classification) <= set(audit_groups) | {"UNREVIEWED"}
    fails["audit_status"] = "Classified"
    fails.loc[fails.confidence.eq("unresolved"), "audit_status"] = "Unresolved audit"
    fails.loc[fails.classification.eq("UNREVIEWED"), "audit_status"] = "Awaiting review"
    fails["failure_category"] = fails.classification.map(audit_groups).where(fails.audit_status.eq("Classified"))
    # The blanks identify current failures requiring adjudication of the current execution.
    passes=d[d.benchmark=="BixBench"].groupby(KEY[:-1]).item_score.sum().rename("other_replicates_correct")
    fails=fails.join(passes,on=KEY[:-1],validate="many_to_one")
    save(fails, F2, "bixbench_current_failures.csv")
    grouped = (fails.assign(another_pass=fails.other_replicates_correct.gt(0))
               .groupby(["condition", "audit_status", "failure_category"], dropna=False)
               .agg(runs=("task", "size"), runs_with_another_pass=("another_pass", "sum")).reset_index())
    grouped["failed_runs_in_policy"] = grouped.groupby("condition").runs.transform("sum")
    grouped["pct_of_incorrect"] = 100 * grouped.runs / grouped.failed_runs_in_policy
    counts=fails.groupby(["classification","other_replicates_correct"]).size().unstack(fill_value=0)
    counts.columns=[f"other_{int(v)}_correct" for v in counts.columns]
    counts["runs"]=counts.sum(axis=1)
    # The condition split asks which failures are specific to working through Galaxy.
    split=fails.groupby(["classification","condition"]).size().unstack(fill_value=0)
    counts["galaxy_runs"]=split[G]
    counts["custom_code_runs"]=split[C]
    assert counts[["galaxy_runs","custom_code_runs"]].sum(axis=1).eq(counts.runs).all()
    counts=counts.reset_index()
    return counts, grouped


def run_batches(d, report):
    """Record which execution batch produced every primary run, so replacements beyond the report are visible."""
    runs = d[KEY+["batch"]].merge(report[KEY].assign(in_report=True), on=KEY, how="left", validate="one_to_one")
    runs["in_report"] = runs.in_report.eq(True)
    runs["batch_class"] = runs.batch
    runs.loc[runs.in_report, "batch_class"] = "October integrity rerun (report)"
    runs.loc[(runs.benchmark=="CompBioBench") & (runs.batch=="adopted rerun") & ~runs.in_report,
             "batch_class"] = "earlier adopted rerun (not in report)"
    runs.loc[runs.batch_class.isin(["original","primary batch"]), "batch_class"] = "original or primary batch"
    assert not runs[(runs.batch_class=="October integrity rerun") & ~runs.in_report].shape[0]
    table = runs.groupby(["benchmark","model","condition","batch_class"]).size().rename("runs").reset_index()
    assert table.runs.sum()==3840 and runs.in_report.sum()==77
    save(table, S2, "run_batches.csv")
    return table


def no_udt_baseline():
    """Read the historical BixBench campaign that had no user-defined tools from the archived results page."""
    doc = html.fromstring((SOURCES/"bixbench_index.html").read_bytes())
    card, = doc.xpath('//section[@id="no-udt-baseline"]')
    passed, total = map(int, card.xpath('.//div[@class="no-udt-score"]/strong/text()')[0].split("/"))
    when = card.xpath('.//p[@class="eyebrow"]/text()')[0]
    text = " ".join(card.text_content().split())
    assert (passed, total) == (42, 50) and "no user-defined tool could be created or run" in text
    table = pd.DataFrame([dict(campaign=when, condition="Galaxy without user-defined tools", tasks=total,
                               runs_per_task=1, accepted=passed, model="not stated on the source page",
                               source="sources/bixbench_index.html#no-udt-baseline")])
    save(table, S1, "no_udt_baseline.csv")
    return table


def number(text):
    """Parse a page value with an optional thousand or million suffix, such as '446.7M' or '74.6K'."""
    match = re.search(r"(-?[\d,]*\.?\d+)([MK]?)", text)
    return float(match[1].replace(",", "")) * {"M": 1e6, "K": 1e3, "": 1}[match[2]]


def token_drivers():
    """Tabulate the published July 6 trace accounting: token classes, loop structure, command purposes and skills."""
    doc = html.fromstring((SOURCES/"bixbench_july6_token-drivers_index.html").read_bytes())
    tables = doc.xpath("//table")
    cells = lambda t: [[" ".join(td.text_content().split()) for td in tr.xpath("./td|./th")] for tr in t.xpath(".//tbody/tr")]
    rows = []
    source = "sources/bixbench_july6_token-drivers_index.html"
    for name, _, galaxy, custom, _ in cells(tables[0]):
        g_tokens, g_pct = galaxy.split("M")[0] + "M", float(re.search(r"([\d.]+)% of", galaxy)[1])
        c_tokens, c_pct = custom.split("M")[0] + "M", float(re.search(r"([\d.]+)% of", custom)[1])
        if name in ("Total", "Cached input", "Uncached input", "Output"):
            rows += [dict(panel="token_classes", metric=name, condition=G, value=number(g_tokens), share_pct=g_pct, source=source),
                     dict(panel="token_classes", metric=name, condition=C, value=number(c_tokens), share_pct=c_pct, source=source)]
    for name, _, _, galaxy, custom, ratio in cells(tables[1]):
        # The page's ratio column uses unrounded counts; keep it rather than dividing rounded per-run means.
        page_ratio = float(ratio.removesuffix("x"))
        if name in ("Agent loop steps", "Shell commands"):
            for cond, cell in ((G, galaxy), (C, custom)):
                total, per = re.match(r"([\d,]+) total · ([\d.]+) per replicate", cell).groups()
                rows.append(dict(panel="loops", metric=name+" per run", condition=cond, value=float(per),
                                 total=float(total.replace(",", "")), page_ratio=page_ratio, source=source))
        if name == "Cached input per agent message":
            rows += [dict(panel="loops", metric="Cached input per loop step", condition=cond, value=number(cell),
                          page_ratio=page_ratio, source=source) for cond, cell in ((G, galaxy), (C, custom))]
    for name, galaxy, custom, _ in cells(tables[2]):
        label = re.match(r"^(Skill reads|Platform/API operations|Payload, evidence, verification, and answer work|"
                         r"Local input and task work|User-defined tool operations|Other commands)", name)[1]
        for cond, cell in ((G, galaxy), (C, custom)):
            commands, size = re.match(r"([\d,]+) commands([\d.]+ [KM]?B)", cell).groups()
            unit = {"KB": 1e3, "MB": 1e6, "B": 1}[size.split()[1]]
            rows.append(dict(panel="command_purpose", metric=label, condition=cond, value=float(commands.replace(",", "")),
                             visible_bytes=float(size.split()[0]) * unit, source=source))
    # The four July 6 conditions: total tokens from the archived token page, acceptance from the accuracy page.
    tokens_doc = " ".join(html.fromstring((SOURCES/"bixbench_july6_tokens_index.html").read_bytes()).text_content().split())
    accuracy_doc = " ".join(html.fromstring((SOURCES/"bixbench_july6_index.html").read_bytes()).text_content().split())
    for label, cond, skills in [("Galaxy-API code with skills", G, True), ("Galaxy-API code without skills", G, False),
                                ("Open-ended code with skills", C, True), ("Open-ended code without skills", C, False)]:
        total = number(re.search(re.escape(label) + r" ([\d.]+M) 150 replicates", tokens_doc)[1])
        passed = int(re.search(re.escape(label) + r" [\d.]+% (\d+)/150 correct", accuracy_doc)[1])
        rows.append(dict(panel="skills", metric="Total tokens", condition=cond, skills=skills, value=total,
                         accepted=passed, runs=150, source="sources/bixbench_july6_tokens_index.html; sources/bixbench_july6_index.html"))
    table = pd.DataFrame(rows)
    # Reconcile the page's own derived values before plotting them.
    cls = table[table.panel=="token_classes"].pivot(index="metric", columns="condition", values="value")
    pct = table[table.panel=="token_classes"].pivot(index="metric", columns="condition", values="share_pct")
    assert np.allclose(pct.drop("Total").sum(), 100, atol=.01)
    assert np.allclose(cls.drop("Total").sum(), cls.loc["Total"], atol=.15e6)
    loops = table[table.panel=="loops"].set_index(["metric","condition"])
    for cond in (G, C):
        steps = loops.loc[("Agent loop steps per run", cond)]
        assert abs(steps.total/150 - steps.value) < .051
        assert abs(cls.loc["Cached input", cond]/steps.total - loops.loc[("Cached input per loop step", cond)].value) < .06e3
    for metric in ("Agent loop steps per run", "Shell commands per run"):
        ratio = loops.loc[(metric, G)].total / loops.loc[(metric, C)].total
        assert abs(ratio - loops.loc[(metric, G)].page_ratio) < .006, metric
    skills = table[table.panel=="skills"].set_index(["condition","skills"]).value
    assert skills[(G, True)] == cls.loc["Total", G] and skills[(C, True)] == cls.loc["Total", C]
    table["accepted_pct"] = 100 * table.accepted / table.runs
    save(table, S7)
    return table


def request_failures():
    counts = pd.read_csv(SOURCES/"galaxy_failure_classes.csv").groupby(["benchmark","failure_stage","failure_class"]).requests.sum().reset_index()
    counts["benchmark"] = counts.benchmark.replace({"BixBench-Verified-50":"BixBench"})
    counts["class_share"] = counts.requests/counts.groupby("benchmark").requests.transform("sum")
    counts["class_pct"] = 100 * counts.class_share
    counts["benchmark_failures"] = counts.groupby("benchmark").requests.transform("sum")
    counts["stage_failures"] = counts.groupby(["benchmark","failure_stage"]).requests.transform("sum")
    save(counts,S5)
    coverage = pd.read_csv(SOURCES/"galaxy_traced_runs.csv").groupby("benchmark").size().rename("traced_runs").reset_index()
    save(coverage,S5,"historical_trace_coverage.csv")
    return counts.groupby("failure_class").requests.sum().reset_index()


def development_ratios(rounds):
    """Historical BixBench series shown on page 18 of the CSHL presentation."""
    stage_names = {"baseline": "Baseline", "round1": "Prompt and skills", "round1-rerun": "Prompt and skills",
                   "round3a": "Compact replies", "round3b": "Longer waits"}
    series = rounds[rounds.slug.isin(stage_names)][
        ["model", "slug", "galaxy_tokens_m", "custom_code_tokens_m", "ratio", "evidence", "source"]
    ].copy()
    series["stage"] = series.slug.map(stage_names)

    # All four MCP points come from the same pre-rerun token snapshot.
    archived = pd.read_csv(ROOT / "data/site_token_totals.csv")
    bix = archived[archived.benchmark == "BixBench-Verified-50"]
    assert set(bix.model) == set(MODELS) and len(bix) == 2 * len(MODELS)
    assert bix.source.nunique() == 1 and "2026-10-12" in bix.source.iloc[0]
    mcp = main_run_ratios(bix)
    mcp = mcp[mcp.model.isin(MODELS)].copy()
    mcp["galaxy_tokens_m"] = mcp.galaxy_total_tokens / 1e6
    mcp["custom_code_tokens_m"] = mcp.custom_code_total_tokens / 1e6
    mcp = mcp.assign(slug="mcp_execution", stage="MCP execution", evidence="reported token totals",
                     source=bix.source.iloc[0])
    return pd.concat([series, mcp[series.columns]], ignore_index=True)


def tokens_and_stages(tokens):
    keys = ["assigned","observed","total_tokens","cached_input_tokens","output_tokens","input_tokens"]
    pooled = tokens.groupby(["benchmark","condition"])[keys].sum().reset_index().assign(model="Pooled")
    sums = pd.concat([tokens.groupby(["benchmark","model","condition"])[keys].sum().reset_index(),pooled],ignore_index=True)
    sums = sums.pivot(index=["benchmark","model"],columns="condition",values=keys)
    sums.columns = [f"{v}_{c.replace(' ','_')}" for v,c in sums.columns]
    sums["ratio"]=sums.total_tokens_Galaxy/sums.total_tokens_custom_code
    main = sums.reset_index()
    save(tokens, S6, "replicate_usage.csv")
    stages = json.loads((SOURCES/"bixbench_token-optimization-oct2026_summary.json").read_bytes())
    batch = pd.DataFrame(stages["runs"])
    assert len(batch)==150 and not batch.duplicated(["item_id","replicate"]).any()
    for r in stages["statistics"]["current_rounds"]:
        sub = batch[batch.replicate==r["replicate"]]
        assert (len(sub),sub.total_tokens.sum(),sub.passed.sum())==(50,r["tokens"],r["correct"])
    stage = pd.DataFrame(stages["statistics"]["stages"]).T
    original = tokens[(tokens.benchmark=="BixBench") & (tokens.model=="GPT-5.6 Sol")].groupby("condition").total_tokens.sum()
    assert stage.loc["open_ended","total_tokens"]==original[C] and stage.loc["website_galaxy","total_tokens"]==original[G]
    stage = stage.loc[["open_ended","website_galaxy","mcp_v2","long_wait"],
                      ["replicates","items_per_replicate","total_tokens","mean_tokens","mean_model_requests","mean_wait_calls",
                       "galaxy_over_open_ended"]].rename_axis("stage").reset_index()
    assert batch.total_tokens.sum()==stage.iloc[-1].total_tokens and batch.passed.sum()==137
    baseline = tokens[(tokens.benchmark=="BixBench") & (tokens.model=="GPT-5.6 Sol")].copy()
    baseline["stage"] = baseline.condition.map({C:"open_ended", G:"website_galaxy"})
    observations = [baseline[["stage","replicate","total_tokens"]]]
    compact = stage.set_index("stage").loc["mcp_v2"]
    observations.append(pd.DataFrame([dict(stage="mcp_v2",replicate=1,total_tokens=compact.total_tokens,
                                           wait_calls=compact.mean_wait_calls,model_requests=compact.mean_model_requests)]))
    rounds = pd.DataFrame(stages["statistics"]["current_rounds"]).rename(
        columns={"tokens":"total_tokens","waits":"wait_calls","requests":"model_requests","correct":"accepted"})
    observations.append(rounds.assign(stage="long_wait").drop(columns="ratio"))
    observations = pd.concat(observations,ignore_index=True)
    for key, group in observations.groupby("stage"):
        expected = stage.set_index("stage").loc[key]
        assert len(group)==expected.replicates and group.total_tokens.sum()==expected.total_tokens
        for metric in ("wait_calls","model_requests"):
            if pd.notna(expected[f"mean_{metric}"]):
                assert np.isclose(group[metric].mean(), expected[f"mean_{metric}"])
    save(batch[["item_id","replicate","passed","total_tokens"]], F2,"optimized_runs.csv")
    # Sensitivity only: apply the October two-target tolerance to the one changed key.
    phykit, = [i for i in load_site("bixbench/data/results.json")["items"] if i["item_id"]=="bix-45-q1"]
    targets=list(map(float,phykit["accepted_answers"]))
    regraded=batch[["item_id","replicate","passed"]].copy()
    regraded["pass_with_updated_phykit_key"]=regraded.passed
    mask=batch.item_id.eq("bix-45-q1")
    regraded.loc[mask,"pass_with_updated_phykit_key"]=batch.loc[mask,"answer"].map(
        lambda a:any(abs(float(a)-v)<=.05*v for v in targets))
    save(regraded,F2,"optimization_key_sensitivity.csv")
    early = pd.read_csv(ROOT/"data/token_optimization_rounds.csv")
    early["ratio"] = (early.galaxy_tokens_m/early.custom_code_tokens_m).fillna(early.ratio_reported)
    early["evidence"] = np.where(early.ratio_reported.isna(),"reported token totals","author estimate")
    main["missing_usage_Galaxy"] = main.assigned_Galaxy - main.observed_Galaxy
    main["galaxy_token_change_pct"] = 100 * (main.ratio - 1)
    save(early,S6,"historical_rounds.csv")
    save(pd.concat([main.assign(panel="main_runs"),early.assign(panel="historical_rounds")],ignore_index=True),S6)
    return stage, observations, development_ratios(early)


def iwc_outputs(d, workflows):
    w = d[d.benchmark=="IWC"].copy()
    w["score_band"] = np.select([w.item_score==1, w.item_score>=.99, w.item_score>=.90, w.item_score>0],
                                ["exact","near","high","partial"], default="zero")
    doc = html.fromstring((SOURCES/"iwc_error-analysis_index.html").read_bytes())
    reasons = []
    for card in doc.xpath('//section[@id]//article'):
        task = card.xpath('ancestor::section[@id][1]/@id')[0]
        m,t,r = card.xpath('.//div[@class="iwc-run-head"]//strong/text()')[0].split(" · ")
        label = m.replace("Codex + ","")
        for cause in card.xpath('.//div[@class="condition-cause"]'):
            reasons.append(dict(benchmark="IWC",task=task,model=label,condition=G if "Galaxy" in t else C,
                                replicate=int(r[1:]),explanation=cause.findtext("strong"),
                                source_anchor="iwc/error-analysis/index.html#"+task))
    reason = pd.DataFrame(reasons)
    low = w[w.item_score<1][KEY+["item_score"]]
    joined = low.merge(reason,on=KEY,how="outer",indicator=True,validate="one_to_many")
    assert joined._merge.eq("both").all()
    save(joined.drop(columns="_merge"),S4,"score_explanations.csv")
    values = w.groupby(["task","condition"]).item_score.agg(mean="mean",minimum="min",maximum="max",runs="size",
                                                           below_099=lambda x:(x<.99).sum()).reset_index()
    values["mean_agreement_pct"] = 100 * values["mean"]
    individual = w[KEY+["item_score","score_band","item_url","locator"]].copy()
    individual["item_score"] = individual.item_score.map(repr)
    save(pd.concat([values.merge(workflows,on="task").assign(panel="workflow_summary"),
                    individual.assign(panel="individual_run")],ignore_index=True),S4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--tables-only",action="store_true")
    mode.add_argument("--figure",choices=FIGS,help="redraw one plate from the existing local source tables")
    args = parser.parse_args()
    verify()
    # Matplotlib derives PDF subset font names from Python hashes of glyph names.
    plot_env = {**os.environ,"PYTHONHASHSEED":"0","SOURCE_DATE_EPOCH":"1793145600"}
    if args.figure:
        subprocess.run([sys.executable,str(BASE/args.figure/"code/make_figure.py")],env=plot_env,check=True)
        return
    if REPORT_PDF.exists():
        extract_report()
    else:
        print(f"{REPORT_PDF.name} is held by the authors, not the repository; using the committed {S2}/dataset/report_*.csv")
    d,off,t,w = records()
    question_index()
    performance(d,off)
    repeat = repeatability(d)
    report = audit_report(d,off)
    promoter = independent_checks(d)
    save(pd.concat([repeat.assign(panel="repeatability"), pd.DataFrame([promoter]).assign(panel="promoter")],
                   ignore_index=True), S3)
    causes, grouped_causes = routes_and_causes(d,report)
    batches = run_batches(d,report)
    no_udt_baseline()
    token_drivers()
    requests = request_failures()
    stage, observations, history = tokens_and_stages(t)
    save(pd.concat([causes.assign(panel="current_failures"), grouped_causes.assign(panel="failure_categories", figure_panel="a"),
                    requests.assign(panel="request_classes"), repeat.assign(panel="answer_selection", figure_panel="b"),
                    stage.assign(panel="optimization"), observations.assign(panel="replicates"),
                    history.assign(benchmark="BixBench", panel="development_ratios", figure_panel="c")],
                   ignore_index=True), F2)
    iwc_outputs(d,w)
    figure_inputs()
    print(f"Validated {len(d)} paired runs, {len(off)} official submissions, {len(report)} replacements. Promoter: {promoter}")
    print(batches[batches.batch_class!="original or primary batch"].to_string(index=False))
    if not args.tables_only:
        for folder in FIGS:
            subprocess.run([sys.executable,str(BASE/folder/"code/make_figure.py")],env=plot_env,check=True)


if __name__=="__main__":
    main()
