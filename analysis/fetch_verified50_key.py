"""Archive the upstream reference fields and their exact Hub revision, without any execution records."""
import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

D = Path(__file__).resolve().parents[1]/"figures/benchmark_results_summary/sources"
REPO = "phylobio/BixBench-Verified-50"


def main():
    rev = "c77fc8ea4611b546947b8a4710ed36ab72ee233c"
    url = f"https://huggingface.co/datasets/{REPO}/resolve/{rev}/BixBench-Verified-50.jsonl"
    token=os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("Optional upstream check requires granted dataset access and HF_TOKEN.")
    with urlopen(Request(url,headers={"Authorization":"Bearer "+token}),timeout=45) as f:
        raw = f.read()
    rows = [json.loads(line) for line in raw.splitlines() if line]
    assert len(rows)==50
    with (D/"verified50_reference.csv").open("w",newline="",encoding="utf8") as f:
        w = csv.DictWriter(f,fieldnames=["question_id","capsule_uuid","eval_mode","ideal"],extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    record = dict(url=url,revision=rev,retrieved_utc=datetime.now(timezone.utc).date().isoformat(),
                  upstream_bytes=len(raw),upstream_sha256=sha256(raw).hexdigest())
    (D/"verified50_revision.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf8")


if __name__ == "__main__":
    main()
