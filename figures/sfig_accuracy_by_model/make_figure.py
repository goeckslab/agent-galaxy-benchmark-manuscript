#!/usr/bin/env python3
"""Supplementary figure: accuracy by benchmark, model and condition, main runs.

Reads data/accuracy_by_model.csv (written by analysis/accuracy.py) and writes the figure
(PDF and PNG) and source_data.csv next to this script.

One panel per benchmark. Each row is a model, plus all models together. Large markers are
the model's accuracy in each condition; small faint markers are its three replicates.
Each panel has its own accuracy axis, because the benchmarks' accuracy ranges differ.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "accuracy_by_model.csv"
NAME = HERE.name

BENCHMARKS = ["BixBench-Verified-50", "CompBioBench", "IWC", "IWC multi-step"]
METRIC = {
    "BixBench-Verified-50": "Runs answered correctly (%)",
    "CompBioBench": "Official score (%)",
    "IWC": "Mean output agreement, acc (%)",
    "IWC multi-step": "Required results that pass, acc (%)",
}
MODELS = ["GPT-5.5", "GPT-5.6 Sol", "GPT-5.6 Luna", "DeepSeek V4 Pro", "All models"]
# Okabe-Ito blue and orange (colorblind-safe), with marker shape as a second cue.
STYLE = {"Galaxy": dict(color="#0072B2", marker="o", dy=0.13),
         "custom code": dict(color="#E69F00", marker="s", dy=-0.13)}
INK, INK2, GRID = "#222222", "#666666", "#e5e5e5"


def main() -> None:
    df = pd.read_csv(DATA)
    df = df[df.benchmark.isin(BENCHMARKS) & df.model.isin(MODELS)]
    cols = ["benchmark", "model", "condition", "accuracy_pct", "rep1", "rep2", "rep3", "n_runs", "definition"]
    df[cols].to_csv(HERE / "source_data.csv", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.4))
    for ax, bench in zip(axes.flat, BENCHMARKS):
        d = df[df.benchmark == bench]
        models = [m for m in MODELS if m in set(d.model)]
        ys = {m: -i for i, m in enumerate(models)}
        lo = min(d[["accuracy_pct", "rep1", "rep2", "rep3"]].min(skipna=True))
        hi = max(d[["accuracy_pct", "rep1", "rep2", "rep3"]].max(skipna=True))
        for m in models:
            y, g = ys[m], d[d.model == m].set_index("condition")
            pooled = m == "All models"
            ax.plot(g.accuracy_pct.values, [y + STYLE[c]["dy"] for c in g.index], color=INK2, lw=0.8, zorder=1)
            for c, s in STYLE.items():
                if c not in g.index:
                    continue
                r = g.loc[c]
                reps = [r[k] for k in ("rep1", "rep2", "rep3") if pd.notna(r[k])]
                ax.scatter(reps, [y + s["dy"]] * len(reps), s=12, marker=s["marker"], color=s["color"],
                           alpha=0.35, lw=0, zorder=2)
                ax.scatter([r.accuracy_pct], [y + s["dy"]], s=58 if pooled else 40, marker=s["marker"],
                           color=s["color"], edgecolor="white", lw=0.8, zorder=3)
        if "All models" in ys:
            ax.axhline(ys["All models"] + 0.5, color=GRID, lw=0.8, zorder=0)
        span = hi - lo
        ax.set_xlim(lo - 0.08 * span, hi + 0.08 * span)
        ax.set_ylim(-len(models) + 0.45, 0.45)
        ax.set_yticks(list(ys.values()), models, fontsize=8)
        for t in ax.get_yticklabels():
            t.set_fontweight("bold" if t.get_text() == "All models" else "normal")
        ax.set_title(bench, fontsize=9, fontweight="bold", color=INK, loc="left")
        ax.set_xlabel(METRIC[bench], fontsize=8, color=INK2)
        ax.tick_params(axis="x", labelsize=8, colors=INK2)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for side in ["top", "right", "left"]:
            ax.spines[side].set_visible(False)

    handles = [plt.Line2D([], [], ls="", marker=s["marker"], color=s["color"], markersize=7, label=c.capitalize()
                          if c == "custom code" else c) for c, s in STYLE.items()]
    handles.append(plt.Line2D([], [], ls="", marker="o", color=INK2, alpha=0.35, markersize=4,
                              label="Single replicate"))
    fig.legend(handles=handles, loc="upper right", ncol=3, frameon=False, fontsize=8, bbox_to_anchor=(0.99, 0.995))
    fig.suptitle("Accuracy by model in Galaxy and custom code", fontsize=10, x=0.02, ha="left", y=0.985, color=INK)
    plt.tight_layout(rect=(0, 0, 1, 0.965), h_pad=1.2)
    plt.savefig(HERE / f"{NAME}.pdf")
    plt.savefig(HERE / f"{NAME}.png", dpi=300)


if __name__ == "__main__":
    main()
