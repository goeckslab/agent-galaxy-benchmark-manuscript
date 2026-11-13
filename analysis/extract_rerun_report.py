"""Extract the October report tables from their PDF cell boundaries and link annotations."""
import argparse
import csv
from hashlib import sha256
from pathlib import Path
import re
from urllib.parse import urlsplit

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "figures/benchmark_results_summary"
PDF = BASE / "sources/Rerun_Impact_20261028.pdf"
DIGEST = "02bf8e543cf10e45b0f6247c0b36db7fb65f6305c4a418b076ba0880c39cda19"
MODELS = {"GPT-5.5": "GPT-5.5", "GPT-5.6 Sol": "GPT-5.6 Sol", "GPT-5.6 Luna Max": "GPT-5.6 Luna",
          "GPT-5.6 Luna": "GPT-5.6 Luna", "DeepSeek-v4-pro-0813": "DeepSeek V4 Pro", "DeepSeek V4 Pro": "DeepSeek V4 Pro"}


def write_csv(name, rows):
    path = BASE / "s2_reruns/dataset" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)


def table_rows(page):
    # Every table cell has a filled background rectangle and several thinner text decorations.
    cells = [r for r in page.rects if r["height"] > 15 and abs(r["x0"] - 50.775) < 0.06]
    for left in sorted(cells, key=lambda r: r["top"]):
        top, bottom = left["top"], left["bottom"]
        boxes = sorted((r for r in page.rects if abs(r["top"] - top) < .02 and
                        abs(r["bottom"] - bottom) < .02 and r["width"] > 18), key=lambda r: r["x0"])
        values = [page.crop((r["x0"], top, r["x1"], bottom)).extract_text(x_tolerance=1) for r in boxes]
        if values[0] not in ("Model", "Question", "Run"):
            yield top, bottom, values


def parse(pdf=PDF):
    if sha256(pdf.read_bytes()).hexdigest() != DIGEST:
        raise ValueError("Unexpected report edition")
    ledger, effects = [], []
    with pdfplumber.open(pdf) as doc:
        for page_num, page in enumerate(doc.pages, 1):
            bench = "CompBioBench" if page_num <= 13 else ("BixBench" if page_num <= 18 else "IWC")
            for top, bottom, cells in table_rows(page):
                vals = [" ".join(s.split()) for s in cells]
                if page_num in (1, 2, 14, 19):
                    if page_num < 3:
                        m, rep, count, changed, before, after, delta = vals
                        track = "Galaxy" if page_num == 1 else "custom code"
                        baseline = 100
                    else:
                        m, track, count, baseline, before, after, delta = vals
                        track = "Galaxy" if track == "Galaxy" else "custom code"
                        rep, changed = "", ""
                    effects.append(dict(page=page_num, benchmark=bench, model=MODELS[m], condition=track,
                                        replicate=rep.lstrip("R"), reruns=int(count), changed_strings=changed,
                                        baseline=baseline, before_pct=float(before.rstrip("%")),
                                        after_pct=float(after.rstrip("%")), reported_delta_pp=float(delta)))
                    continue
                urls = [a["uri"] for a in page.hyperlinks if top <= (a["top"] + a["bottom"]) / 2 < bottom]
                by_host = {urlsplit(url).netloc: url for url in urls}
                trace = by_host["huggingface.co"]
                question = by_host["goeckslab.github.io"]
                task = question.split("/")[-2]
                rep = int(re.search(r"/replicate_(\d)", trace)[1])
                track = "Galaxy" if "usegalaxy.org" in by_host else "custom code"
                model = next(label for tag, label in [("gpt55","GPT-5.5"),("gpt56_sol","GPT-5.6 Sol"),
                                                       ("luna","GPT-5.6 Luna"),("deepseek","DeepSeek V4 Pro")]
                             if tag in trace.lower())
                answer_cell = cells[2]
                changed = "Unchanged" not in answer_cell
                parts = re.split(r"Rerun:\s*", answer_cell.removeprefix("Original:").strip(), maxsplit=1)
                before = parts[0].removeprefix("Unchanged").strip()
                after = parts[1].strip() if changed else before
                reason = vals[1]
                reason_class = ("direct copying" if "directly copied" in reason else
                                "exposure unconfirmed" if "not confirmed" in reason else
                                "reference access" if "expected" in reason and bench == "IWC" else
                                "prior-run access" if ("read " in reason.lower() or "downloaded" in reason.lower())
                                else "scientific follow-up")
                ledger.append(dict(page=page_num, benchmark=bench, task=task, model=model, condition=track,
                                   replicate=rep, report_changed=changed, reason_class=reason_class,
                                   report_reason=reason, original_cell=before, replacement_cell=after,
                                   question_url=question, history_url=by_host.get("usegalaxy.org",""), trace_url=trace))
    assert len(ledger) == 77 and len(effects) == 25
    write_csv("report_runs.csv", ledger)
    write_csv("report_effects.csv", effects)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=PDF)
    parse(parser.parse_args().pdf)
