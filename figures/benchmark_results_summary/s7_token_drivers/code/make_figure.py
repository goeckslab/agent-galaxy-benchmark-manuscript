"""Where Galaxy runs spent tokens in the July 6 BixBench trace accounting, before the interface changes."""
from pathlib import Path
import sys

from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from plot_style import C, G, MUTED, Plate, data, xgrid

d = data(__file__)
G_LIGHT, C_LIGHT = "#A9CBCB", "#DDB3A0"
plate = Plate(119)
conds = [("Galaxy", G, G_LIGHT), ("custom code", C, C_LIGHT)]
names = {"Galaxy": "Galaxy", "custom code": "Custom code"}

# a: token classes. Output is under 1.4% of either total, so shares are printed rather than drawn.
cls = d[d.panel == "token_classes"].pivot(index="metric", columns="condition", values="value") / 1e6
share = d[d.panel == "token_classes"].pivot(index="metric", columns="condition", values="share_pct")
plate.heading(2, 4, "a", "Cached context dominated token use")
plate.text(6.2, 10, "BixBench, GPT-5.5, 150 runs per policy (July 6 batch)")
ax = plate.axes(26, 16, 54, 15)
for y, (cond, colour, light) in enumerate(conds):
    cached, uncached, output = (cls.loc[k, cond] for k in ("Cached input", "Uncached input", "Output"))
    ax.barh(y, cached, height=.5, color=colour, edgecolor="white", linewidth=.4)
    ax.barh(y, uncached + output, left=cached, height=.5, color=light, edgecolor="white", linewidth=.4)
    ax.text(cls.loc["Total", cond] + 7, y, f"{cls.loc['Total', cond]:.1f}M", va="center", fontsize=6.5, weight="bold")
    plate.text(6.2, 45 + 4.2 * y, names[cond], fontsize=6.5)
    for x, metric in [(44, "Cached input"), (64, "Uncached input"), (82, "Output")]:
        plate.text(x, 45 + 4.2 * y, f"{share.loc[metric, cond]:.1f}%", ha="right", fontsize=6.5)
ax.set(yticks=[0, 1], yticklabels=["Galaxy", "Custom code"], ylim=(1.5, -.5), xlim=(0, 520),
       xticks=[0, 100, 200, 300, 400, 500], xlabel="Total tokens (millions)")
xgrid(ax)
for x, label in [(44, "Cached"), (64, "Uncached"), (82, "Output")]:
    plate.text(x, 41, label, weight="bold", ha="right", fontsize=6.5)

# b: loop structure, one axis per measure (never a shared scale for different units).
loops = d[d.panel == "loops"].pivot(index="metric", columns="condition", values="value")
page_ratio = d[d.panel == "loops"].groupby("metric").page_ratio.first()
plate.heading(92, 4, "b", "More agent turns, each carrying more context")
plate.text(96.2, 10, "Circles, Galaxy  ·  squares, custom code  ·  ratios, Galaxy / custom code", fontsize=6.5)
rows = [("Agent loop steps per run", "Agent turns per run", 1, (0, 45), [0, 20, 40]),
        ("Shell commands per run", "Shell commands per run", 1, (0, 45), [0, 20, 40]),
        ("Cached input per loop step", "Cached input per turn (thousand tokens)", 1e3, (0, 85), [0, 40, 80])]
for i, (metric, label, scale, limits, ticks) in enumerate(rows):
    top = 15.5 + i * 12
    plate.text(96.2, top, label, fontsize=6.5)
    ax = plate.axes(96.2, top + 2.2, 62, 5.2)
    for cond, colour, _ in conds:
        value = loops.loc[metric, cond] / scale
        ax.plot(value, 0, "o" if cond == "Galaxy" else "s", ms=3.8, color=colour, zorder=3)
        ax.annotate(f"{value:.1f}", (value, 0), xytext=(0, 4.5), textcoords="offset points", ha="center", fontsize=6.5)
    ax.hlines(0, loops.loc[metric, "custom code"] / scale, loops.loc[metric, "Galaxy"] / scale, color=MUTED, lw=.6)
    plate.text(170, top + 4.8, f"{page_ratio[metric]:.2f}×", ha="center", weight="bold")
    ax.set(xlim=limits, xticks=ticks, yticks=[], ylim=(-1, 1.6))
    xgrid(ax)
plate.line(2, 54, 178, 54)

# c: what the commands did.
purpose = d[d.panel == "command_purpose"].pivot(index="metric", columns="condition", values="value")
order = ["Platform/API operations", "Payload, evidence, verification, and answer work", "Local input and task work",
         "Skill reads", "User-defined tool operations", "Other commands"]
short = ["Galaxy platform and API", "Payloads, checks and answer", "Local inputs and task code",
         "Reading skill guidance", "User-defined tool work", "Other"]
plate.heading(2, 58.5, "c", "What the agents' commands did")
plate.text(6.2, 64, "Shell commands by purpose across 150 runs per policy", fontsize=6.5)
ax = plate.axes(40, 69.5, 42, 36)
for y, key in enumerate(order):
    for offset, (cond, colour, _) in zip((-.23, .23), conds):
        count = purpose.loc[key, cond]
        ax.barh(y + offset, count, height=.36, color=colour)
        ax.text(count + 25, y + offset, f"{count:,.0f}", va="center", fontsize=6.5)
ax.set(yticks=range(len(order)), yticklabels=short, ylim=(len(order) - .4, -.6), xlim=(0, 2150),
       xticks=[0, 500, 1000, 1500, 2000], xticklabels=["0", "500", "1,000", "1,500", "2,000"], xlabel="Commands")
ax.legend(handles=[Patch(facecolor=G, label="Galaxy"), Patch(facecolor=C, label="Custom code")],
          loc="lower right", fontsize=6.5, handlelength=1, handleheight=.8, borderaxespad=.2)
xgrid(ax)

# d: skill guidance ablation within the same batch.
skills = d[d.panel == "skills"].copy()
plate.heading(92, 58.5, "d", "Token use and answer acceptance with skill guidance")
plate.text(96.2, 64, "Each row includes 150 runs", fontsize=6.5)
plate.text(170.5, 68.5, "Accepted", ha="center", weight="bold", fontsize=6.5)
ax = plate.axes(122.5, 71, 35, 33)
labels = []
for y, (cond, with_skills) in enumerate([("Galaxy", True), ("Galaxy", False), ("custom code", True), ("custom code", False)]):
    r = skills[(skills.condition == cond) & (skills.skills == with_skills)].iloc[0]
    colour = G if cond == "Galaxy" else C
    ax.plot(r.value / 1e6, y, "o" if cond == "Galaxy" else "s", ms=4, mfc=colour if with_skills else "white",
            mec=colour, mew=.9, zorder=3)
    ax.annotate(f"{r.value / 1e6:.1f}", (r.value / 1e6, y), xytext=(4, 0),
                textcoords="offset points", va="center", fontsize=6.5)
    plate.text(170.5, 71 + (y + .5) * 33 / 4, f"{r.accepted_pct:.1f}%", ha="center", weight="bold")
    labels.append(f"{names[cond]}, {'skills' if with_skills else 'no skills'}")
ax.set(yticks=range(4), yticklabels=labels, ylim=(3.5, -.5), xlim=(0, 630), xticks=[0, 200, 400, 600],
       xlabel="Total tokens (millions)")
xgrid(ax)
plate.save(__file__)
