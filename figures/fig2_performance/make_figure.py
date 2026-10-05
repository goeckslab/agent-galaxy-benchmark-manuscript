#!/usr/bin/env python3
"""Figure 2: Agents maintain bioinformatics accuracy when operating through Galaxy.

The panels answer the questions of Results section 1 of the outline:
a, accuracy by benchmark, model and condition, with each replicate as a dot;
b, Galaxy minus custom code by benchmark (runs correct; replicate sets with all three runs correct): is performance
   higher or more consistent on the Galaxy-derived IWC tasks;
c, correct runs of three for each task and model, custom code against Galaxy: why performance is preserved and where
   the conditions disagree;
d, primary cause of each incorrect BixBench-Verified-50 run, by how many runs of its set were incorrect.

A run is correct when accepted (BixBench-Verified-50, CompBioBench) or at >= 0.99 IWC output agreement; panel a shows
IWC as mean agreement. Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are
BixBench source capsules, otherwise tasks). P values come from paired cluster sign-flip randomization tests (200,000
draws, or exact enumeration with at most 16 clusters), Holm-adjusted within each panel.

Reads data/run_scores.csv and data/bixbench_failure_causes.csv (written by analysis/export_galaxy_benchmark_tables.py).
Writes, next to this script, the figure as PDF (vector, TrueType fonts), PNG (600 dpi, RGB) and SVG (editable text),
and source_data.csv. Width 180 mm; Nature Portfolio artwork rules.
"""
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.font_manager import fontManager  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from matplotlib.text import Text  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
from PIL import Image  # noqa: E402

import itertools  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402
HERE = Path(__file__).resolve().parent
FIG_NAME = HERE.name
DATA = HERE.parents[1] / "data"

# ---------------------------------------------------------------- style shared with the paper's other figures
# Okabe-Ito colours (Wong, B. Points of view: Color blindness. Nat. Methods 8, 441; 2011) for the two conditions:
# vermillion = custom code, blue = Galaxy, custom code always first; markers repeat it (square, circle).
OI_ORANGE, OI_SKY, OI_GREEN, OI_YELLOW = '#E69F00', '#56B4E9', '#009E73', '#F0E442'
OI_BLUE, OI_VERMILLION, OI_PURPLE = '#0072B2', '#D55E00', '#CC79A7'
CODE_COLOR, GALAXY = OI_VERMILLION, OI_BLUE
ENVS = ['custom_code', 'galaxy']
ENV_COLOR = {'custom_code': CODE_COLOR, 'galaxy': GALAXY}
ENV_TINT = {'custom_code': '#F6DCCB', 'galaxy': '#CFE3F1'}
ENV_MARKER = {'custom_code': 's', 'galaxy': 'o'}
ENV_LABEL = {'custom_code': 'Custom code', 'galaxy': 'Galaxy'}
CONFIGS = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro']
INK, INK2, GRID = '#1a1a1a', '#555555', '#e4e3df'
NEUTRAL_LIGHT, NEUTRAL_MID, NEUTRAL_DARK = '#DDDDDD', '#999999', '#555555'
# Arial as in Nature artwork; Liberation Sans is metric-compatible with it where Arial is not installed.
FONT = next((f for f in ('Arial', 'Liberation Sans') if f in {e.name for e in fontManager.ttflist}), 'DejaVu Sans')
plt.rcParams.update({
    'font.family': FONT, 'font.size': 6, 'axes.titlesize': 6, 'axes.labelsize': 6,
    'xtick.labelsize': 5.5, 'ytick.labelsize': 5.5, 'legend.fontsize': 5.5, 'legend.title_fontsize': 5.5,
    'axes.linewidth': 0.5, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
    'xtick.major.size': 2, 'ytick.major.size': 2, 'xtick.major.pad': 1.5, 'ytick.major.pad': 1.5,
    'lines.linewidth': 0.75, 'patch.linewidth': 0.5, 'axes.edgecolor': INK2, 'axes.labelcolor': INK,
    'xtick.color': INK2, 'ytick.color': INK, 'text.color': INK, 'axes.spines.top': False,
    'axes.spines.right': False, 'legend.frameon': False, 'legend.handlelength': 1.0,
    'legend.handletextpad': 0.4, 'legend.columnspacing': 0.8, 'legend.borderaxespad': 0.2,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none', 'savefig.dpi': 300,
    'axes.titleweight': 'bold', 'axes.titlepad': 3, 'axes.labelpad': 2,
    'mathtext.fontset': 'custom', 'mathtext.rm': FONT, 'mathtext.it': f'{FONT}:italic',  # italic P
    'mathtext.cal': FONT, 'mathtext.bf': f'{FONT}:bold', 'mathtext.sf': FONT,
})


