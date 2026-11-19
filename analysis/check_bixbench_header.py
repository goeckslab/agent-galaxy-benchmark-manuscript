"""Read three public Galaxy histories and independently check bix-52-q7.

Usage: .venv/Scripts/python.exe analysis/check_bixbench_header.py
Requires network access to usegalaxy.org; no credentials or private traces.
Writes only derived counts and public source fingerprints, not trace contents.
Public responses are cached under .venv/qa/; pass --refresh to reread them.
Long-term archival remains author work.
"""
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/outline_verification"
CACHE = ROOT / ".venv/qa/header-history-public-cache"
BASE = "https://usegalaxy.org"


def main():
    sources, rows = [], []
    CACHE.mkdir(parents=True, exist_ok=True)

    def fetch(url):
        cached = CACHE / hashlib.sha256(url.encode()).hexdigest()
        if cached.exists() and "--refresh" not in sys.argv:
            body = cached.read_bytes()
        else:
            with urllib.request.urlopen(url, timeout=60) as response:
                body = response.read()
            cached.write_bytes(body)
        sources.append(dict(url=url, sha256=hashlib.sha256(body).hexdigest(), bytes=len(body)))
        return body

    data = json.loads((ROOT / "data/site/bixbench/data/results.json").read_text(encoding="utf8"))
    item = next(i for i in data["items"] if i["item_id"] == "bix-52-q7")
    expected = int(item["accepted_answers"][0].replace(",", ""))
    for exp, conditions in item["results"].items():
        if data["experiments"][exp].get("superseded"):
            continue
        model = data["experiments"][exp]["configuration"]["model"]
        for run in conditions["galaxy_strict_skills"]:
            if (model, run["replicate"]) not in [("gpt-5.6-luna", 1), ("gpt-5.6-luna", 2), ("gpt-5.6-sol", 3)]:
                continue
            history = run["history_url"]
            hid = urllib.parse.parse_qs(urllib.parse.urlparse(history).query)["id"][0]
            contents = json.loads(fetch(f"{BASE}/api/histories/{hid}/contents"))
            datasets = {d["hid"]: d for d in contents if not d.get("deleted")}
            tables = {}
            for n in ([5, 6, 7] if run["status"] == "fail" else [5]):
                detail = json.loads(fetch(BASE + datasets[n]["url"]))
                body = fetch(urllib.parse.urljoin(BASE, detail["download_url"]))
                tables[n] = list(csv.reader(io.StringIO(body.decode("utf-8-sig")), delimiter="\t"))
            original = tables[5]
            column = original[0].index("MethylationPercentage")
            removed = sum(10 <= float(row[column]) <= 90 for row in original[1:] if row)
            assert removed == expected
            header_retained = observed_count = filtered_lines = filtered_data = None
            if run["status"] == "fail":
                assert "Filter" in datasets[6]["name"] and "count" in datasets[7]["name"]
                filtered, counted = tables[6], tables[7]
                header_retained = filtered[0] == original[0]
                # wc can return lines alone or lines, words and characters; lines is first.
                count_values = [int(token) for row in counted for cell in row for token in cell.split() if token.isdigit()]
                assert count_values, f"No line count for {model} replicate {run['replicate']}: {counted[:5]!r}"
                observed_count = count_values[0]
                numeric_filtered = [row for row in filtered if row and row != original[0]]
                assert all(10 <= float(row[column]) <= 90 for row in numeric_filtered)
                assert len(numeric_filtered) == removed
                assert header_retained and observed_count == len(filtered) == removed+1
                filtered_lines, filtered_data = len(filtered), len(numeric_filtered)
            else:
                # The correct comparator used Table Compute, not the failed runs' filter/count route.
                assert int(str(run["answer"]).replace(",", "")) == removed
            rows.append(dict(task=item["item_id"], model=model, replicate=run["replicate"],
                history_url=history, history_items=len(datasets), original_data_rows=len(original)-1,
                independently_counted_removed=removed, retained_header=header_retained,
                filtered_physical_lines=filtered_lines, filtered_data_rows=filtered_data,
                line_count_output=observed_count, submitted_answer=run["answer"], status=run["status"]))
            print(f"Checked {model} replicate {run['replicate']}: {removed} data rows, {observed_count} counted lines", flush=True)
    assert len(rows) == 3
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "header_history_check.csv").open("w", encoding="utf8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    evidence = dict(retrieved_utc=datetime.now(timezone.utc).isoformat(),
        question=item["question"], accepted_answer=expected,
        independent_rule="Count input measurements with 10 <= MethylationPercentage <= 90, excluding header",
        script_sha256=hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        sources=sources)
    (OUT / "header_history_sources.json").write_text(json.dumps(evidence, indent=2)+"\n", encoding="utf8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
