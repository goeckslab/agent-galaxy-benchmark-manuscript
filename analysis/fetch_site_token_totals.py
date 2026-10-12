#!/usr/bin/env python3
"""Fetch token totals per benchmark, model and condition from the benchmark results website.

Usage:
    python analysis/fetch_site_token_totals.py

Token totals in the paper come from the public results website
(https://goeckslab.github.io/galaxy-agent-benchmark/). This script reads it and
writes data/site_token_totals.csv, with the fetch date in each row's source:

- CompBioBench and IWC: summed from the per-replicate tables
  compbiobench/data/public_token_usage.tsv and iwc/data/token_usage.tsv.
- BixBench-Verified-50: the per-model table on bixbench/tokens/, which gives
  totals rounded to 0.01M tokens (no data file is published).

The website is deployed from the private repository goeckslab/galaxy-agent-benchmark;
the committed table was fetched on 2026-10-12, when the deployed files matched its
commit ff9c4f5.

Only the four primary model configurations are kept. Total tokens are input plus
output, with cached input counted once inside input.
"""
import argparse
import csv
import datetime
import html
import io
import re
import sys
import urllib.request
from collections import defaultdict

try:  # use the system trust store where a proxy re-signs TLS traffic
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

SITE = "https://goeckslab.github.io/galaxy-agent-benchmark"
TODAY = datetime.date.today().isoformat()
OUT = "data/site_token_totals.csv"

MODELS = {
    "Codex GPT-5.5": "GPT-5.5", "GPT-5.5": "GPT-5.5",
    "Codex GPT-5.6 Sol": "GPT-5.6 Sol", "GPT-5.6 Sol": "GPT-5.6 Sol",
    "Codex GPT-5.6 Luna": "GPT-5.6 Luna", "GPT-5.6 Luna": "GPT-5.6 Luna",
    "Codex + DeepSeek-v4-pro-0813": "DeepSeek V4 Pro", "Codex + DeepSeek V4 Pro": "DeepSeek V4 Pro",
    "DeepSeek V4 Pro via Codex": "DeepSeek V4 Pro",
}
TRACKS = {"galaxy": "Galaxy", "galaxy_tools": "Galaxy", "anycode": "custom code",
          "any_code_no_galaxy_tools": "custom code"}


def fetch(path: str) -> str:
    with urllib.request.urlopen(f"{SITE}/{path}") as r:
        return r.read().decode()


def from_tsv(benchmark: str, path: str, runs_col: str) -> list[dict]:
    sums = defaultdict(lambda: {"runs": 0, "input": 0, "total": 0})
    for row in csv.DictReader(io.StringIO(fetch(path)), delimiter="\t"):
        model, track = MODELS.get(row["model"]), TRACKS.get(row["condition"])
        if model is None or track is None:
            continue
        s = sums[(model, track)]
        s["runs"] += int(row[runs_col])
        s["input"] += int(row["input_tokens"])
        s["total"] += int(row["total_tokens"])
    return [{"benchmark": benchmark, "model": m, "track": t, "runs_with_usage": s["runs"],
             "input_tokens": s["input"], "total_tokens": s["total"], "precision": "exact",
             "source": f"{SITE}/{path} (fetched {TODAY})"} for (m, t), s in sorted(sums.items())]


def from_bixbench_page() -> list[dict]:
    path = "bixbench/tokens/"
    text = re.sub(r"(?s)<(script|style).*?</\1>", "", fetch(path))
    text = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(br|/tr|/p|/div)[^>]*>", "\n", text)))
    rows = []
    for line in text.split("\n"):
        line = re.sub(r"\s+", " ", line).strip()
        m = re.match(r"(.+?) (Galaxy-API code|Open-ended code) with skills Accuracy .*? ([\d.]+)M \S+ ([\d.]+)M", line)
        if not m or "Claude Code" in m.group(1) or m.group(1) not in MODELS:
            continue
        rows.append({"benchmark": "BixBench-Verified-50", "model": MODELS[m.group(1)],
                     "track": "Galaxy" if m.group(2) == "Galaxy-API code" else "custom code",
                     "runs_with_usage": "", "input_tokens": round(float(m.group(4)) * 1e6),
                     "total_tokens": round(float(m.group(3)) * 1e6), "precision": "rounded to 0.01M",
                     "source": f"{SITE}/{path} (fetched {TODAY})"})
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default=OUT)
    args = p.parse_args()

    rows = (from_bixbench_page()
            + from_tsv("CompBioBench", "compbiobench/data/public_token_usage.tsv", "items_with_usage")
            + from_tsv("IWC", "iwc/data/token_usage.tsv", "runs_with_usage"))
    expected = {(b, m, t) for b in ["BixBench-Verified-50", "CompBioBench", "IWC"]
                for m in set(MODELS.values()) for t in ["Galaxy", "custom code"]}
    found = {(r["benchmark"], r["model"], r["track"]) for r in rows}
    if found != expected or len(rows) != len(expected):
        sys.exit(f"Expected one row per benchmark, model and condition; missing {sorted(expected - found)}")

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.out} from {SITE} ({TODAY})")


if __name__ == "__main__":
    main()
