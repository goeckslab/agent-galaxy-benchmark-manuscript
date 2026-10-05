#!/usr/bin/env python3
"""Figure 2: Galaxy matches agent performance with custom code.

The panels follow the argument of the section:
a, accuracy by model and condition (BixBench-Verified-50 and CompBioBench runs pooled): the conditions match;
b, replicate sets with all three runs correct, by benchmark and condition: Galaxy is at least as consistent;
c, accuracy by benchmark and model in the Galaxy condition, with replicate dots, pairwise tests and a model x benchmark
   ranking test;
d, the 15 most used installed Galaxy tools, as the share of each model's Galaxy runs.

Reads data/run_scores.csv, data/galaxy_traced_runs.csv and data/galaxy_tool_use.csv (written by
analysis/export_galaxy_benchmark_tables.py). Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples;
clusters are BixBench source capsules, otherwise tasks). P values come from paired cluster sign-flip randomization tests
(200,000 draws, or exact enumeration with at most 16 clusters).

Writes, next to this script: fig2_performance.pdf (vector, embedded TrueType fonts), fig2_performance.png (600 dpi,
RGB), fig2_performance.svg (editable text) and source_data.csv. Width 180 mm; Nature Portfolio artwork rules.
"""
import io
import itertools
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.font_manager import fontManager  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.text import Text  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
from PIL import Image  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG_NAME = HERE.name
DATA = HERE.parents[4] / "data"   # archived under supplement/figures/previous_versions/<date>/

# ---------------------------------------------------------------- style shared with the paper's other figures
# Okabe-Ito colours (Wong, B. Points of view: Color blindness. Nat. Methods 8, 441; 2011) for the two conditions:
# vermillion = custom code, blue = Galaxy, custom code always first. Models take Paul Tol's muted hues, which avoid
# the condition colours; adjacent pairs pass the deuteranopia/protanopia check (worst Delta E 13.3, OKLab x100) and
# the normal-vision floor (29.0).
CODE_T, GAL_T = "custom code", "Galaxy"           # track values in data/run_scores.csv
ENVS = [CODE_T, GAL_T]
ENV_COLOR = {CODE_T: "#D55E00", GAL_T: "#0072B2"}
ENV_LABEL = {CODE_T: "Custom code", GAL_T: "Galaxy"}
CFG = ["GPT-5.5", "GPT-5.6 Sol", "GPT-5.6 Luna", "DeepSeek V4 Pro"]
MODEL_COLOR = dict(zip(CFG, ["#117733", "#AA4499", "#999933", "#882255"]))
TICK = {"GPT-5.5": "GPT-5.5", "GPT-5.6 Sol": "GPT-5.6\nSol", "GPT-5.6 Luna": "GPT-5.6\nLuna",
        "DeepSeek V4 Pro": "DeepSeek\nV4 Pro"}
BENCH = ["BixBench-Verified-50", "CompBioBench", "IWC"]
BENCH_2L = {"BixBench-Verified-50": "BixBench-\nVerified-50", "CompBioBench": "CompBioBench", "IWC": "IWC"}
BIN = BENCH[:2]                                    # binary endpoints
INK, INK2, GRID = "#1a1a1a", "#555555", "#e4e3df"
# Arial as in Nature artwork; Liberation Sans is metric-compatible with it where Arial is not installed.
FONT = next((f for f in ("Arial", "Liberation Sans") if f in {e.name for e in fontManager.ttflist}), "DejaVu Sans")
plt.rcParams.update({
    "font.family": FONT, "font.size": 6, "axes.titlesize": 6, "axes.labelsize": 6,
    "xtick.labelsize": 5.5, "ytick.labelsize": 5.5, "legend.fontsize": 5.5, "legend.title_fontsize": 5.5,
    "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "xtick.major.size": 2, "ytick.major.size": 2, "xtick.major.pad": 1.5, "ytick.major.pad": 1.5,
    "lines.linewidth": 0.75, "patch.linewidth": 0.5, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK, "text.color": INK, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "legend.handlelength": 1.0,
    "legend.handletextpad": 0.4, "legend.columnspacing": 0.8, "legend.borderaxespad": 0.2,
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none", "savefig.dpi": 300,
    "axes.titleweight": "bold", "axes.titlepad": 3, "axes.labelpad": 2,
    "mathtext.fontset": "custom", "mathtext.rm": FONT, "mathtext.it": f"{FONT}:italic",  # italic P
    "mathtext.cal": FONT, "mathtext.bf": f"{FONT}:bold", "mathtext.sf": FONT,
})
W, MM = 180.0, 1 / 25.4