def grid_y(ax):
    ax.yaxis.grid(True, color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)


def grid_x(ax):
    ax.xaxis.grid(True, color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)


def enforce_min_font(fig, minimum=5.0):
    """Nature requires 5-7 pt text at final size; raise any smaller text to the floor."""
    for t in fig.findobj(Text):
        if t.get_text() and t.get_fontsize() < minimum:
            t.set_fontsize(minimum)


# Tables in data/ use display names; the analysis code keys benchmarks and conditions as below.
BENCH_KEY = {'BixBench-Verified-50': 'BixBench50', 'CompBioBench': 'CompBio', 'IWC': 'IWC'}
TRACK_KEY = {'custom code': 'custom_code', 'Galaxy': 'galaxy'}


def read_runs_table(name):
    t = pd.read_csv(DATA / name)
    if t.empty:
        raise SystemExit(f'{DATA / name} is empty; run analysis/export_galaxy_benchmark_tables.py first.')
    t = t.assign(benchmark=t.benchmark.map(BENCH_KEY)).rename(columns={'task_id': 'task', 'model': 'cfg'})
    if 'track' in t:
        t = t.assign(env=t.track.map(TRACK_KEY)).drop(columns='track')
    return t

BENCH = ['BixBench50', 'CompBio', 'IWC']

B, SEED = 20000, 20261002
B_PERM = 200000          # randomization draws; Monte Carlo error on a Holm-adjusted P near 0.05 is below 0.003
W, MM = 180.0, 1 / 25.4
CFG = CONFIGS
ENVS = ENVS                                    # custom code first, always
CODE, GAL = ENVS
BENCH = BENCH
TICK = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6\nSol', 'GPT-5.6 Luna': 'GPT-5.6\nLuna',
        'DeepSeek V4 Pro': 'DeepSeek\nV4 Pro'}
BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
# A run is correct when accepted; an IWC run when it reaches >= 0.99 output agreement (172 of 216 IWC runs), the rule
# used for replicate sets in every figure.
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
# Panel d: every scored-incorrect BixBench-Verified-50 run has one primary cause in the run-level failure ledger.
CAUSE_OF = {'RIGOR': 'No answer validation', 'KNOWLEDGE': 'Lacking biological knowledge',
            'PLATFORM': 'Not able to use Galaxy', 'HARNESS': 'No answer submitted',
            'SPEC': 'Benchmark specification or scoring', 'EVALUATOR': 'Benchmark specification or scoring',
            'CONTRACT': 'Benchmark specification or scoring'}
CAUSES = ['No answer validation', 'Lacking biological knowledge', 'Not able to use Galaxy', 'No answer submitted',
          'Benchmark specification or scoring']
CAUSE_COLOR = dict(zip(CAUSES, [NEUTRAL_DARK, OI_YELLOW, OI_PURPLE, NEUTRAL_LIGHT,
                                OI_GREEN]))
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


def boot_means(frames, group_cols, value='score'):
    """Pooled means per group with cluster-bootstrap draws; clusters resampled within each benchmark."""
    point, num, den = None, 0.0, 0.0
    for _, d in frames.groupby('benchmark'):
        s = d.pivot_table(index='cluster', columns=group_cols, values=value, aggfunc='sum').fillna(0)
        n = d.pivot_table(index='cluster', columns=group_cols, values=value, aggfunc='count').fillna(0)
        wts = rng.multinomial(len(s), np.full(len(s), 1 / len(s)), size=B)
        num = num + wts @ s.values
        den = den + wts @ n.values
        point = (s.sum(), n.sum()) if point is None else (point[0] + s.sum(), point[1] + n.sum())
    est = point[0] / point[1]
    return est, pd.DataFrame(num / den, columns=est.index)


def ci(draws):
    return np.percentile(draws, 2.5, axis=0), np.percentile(draws, 97.5, axis=0)


# ---------------------------------------------------------------- data
def load_runs():
    r = read_runs_table('run_scores.csv')
    r['cluster'] = r.benchmark + ':' + r.cluster.astype(str)
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    return r


