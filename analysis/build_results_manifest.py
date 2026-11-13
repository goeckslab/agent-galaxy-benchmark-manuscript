"""Write data/results_manifest.csv: one row per primary run, linking each reported number to its run record.

Reads only the frozen website exports in data/site (checked against data/site/MANIFEST.csv). Fields that the
exports do not publish are left blank and explained in `notes`; nothing is inferred or filled from elsewhere.
"""
import csv

import site_data as sd
from benchmark_records import BIX, COMP, IWC, ROOT, load_site, verify_site

FIELDS = ["task_id", "track", "model", "model_string", "replicate", "run_date", "trace_path",
          "trace_dataset_revision", "final_answer", "expected_answer", "correct", "notes"]
TRACES = "goeckslab/galaxy-agent-benchmark-run-traces"
REVISION_NOTE = "trace dataset revision not published per run in the site export"


def bixbench():
    data = load_site("bixbench/data/results.json")
    for item in data["items"]:
        for key, model in BIX.items():
            exp = data["experiments"][key]
            cfg = exp["configuration"]
            string = f"{cfg['model']}; {cfg['harness']}; reasoning {cfg['reasoning_effort']}"
            for condition, runs in item["results"][key].items():
                track = sd.BIX_CONDITION[condition]
                for r in runs:
                    yield dict(task_id=item["item_id"], track=track, model=model, model_string=string,
                               replicate=r["replicate"], run_date=exp["date"],
                               trace_path=f"{data['trace_repository']}:{r['trace_path']}" if r.get("trace_path") else "",
                               trace_dataset_revision="", final_answer=r["answer"],
                               expected_answer=" | ".join(map(str, item["accepted_answers"])),
                               correct=str(r["status"] == "pass").lower(),
                               notes="; ".join([
                                   "benchmark=BixBench-Verified-50", "endpoint=reviewed acceptance (status)",
                                   f"raw_status={r['raw_status']}", f"source_run={r.get('source_run') or ''}",
                                   f"galaxy_history={r.get('history_url') or ''}", REVISION_NOTE]))


def compbiobench():
    data = load_site("compbiobench/data/paper_results.json")
    meta = {m["id"]: m for m in data["models"]}
    for task, item in data["items"].items():
        for key, model in COMP.items():
            m = meta[key]
            for condition, runs in item["runs"][key].items():
                track = sd.CBB_CONDITION[condition]
                for r in runs:
                    yield dict(task_id=task, track=track, model=model, model_string=f"{m['label']}; {m['setting']}",
                               replicate=int(r["replicate_id"][1:]), run_date=m["date"],
                               trace_path=r.get("trace_url", ""), trace_dataset_revision="",
                               final_answer=r["answer"], expected_answer=item["reference"],
                               correct=str(r["status"] == "match").lower(),
                               notes="; ".join([
                                   "benchmark=CompBioBench",
                                   "correct=match to the reconstructed evidence-based item reference (diagnostic only)",
                                   f"endpoint=official submission score {r['official_score']}/100 for this replicate",
                                   f"replicate_note={r.get('replicate_note', '')}",
                                   f"galaxy_history={r.get('history_url') or ''}",
                                   "trace_path is the dataset folder published by the export, not a run-specific path",
                                   REVISION_NOTE]))


def iwc():
    data = load_site("iwc/data/results.json")
    for item in data["items"]:
        for key, model in IWC.items():
            for condition, runs in item["results"][key].items():
                track = sd.IWC_CONDITION[condition]
                for r in runs:
                    path = r.get("hf_trace_path", "")
                    yield dict(task_id=item["id"], track=track, model=model, model_string=f"{key}; Codex",
                               replicate=r["replicate"], run_date="",
                               trace_path=f"{TRACES}:{path}" if path else "", trace_dataset_revision="",
                               final_answer="", expected_answer=item["ground_truth_history"]["url"],
                               correct="",
                               notes="; ".join([
                                   "benchmark=IWC", f"endpoint=continuous output agreement acc={r['acc']}",
                                   f"evaluator={item['evaluator']['type']}", f"step_score={r.get('step_score')}",
                                   f"galaxy_history={(r.get('galaxy_history') or {}).get('url', '')}",
                                   "correct left blank: the endpoint is continuous; final outputs are files in the history",
                                   "run_date not published in the export", REVISION_NOTE]))


def main():
    verify_site()
    rows = [*bixbench(), *compbiobench(), *iwc()]
    keys = {(r["task_id"], r["track"], r["model"], str(r["replicate"])) for r in rows}
    assert len(rows) == len(keys) == 3840
    with (ROOT / "data/results_manifest.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with_trace = sum(bool(r["trace_path"]) and "tree/main" not in r["trace_path"] for r in rows)
    print(f"Wrote {len(rows)} runs to data/results_manifest.csv; {with_trace} carry a run-specific trace path.")


if __name__ == "__main__":
    main()