# ---------------------------------------------------------------- analysis settings
B, SEED = 20000, 20261002
B_PERM = 200000          # randomization draws; Monte Carlo error on a Holm-adjusted P near 0.05 is below 0.003
N_RANK_PERM = 100000     # permutations for the model x benchmark ranking test
# A replicate set counts as solved when all three runs are correct. IWC scores are continuous output agreement, so an
# IWC run counts as correct at >= 0.99 agreement: 172 of 216 IWC runs reach it, and set counts are the same at 0.98 and
# 0.99 (sensitivity at 0.95 and 1.0 is written to the source data).
CORRECT_AT = {"BixBench-Verified-50": 1.0, "CompBioBench": 1.0, "IWC": 0.99}
IWC_SENSITIVITY = (0.95, 1.0)
N_TOOLS = 15
TOOL_LABEL = {
    "toolshed.g2.bx.psu.edu/repos/iuc/filter_tabular/filter_tabular": "Filter tabular",
    "Cut1": "Cut columns",
    "toolshed.g2.bx.psu.edu/repos/iuc/datamash_ops/datamash_ops": "Datamash",
    "toolshed.g2.bx.psu.edu/repos/devteam/column_maker/Add_a_column1": "Compute column",
    "toolshed.g2.bx.psu.edu/repos/ufz/xlsx2tsv/xlsx2tsv": "XLSX to TSV",
    "Filter1": "Filter rows",
    "csv_to_tabular": "CSV to tabular",
    "Grep1": "Select lines",
    "toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem": "BWA-MEM",
    "toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_grep_tool": "Search text (grep)",
    "toolshed.g2.bx.psu.edu/repos/goeckslab/phykit_metrics/phykit_metrics": "PhyKIT metrics",
    "toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_sort_header_tool": "Sort with header",
    "toolshed.g2.bx.psu.edu/repos/iuc/anndata_inspect/anndata_inspect": "Inspect AnnData",
    "Grouping1": "Group",
    "join1": "Join datasets",
}
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- statistics
def holm(p):
    p = np.asarray(p, float)
    order, adj, run = np.argsort(p), np.empty(len(p)), 0.0
    for i, k in enumerate(order):
        run = max(run, (len(p) - i) * p[k])
        adj[k] = min(1.0, run)
    return adj


