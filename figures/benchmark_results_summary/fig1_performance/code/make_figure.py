"""A crossed experimental design with absolute benchmark scores and paired effects."""
from math import isfinite
from pathlib import Path
import sys

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from plot_style import BENCH, C, G, GRID, INK, MODELS, MUTED, PALE, Plate, data, xgrid

scores = data(__file__)
pooled = scores[scores.model == "Pooled"].set_index("benchmark").loc[BENCH]
cell = pooled.iloc[0]
p = Plate(111)

p.heading(2, 3.5, "a", "Paired experimental design")
for x, w, label in [(4, 35, f"{cell.model_count:.0f} models in Codex"),
                    (48, 39, f"{cell.policies:.0f} execution policies"),
                    (98, 39, f"{pooled.tasks.sum():.0f} benchmark tasks")]:
    p.text(x, 9, label, weight="bold")
    p.line(x, 11.5, x + w, 11.5, color=MUTED)
for i, model in enumerate(MODELS):
    p.text(4, 14.4 + 4.1 * i, model)
for x in (43, 92):
    p.text(x, 21, "×", ha="center", weight="bold")
for y, policy, note, color in [(16, "Galaxy", "Installed or user-defined tools", G),
                               (24, "Custom code", "Agent-written analysis", C)]:
    p.line(48.2, y - 1.3, 48.2, y + 4.2, color=color, lw=1.8)
    p.text(50.4, y, policy, weight="bold")
    p.text(50.4, y + 3.6, note, fontsize=6.5)
for i, (bench, r) in enumerate(pooled.iterrows()):
    y = 15.3 + 5.2 * i
    p.text(98, y, "BixBench-Verified-50" if bench == "BixBench" else bench)
    p.text(136, y, f"{r.tasks:.0f}", ha="right")
p.arrow(138, 20, 145, 20)
p.box(146, 9, 31, 19, PALE)
p.text(161.5, 14.8, f"{cell.replicates_per_task_model:.0f} runs per combination", ha="center", fontsize=6.5)
p.text(161.5, 22.4, f"{(pooled.runs_per_condition * pooled.policies).sum():,.0f} runs", ha="center", weight="bold")

p.heading(2, 34.5, "b", "Pooled benchmark scores")
policies = [("Galaxy", "galaxy", G, G), ("Custom code", "custom_code", "#FAEEE8", C)]
handles = [Patch(facecolor=fill, edgecolor=edge, linewidth=1, label=name) for name, _, fill, edge in policies]
p.fig.legend(handles=handles, loc="center left", bbox_to_anchor=(.083, 1 - 41.3 / p.height),
             ncol=2, borderaxespad=0, handlelength=1.25, columnspacing=1.7)
ax = p.axes(15, 48, 71, 24)
centers = np.arange(len(BENCH))
for j, (_, field, fill, edge) in enumerate(policies):
    xs = centers + (j - .5) * .425
    values = pooled[field].to_numpy()
    ax.bar(xs, values, width=.385, color=fill, edgecolor=edge, linewidth=.95, zorder=2)
    for x, value in zip(xs, values):
        ax.annotate(f"{value:.2f}", (x, value), xytext=(0, 1.3), textcoords="offset points",
                    ha="center", va="bottom", weight="bold", fontsize=6.5)
ax.set(xlim=(-.55, 2.55), ylim=(0, 104), xticks=centers, xticklabels=BENCH,
       yticks=[0, 50, 100], ylabel="Score (%)")
ax.tick_params(axis="x", length=0, pad=3, labelsize=7)
ax.grid(axis="y", lw=.45, color=GRID)
ax.set_axisbelow(True)
for label in ax.get_xticklabels():
    label.set_weight("bold")
for i, endpoint in enumerate(["Accepted answers", "Official score", "Output agreement"]):
    ax.text(i, -.32, endpoint, transform=ax.get_xaxis_transform(), ha="center", va="center", fontsize=6.5)

p.heading(91, 34.5, "c", "Scores by model and policy (%)")
matrix = scores[scores.model != "Pooled"].set_index(["model", "benchmark"]).loc[MODELS]
model_scores = np.column_stack([matrix.xs(bench, level="benchmark").loc[MODELS, field]
                                for bench in BENCH for _, field, _, _ in policies])
shading = LinearSegmentedColormap.from_list("score", ["#F5F7F8", "#CAD8DF", "#9DB4C1"])
cell_width = 60.8 / 6
for j, bench in enumerate(BENCH):
    x = 116.5 + (2 * j + 1) * cell_width
    p.text(x, 41, bench, ha="center", weight="bold", fontsize=6.5)
    p.line(x - 9.4, 43.5, x + 9.4, 43.5)
    for shift, label in [(-5.05, "G"), (5.05, "C")]:
        p.text(x + shift, 46, label, ha="center", weight="bold", fontsize=6.5)
for i, model in enumerate(MODELS):
    top = 49 + i * 7.1
    p.text(91.8, top + 3.55, model, fontsize=6.5)
    for j, value in enumerate(model_scores[i]):
        left = 116.5 + j * cell_width
        gutter = .9 if j % 2 == 1 else .25
        p.box(left, top, cell_width - gutter, 6.75, shading((value - 80) / 20))
        p.text(left + (cell_width - gutter) / 2, top + 3.4, f"{value:.1f}", ha="center", weight="bold")
p.text(91.8, 81, "G, Galaxy  ·  C, custom code  ·  darker cells, higher scores", fontsize=6.5)

p.heading(2, 87, "d", "Pooled difference, Galaxy minus custom code")
p.text(129.5, 87, "Difference [95% interval]", weight="bold", fontsize=6.5)
ax = p.axes(33, 91, 88, 13.5)
ax.axvline(0, lw=.8, color=INK)
for y, (bench, r) in enumerate(pooled.iterrows()):
    py = 93.25 + y * 4.5
    p.text(4, py, bench)
    has_interval = isfinite(r.lower_95) and isfinite(r.upper_95)
    if has_interval:
        ax.hlines(y, r.lower_95, r.upper_95, color=G, lw=1.35)
        ax.vlines([r.lower_95, r.upper_95], y - .14, y + .14, color=G, lw=.85)
        interval = f"[{r.lower_95:.1f}, {r.upper_95:.1f}]".replace("-", "−")
    else:
        interval = "unavailable"
    ax.plot(r.difference, y, "D", ms=4.2, mec=G, mfc=G if has_interval else "white", mew=1)
    p.text(129.5, py, f"{r.difference:+.2f}", weight="bold")
    p.text(141, py, interval, fontsize=6.5)
ax.set(xlim=(-4.6, 8.8), ylim=(2.5, -.5), yticks=[], xticks=[-4, 0, 4, 8])
xgrid(ax)
p.text(129.5, 107.4, "Percentage points", fontsize=6.5)
p.save(__file__)