def replicate_sets(r):
    """One row per task x model x condition: correct runs of three."""
    return r.groupby(['benchmark', 'cluster', 'task', 'cfg', 'env']).ok.sum().rename('n_correct').reset_index()


def load_ledger(r):
    """Run-level failure-audit codes of every incorrect BixBench-Verified-50 run (data/bixbench_failure_causes.csv)."""
    led = read_runs_table('bixbench_failure_causes.csv').rename(columns={'primary_cause': 'p', 'secondary_cause': 's'})
    led['s'] = led.s.fillna('-')
    led['cause'] = led.p.map(CAUSE_OF)
    wrong = r[(r.benchmark == 'BixBench50') & (r.ok == 0)]
    key = ['task', 'cfg', 'env', 'replicate']
    j = wrong.merge(led[key + ['p', 's', 'cause']], on=key, how='outer', indicator=True)
    assert (j._merge == 'both').all() and not led.duplicated(key).any(), 'the audit must label every incorrect run once'
    return j.drop(columns='_merge')


# ---------------------------------------------------------------- panels: statistics
def panel_a(r):
    """Mean score per benchmark, model and condition (IWC: output agreement), with each replicate's mean."""
    rows, tests = [], []
    for bm in BENCH:
        d = r[r.benchmark == bm]
        est, draws = boot_means(d, ['cfg', 'env'])
        lo, hi = ci(draws)
        for (c, env), v, a, b in zip(est.index, est.values, lo, hi):
            rows.append(dict(benchmark=bm, cfg=c, env=env, value=v * 100, lo=a * 100, hi=b * 100,
                             n=int(((d.cfg == c) & (d.env == env)).sum()), tasks=d.task.nunique()))
        task = d.groupby(['cluster', 'task', 'cfg', 'env']).score.mean().unstack('env')
        for c in CFG:
            t = task.xs(c, level='cfg')
            diff = (t[GAL] - t[CODE]).groupby(level='cluster').sum()
            dd = (draws[(c, GAL)] - draws[(c, CODE)]) * 100
            tests.append(dict(benchmark=bm, cfg=c, diff=(est[(c, GAL)] - est[(c, CODE)]) * 100,
                              lo=np.percentile(dd, 2.5), hi=np.percentile(dd, 97.5), p=signflip_p(diff.values)))
    tests = pd.DataFrame(tests)
    tests['p_holm'] = holm(tests.p)      # 12 comparisons: 4 models in each of 3 benchmarks
    reps = r.groupby(['benchmark', 'cfg', 'env', 'replicate']).score.agg(['mean', 'size']).reset_index()
    reps = reps.rename(columns={'mean': 'value', 'size': 'n'}).assign(value=lambda x: x.value * 100)
    return pd.DataFrame(rows), tests, reps


def panel_b(r, sets):
    """Galaxy minus custom code by benchmark, models pooled: runs correct, and replicate sets with 3/3 correct."""
    s = sets.assign(solved=(sets.n_correct == 3).astype(int))
    out = []
    for measure, frame, col in (('runs_correct', r, 'ok'), ('sets_all_three_correct', s, 'solved')):
        for bm in BENCH:
            d = frame[frame.benchmark == bm]
            est, draws = boot_means(d, ['env'], value=col)
            dd = (draws[GAL] - draws[CODE]) * 100
            cell = d.groupby(['cluster', 'task', 'cfg', 'env'])[col].mean().unstack('env')
            diff = (cell[GAL] - cell[CODE]).groupby(level='cluster').sum()
            out.append(dict(measure=measure, benchmark=bm, code=est[CODE] * 100, galaxy=est[GAL] * 100,
                            diff=(est[GAL] - est[CODE]) * 100, lo=np.percentile(dd, 2.5), hi=np.percentile(dd, 97.5),
                            p=signflip_p(diff.values), clusters=len(diff)))
    out = pd.DataFrame(out)
    out['p_holm'] = holm(out.p)          # 6 comparisons: 2 measures in each of 3 benchmarks
    return out