def signflip_p(cluster_diffs):
    """Two-sided paired randomization test: flip the sign of each cluster's summed difference."""
    d = np.asarray(cluster_diffs, float)
    if len(d) <= 16:  # enumerate every sign vector exactly
        signs = np.array(list(itertools.product([-1.0, 1.0], repeat=len(d))))
        return float(np.mean(np.abs(signs @ d) >= abs(d.sum()) - 1e-12))
    hits = 0
    for _ in range(B_PERM // 20000):
        null = rng.choice([-1.0, 1.0], size=(20000, len(d))) @ d
        hits += np.sum(np.abs(null) >= abs(d.sum()) - 1e-12)
    return (1 + hits) / (B_PERM + 1)


def boot_weights(n_clusters):
    return rng.multinomial(n_clusters, np.full(n_clusters, 1 / n_clusters), size=B)


def boot_means(frames, group_cols):
    """Pooled run means per group with cluster-bootstrap draws; clusters resampled within each benchmark."""
    point, num, den = None, 0.0, 0.0
    for _, d in frames.groupby("benchmark"):
        s = d.pivot_table(index="cluster", columns=group_cols, values="score", aggfunc="sum").fillna(0)
        n = d.pivot_table(index="cluster", columns=group_cols, values="score", aggfunc="count").fillna(0)
        wts = boot_weights(len(s))
        num = num + wts @ s.values
        den = den + wts @ n.values
        point = (s.sum(), n.sum()) if point is None else (point[0] + s.sum(), point[1] + n.sum())
    est = point[0] / point[1]
    return est, pd.DataFrame(num / den, columns=est.index)


def ci(draws):
    return np.percentile(draws, 2.5, axis=0), np.percentile(draws, 97.5, axis=0)


def load_runs():
    r = pd.read_csv(DATA / "run_scores.csv").rename(columns={"model": "cfg", "track": "env", "task_id": "task"})
    if r.empty:
        raise SystemExit(f"{DATA / 'run_scores.csv'} is empty; run analysis/export_galaxy_benchmark_tables.py first.")
    r["cluster"] = r.benchmark + ":" + r.cluster.astype(str)
    return r


def panel_a(r):
    d = r[r.benchmark.isin(BIN)]
    est, draws = boot_means(d, ["cfg", "env"])
    lo, hi = ci(draws)
    tab = pd.DataFrame({"value": est * 100, "lo": lo * 100, "hi": hi * 100}, index=est.index)
    tab["n"] = d.groupby(["cfg", "env"]).size()
    tests = []
    task = d.groupby(["cluster", "task", "cfg", "env"]).score.mean().unstack("env")
    for c in CFG:
        t = task.xs(c, level="cfg")
        diff = (t[GAL_T] - t[CODE_T]).groupby(level="cluster").sum()
        dd = (draws[(c, GAL_T)] - draws[(c, CODE_T)]) * 100
        tests.append(dict(cfg=c, diff=(est[(c, GAL_T)] - est[(c, CODE_T)]) * 100,
                          lo=np.percentile(dd, 2.5), hi=np.percentile(dd, 97.5), p=signflip_p(diff.values)))
    tests = pd.DataFrame(tests)
    tests["p_holm"] = holm(tests.p)
    return tab, tests


def solved_sets(r, thresholds):
    """One row per replicate set (task x model x condition): solved when all three runs reach the threshold."""
    r = r.assign(ok=r.score >= r.benchmark.map(thresholds) - 1e-9)
    return r.groupby(["benchmark", "cluster", "task", "cfg", "env"]).ok.all().unstack("env").astype(int)


def panel_b(r):
    sets = solved_sets(r, CORRECT_AT)
    rows, tests = [], []
    for bm in BENCH:
        d = sets.xs(bm, level="benchmark")
        for env in ENVS:
            rows.append(dict(benchmark=bm, env=env, value=int(d[env].sum()), n=len(d), threshold=CORRECT_AT[bm]))
        diff = (d[GAL_T] - d[CODE_T]).groupby(level="cluster").sum()
        tests.append(dict(benchmark=bm, diff=int(diff.sum()), p=signflip_p(diff.values)))
    tests = pd.DataFrame(tests)
    tests["p_holm"] = holm(tests.p)
    sens = []
    for thr in IWC_SENSITIVITY:
        d = solved_sets(r[r.benchmark == "IWC"], {"IWC": thr}).xs("IWC", level="benchmark")
        diff = (d[GAL_T] - d[CODE_T]).groupby(level="cluster").sum()
        sens.append(dict(threshold=thr, code=int(d[CODE_T].sum()), galaxy=int(d[GAL_T].sum()), n=len(d),
                         p=signflip_p(diff.values)))
    return pd.DataFrame(rows), tests, pd.DataFrame(sens)


def rank_interaction(g, benches):
    """Model x benchmark interaction on within-task model ranks (ties averaged, so binary accuracy and continuous IWC
    agreement are comparable). Statistic: task-weighted squared departure of each benchmark's mean model ranks from the
    overall mean ranks. Null: whole clusters (BixBench capsules, otherwise tasks) permuted between benchmarks."""
    t = g[g.benchmark.isin(benches)].groupby(["benchmark", "cluster", "task", "cfg"]).score.mean().unstack("cfg")[CFG]
    ranks = t.rank(axis=1, method="average").values - (len(CFG) + 1) / 2
    clusters = t.index.get_level_values("cluster")
    uniq, inv = np.unique(clusters, return_inverse=True)
    sums = np.zeros((len(uniq), len(CFG)))
    np.add.at(sums, inv, ranks)
    sizes = np.bincount(inv).astype(float)
    home = pd.Series(t.index.get_level_values("benchmark"), index=clusters).groupby(level=0).first().loc[uniq]
    home = np.asarray(home, dtype=str)
    overall = ranks.mean(0)

    def stat(labels):                       # labels: (k, clusters) array of benchmark names
        total = 0.0
        for b in benches:
            m = (labels == b).astype(float)
            n = m @ sizes
            total = total + n * (((m @ sums) / n[:, None] - overall) ** 2).sum(1)
        return total
    observed = stat(home[None, :])[0]
    hits = 0
    for _ in range(N_RANK_PERM // 10000):
        perm = np.array([rng.permutation(home) for _ in range(10000)])
        hits += np.sum(stat(perm) >= observed - 1e-12)
    return dict(benchmarks="+".join(benches), statistic=observed, p=(1 + hits) / (N_RANK_PERM + 1), clusters=len(uniq))


def panel_c(r):
    """Galaxy condition only. Bars and intervals use all Galaxy runs; reps holds each replicate's accuracy (dots)."""
    g = r[r.env == GAL_T]
    rows, tests = [], []
    for bm in BENCH:
        d = g[g.benchmark == bm]
        est, draws = boot_means(d, ["cfg"])
        lo, hi = ci(draws)
        for c, v, a, b in zip(est.index, est.values, lo, hi):
            rows.append(dict(benchmark=bm, cfg=c, value=v * 100, lo=a * 100, hi=b * 100,
                             n=int((d.cfg == c).sum()), tasks=d.task.nunique()))
        task = d.groupby(["cluster", "task", "cfg"]).score.mean().unstack("cfg")
        for a, b in itertools.combinations(CFG, 2):
            diff = (task[a] - task[b]).groupby(level="cluster").sum()
            tests.append(dict(benchmark=bm, a=a, b=b, diff=(est[a] - est[b]) * 100, p=signflip_p(diff.values)))
    tests = pd.DataFrame(tests)
    tests["p_holm"] = holm(tests.p)      # 18 comparisons: 6 model pairs in each of 3 benchmarks
    reps = g.groupby(["benchmark", "cfg", "replicate"]).score.agg(["mean", "size"]).reset_index()
    reps = reps.rename(columns={"mean": "value", "size": "n"}).assign(value=lambda x: x.value * 100)
    inter = pd.DataFrame([rank_interaction(g, BENCH), rank_interaction(g, BIN)])
    return pd.DataFrame(rows), tests, reps, inter


def panel_d():
    runs = pd.read_csv(DATA / "galaxy_traced_runs.csv").groupby("model").size()
    use = pd.read_csv(DATA / "galaxy_tool_use.csv")
    installed = use[use.kind == "installed"]
    overall = installed.groupby("tool_id").size().sort_values(ascending=False, kind="stable") / runs.sum() * 100
    top = overall.head(N_TOOLS)
    missing = set(top.index) - set(TOOL_LABEL)
    assert not missing, f"add display names for {missing}"
    per = (installed.groupby(["tool_id", "model"]).size().unstack(fill_value=0) / runs * 100).loc[top.index, CFG]
    udt = use[use.kind == "udt"].groupby("model").size() / runs * 100
    return top, per, udt.reindex(CFG), runs.reindex(CFG)


# ---------------------------------------------------------------- drawing helpers
def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight="bold", va="top", ha="left")
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight="bold", va="top", ha="left")


