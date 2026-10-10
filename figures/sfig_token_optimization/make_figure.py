#!/usr/bin/env python3
"""Supplementary figure: Galaxy / custom-code tokens on BixBench-Verified-50 across the optimization rounds.

Reads data/token_optimization_ratios.csv (written by analysis/token_usage.py) and writes
the figure (PDF and PNG) and source_data.csv next to this script.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "token_optimization_ratios.csv"
NAME = HERE.name
ACCENT, INK, INK2 = "#0072B2", "#222222", "#666666"


def main() -> None:
    df = pd.read_csv(DATA).sort_values("order")
    df[["order", "stage", "change", "model", "runs_per_task", "galaxy_tokens_m", "custom_code_tokens_m",
        "token_unit", "ratio", "approximate", "galaxy_correct", "galaxy_runs"]].to_csv(HERE / "source_data.csv", index=False)

    models = list(dict.fromkeys(df.model))
    df["x"] = [i + 0.5 * models.index(m) for i, m in enumerate(df.model)]

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for m in models:
        d = df[df.model == m]
        ax.plot(d.x, d.ratio, color=ACCENT, lw=2, zorder=2)
        for _, r in d.iterrows():
            ax.scatter([r.x], [r.ratio], s=45, zorder=3, color="white" if r.approximate else ACCENT,
                       edgecolors=ACCENT, linewidths=1.8)
            label = f"about {r.ratio:g}×" if r.approximate else f"{r.ratio:.2f}×"
            ax.annotate(label, (r.x, r.ratio), xytext=(6, 7), textcoords="offset points", fontsize=8,
                        fontweight="bold", color=INK)
            if pd.notna(r.galaxy_correct):
                ax.annotate(f"{int(r.galaxy_correct)}/{int(r.galaxy_runs)} correct", (r.x, r.ratio),
                            xytext=(0, -15), textcoords="offset points", ha="center", fontsize=7, color=INK2)
        ax.annotate(m, ((d.x.min() + d.x.max()) / 2, 30), ha="center", fontsize=9, fontweight="bold", color=INK)
        ax.plot([d.x.min() - 0.2, d.x.max() + 0.2], [26, 26], color=INK2, lw=0.8)
    ax.axhline(1, color=INK2, lw=1, zorder=1)
    ax.text(df.x.min() - 0.3, 1.06, "Same as custom code", fontsize=8, color=INK2, va="bottom")
    ax.set_yscale("log", base=2)
    ax.set_ylim(0.9, 34)
    ax.set_yticks([1, 2, 4, 8, 16], ["1×", "2×", "4×", "8×", "16×"])
    ax.set_xticks(df.x, [f"{s}\n{c}" for s, c in zip(df.stage, df.change)], fontsize=7.5)
    ax.set_xlim(df.x.min() - 0.5, df.x.max() + 0.6)
    ax.grid(axis="y", color="#e5e5e5", lw=0.8)
    ax.set_axisbelow(True)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", length=0)
    ax.set_ylabel("Galaxy ÷ custom-code total tokens; log scale", fontsize=8)
    ax.scatter([], [], s=40, color="white", edgecolors=ACCENT, linewidths=1.8, label="approximate: 1 run per task")
    ax.scatter([], [], s=40, color=ACCENT, label="measured: 3 runs per task (round 3a: 1 Galaxy run per task)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False, fontsize=7.5)
    ax.set_title("Galaxy's token overhead on BixBench fell from about 20× to 1.53× custom code",
                 fontsize=10, loc="left", color=INK, pad=12)
    plt.tight_layout()
    plt.savefig(HERE / f"{NAME}.pdf")
    plt.savefig(HERE / f"{NAME}.png", dpi=300)


if __name__ == "__main__":
    main()