def panel_c(sets):
    """Correct runs of three in custom code against Galaxy, one count per task x model."""
    pair = sets.pivot_table(index=['benchmark', 'task', 'cfg'], columns='env', values='n_correct').dropna().astype(int)
    grid = pd.crosstab(pair[GAL], pair[CODE]).reindex(index=range(4), columns=range(4), fill_value=0)
    by_bench = pair.reset_index().groupby(['benchmark', GAL, CODE]).size().rename('cells').reset_index()
    return grid, by_bench, len(pair)


def panel_d(ledger):
    sets_wrong = ledger.groupby(['task', 'cfg', 'env']).replicate.transform('size')   # incorrect runs in the set
    lg = ledger.assign(n_wrong=sets_wrong)
    tab = lg.groupby(['n_wrong', 'env', 'cause']).size().unstack('cause', fill_value=0).reindex(columns=CAUSES,
                                                                                               fill_value=0)
    secondary = lg[(lg.p == 'SPEC') & (lg.s == 'RIGOR')].shape[0], lg[lg.p == 'SPEC'].shape[0]
    return tab, secondary


# ---------------------------------------------------------------- drawing helpers
def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')


def fmt_p(p):
    if p < 0.001:
        return r'$\mathit{P}$ < 0.001'
    return rf'$\mathit{{P}}$ = {p:.2f}' if p >= 0.01 else rf'$\mathit{{P}}$ = {p:.3f}'


def bracket(ax, x0, x1, y, text, h=1.6):
    ax.plot([x0, x0, x1, x1], [y, y + h, y + h, y], color=INK, lw=0.5, zorder=4, clip_on=False)
    ax.text((x0 + x1) / 2, y + h + 0.8, text, ha='center', va='bottom', fontsize=5, color=INK, clip_on=False)


# ---------------------------------------------------------------- panels: drawing
def draw_a(fig, H, tab, tests, reps):
    label(fig, 0, 0, 'a', 'Accuracy by benchmark, model and condition', H)
    ax = axes_mm(fig, 11.0, 11.0, 168.0, 33.0, H)
    wd, step = 0.36, 0.04
    xpos = {}
    for b, bm in enumerate(BENCH):
        for i, c in enumerate(CFG):
            xpos[(bm, c)] = b * 4.8 + i
    for k, env in enumerate(ENVS):
        for (bm, c), x0 in xpos.items():
            t = tab[(tab.benchmark == bm) & (tab.cfg == c) & (tab.env == env)].iloc[0]
            x = x0 + (k - 0.5) * (wd + step)
            ax.bar(x, t.value, width=wd, color=ENV_COLOR[env], zorder=3)
            ax.errorbar(x, t.value, yerr=[[t.value - t.lo], [t.hi - t.value]], fmt='none', ecolor=INK,
                        elinewidth=0.6, capsize=1.2, capthick=0.6, zorder=4)
            v = reps[(reps.benchmark == bm) & (reps.cfg == c) & (reps.env == env)].sort_values('replicate').value
            ax.plot(x + np.array([-0.09, 0.0, 0.09])[:len(v)], v.values, ls='', marker='o', ms=1.7, mfc='white',
                    mec=INK, mew=0.45, zorder=5)
    ax.set_ylim(0, 116)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.spines['left'].set_bounds(0, 100)
    grid_y(ax)
    for t in tests.itertuples():                      # every Galaxy - custom code pair, Holm-adjusted across 12
        x0 = xpos[(t.benchmark, t.cfg)]
        top = tab[(tab.benchmark == t.benchmark) & (tab.cfg == t.cfg)].hi.max()
        bracket(ax, x0 - 0.2, x0 + 0.2, min(top, 100) + 2.5, 'n.s.' if t.p_holm >= 0.05 else fmt_p(t.p_holm), h=1.4)
    ax.set_xticks(list(xpos.values()), [TICK[c] for (_, c) in xpos])
    ax.tick_params(axis='x', length=0, pad=2, labelsize=5)
    ax.set_xlim(-0.65, max(xpos.values()) + 0.65)
    ax.set_ylabel('Accuracy (%)')
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for b, bm in enumerate(BENCH):
        mid = b * 4.8 + 1.5
        ntask = int(tab[tab.benchmark == bm].tasks.iloc[0])
        name = f'{BENCH_NAME[bm]}  ·  {ntask} tasks' + ('  ·  mean output agreement' if bm == 'IWC' else '')
        ax.plot([mid - 1.7, mid + 1.7], [-0.215, -0.215], transform=tr, color=INK2, lw=0.5, clip_on=False)
        ax.text(mid, -0.245, name, transform=tr, ha='center', va='top', fontsize=5.5, fontweight='bold')
        if b:
            ax.axvline(b * 4.8 - 1.4, color=GRID, lw=0.6, zorder=1)
    dot = Line2D([], [], ls='', marker='o', ms=1.7, mfc='white', mec=INK, mew=0.45)
    ax.legend(handles=[Patch(fc=ENV_COLOR[e]) for e in ENVS] + [dot],
              labels=[ENV_LABEL[e] for e in ENVS] + ['Replicate (one run per task)'], ncol=3, loc='lower right',
              bbox_to_anchor=(1.0, 1.03), fontsize=5.5, handlelength=1.0, columnspacing=1.2, borderaxespad=0)
    ax.text(0.0, 1.035, r'n.s., Holm-adjusted $\mathit{P}$ ≥ 0.05 for Galaxy against custom code', transform=ax.transAxes,
            ha='left', va='bottom', fontsize=5, color=INK2)