def grid(ax, axis):
    getattr(ax, f"{axis}axis").grid(True, color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)


def pct_axis(ax, top=100):
    ax.set_ylim(0, top * 1.16)
    ax.set_yticks(np.arange(0, top + 1, top / 4))
    ax.spines["left"].set_bounds(0, top)
    grid(ax, "y")


def errbars(ax, x, v, lo, hi):
    ax.errorbar(x, v, yerr=[np.asarray(v) - lo, np.asarray(hi) - v], fmt="none", ecolor=INK, elinewidth=0.6,
                capsize=1.4, capthick=0.6, zorder=4)


def bracket(ax, x0, x1, y, text, h=1.6):
    ax.plot([x0, x0, x1, x1], [y, y + h, y + h, y], color=INK, lw=0.5, zorder=4, clip_on=False)
    ax.text((x0 + x1) / 2, y + h + 0.8, text, ha="center", va="bottom", fontsize=5, color=INK, clip_on=False)


def fmt_p(p):
    return r"$\mathit{P}$ < 0.001" if p < 0.001 else rf"$\mathit{{P}}$ = {p:.2f}" if p >= 0.01 else \
        rf"$\mathit{{P}}$ = {p:.3f}"


def env_legend(ax, y=1.02):
    ax.legend(handles=[Patch(fc=ENV_COLOR[e], label=ENV_LABEL[e]) for e in ENVS], ncol=2, loc="lower left",
              bbox_to_anchor=(0.0, y), fontsize=5.5, handlelength=1.0, columnspacing=1.2, borderaxespad=0)


