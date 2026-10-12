#!/usr/bin/env python3
"""Galaxy versus custom-code token use, in the main runs and across the optimization rounds.

Usage:
    python analysis/token_usage.py

Inputs (in data/):
- site_token_totals.csv: total tokens per benchmark, model and condition of the
  main runs, from the results website (written by fetch_site_token_totals.py).
- token_optimization_rounds.csv: BixBench-Verified-50 token totals at each
  optimization stage, transcribed from the benchmark results site and Junhao
  Qiu's notes (one source per row).

Outputs (in data/):
- token_ratios_main_runs.csv: Galaxy and custom-code total tokens per
  benchmark and model, plus all models pooled, and their ratio.
- token_optimization_ratios.csv: the rounds table with the Galaxy / custom-code
  ratio of each stage, computed from the totals where they exist and otherwise
  the approximate ratio reported.

All token totals come from the results website. Total tokens are input plus
output, with cached input counted once inside input.
"""
import argparse
import sys

import pandas as pd

TRACKS = ["Galaxy", "custom code"]


def main_run_ratios(totals: pd.DataFrame) -> pd.DataFrame:
    unknown = set(totals.track) - set(TRACKS)
    if unknown:
        sys.exit(f"Unexpected tracks: {unknown}")
    if totals.duplicated(["benchmark", "model", "track"]).any():
        sys.exit("Expected one row per benchmark, model and condition.")
    rows = []
    for (benchmark, model), g in list(totals.groupby(["benchmark", "model"])) + \
            [((b, "All models"), g) for b, g in totals.groupby("benchmark")]:
        row = {"benchmark": benchmark, "model": model}
        for track, key in [("Galaxy", "galaxy"), ("custom code", "custom_code")]:
            row[f"{key}_total_tokens"] = g.loc[g.track == track, "total_tokens"].sum()
        row["ratio"] = row["galaxy_total_tokens"] / row["custom_code_total_tokens"]
        rows.append(row)
    return pd.DataFrame(rows)


def round_ratios(rounds: pd.DataFrame) -> pd.DataFrame:
    out = rounds.sort_values("order").copy()
    measured = out.galaxy_tokens_m.notna() & out.custom_code_tokens_m.notna()
    if (measured & out.ratio_reported.notna()).any() or (~measured & out.ratio_reported.isna()).any():
        sys.exit("Each round needs either both token totals or a reported ratio, not both.")
    out["ratio"] = (out.galaxy_tokens_m / out.custom_code_tokens_m).where(measured, out.ratio_reported)
    out["approximate"] = ~measured
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="data", help="Directory holding the input tables")
    p.add_argument("--out", default="data", help="Directory for the output tables")
    args = p.parse_args()

    main_runs = main_run_ratios(pd.read_csv(f"{args.data}/site_token_totals.csv"))
    rounds = round_ratios(pd.read_csv(f"{args.data}/token_optimization_rounds.csv"))
    main_runs.round(4).to_csv(f"{args.out}/token_ratios_main_runs.csv", index=False)
    rounds.round(4).to_csv(f"{args.out}/token_optimization_ratios.csv", index=False)

    with pd.option_context("display.width", 200, "display.max_columns", None):
        show = main_runs.assign(galaxy_m=main_runs.galaxy_total_tokens / 1e6,
                                custom_code_m=main_runs.custom_code_total_tokens / 1e6)
        print(show[["benchmark", "model", "galaxy_m", "custom_code_m", "ratio"]].round(2).to_string(index=False))
        print()
        print(rounds[["stage", "change", "model", "galaxy_tokens_m", "custom_code_tokens_m", "ratio", "approximate"]]
              .round(2).to_string(index=False))
    print(f"\nWrote token_ratios_main_runs.csv and token_optimization_ratios.csv to {args.out}/")


if __name__ == "__main__":
    main()
