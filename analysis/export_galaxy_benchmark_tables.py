#!/usr/bin/env python3
"""Export the small derived tables that Figure 2 reads from the Galaxy_benchmark run archive.

Usage:
    python analysis/export_galaxy_benchmark_tables.py --source /path/to/Galaxy_benchmark

Reads three tracked files of the archive (paulocilasjr/Galaxy_benchmark) and writes, into data/:

- run_scores.csv: one row per scored run of the four primary model configurations (3,816 runs).
- galaxy_traced_runs.csv: Galaxy-condition runs of those configurations with a parsed trace (1,908 runs).
- galaxy_tool_use.csv: one row per traced Galaxy run and installed tool it called, plus one row per run that called
  a user-defined tool (UDT).

The tables hold identifiers, scores and tool identifiers only: no trace text, prompts or answers.
The script prints the archive commit; record it in data/README.md.
"""
import argparse
import subprocess
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
SCORES = "manuscript_narrative/original_layout/analysis/accuracy_primary_runs.csv"
CALLS = "manuscript_narrative/derived/galaxy_calls/calls.csv.gz"
COVERAGE = "manuscript_narrative/derived/galaxy_calls/run_coverage.csv"
BENCHMARK = {"BixBench50": "BixBench-Verified-50", "CompBio": "CompBioBench", "IWC": "IWC"}
TRACK = {"open_ended_code": "custom code", "galaxy": "Galaxy"}  # values defined in data/README.md
# Trace model labels of the four primary configurations; the superseded Claude Code harness is left out.
TRACE_MODEL = {
    "codex_gpt_5_5": "GPT-5.5",
    "codex_gpt_5_6_sol": "GPT-5.6 Sol",
    "codex_gpt_5_6_luna": "GPT-5.6 Luna",
    "deepseek_v4_pro_via_codex": "DeepSeek V4 Pro",
    "codex_deepseek_v4_pro_0813": "DeepSeek V4 Pro",
    "codex_deepseek_v4_pro": "DeepSeek V4 Pro",
}
RUN_KEY = ["benchmark", "task_id", "model", "replicate"]


def archive_commit(source: Path) -> str:
    sha = subprocess.run(["git", "-C", str(source), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(source), "status", "--porcelain", "--", SCORES, CALLS, COVERAGE],
                           capture_output=True, text=True)
    if dirty.stdout.strip():
        raise SystemExit(f"Source files have uncommitted changes:\n{dirty.stdout}")
    return sha.stdout.strip()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", required=True, type=Path, help="Path to a Galaxy_benchmark checkout")
    args = p.parse_args()
    print(f"Galaxy_benchmark commit: {archive_commit(args.source)}")

    scores = pd.read_csv(args.source / SCORES)
    scores = pd.DataFrame({
        "benchmark": scores.benchmark.map(BENCHMARK),
        "task_id": scores.task,
        "cluster": scores.cluster,          # bootstrap and permutation unit: BixBench source capsule, otherwise task
        "model": scores.cfg,
        "track": scores.env.map(TRACK),
        "replicate": scores.replicate,
        "score": scores.score,              # 0/1 acceptance; IWC: output agreement 0-1
    })
    assert scores.notna().all().all() and len(scores) == 3816, "unexpected run_scores content"
    scores.to_csv(DATA / "run_scores.csv", index=False)

    cov = pd.read_csv(args.source / COVERAGE)
    cov = cov[cov.model.isin(TRACE_MODEL)]
    runs = pd.DataFrame({"benchmark": cov.benchmark.map(BENCHMARK), "task_id": cov.task,
                         "model": cov.model.map(TRACE_MODEL), "replicate": cov.replicate})
    runs = runs.drop_duplicates().sort_values(RUN_KEY)
    runs.to_csv(DATA / "galaxy_traced_runs.csv", index=False)

    calls = pd.read_csv(args.source / CALLS, low_memory=False,
                        usecols=["benchmark", "task", "model", "replicate", "tool", "galaxy_server", "tool_id_base"])
    calls = calls[calls.model.isin(TRACE_MODEL) & calls.galaxy_server]
    calls = calls.assign(benchmark=calls.benchmark.map(BENCHMARK), task_id=calls.task,
                         model=calls.model.map(TRACE_MODEL))
    installed = calls[calls.tool == "run_galaxy_tool_and_wait"].dropna(subset=["tool_id_base"])
    installed = installed.assign(tool_id=installed.tool_id_base, kind="installed")
    udt = calls[calls.tool == "run_galaxy_udt_and_wait"].assign(tool_id="UDT", kind="udt")
    use = pd.concat([installed, udt])[RUN_KEY + ["tool_id", "kind"]].drop_duplicates().sort_values(RUN_KEY + ["tool_id"])
    assert use.merge(runs, on=RUN_KEY, how="left", indicator=True)._merge.eq("both").all(), "tool use outside traced runs"
    use.to_csv(DATA / "galaxy_tool_use.csv", index=False)

    print(f"run_scores.csv: {len(scores)} runs; galaxy_traced_runs.csv: {len(runs)} runs; "
          f"galaxy_tool_use.csv: {len(use)} rows")


if __name__ == "__main__":
    main()