def enforce_min_font(fig, minimum=5.0):
    """Nature requires 5-7 pt text at final size; raise any smaller text to the floor."""
    for t in fig.findobj(Text):
        if t.get_text() and t.get_fontsize() < minimum:
            t.set_fontsize(minimum)


# ---------------------------------------------------------------- panels
def draw_a(fig, H, tab, tests):
    label(fig, 0, 0, "a", "Overall accuracy by model", H)
    ax = axes_mm(fig, 10.0, 10.5, 72.0, 39.0, H)
    wd = 0.36
    for k, env in enumerate(ENVS):
        xs = np.arange(len(CFG)) + (k - 0.5) * (wd + 0.04)
        t = tab.xs(env, level="env").loc[CFG]
        ax.bar(xs, t.value, width=wd, color=ENV_COLOR[env], zorder=3)
        errbars(ax, xs, t.value.values, t.lo.values, t.hi.values)
    pct_axis(ax)
    for i, c in enumerate(CFG):
        top = tab.loc[c].hi.max()
        p = tests.set_index("cfg").loc[c, "p_holm"]
        bracket(ax, i - 0.2, i + 0.2, top + 2.5, "n.s." if p >= 0.05 else fmt_p(p))
    ax.set_xticks(range(len(CFG)), [TICK[c] for c in CFG])
    ax.tick_params(axis="x", length=0, pad=2)
    ax.set_ylabel("Accuracy (%)")
    ax.set_xlim(-0.6, len(CFG) - 0.4)
    env_legend(ax)
    n = int(tab.n.iloc[0])
    ax.text(1.0, 1.035, f"{n} runs per bar", transform=ax.transAxes, ha="right", va="bottom", fontsize=5,
            color=INK2)


