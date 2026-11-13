"""Task failures, answer selection and historical BixBench token ratios."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from plot_style import BENCH, C, G, INK, Plate, data, xgrid

d = data(__file__)
plate = Plate(132)
causes = d[d.panel == "failure_categories"]
assigned = causes[causes.audit_status == "Classified"].set_index(["failure_category", "condition"])
policies = [("Galaxy", G), ("custom code", C)]
plate.heading(2, 4, "a", "Primary causes of incorrect BixBench answers")
plate.text(6.2, 10, "Percent of incorrect runs under each policy", fontsize=6.5)
for x, (cond, color) in zip([6.2, 44.5], policies):
    total = causes.loc[causes.condition == cond, "runs"].sum()
    plate.box(x, 14, 3, 1.9, color)
    plate.text(x + 4.5, 14.95, f"{cond.capitalize()} (n = {total:.0f})", fontsize=6.5)
categories = ["Task or scoring ambiguity", "Missing validation", "Platform or harness", "Model knowledge"]
ax = plate.axes(38, 19.6, 36, 29.2)
for i, category in enumerate(categories):
    plate.text(4, 19.6 + (i + .5) * 7.3, category, weight="bold", fontsize=6.5)
    for j, (cond, color) in enumerate(policies):
        # A category with no run under a policy is a measured zero.
        pct, runs = (assigned.loc[(category, cond), ["pct_of_incorrect", "runs"]]
                     if (category, cond) in assigned.index else (0, 0))
        row = i + (-.20 if j == 0 else .20)
        ax.barh(row, pct, height=.29, facecolor=color)
        ax.annotate(f"{pct:.1f}% ({runs:.0f})", (pct, row),
                    xytext=(3, 0), textcoords="offset points", va="center", fontsize=6.5, weight="bold")
ax.set(xlim=(0, 100), ylim=(len(categories) - .5, -.5), yticks=[], xticks=[0, 50, 100])
xgrid(ax)
pending = causes[causes.audit_status != "Classified"].groupby("condition").runs.sum()
plate.text(4, 53.4, f"Cause unassigned in {pending['Galaxy']:.0f} Galaxy and {pending['custom code']:.0f} custom-code runs.",
           fontsize=6.5)
knowledge = assigned.loc["Model knowledge"]
plate.text(4, 59.2, f"Same model passed the same task in another attempt for "
           f"{knowledge.runs_with_another_pass.sum():.0f}/{knowledge.runs.sum():.0f} knowledge errors.", fontsize=6.5)

selection = d[d.panel == "answer_selection"].set_index(["benchmark", "condition"])
plate.heading(90, 4, "b", "Consensus and validation across benchmarks")
rules = [("single_pct", "Single run", "o"),
         ("majority_pct", "Majority of 3", "^"),
         ("any_correct_pct", "Correct once", "s")]
for x, (_, label, marker) in zip([94, 118, 147], rules):
    plate.mark(x, 10.4, marker, INK, INK if marker == "o" else "white", size=4.4)
    plate.text(x + 3, 10.4, label, fontsize=6.5)

ax = plate.axes(131.5, 14.6, 45, 36.8)
for i, bench in enumerate(BENCH):
    y = 17.3 + i * 13.2
    name = "BixBench-\nVerified-50" if bench == "BixBench" else bench
    plate.text(90.7, y + 2.8, name, weight="bold", fontsize=6.5, linespacing=1.04)
    for j, (cond, color) in enumerate([("Galaxy", G), ("custom code", C)]):
        row = y + j * 5.6
        plate.box(110.2, row - .95, 2.2, 1.9, color)
        plate.text(113.5, row, cond.capitalize(), fontsize=6.5)
        rates = selection.loc[(bench, cond)]
        values = [rates[field] for field, _, _ in rules]
        ax.hlines(row, min(values), max(values), color=color, lw=2.9, alpha=.32, zorder=2)
        # Small vertical offsets keep nearby estimates legible at their exact horizontal positions.
        for offset, value, (_, _, marker) in zip([-.65, .65, 0], values, rules):
            ax.plot(value, row + offset, marker, ms=4.2 if marker == "o" else 4.7,
                    mec=color, mfc=color if marker == "o" else "white", mew=1, zorder=3)
        ax.annotate(f"{rates.any_correct_pct:.1f}", (rates.any_correct_pct, row),
                    xytext=(4.1, 0), textcoords="offset points", va="center",
                    weight="bold", color=color, fontsize=6.5)
ax.set(yticks=[], ylim=(51.4, 14.6), xlim=(68, 102), xticks=[70, 75, 80, 85, 90, 95, 100],
       xlabel="Meeting benchmark criterion (%)")
xgrid(ax)

plate.line(2, 65.5, 178, 65.5)
plate.text(2, 70, "c", weight="bold")
plate.text(6.2, 70, "Galaxy-to-custom-code token ratio across development stages", weight="bold")
history = d[d.panel == "development_ratios"].copy()
steps = ["Baseline", "Prompt and skills", "MCP execution", "Compact replies", "Longer waits"]
positions = {name: i for i, name in enumerate(steps)}
history["x"] = history.stage.map(positions).astype(float)
styles = {
    "GPT-5.5": ("o", "#2A78D6"), "GPT-5.6 Sol": ("s", "#E34948"),
    "GPT-5.6 Luna": ("^", "#1BAF7A"), "DeepSeek V4 Pro": ("D", "#EDA100"),
}
for x, (model, (marker, color)) in zip([14, 40, 70, 102], styles.items()):
    plate.mark(x, 76.4, marker, color, color, size=5)
    plate.text(x + 3, 76.4, model, color="#1F2433")

# Offsets separate points at the same categorical stage, as on page 18.
history.loc[history.slug == "round1", "x"] -= .11
history.loc[history.slug == "round1-rerun", "x"] += .11
mcp_offsets = {"GPT-5.5": -.07, "GPT-5.6 Sol": .25, "GPT-5.6 Luna": -.26, "DeepSeek V4 Pro": .05}
at_mcp = history.stage == "MCP execution"
history.loc[at_mcp, "x"] += history.loc[at_mcp, "model"].map(mcp_offsets)
ax = plate.axes(13, 80.6, 164, 41)
ax.set_yscale("log")
ax.set_xlim(-.5, 4.5)
ax.set_ylim(.86, 34)
ax.axvspan(1.53, 2.47, color="#EEF2F7", lw=0, zorder=0)
ax.text(2, 29.4, "all four models", ha="center", va="center", fontsize=7, color="#6F6862")
for tick in [2, 5, 10, 20]:
    ax.axhline(tick, color="#E1E5EC", lw=.55, zorder=1)
ax.axhline(1, color="#B8732E", lw=1, ls=(0, (4, 3)), zorder=1)
ax.text(-.46, 1.04, "Custom code = 1×", ha="left", va="bottom", fontsize=7, color="#6F6862")

for model, (marker, color) in styles.items():
    series = history[history.model == model].sort_values("x")
    if model == "GPT-5.5":
        for i, linestyle in enumerate(["-", ":", "-"]):
            pair = series.iloc[i:i + 2]
            ax.plot(pair.x, pair.ratio, color=color, lw=1.1, ls=linestyle, zorder=2)
    elif model == "GPT-5.6 Sol":
        ax.plot(series.x, series.ratio, color=color, lw=1.1, zorder=2)
    ax.plot(series.x, series.ratio, marker=marker, ls="none", ms=5.6, mfc=color,
            mec="white", mew=.55, zorder=3)
    for r in series.itertuples():
        label = f"~{r.ratio:.0f}×" if r.evidence == "author estimate" else f"{r.ratio:.2f}×"
        below = model == "GPT-5.5" and r.slug in ("round1-rerun", "mcp_execution")
        dx, dy, ha = 0, (-2.8 if below else 3.3), "center"
        if r.slug == "mcp_execution" and model == "GPT-5.6 Sol":
            dx, dy, ha = 3, 2, "left"
        if model == "DeepSeek V4 Pro":
            dx, dy, ha = 0, 5.5, "center"
        if r.slug == "round1":
            dx, ha = -2, "right"
        ax.annotate(label, (r.x, r.ratio), xytext=(dx, dy), textcoords="offset points", ha=ha,
                    va="top" if below else "bottom", weight="bold", fontsize=7, color="#1F2433")
ax.set_yticks([1, 2, 5, 10, 20], labels=["1×", "2×", "5×", "10×", "20×"])
ax.set_xticks(range(len(steps)), labels=steps)
ax.set_ylabel("Galaxy / custom-code tokens", fontsize=7, fontweight="normal", labelpad=2, color="#555559")
ax.set_xlabel("Development stage", fontsize=7, labelpad=2, color="#555559")
ax.spines["bottom"].set_visible(False)
ax.minorticks_off()
ax.tick_params(axis="both", length=0, labelsize=7, pad=2, colors="#2E2E38")
plate.save(__file__)
