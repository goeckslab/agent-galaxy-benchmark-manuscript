"""Reference-based selection, exact answer voting and an independent sequence check."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from plot_style import BENCH, C, G, INK, MUTED, Plate, data, xgrid

source = data(__file__)
groups = source[source.panel == "repeatability"].set_index(["benchmark", "condition"])
case = source[source.panel == "promoter"].iloc[0]
p = Plate(116)
policies = [("Galaxy", G), ("custom code", C)]
rules = [("single_pct", "Single run", "o"), ("majority_pct", "≥2 of 3", "^"), ("any_correct_pct", "≥1 of 3", "s")]

p.heading(2, 3.7, "a", "Replicates meeting the benchmark criterion")
for x, (_, label, marker) in zip([108, 133, 156], rules):
    p.mark(x, 3.7, marker, INK, INK if marker == "o" else "white", size=4)
    p.text(x + 3, 3.7, label, fontsize=6.5)
p.text(4, 10, "Benchmark (groups per policy)", weight="bold", fontsize=6.5)
p.text(45, 10, "Policy", weight="bold", fontsize=6.5)
p.text(116, 10, "Meeting criterion (%)", ha="center", weight="bold")
p.text(174.5, 10, "Any pass", ha="right", weight="bold", fontsize=6.5)
ax = p.axes(70, 14, 90, 35)
criteria = ["Reviewed acceptance", "Reconstructed item match", "Output agreement ≥99%"]
for i, (bench, criterion) in enumerate(zip(BENCH, criteria)):
    y = 16.5 + 12.3 * i
    n = groups.loc[(bench, "Galaxy"), "groups"]
    p.text(4, y, f"{bench} ({n:.0f})", weight="bold")
    p.text(4, y + 4.9, criterion, color=MUTED, fontsize=6.5)
    for j, (cond, color) in enumerate(policies):
        row = y + 4.9 * j
        p.text(45, row, cond.capitalize())
        r = groups.loc[(bench, cond)]
        values = [r[field] for field, _, _ in rules]
        ax.hlines(row, min(values), max(values), color=color, lw=1.1, alpha=.65)
        for k, ((_, _, marker), value) in enumerate(zip(rules, values)):
            ax.plot(value, row + (k - 1) * .72, marker, ms=4, mec=color, mew=1,
                    mfc=color if k == 0 else "white", zorder=3)
        p.text(174.5, row, f"{r.any_correct_pct:.1f}%", ha="right", weight="bold")
ax.set(xlim=(64.5, 100.5), ylim=(49, 14), yticks=[], xticks=[65, 70, 75, 80, 85, 90, 95, 100])
xgrid(ax)

p.heading(2, 58.5, "b", "Outcome of an exact answer vote")
outcomes = [("vote_correct", "Pass", "#496679", None),
            ("vote_incorrect", "Fail", "#C3CFD6", "////"),
            ("vote_abstained", "Abstain", "white", None)]
for x, (_, label, color, hatch) in zip([111, 132, 151.5], outcomes):
    key = p.axes(x, 57.3, 4, 2.4)
    key.barh(0, 1, height=1, facecolor=color, edgecolor=MUTED, lw=.65, hatch=hatch)
    key.set(xlim=(0, 1), ylim=(-.5, .5))
    key.set_axis_off()
    p.text(x + 5.3, 58.5, label, fontsize=6.5)
ax = p.axes(70, 63, 90, 20.8)
p.text(174.5, 61.8, "Pass (%)", ha="right", weight="bold", fontsize=6.5)
for i, bench in enumerate(["BixBench", "CompBioBench"]):
    for j, (cond, _) in enumerate(policies):
        idx = 2 * i + j
        row_y = 65.6 + 5.2 * idx
        r = groups.loc[(bench, cond)]
        if j == 0:
            p.text(4, row_y, f"{bench} ({r.groups:.0f})", weight="bold")
        p.text(45, row_y, cond.capitalize())
        assert r.vote_ungraded == 0 and sum(r[field] for field, *_ in outcomes) == r.groups
        start = 0
        for field, _, color, hatch in outcomes:
            width = r[field + "_pct"]
            ax.barh(idx, width, left=start, height=.66, facecolor=color, edgecolor=MUTED, lw=.55, hatch=hatch)
            start += width
        p.text(174.5, row_y, f"{r.vote_correct_pct:.2f}", ha="right", weight="bold")
ax.set(xlim=(0, 100), ylim=(3.5, -.5), yticks=[], xticks=[0, 25, 50, 75, 100])
p.text(4, 88, "Each bar includes all groups, including abstentions.", fontsize=6.5)
p.text(115, 91.6, "Share of task–model groups (%)", ha="center", weight="bold", fontsize=6.5)

p.heading(2, 97, "c", "Independent check of promoter GC content in CompBioBench")
for x, title in [(4, "Submitted answers"), (56, "Reference interval (GRCh38)"), (131, "Reference sequence")]:
    p.text(x, 102.6, title, weight="bold")
p.text(4, 107.7, f"{case.answers_matching:.0f}/{case.answers_checked:.0f} answers agree")
p.text(4, 112.2, f"Reported GC fraction {case.reported_fraction:.2f}")
p.arrow(42, 108.7, 52, 108.7)
p.text(56, 107.7, f"{case.chromosome}:{case.interval_start:,.0f}–{case.interval_end:,.0f}")
p.text(56, 112.2, f"{case.transcript}  ·  minus strand", fontsize=6.5)
p.arrow(117, 108.7, 127, 108.7)
p.text(131, 107.7, f"{case.gc_bases:.0f} G/C bases in {case.bases:.0f} bp")
p.text(131, 112.2, f"{100 * case.gc_fraction:.2f}% GC (fraction {case.reported_fraction:.2f} rounded)", fontsize=6.5)
p.save(__file__)
