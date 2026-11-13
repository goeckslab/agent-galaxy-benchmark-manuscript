"""Experimental architecture, observed Galaxy execution and a reference-output check."""
from pathlib import Path
import sys

from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from plot_style import BENCH, C, G, INK, MODELS, MUTED, PALE, Plate, data, xgrid

source = data(__file__)
design = source[source.panel == "design"].set_index("benchmark").loc[BENCH]
routes = source[source.panel == "routes"]
check = source[source.panel == "history"].iloc[0]
p = Plate(134)

p.heading(2, 4, "a", "From a biological task to a benchmark score")
for x, w, title in [(4, 36, "Benchmark inputs"), (52, 29, "Agent in Codex"),
                    (95, 41, "Execution policy"), (148, 28, "Benchmark readout")]:
    p.text(x, 11, title, weight="bold")
    p.line(x, 14, x + w, 14, color=MUTED)
for i, (bench, r) in enumerate(design.iterrows()):
    y = 21 + i * 6
    p.text(4, y, "BixBench-Verified-50" if bench == "BixBench" else bench)
    p.text(40, y, f"{r.tasks:.0f}", ha="right")
for i, model in enumerate(MODELS):
    p.text(52, 20 + i * 4.8, model)
p.arrow(42, 27, 50, 27)
p.line(81.8, 27, 87, 27, color=MUTED)
p.line(87, 21, 87, 34.5, color=MUTED)
for y, name, note, color, background in [
    (21, "Galaxy", "Tool job and recorded history", G, PALE),
    (34.5, "Custom code", "Software and analysis files", C, "#F9EFEA"),
]:
    p.arrow(87, y, 93.7, y)
    p.box(95, y - 4.5, 41, 10, background)
    p.line(95, y - 4.5, 95, y + 5.5, color=color, lw=1.1)
    p.text(97, y - 1.1, name, weight="bold")
    p.text(97, y + 3, note, fontsize=6.5)
    p.line(136.3, y, 140.5, y, color=MUTED)
p.line(140.5, 21, 140.5, 34.5, color=MUTED)
p.arrow(140.5, 27, 146.7, 27)
for i, label in enumerate(["Reviewed answers", "Official submissions", "Workflow outputs"]):
    p.text(148, 21 + 6 * i, label)
cell = design.iloc[0]
p.box(4, 41.5, 172, 6.3, PALE)
p.text(90, 44.65, f"{design.tasks.sum():.0f} tasks   ×   {cell.models:.0f} models   ×   "
       f"{cell.policies:.0f} policies   ×   {cell.replicates:.0f} replicates   =   {design.runs.sum():,.0f} runs",
       ha="center", weight="bold")

palette = {"udt_only": G, "udt_and_standard": "#99C6C3", "standard_only": "#E2E7E8",
           "no_udt_recorded": "#F3F4F4", "no_analysis_jobs": INK}
hatches = {"standard_only": "..", "no_udt_recorded": "///"}
labels = {"udt_only": "UDT only", "udt_and_standard": "UDT + installed tools",
          "standard_only": "Installed tools only", "no_udt_recorded": "No UDT recorded",
          "no_analysis_jobs": "No analysis job"}
for i, (bench, left) in enumerate([("BixBench", 31), ("CompBioBench", 113)]):
    block = routes[routes.benchmark == bench]
    number = block.loc[block.route.isin(["udt_only", "udt_and_standard"]), "runs"].sum()
    x = 2 if i == 0 else 92
    p.heading(x, 52.7, "bc"[i], f"{bench} tool use in Galaxy")
    p.text(x + 4.2, 57.8, f"{100 * number / block.runs.sum():.1f}% of {block.runs.sum():,.0f} runs used a user-defined tool")
    ax = p.axes(left, 61.7, 59.5, 19.2)
    table = block.pivot(index="model", columns="route", values="runs_pct").reindex(MODELS).fillna(0)
    for y, (_, row) in enumerate(table.iterrows()):
        start = 0
        for route, color in palette.items():
            value = row.get(route, 0)
            if value:
                ax.barh(y, value, left=start, height=.55, color=color, hatch=hatches.get(route),
                        edgecolor=MUTED, linewidth=.35)
                start += value
    ax.set(xlim=(0, 100), xticks=[0, 25, 50, 75, 100], ylim=(3.5, -.5), yticks=range(4),
           yticklabels=MODELS if i == 0 else [])
    xgrid(ax)
handles = [Patch(facecolor=palette[k], hatch=hatches.get(k), edgecolor=MUTED, linewidth=.45,
                 label=labels[k]) for k in palette]
p.text(90, 89, "Galaxy runs per model (%)", ha="center", weight="bold")
p.fig.legend(handles=handles, loc="center", bbox_to_anchor=(.5, 1 - 94.4 / p.height), ncol=5,
             handlelength=1.5, columnspacing=1.7, handletextpad=.5)
p.line(3, 98.7, 177, 98.7)

p.heading(2, 103, "d", "Tracing one yeast RNA-seq result")
p.text(6.2, 108, "IWC workflow 002  ·  GPT-5.5  ·  Galaxy replicate 1", color=MUTED, fontsize=6.5)
version = check.tool_id.rsplit("/", 1)[-1]
steps = [(114.5, "Inputs", "Four prefiltered count tables"),
         (121.3, "Tool", f"DESeq2 wrapper {version}"),
         (128.1, "Output", f"Dataset {check.hid:.0f} with {check.run_genes:,.0f} genes")]
p.line(7.5, steps[0][0], 7.5, steps[-1][0], color=G, lw=.9)
for y, label, value in steps:
    p.mark(7.5, y, "o", G, "white")
    p.text(11, y, label, weight="bold")
    p.text(23, y, value)

p.heading(88, 103, "e", "Overlap of significant genes")
p.text(92.2, 108, "One column per gene at adjusted P < 0.05", fontsize=6.5)
shared = int(check.shared_significant)
agent_only = int(check.run_significant) - shared
reference_only = int(check.reference_significant) - shared
positions = range(shared + agent_only + reference_only)
x0, pitch = 118, 4
for y, label, count in [(114.5, "Agent", check.run_significant), (121.3, "Reference", check.reference_significant)]:
    p.text(92.2, y, f"{label} ({count:.0f})")
    for j in positions:
        both = j < shared
        agent = shared <= j < shared + agent_only
        if both or (agent == (label == "Agent")):
            p.mark(x0 + pitch * j, y, "o" if both else "s", G if both else INK, G if both else "white", 3.9)
p.line(x0, 124.3, x0 + (shared - 1) * pitch, 124.3, color=G, lw=.75)
p.text(x0 + (shared - 1) * pitch / 2, 128.1, f"{shared} shared", ha="center", weight="bold")
p.save(__file__)