def draw_b(fig, H, y0, tab):
    label(fig, 0, y0, 'b', 'Difference between conditions by benchmark', H)
    ax = axes_mm(fig, 27.0, y0 + 13.0, 44.0, 29.0, H)
    rows = {bm: i for i, bm in enumerate(BENCH)}
    mk = {'runs_correct': ('o', INK, 'Runs correct'),
          'sets_all_three_correct': ('D', 'white', 'Replicate sets with\nall three runs correct')}
    for j, (measure, (m, face, _)) in enumerate(mk.items()):
        t = tab[tab.measure == measure]
        for x in t.itertuples():
            y = rows[x.benchmark] + (j - 0.5) * 0.36
            ax.plot([x.lo, x.hi], [y, y], color=INK, lw=0.7, zorder=3, solid_capstyle='butt')
            ax.plot(x.diff, y, ls='', marker=m, ms=3.2 if m == 'o' else 2.9, mfc=face, mec=INK, mew=0.6,
                    zorder=4)
            ax.text(31.5, y, fmt_p(x.p_holm), ha='left', va='center', fontsize=5, color=INK2, clip_on=False)
    ax.axvline(0, color=INK2, lw=0.6, zorder=2)
    ax.set_ylim(len(BENCH) - 0.45, -0.95)
    ax.set_yticks(range(len(BENCH)), ['BixBench-\nVerified-50', 'CompBioBench', 'IWC\n(Galaxy-derived)'])
    ax.tick_params(axis='y', length=0)
    ax.set_xlim(-12, 30)
    ax.set_xticks([-10, 0, 10, 20, 30])
    grid_x(ax)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Galaxy minus custom code\n(percentage points)', linespacing=1.15)
    ax.text(-0.8, -0.72, '← custom code higher', ha='right', va='center', fontsize=5, color=INK2)
    ax.text(0.8, -0.72, 'Galaxy higher →', ha='left', va='center', fontsize=5, color=INK2)
    handles = [Line2D([], [], ls='', marker=m, ms=3.0, mfc=f, mec=INK, mew=0.6, label=lab)
               for m, f, lab in mk.values()]
    ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(-0.55, 1.03), ncol=2, fontsize=5.3,
              handletextpad=0.3, columnspacing=0.9, borderaxespad=0)


def draw_c(fig, H, y0, grid, runs):
    label(fig, 96.0, y0, 'c', 'Same task and model in both conditions', H)
    fig.text((96.0 + 4.4) / W, 1 - (y0 + 4.6) / H, f'Total runs: custom code = {runs[CODE]:,}; Galaxy = {runs[GAL]:,}',
             fontsize=5, color=INK2, va='top')
    ax = axes_mm(fig, 121.0, y0 + 10.5, 33.0, 33.0, H)
    m = grid.values.astype(float)                      # rows: Galaxy 0..3, columns: custom code 0..3
    ax.imshow(np.where(m > 0, m, np.nan), origin='lower', cmap='Greys', norm=LogNorm(vmin=1, vmax=m.max() * 1.6),
              extent=(-0.5, 3.5, -0.5, 3.5), zorder=1)
    for g in range(4):
        for c in range(4):
            v = int(m[g, c])
            ax.text(c, g, f'{v}', ha='center', va='center', fontsize=5.5,
                    color='white' if v >= 60 else INK, fontweight='bold' if g == c else 'normal', zorder=3)
            if g == c:
                ax.add_patch(Rectangle((c - 0.5, g - 0.5), 1, 1, fill=False, ec=INK, lw=0.8, zorder=2))
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlabel('Correct runs of 3, custom code')
    ax.set_ylabel('Correct runs of 3, Galaxy')