def draw_b(fig, H, tab, tests):
    label(fig, 92.0, 0, "b", "Replicate sets with 3/3 correct", H)
    ax = axes_mm(fig, 102.0, 10.5, 77.0, 39.0, H)
    wd = 0.34
    for k, env in enumerate(ENVS):
        t = tab[tab.env == env].set_index("benchmark").loc[BENCH]
        xs = np.arange(len(BENCH)) + (k - 0.5) * (wd + 0.04)
        pct = 100 * t.value / t.n
        ax.bar(xs, pct, width=wd, color=ENV_COLOR[env], zorder=3)
        for x, v, c in zip(xs, pct, t.value):
            ax.text(x, v + 1.2, f"{c}", ha="center", va="bottom", fontsize=5, color=INK)
    pct_axis(ax)
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for i, bm in enumerate(BENCH):
        t = tab[tab.benchmark == bm]
        n = int(t.n.iloc[0])
        sub = f"{n} sets" + (f" · runs ≥ {CORRECT_AT[bm]:.2f}" if bm == "IWC" else "")
        ax.text(i, -0.175, sub, transform=tr, ha="center", va="top", fontsize=5, color=INK2)
        p = tests.set_index("benchmark").loc[bm, "p_holm"]
        bracket(ax, i - 0.19, i + 0.19, (100 * t.value / t.n).max() + 7.0, fmt_p(p))
    ax.set_xticks(range(len(BENCH)), [BENCH_2L[b] for b in BENCH])
    ax.tick_params(axis="x", length=0, pad=2)
    ax.set_xlim(-0.55, len(BENCH) - 0.45)
    ax.set_ylabel("Replicate sets solved (%)")
    env_legend(ax)


def draw_c(fig, H, y0, tab, tests, reps):
    label(fig, 0, y0, "c", "Accuracy by benchmark and model in Galaxy", H)
    ax = axes_mm(fig, 10.0, y0 + 15.0, 57.0, 40.0, H)
    wd, gap = 0.19, 0.015
    offs = (np.arange(len(CFG)) - 1.5) * (wd + gap)
    xpos = {}
    for j, c in enumerate(CFG):
        t = tab[tab.cfg == c].set_index("benchmark").loc[BENCH]
        xs = np.arange(len(BENCH)) + offs[j]
        xpos.update({(bm, c): x for bm, x in zip(BENCH, xs)})
        ax.bar(xs, t.value, width=wd, color=MODEL_COLOR[c], zorder=3, label=c)
        errbars(ax, xs, t.value.values, t.lo.values, t.hi.values)
        for bm, x in zip(BENCH, xs):   # replicate dots, spread across the bar so they clear the error bar
            v = reps[(reps.benchmark == bm) & (reps.cfg == c)].sort_values("replicate").value.values
            ax.plot(x + np.array([-0.055, 0.0, 0.055])[:len(v)], v, ls="", marker="o", ms=2.0, mfc="white",
                    mec=INK, mew=0.5, zorder=5)
    pct_axis(ax)
    sig = tests[tests.p_holm < 0.05].sort_values(["benchmark", "p_holm"])
    for bm, g in sig.groupby("benchmark"):
        top = tab[tab.benchmark == bm].hi.max()
        for k, row in enumerate(g.sort_values("diff").itertuples()):
            x0, x1 = sorted((xpos[(bm, row.a)], xpos[(bm, row.b)]))
            bracket(ax, x0, x1, top + 2.5 + k * 9.5, fmt_p(row.p_holm))
    ax.set_xticks(range(len(BENCH)), [BENCH_2L[b] for b in BENCH])
    ax.tick_params(axis="x", length=0, pad=2)
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for i, bm in enumerate(BENCH):
        ntask = int(tab[tab.benchmark == bm].tasks.iloc[0])
        sub = f"{ntask} tasks" + ("\noutput agreement" if bm == "IWC" else "")
        ax.text(i, -0.175, sub, transform=tr, ha="center", va="top", fontsize=5, color=INK2, linespacing=1.1)
    ax.set_ylabel("Accuracy (%)")
    ax.set_xlim(-0.55, len(BENCH) - 0.45)
    models = ax.legend(ncol=2, loc="lower left", bbox_to_anchor=(0.0, 1.02), fontsize=5.5, handlelength=1.0,
                       columnspacing=1.0, labelspacing=0.3, borderaxespad=0)
    ax.add_artist(models)
    dot = Line2D([], [], ls="", marker="o", ms=2.0, mfc="white", mec=INK, mew=0.5)
    ax.legend(handles=[dot], labels=["Replicate"], loc="lower right", bbox_to_anchor=(1.0, 1.02), fontsize=5.5,
              handlelength=0.8, handletextpad=0.3, borderaxespad=0)


