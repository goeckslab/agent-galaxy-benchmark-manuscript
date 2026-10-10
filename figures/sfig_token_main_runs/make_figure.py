#!/usr/bin/env python3
"""Supplementary figure: Galaxy / custom-code input tokens by benchmark and model, main runs.

Reads data/token_ratios_main_runs.csv (written by analysis/token_usage.py) and writes
the figure (PDF and PNG) and source_data.csv next to this script.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "token_ratios_main_runs.csv"
NAME = HERE.name

BENCHMARKS = ["BixBench-Verified-50", "CompBioBench", "IWC"]
MODELS = ["GPT-5.5", "GPT-5.6 Sol", "GPT-5.6 Luna", "DeepSeek V4 Pro", "All models"]
GREY, ACCENT, INK, INK2 = "#9a9a9a", "#0072B2", "#222222", "#666666"


def fmt(v: float) -> str:
    return f"{v:.2f}×" if v < 1 else f"{v:.1f}×"


def main() -> None:
    df = pd.read_csv(DATA)
    df = df[df.benchmark.isin(BENCHMARKS) & df.model.isin(MODELS)]
    df = df.assign(b=df.benchmark.map(BENCHMARKS.index), m=df.model.map(MODELS.index)).sort_values(["b", "m"])
    df[["benchmark", "model", "galaxy_input_tokens", "custom_code_input_tokens", "ratio",
        "galaxy_runs_without_tokens", "custom_code_runs_without_tokens"]].to_csv(HERE / "source_data.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 6.0))
    y, ticks, labels = 0, [], []
    for benchmark in BENCHMARKS:
        y -= 0.6
        ax.text(0.205, y, benchmark, fontsize=9, fontweight="bold", color=INK, va="center")
        y -= 1
        for _, r in df[df.benchmark == benchmark].iterrows():
            pooled = r.model == "All models"
            color = ACCENT if pooled else GREY
            ax.plot([1, r.ratio], [y, y], color=color, lw=2 if pooled else 1.2, zorder=2)
            ax.scatter([r.ratio], [y], s=55 if pooled else 30, marker="D" if pooled else "o", color=color, zorder=3)
            right = r.ratio >= 1
            ax.annotate(fmt(r.ratio), (r.ratio, y), xytext=(7 if right else -7, 0), textcoords="offset points",
                        ha="left" if right else "right", va="center", fontsize=8,
                        fontweight="bold" if pooled else "normal", color=INK if pooled else INK2)
            ticks.append(y)
            labels.append(f"All {len(MODELS) - 1} models" if pooled else r.model)
            y -= 1
    ax.axvline(1, color=INK2, lw=1, zorder=1)
    ax.text(1.05, 0.2, "Same as custom code", fontsize=8, color=INK2, va="bottom")
    ax.set_xscale("log", base=2)
    ax.set_xlim(0.2, 10)
    ax.set_xticks([0.25, 0.5, 1, 2, 4, 8], ["0.25×", "0.5×", "1×", "2×", "4×", "8×"])
    ax.set_yticks(ticks, labels, fontsize=8)
    for t, lab in zip(ax.get_yticklabels(), labels):
        t.set_fontweight("bold" if lab.startswith("All") else "normal")
    ax.set_ylim(y + 0.4, 0.8)
    ax.grid(axis="x", color="#e5e5e5", lw=0.8)
    ax.set_axisbelow(True)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Galaxy ÷ custom-code input tokens (incl. cached context); log scale", fontsize=8)
    fig.suptitle("Galaxy used more tokens than custom code on BixBench and CompBioBench, not on IWC",
                 fontsize=10, x=0.02, ha="left", color=INK)
    plt.tight_layout()
    plt.savefig(HERE / f"{NAME}.pdf")
    plt.savefig(HERE / f"{NAME}.png", dpi=300)


if __name__ == "__main__":
    main()