def draw_d(fig, H, y0, tab, secondary):
    label(fig, 0, y0, 'd', 'Causes of single and persistent failures (BixBench-Verified-50)', H)
    ax = axes_mm(fig, 30.0, y0 + 9.0, 78.0, 34.0, H)
    rows = [(k, env) for k in (1, 2, 3) for env in ENVS]
    ypos, y = [], 0.0
    for k, env in rows:
        ypos.append(y)
        y += 1.0 if env == CODE else 2.05      # room between groups for counts placed outside narrow segments
    bar_h, width_mm = 0.72, 78.0
    dark = ('No answer validation', 'Benchmark specification or scoring', 'Not able to use Galaxy')
    for (k, env), yy in zip(rows, ypos):
        t = tab.loc[(k, env)] if (k, env) in tab.index else pd.Series(0, index=CAUSES)
        n = int(t.sum())
        left, outside = 0.0, []
        for cause in CAUSES:
            v = 100 * t[cause] / n if n else 0
            if v:
                ax.barh(yy, v, left=left, height=bar_h, color=CAUSE_COLOR[cause], ec='white', lw=0.4, zorder=3)
                txt = f'{int(t[cause])}'
                if v / 100 * width_mm >= 1.25 * len(txt) + 1.0:     # count fits inside the segment
                    ax.text(left + v / 2, yy, txt, ha='center', va='center', fontsize=5,
                            color='white' if cause in dark else INK, zorder=4)
                else:
                    outside.append([left + v / 2, txt, left + v / 2])
            left += v
        for a_, b_ in zip(outside, outside[1:]):          # keep neighbouring labels at least 4 points apart
            if b_[0] - a_[0] < 4.0:
                b_[0] = a_[0] + 4.0
        sign = -1 if env == CODE else 1
        for xc, txt, seg in outside:
            edge, tip = yy + sign * bar_h / 2, yy + sign * (bar_h / 2 + 0.32)
            xc = xc + 2.0
            ax.plot([seg, xc], [edge, tip], color=INK2, lw=0.4, zorder=4, clip_on=False)
            ax.text(xc, tip + sign * 0.05, txt, ha='center', va='bottom' if sign < 0 else 'top', fontsize=5,
                    color=INK, zorder=4, clip_on=False)
        ax.text(101.5, yy, f'{n}', ha='left', va='center', fontsize=5, color=INK2)
        ax.text(-1.2, yy, ENV_LABEL[env], ha='right', va='center', fontsize=5, color=INK)
    ax.set_ylim(ypos[-1] + 1.25, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Incorrect runs (%)')
    grid_x(ax)
    for k in (1, 2, 3):
        mid = (ypos[rows.index((k, CODE))] + ypos[rows.index((k, GAL))]) / 2
        ax.text(-0.235, mid, f'{k} of 3\nincorrect', transform=blended_transform_factory(ax.transAxes, ax.transData),
                ha='right', va='center', fontsize=5.5, fontweight='bold', linespacing=1.1)
    ax.text(101.5, -0.95, 'Runs', ha='left', va='center', fontsize=5, color=INK2)
    ax.legend(handles=[Patch(fc=CAUSE_COLOR[c], label=c) for c in CAUSES], loc='upper left',
              bbox_to_anchor=(1.10, 1.0), fontsize=5.3, handlelength=1.0, labelspacing=0.45, borderaxespad=0,
              title='Primary cause of the incorrect run', title_fontsize=5.3, alignment='left')
    k, n = secondary
    ax.text(1.10, 0.30, f'Under-specified runs often also lacked\nanswer validation ({k} of {n}, secondary cause)',
            transform=ax.transAxes, ha='left', va='top', fontsize=5, color=INK2, linespacing=1.2)


# ---------------------------------------------------------------- source data and assembly
def source_data(a_tab, a_t, a_reps, b_tab, grid, c_bench, d_tab, secondary):
    rows = []
    endpoint = {'IWC': 'output_agreement_x100'}
    for r in a_tab.itertuples():
        rows.append(dict(panel='a', benchmark=r.benchmark, model=r.cfg, condition=r.env,
                         measure=endpoint.get(r.benchmark, 'accuracy_pct'), value=r.value, ci95_low=r.lo,
                         ci95_high=r.hi, n=r.n))
    for r in a_reps.itertuples():
        rows.append(dict(panel='a', benchmark=r.benchmark, model=r.cfg, condition=r.env, replicate=r.replicate,
                         measure=endpoint.get(r.benchmark, 'accuracy_pct') + '_replicate', value=r.value, n=r.n))
    for r in a_t.itertuples():
        rows.append(dict(panel='a', benchmark=r.benchmark, model=r.cfg, condition='galaxy-custom_code',
                         measure='difference_points', value=r.diff, ci95_low=r.lo, ci95_high=r.hi, p=r.p,
                         p_holm=r.p_holm))
    for r in b_tab.itertuples():
        for env, v in ((CODE, r.code), (GAL, r.galaxy)):
            rows.append(dict(panel='b', benchmark=r.benchmark, model='all four', condition=env,
                             measure=f'{r.measure}_pct', value=v))
        rows.append(dict(panel='b', benchmark=r.benchmark, model='all four', condition='galaxy-custom_code',
                         measure=f'{r.measure}_difference_points', value=r.diff, ci95_low=r.lo, ci95_high=r.hi,
                         n=r.clusters, p=r.p, p_holm=r.p_holm))
    for g in range(4):
        for c in range(4):
            rows.append(dict(panel='c', benchmark='all', model='all four', condition='galaxy x custom_code',
                             measure=f'cells_galaxy_{g}_custom_code_{c}_correct_of_3', value=int(grid.loc[g, c])))
    for r in c_bench.itertuples():
        rows.append(dict(panel='c', benchmark=r.benchmark, model='all four', condition='galaxy x custom_code',
                         measure=f'cells_galaxy_{getattr(r, GAL)}_custom_code_{getattr(r, CODE)}_correct_of_3',
                         value=r.cells))
    for (k, env), t in d_tab.iterrows():
        for cause in CAUSES:
            rows.append(dict(panel='d', benchmark='BixBench50', model='all four', condition=env,
                             measure=f'incorrect_runs_in_sets_with_{k}_of_3_incorrect: {cause}', value=int(t[cause])))
    rows.append(dict(panel='d', benchmark='BixBench50', model='all four', condition='both',
                     measure='spec_primary_with_rigor_secondary', value=secondary[0], n=secondary[1]))
    cols = ['panel', 'benchmark', 'model', 'condition', 'replicate', 'measure', 'value', 'ci95_low', 'ci95_high', 'n',
            'p', 'p_holm']
    out = pd.DataFrame(rows).reindex(columns=cols)
    out['condition'] = out.condition.str.replace('custom_code', 'custom_code')
    out.round(4).to_csv(HERE / 'source_data.csv', index=False)


def main():
    r = load_runs()
    sets = replicate_sets(r)
    a_tab, a_t, a_reps = panel_a(r)
    b_tab = panel_b(r, sets)
    grid, c_bench, n_cells = panel_c(sets)
    d_tab, secondary = panel_d(load_ledger(r))
    for name, t in (('a: Galaxy - custom code by benchmark and model', a_t), ('b: Galaxy advantage by benchmark', b_tab),
                    ('c: correct runs of 3, rows Galaxy, columns custom code', grid), ('d: causes', d_tab)):
        print(name)
        print(t.round(4).to_string())

    H = 166.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    draw_a(fig, H, a_tab, a_t, a_reps)
    y2 = 59.0
    draw_b(fig, H, y2, b_tab)
    draw_c(fig, H, y2, grid, r.groupby('env').size())
    draw_d(fig, H, 116.0, d_tab, secondary)
    enforce_min_font(fig)
    title = 'Fig. 2 | Agents maintain bioinformatics accuracy when operating through Galaxy'
    fig.savefig(HERE / f'{FIG_NAME}.svg', metadata={'Title': title})
    fig.savefig(HERE / f'{FIG_NAME}.pdf', metadata={'Title': title})
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(HERE / f'{FIG_NAME}.png', dpi=(600, 600))
    source_data(a_tab, a_t, a_reps, b_tab, grid, c_bench, d_tab, secondary)


if __name__ == '__main__':
    main()