def draw_d(fig, H, y0, top, per, udt, runs):
    x_lab = 70.0
    label(fig, x_lab, y0, "d", f"{N_TOOLS} most used Galaxy tools", H)
    x0, pw, gap = 96.5, 19.0, 2.2
    ytop, h = y0 + 16.0, 43.0
    labels = [TOOL_LABEL[t] for t in top.index]
    for j, c in enumerate(CFG):
        ax = axes_mm(fig, x0 + j * (pw + gap), ytop, pw, h, H)
        ax.barh(range(N_TOOLS), per[c].values, height=0.68, color=MODEL_COLOR[c], zorder=3)
        ax.set_ylim(N_TOOLS - 0.5, -0.5)
        ax.set_xlim(0, 25)
        ax.set_xticks([0, 10, 20])
        grid(ax, "x")
        ax.tick_params(axis="y", length=0)
        if j == 0:
            ax.set_yticks(range(N_TOOLS), labels)
            rank_x = -(x0 - x_lab - 1.2) / pw
            tr = blended_transform_factory(ax.transAxes, ax.transData)
            ax.text(rank_x, -1.25, "Rank", transform=tr, ha="left", va="center", fontsize=5, color=INK2)
            for i in range(N_TOOLS):
                ax.text(rank_x + 0.08, i, f"{i + 1}", transform=tr, ha="center", va="center", fontsize=5.5,
                        color=INK2)
        else:
            ax.set_yticks(range(N_TOOLS), [""] * N_TOOLS)
            ax.spines["left"].set_visible(False)
        ax.set_title(c, fontsize=5.5, fontweight="bold", pad=8.5, loc="left")
        ax.text(0, 1.018, f"UDTs in {udt[c]:.0f}% of runs", transform=ax.transAxes, ha="left", va="bottom",
                fontsize=5, color=INK2)
        if j == 1:
            ax.text(1 + gap / pw / 2, -0.115, "Galaxy runs using the tool (%)", transform=ax.transAxes,
                    ha="center", va="top", fontsize=6)
    fig.text((x_lab + 4.4) / W, 1 - (y0 + 4.6) / H, f"Galaxy condition; {int(runs.min())}–{int(runs.max())} runs "
             "per model", fontsize=5, color=INK2, va="top")


