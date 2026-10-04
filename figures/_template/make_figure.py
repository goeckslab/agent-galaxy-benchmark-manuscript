#!/usr/bin/env python3
"""Template figure script: pass rate by model and track from the results manifest.

Copy this file into a new figures/figN_short_name/ folder and adapt it.
It writes the figure (PDF and PNG) and source_data.csv next to the script.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
MANIFEST = HERE.parents[1] / "data" / "results_manifest.csv"
NAME = HERE.name if HERE.name != "_template" else "template"


def main() -> None:
    df = pd.read_csv(MANIFEST)
    if df.empty:
        raise SystemExit(f"{MANIFEST} has no rows yet; nothing to plot.")

    df["correct"] = df["correct"].astype(str).str.lower().isin(["true", "1", "yes"])
    summary = (
        df.groupby(["model", "track"])["correct"]
        .agg(pass_rate="mean", n_runs="count")
        .reset_index()
    )
    summary.to_csv(HERE / "source_data.csv", index=False)

    pivot = summary.pivot(index="model", columns="track", values="pass_rate")
    ax = pivot.plot.bar(figsize=(6, 4), rot=30)
    ax.set_ylabel("Pass rate")
    ax.set_ylim(0, 1)
    ax.legend(title="Track")
    plt.tight_layout()
    plt.savefig(HERE / f"{NAME}.pdf")
    plt.savefig(HERE / f"{NAME}.png", dpi=300)


if __name__ == "__main__":
    main()