# ---------------------------------------------------------------- source data and assembly
def source_data(a_tab, a_t, b_tab, b_t, b_sens, c_tab, c_t, c_reps, c_int, top, per, udt, runs):
    rows = []
    for (c, env), r in a_tab.iterrows():
        rows.append(dict(panel="a", benchmark="BixBench-Verified-50+CompBioBench", model=c, condition=env,
                         measure="accuracy_pct", value=r.value, ci95_low=r.lo, ci95_high=r.hi, n=int(r.n)))
    for r in a_t.itertuples():
        rows.append(dict(panel="a", benchmark="BixBench-Verified-50+CompBioBench", model=r.cfg,
                         condition="Galaxy - custom code", measure="difference_pct_points", value=r.diff,
                         ci95_low=r.lo, ci95_high=r.hi, p=r.p, p_holm=r.p_holm))
    for r in b_tab.itertuples():
        rows.append(dict(panel="b", benchmark=r.benchmark, model="all four", condition=r.env,
                         measure=f"sets_all_three_runs_at_least_{r.threshold:g}", value=r.value, n=r.n))
    for r in b_t.itertuples():
        rows.append(dict(panel="b", benchmark=r.benchmark, model="all four", condition="Galaxy - custom code",
                         measure="difference_sets", value=r.diff, p=r.p, p_holm=r.p_holm))
    for r in b_sens.itertuples():
        for env, v in ((CODE_T, r.code), (GAL_T, r.galaxy)):
            rows.append(dict(panel="b (sensitivity)", benchmark="IWC", model="all four", condition=env,
                             measure=f"sets_all_three_runs_at_least_{r.threshold:g}", value=v, n=r.n))
        rows.append(dict(panel="b (sensitivity)", benchmark="IWC", model="all four", condition="Galaxy - custom code",
                         measure=f"difference_sets_at_least_{r.threshold:g}", value=r.galaxy - r.code, p=r.p))
    endpoint = {"IWC": "output_agreement_x100"}
    for r in c_tab.itertuples():
        rows.append(dict(panel="c", benchmark=r.benchmark, model=r.cfg, condition=GAL_T,
                         measure=endpoint.get(r.benchmark, "accuracy_pct"), value=r.value, ci95_low=r.lo,
                         ci95_high=r.hi, n=r.n))
    for r in c_reps.itertuples():
        rows.append(dict(panel="c", benchmark=r.benchmark, model=r.cfg, condition=GAL_T, replicate=r.replicate,
                         measure=endpoint.get(r.benchmark, "accuracy_pct") + "_replicate", value=r.value, n=r.n))
    for r in c_t.itertuples():
        rows.append(dict(panel="c", benchmark=r.benchmark, model=f"{r.a} - {r.b}", condition=GAL_T,
                         measure="difference_points", value=r.diff, p=r.p, p_holm=r.p_holm))
    for r in c_int.itertuples():
        rows.append(dict(panel="c", benchmark=r.benchmarks, model="all four", condition=GAL_T,
                         measure="model_x_benchmark_rank_interaction", value=r.statistic, n=r.clusters, p=r.p))
    for rank, t in enumerate(top.index, 1):
        rows.append(dict(panel="d", benchmark="all", model="all four", condition=GAL_T, measure="pct_runs_using_tool",
                         value=top[t], n=int(runs.sum()), tool_rank=rank, tool_id=t, tool_label=TOOL_LABEL[t]))
        for c in CFG:
            rows.append(dict(panel="d", benchmark="all", model=c, condition=GAL_T, measure="pct_runs_using_tool",
                             value=per.loc[t, c], n=int(runs[c]), tool_rank=rank, tool_id=t,
                             tool_label=TOOL_LABEL[t]))
    for c in CFG:
        rows.append(dict(panel="d", benchmark="all", model=c, condition=GAL_T, measure="pct_runs_with_udt_call",
                         value=udt[c], n=int(runs[c])))
    cols = ["panel", "benchmark", "model", "condition", "replicate", "measure", "value", "ci95_low", "ci95_high", "n",
            "p", "p_holm", "tool_rank", "tool_id", "tool_label"]
    pd.DataFrame(rows).reindex(columns=cols).round(4).to_csv(HERE / "source_data.csv", index=False)


def main() -> None:
    r = load_runs()
    a_tab, a_t = panel_a(r)
    b_tab, b_t, b_sens = panel_b(r)
    c_tab, c_t, c_reps, c_int = panel_c(r)
    top, per, udt, runs = panel_d()
    for name, t in (("a: Galaxy - custom code by model (BixBench + CompBio)", a_t),
                    ("b: 3/3 sets, Galaxy - custom code", b_t), ("b: IWC threshold sensitivity", b_sens),
                    ("c: model pairs, Galaxy condition", c_t), ("c: model x benchmark ranking test", c_int)):
        print(name)
        print(t.round(4).to_string(index=False))

    H = 132.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    draw_a(fig, H, a_tab, a_t)
    draw_b(fig, H, b_tab, b_t)
    y2 = 66.0
    draw_c(fig, H, y2, c_tab, c_t, c_reps)
    draw_d(fig, H, y2, top, per, udt, runs)
    enforce_min_font(fig)
    title = "Fig. 2 | Galaxy matches agent performance with custom code"
    fig.savefig(HERE / f"{FIG_NAME}.svg", metadata={"Title": title})
    fig.savefig(HERE / f"{FIG_NAME}.pdf", metadata={"Title": title})
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=600, facecolor="white")
    Image.open(buf).convert("RGB").save(HERE / f"{FIG_NAME}.png", dpi=(600, 600))
    source_data(a_tab, a_t, b_tab, b_t, b_sens, c_tab, c_t, c_reps, c_int, top, per, udt, runs)


if __name__ == "__main__":
    main()
