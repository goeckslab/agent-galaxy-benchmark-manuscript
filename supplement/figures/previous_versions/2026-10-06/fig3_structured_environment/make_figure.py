#!/usr/bin/env python3
"""Figure 3: Galaxy provides a structured environment for agent analyses.

The panels answer the questions of Results section 2 of the outline:
a, which tasks did agents complete through Galaxy (runs correct by task domain, Galaxy against custom code);
b, what enables agents to complete these tasks, and when do they use user-defined tools (how each Galaxy run used
   Galaxy: installed tools, UDTs, both or neither, by benchmark and model);
c, what are the major error categories, and how do they differ between Galaxy tools, UDTs and custom code;
d, does Galaxy help agents recover from failures (runs ending correct by the number of execution errors);
e, does Galaxy help agents set parameters (parameter checks on installed-tool jobs);
f, what infrastructure changes would reduce these errors (failed Galaxy requests grouped by what would prevent them).

A run is correct when accepted (BixBench-Verified-50, CompBioBench) or at >= 0.99 IWC output agreement. Intervals are
95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks).
P values come from paired cluster randomization tests (200,000 draws), Holm-adjusted within each panel.

Reads data/run_scores.csv, run_execution_errors.csv, execution_error_types.csv, compbiobench_task_domains.csv,
galaxy_run_steps.csv, galaxy_traced_runs.csv, galaxy_parameter_checks.csv and galaxy_failure_classes.csv (written by
analysis/export_galaxy_benchmark_tables.py). Writes, next to this script, the figure as PDF, PNG (600 dpi) and SVG,
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
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.text import Text  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
from PIL import Image  # noqa: E402

import itertools  # noqa: E402
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

B, SEED, B_PERM = 20000, 20261002, 200000
W, MM = 180.0, 1 / 25.4
CFG = CONFIGS
ENVS = ENVS                                    # custom code first, always
CODE, GAL = ENVS
BENCH = BENCH
BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}       # as in Fig. 2
# Panel a: CompBioBench task domains as labelled by the benchmark; two small domains are merged.
DOMAIN = {'Population Genetics': 'Population genetics', 'Machine Learning': 'Machine learning',
          'Spatial': 'Spatial and structure', 'Structure': 'Spatial and structure'}
# Panel b: how a Galaxy run used Galaxy, from the jobs it submitted through the agent interface.
ROUTES = [('I', 'Installed tools only', GALAXY), ('IU', 'Installed tools and UDTs', '#56B4E9'),
          ('U', 'UDTs only', '#CFE3F1'), ('', 'No tool or UDT job', NEUTRAL_LIGHT)]
# Panel c: error types as classified for On-demand Fig. 5 (error text, exit code and command of every error).
ETYPES = [('Code, parameter or syntax error', '#44BB99'), ('Missing software, package or container', '#BBCC33'),
          ('File, path or input format', '#EEDD88'), ('Time or memory limit', '#FFAABB'),
          ('Network or download', '#99DDFF'), ('Galaxy job never started', '#AAAA00'),
          ('No or unclassified message', NEUTRAL_LIGHT)]
CHANNELS = [('galaxy_tool', 'Installed tools', 'Galaxy runs'), ('galaxy_udt', 'UDTs', 'Galaxy runs'),
            ('galaxy_shell', 'Shell commands', 'Galaxy runs'), ('code_shell', 'Shell commands', 'Custom-code runs')]
# Panel d: recovery, as approved in the previous Fig. 3b.
ERROR_BINS = [(0, 0, '0'), (1, 2, '1–2'), (3, 5, '3–5'), (6, 10, '6–10'), (11, 10 ** 9, '>10')]
FINE_BINS = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 7), (8, 10), (11, 15), (16, 25), (26, 10 ** 6)]
B_CURVE = 2000           # cluster-bootstrap resamples for the fitted-curve bands
# Panel e: parameter checks returned by the agent interface for installed-tool jobs.
CHECKS = [('matched|post_run', 'Matched after the run', NEUTRAL_DARK),
          ('mismatch|validation', 'Mismatch caught before the job ran', OI_GREEN),
          ('mismatch|post_run', 'Mismatch after the run', OI_PURPLE),
          ('none_to_compare', 'No parameters to compare', '#BBBBBB'),
          ('no_check', 'No check result', '#E8E8E8')]
# Panel f: classes of failed Galaxy requests (token analysis, four primary configurations), grouped by the change
# that would prevent them. The grouping is ours; the classes come from the request and job error records.
FIXES = [('API design', ('A1', 'A3', 'A5'),
          'tool forms that need history context; nested parameter keys; dataset and job IDs'),
         ('Error diagnostics', ('B2',), 'jobs that failed without any diagnostic message'),
         ('Tool and parameter descriptions', ('A4', 'A2'), 'invalid parameter values or datatypes; tool IDs not found'),
         ('Datatypes and uploads', ('A7', 'B4'), 'upload or datatype registry; input format, compression or index'),
         ('UDT support', ('A6', 'B1'), 'UDT definition schema; missing dependency in the UDT container'),
         ('Server capacity', ('A8', 'B5'), 'server, transport or rate limits; job memory or resources'),
         ('Tool runtime error', ('B3',), 'tool wrote an error; agent input or tool, not attributable'),
         ('Other or unclassified', ('X', 'Z'), 'other transport or tool exceptions; unclassified')]
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


# ---------------------------------------------------------------- data
def load_runs():
    r = read_runs_table('run_scores.csv')
    r['cluster'] = r.benchmark + ':' + r.cluster.astype(str)
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    return r


def load_calls():
    """Steps that ran as Galaxy jobs in each traced Galaxy run, and the traced runs (data/galaxy_run_steps.csv,
    data/galaxy_traced_runs.csv)."""
    steps = read_runs_table('galaxy_run_steps.csv')
    traced = read_runs_table('galaxy_traced_runs.csv')
    return steps, traced[['benchmark', 'task', 'cfg', 'replicate']].drop_duplicates()


def load_errors(r):
    """Execution errors per run: failed shell commands plus Galaxy jobs in the error state (data/run_execution_errors.csv)."""
    e = read_runs_table('run_execution_errors.csv')
    e['errors'] = e.failed_shell_commands + e.galaxy_jobs_in_error_state
    m = r.merge(e[['benchmark', 'cfg', 'env', 'task', 'replicate', 'errors']],
                on=['benchmark', 'cfg', 'env', 'task', 'replicate'], how='inner')
    m['bin'] = pd.cut(m.errors, [b[0] - 0.5 for b in ERROR_BINS] + [1e12], labels=[b[2] for b in ERROR_BINS])
    return m


# ---------------------------------------------------------------- panels: statistics
def panel_a(r):
    """Runs correct by task domain and condition: CompBioBench domains, BixBench-Verified-50 and IWC."""
    dom = {t.task_id: DOMAIN.get(t.domain, t.domain)
           for t in pd.read_csv(DATA / 'compbiobench_task_domains.csv').itertuples()}
    d = r.assign(domain=np.where(r.benchmark == 'CompBio', r.task.map(dom), r.benchmark.map(BENCH_NAME)))
    assert d.domain.notna().all(), 'every CompBioBench task needs a domain'
    rows, tests = [], []
    for name, g in d.groupby('domain'):                 # each domain lies within one benchmark
        est, draws = boot_means(g, ['env'], value='ok')
        for env in ENVS:
            rows.append(dict(domain=name, env=env, value=est[env] * 100, lo=np.percentile(draws[env], 2.5) * 100,
                             hi=np.percentile(draws[env], 97.5) * 100, tasks=g.task.nunique()))
        cell = g.groupby(['cluster', 'task', 'cfg', 'env']).ok.mean().unstack('env')
        diff = (cell[GAL] - cell[CODE]).groupby(level='cluster').sum()
        tests.append(dict(domain=name, diff=100 * (g[g.env == GAL].ok.mean() - g[g.env == CODE].ok.mean()),
                          p=signflip_p(diff.values)))
    tests = pd.DataFrame(tests)
    tests['p_holm'] = holm(tests.p)
    return pd.DataFrame(rows), tests


def panel_b(steps, runs):
    """Route of each traced Galaxy run: installed-tool jobs, UDT jobs, both or neither (through the interface)."""
    k = ['benchmark', 'task', 'cfg', 'replicate']
    inst = steps[steps.step != 'UDT'][k].drop_duplicates().assign(I='I')
    udt = steps[steps.step == 'UDT'][k].drop_duplicates().assign(U='U')
    m = runs.merge(inst, on=k, how='left').merge(udt, on=k, how='left').fillna({'I': '', 'U': ''})
    m['route'] = m.I + m.U
    tab = m.groupby(['benchmark', 'cfg', 'route']).size().unstack('route', fill_value=0)
    return tab.reindex(columns=[c for c, _, _ in ROUTES], fill_value=0)


def panel_c(steps):
    """Execution errors by type and by where they occurred (data/execution_error_types.csv)."""
    e = read_runs_table('execution_error_types.csv')
    job = {'Galaxy job, UDT': 'galaxy_udt', 'Galaxy job, installed tool': 'galaxy_tool'}
    e['where'] = np.where(e.channel.isin(list(job)), e.channel.map(job),
                          np.where(e.env == GAL, 'galaxy_shell', 'code_shell'))
    tab = e.groupby(['where', 'error_type']).errors.sum().unstack('error_type', fill_value=0)
    tab = tab.reindex(index=[c for c, _, _ in CHANNELS], columns=[t for t, _ in ETYPES], fill_value=0)
    runs = read_runs_table('run_execution_errors.csv').groupby('env').size()
    return tab, runs


def stratified_difference(sG, nG, sC, nC, weights):
    return np.sum(weights * (sG / nG - sC / nC), axis=-1)


def recovery_test(e, bins):
    """Weighted Galaxy - custom code difference over error bins, with a cluster condition-swap randomization test."""
    agg = e.groupby(['cluster', 'env', 'bin'], observed=True).ok.agg(['sum', 'count']).unstack(['env', 'bin'])
    agg = agg.reindex(columns=pd.MultiIndex.from_product([['sum', 'count'], ENVS, bins]), fill_value=0).fillna(0)
    sG, nG = agg['sum'][GAL].values, agg['count'][GAL].values
    sC, nC = agg['sum'][CODE].values, agg['count'][CODE].values
    wts = (nG.sum(0) + nC.sum(0)) / (nG.sum() + nC.sum())
    observed = stratified_difference(sG.sum(0), nG.sum(0), sC.sum(0), nC.sum(0), wts)
    hits = 0
    for _ in range(B_PERM // 20000):
        f = rng.integers(0, 2, size=(20000, len(agg)))[:, :, None]
        g_s, g_n = ((1 - f) * sG + f * sC).sum(1), ((1 - f) * nG + f * nC).sum(1)
        c_s, c_n = (f * sG + (1 - f) * sC).sum(1), (f * nG + (1 - f) * nC).sum(1)
        hits += np.sum(np.abs(stratified_difference(g_s, g_n, c_s, c_n, wts)) >= abs(observed) - 1e-12)
    return observed, (1 + hits) / (B_PERM + 1)


def logistic_fit(x, succ, n, iters=30):
    """Binomial logistic regression of P(correct) on x by iteratively reweighted least squares."""
    X = np.column_stack([np.ones_like(x), x])
    beta = np.array([np.log((succ.sum() + 0.5) / (n.sum() - succ.sum() + 0.5)), 0.0])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(X @ beta)))
        w = n * p * (1 - p)
        z = X @ beta + np.divide(succ - n * p, w, out=np.zeros_like(w), where=w > 0)
        step = np.linalg.solve(X.T @ (X * w[:, None]) + 1e-9 * np.eye(2), X.T @ (w * z))
        if np.allclose(step, beta, atol=1e-10):
            break
        beta = step
    return beta


def recovery_curves(m, grid):
    """Logistic fit of runs ending correct on log(1 + errors), per condition, with cluster-bootstrap bands."""
    agg = m.groupby(['benchmark', 'cluster', 'env', 'errors']).ok.agg(['sum', 'count']).reset_index()
    out, coef = {}, {}
    for env in ENVS:
        d = agg[agg.env == env]
        x, succ, n = np.log1p(d.errors.values.astype(float)), d['sum'].values.astype(float), d['count'].values.astype(float)
        beta = logistic_fit(x, succ, n)
        clusters = d.cluster.values
        weights = np.ones((B_CURVE, len(d)))
        for bm in d.benchmark.unique():
            names = np.unique(clusters[d.benchmark.values == bm])
            draw = rng.multinomial(len(names), np.full(len(names), 1 / len(names)), size=B_CURVE)
            col = {c: i for i, c in enumerate(names)}
            idx = np.array([col[c] for c in clusters[d.benchmark.values == bm]])
            weights[:, d.benchmark.values == bm] = draw[:, idx]
        curves = np.empty((B_CURVE, len(grid)))
        betas = np.empty((B_CURVE, 2))
        for k in range(B_CURVE):
            bk = logistic_fit(x, succ * weights[k], n * weights[k])
            betas[k] = bk
            curves[k] = 1 / (1 + np.exp(-(bk[0] + bk[1] * np.log1p(grid))))
        out[env] = (100 / (1 + np.exp(-(beta[0] + beta[1] * np.log1p(grid)))),
                    100 * np.percentile(curves, 2.5, axis=0), 100 * np.percentile(curves, 97.5, axis=0))
        coef[env] = dict(intercept=beta[0], slope=beta[1], slope_lo=np.percentile(betas[:, 1], 2.5),
                         slope_hi=np.percentile(betas[:, 1], 97.5), runs=int(n.sum()))
    return out, coef


def fine_bins(m):
    rows = []
    for env in ENVS:
        d = m[m.env == env]
        for lo, hi in FINE_BINS:
            g = d[(d.errors >= lo) & (d.errors <= hi)]
            if len(g):
                lab = f'{lo}' if lo == hi else (f'>{lo - 1}' if hi > 10 ** 5 else f'{lo}–{hi}')
                rows.append(dict(env=env, bin=lab, mean_errors=g.errors.mean(), value=100 * g.ok.mean(), n=len(g)))
    return pd.DataFrame(rows)


def panel_d(m):
    """Error-adjusted recovery (chosen after inspecting the bins; the unadjusted test is reported too)."""
    e = m[m.errors > 0]
    adjusted = recovery_test(e, [b[2] for b in ERROR_BINS[1:]])
    unadjusted = recovery_test(e.assign(bin='any'), ['any'])
    rec = dict(difference=adjusted[0] * 100, p=adjusted[1], unadjusted=unadjusted[0] * 100, p_unadjusted=unadjusted[1],
               runs_with_errors=int(len(e)))
    grid = np.linspace(0, 40, 161)
    curves, coef = recovery_curves(m, grid)
    return rec, fine_bins(m), grid, curves, coef


def panel_e(steps):
    """Parameter checks on installed-tool requests, by benchmark (data/galaxy_parameter_checks.csv)."""
    r = read_runs_table('galaxy_parameter_checks.csv')
    key = (r.prov_status + '|' + r.prov_stage).replace({'no_explicit_non_dataset_parameters|post_run': 'none_to_compare',
                                                        'not_comparable|post_run': 'no_check', 'none|none': 'no_check'})
    tab = r.assign(key=key).pivot_table(index='benchmark', columns='key', values='requests', aggfunc='sum')
    tab = tab.reindex(index=BENCH, columns=[c for c, _, _ in CHECKS]).fillna(0).astype(int)
    tab.loc['all'] = tab.sum()
    return tab


def panel_f():
    t = read_runs_table('galaxy_failure_classes.csv').rename(columns={'requests': 'calls'})
    t['code'] = t.failure_class.str.split(' ').str[0]
    per_class = t.groupby(['code', 'failure_class']).calls.sum().reset_index()
    rows = []
    for name, codes, desc in FIXES:
        n = int(per_class[per_class.code.isin(codes)].calls.sum())
        rows.append(dict(fix=name, classes='+'.join(codes), description=desc, requests=n))
    tab = pd.DataFrame(rows)
    assert tab.requests.sum() == per_class.calls.sum(), 'every failure class must map to one fix'
    tab['pct'] = 100 * tab.requests / tab.requests.sum()
    return tab, per_class


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


def pct_text(v):
    return '<1' if 0 < v < 0.5 else f'{v:.0f}'


def stacked_rows(ax, ypos, shares, colors, width_mm, bar_h=0.72, dark=(), last_right=False, lead=0.42):
    """Horizontal 100% bars with every share printed: inside its segment when it fits; otherwise above the bar with a
    short leader (or, for the last segment when last_right is set, just right of the bar)."""
    for y, row in zip(ypos, shares):
        left, out = 0.0, []
        last = max(i for i, v in enumerate(row) if v > 0)
        for i, (v, c) in enumerate(zip(row, colors)):
            if v <= 0:
                continue
            ax.barh(y, v, left=left, height=bar_h, color=c, ec='white', lw=0.4, zorder=3)
            txt = pct_text(v)
            if v / 100 * width_mm >= 1.25 * len(txt) + 0.6:          # fits inside at 5 pt
                ax.text(left + v / 2, y, txt, ha='center', va='center', fontsize=5,
                        color='white' if c in dark else INK, zorder=4)
            elif i == last and last_right:
                ax.text(101.2, y, txt, ha='left', va='center', fontsize=5, color=INK, zorder=4, clip_on=False)
            else:
                out.append([left + v / 2, txt, left + v / 2])
            left += v
        for a_, b_ in zip(out, out[1:]):                    # neighbouring outside labels at least 5 points apart
            if b_[0] - a_[0] < 5.0:
                b_[0] = a_[0] + 5.0
        for xc, txt, seg in out:
            edge, tip = y - bar_h / 2, y - bar_h / 2 - lead     # y axis inverted: smaller y is higher
            ax.plot([seg, xc], [edge, tip], color=INK2, lw=0.4, zorder=4, clip_on=False)
            ax.text(xc, tip - 0.04, txt, ha='center', va='bottom', fontsize=5, color=INK, zorder=4,
                    clip_on=False)


# ---------------------------------------------------------------- panels: drawing
def draw_a(fig, H, tab, tests):
    label(fig, 0, 0, 'a', 'Tasks completed, by domain', H)
    ax = axes_mm(fig, 31.0, 12.0, 24.0, 42.0, H)
    gal = tab[tab.env == GAL].set_index('domain')
    comp = [d for d in gal.value.sort_values(ascending=False).index if d not in BENCH_NAME.values()]
    order = comp + ['BixBench-Verified-50', 'IWC']
    ys = {d: i + (0.6 if d in ('BixBench-Verified-50', 'IWC') else 0) for i, d in enumerate(order)}
    for k, env in enumerate(ENVS):
        t = tab[tab.env == env].set_index('domain')
        for d in order:
            y = ys[d] + (k - 0.5) * 0.34
            ax.plot([t.loc[d, 'lo'], t.loc[d, 'hi']], [y, y], color=ENV_COLOR[env], lw=0.7, zorder=3)
            ax.plot(t.loc[d, 'value'], y, ls='', marker=ENV_MARKER[env], ms=2.9, mfc=ENV_COLOR[env],
                    mec='white', mew=0.35, zorder=4)
    ax.set_ylim(max(ys.values()) + 0.6, -0.6)
    ax.set_yticks([ys[d] for d in order], [f'{d} ({int(gal.loc[d, "tasks"])})' for d in order], fontsize=5)
    ax.tick_params(axis='y', length=0)
    ax.axhline(len(comp) - 0.2, color=NEUTRAL_MID, lw=0.5, zorder=1)
    ax.set_xlim(40, 100)
    ax.set_xticks([50, 75, 100])
    grid_x(ax)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Runs correct (%)')
    ax.text(-0.04, -0.75, 'CompBioBench domains (tasks)', transform=blended_transform_factory(ax.transAxes, ax.transData),
            ha='right', va='center', fontsize=5, fontweight='bold')
    hand = [Line2D([], [], ls='', marker=ENV_MARKER[e], ms=2.9, mfc=ENV_COLOR[e], mec='white', mew=0.35,
                   label=ENV_LABEL[e]) for e in ENVS]
    ax.legend(handles=hand, loc='lower left', bbox_to_anchor=(-1.25, 1.07), ncol=2, fontsize=5.3, handletextpad=0.2,
              columnspacing=0.8, borderaxespad=0)
    worst = tests.p_holm.min()
    ax.text(1.0, 1.02, f'no domain differs\n(Holm-adjusted {fmt_p(worst).replace("= ", "≥ ")})',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=5, color=INK2, linespacing=1.15)


def draw_b(fig, H, tab):
    label(fig, 60.0, 0, 'b', 'How Galaxy runs used Galaxy', H)
    ax = axes_mm(fig, 92.0, 13.0, 74.0, 41.0, H)
    rows = [(bm, c) for bm in BENCH for c in CFG]
    ypos = [i + 0.45 * BENCH.index(bm) for i, (bm, c) in enumerate(rows)]
    shares = [100 * tab.loc[(bm, c)].values / tab.loc[(bm, c)].sum() for bm, c in rows]
    stacked_rows(ax, ypos, shares, [col for _, _, col in ROUTES], 74.0, dark=(GALAXY,), last_right=True)
    ax.set_ylim(max(ypos) + 0.6, -0.6)
    ax.set_yticks(ypos, [c for _, c in rows], fontsize=5)
    ax.tick_params(axis='y', length=0)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Galaxy runs (%)')
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    for bm in BENCH:
        ys = [y for y, (b, _) in zip(ypos, rows) if b == bm]
        ax.text(-0.42, np.mean(ys), BENCH_NAME[bm].replace('-Verified-50', '-\nVerified-50'), transform=tr,
                ha='left', va='center', fontsize=5, fontweight='bold', linespacing=1.1)
    ax.text(1.035, np.mean(ypos[-4:]), 'UDTs not\noffered', transform=tr, ha='left', va='center', fontsize=5,
            color=INK2, linespacing=1.1)
    ax.legend(handles=[Patch(fc=col, ec=NEUTRAL_MID if col == '#CFE3F1' else col, lw=0.3, label=lab)
                       for _, lab, col in ROUTES], loc='lower left', bbox_to_anchor=(-0.42, 1.02), ncol=4,
              fontsize=5.0, handlelength=0.9, handletextpad=0.3, columnspacing=0.8, borderaxespad=0)


def draw_c(fig, H, tab, runs):
    label(fig, 0, 62.0, 'c', 'Execution errors by type and where they occurred', H)
    ax = axes_mm(fig, 26.0, 71.0, 60.0, 25.0, H)
    shares = [100 * tab.loc[c].values / tab.loc[c].sum() for c, _, _ in CHANNELS]
    ypos = [0, 1.7, 3.4, 5.5]
    stacked_rows(ax, ypos, shares, [col for _, col in ETYPES], 60.0, bar_h=0.78)
    ax.set_ylim(6.05, -1.25)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Errors (%)')
    for y, (c, name, where) in zip(ypos, CHANNELS):
        ax.text(-1.5, y, name, ha='right', va='center', fontsize=5)
        n = int(tab.loc[c].sum())
        per = n / runs[CODE if c == 'code_shell' else GAL]
        ax.text(101.5, y, f'{n:,} ({per:.1f}/run)', ha='left', va='center', fontsize=5, color=INK2)
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(-0.42, ypos[1], 'Galaxy\nruns', transform=tr, ha='left', va='center', fontsize=5, fontweight='bold',
            linespacing=1.1)
    ax.text(-0.42, ypos[3], 'Custom-\ncode runs', transform=tr, ha='left', va='center', fontsize=5, fontweight='bold',
            linespacing=1.1)
    ax.text(101.5, -0.95, 'Errors', ha='left', va='center', fontsize=5, color=INK2)
    ax.legend(handles=[Patch(fc=col, label=lab) for lab, col in ETYPES], loc='upper left', bbox_to_anchor=(-0.42, -0.36),
              ncol=2, fontsize=5.0, handlelength=0.9, handletextpad=0.3, columnspacing=0.8, labelspacing=0.25,
              borderaxespad=0)


def draw_d(fig, H, y0, rec, fine, grid, curves, runs, max_errors):
    label(fig, 104.0, y0, 'd', 'Recovery from execution errors', H)
    ax = axes_mm(fig, 114.0, y0 + 13.0, 65.0, 32.0, H)
    gx = np.log1p(grid)
    for k, env in enumerate(ENVS):
        fit, lo, hi = curves[env]
        keep = grid <= max_errors[env]                  # no extrapolation beyond the condition's observed runs
        ax.fill_between(gx[keep], lo[keep], hi[keep], color=ENV_COLOR[env], alpha=0.15, lw=0, zorder=2)
        ax.plot(gx[keep], fit[keep], color=ENV_COLOR[env], lw=0.8, zorder=3)
        f = fine[fine.env == env]
        dodge = (k - 0.5) * 0.07
        ax.scatter(np.log1p(f.mean_errors) + dodge, f.value, s=np.maximum(f.n * 0.11, 3.0),
                   marker=ENV_MARKER[env], facecolor=ENV_COLOR[env], edgecolor='white', lw=0.4,
                   alpha=0.9, zorder=4)
    ticks = [0, 1, 2, 5, 10, 20, 40]
    ax.set_xticks(np.log1p(ticks), [str(t) for t in ticks])
    ax.set_xlim(-0.15, np.log1p(42))
    ax.set_ylim(20, 100)
    ax.set_yticks(range(20, 101, 20))
    grid_y(ax)
    ax.set_xlabel('Execution errors in the run (log scale)')
    ax.set_ylabel('Runs ending correct (%)')
    cond = [Line2D([], [], color=ENV_COLOR[e], lw=0.8, marker=ENV_MARKER[e], ms=3.6,
                   mfc=ENV_COLOR[e], mec='white', mew=0.4, label=f'{ENV_LABEL[e]} ({runs[e]:,} runs)')
            for e in ENVS]
    leg = ax.legend(handles=cond, ncol=1, loc='lower left', bbox_to_anchor=(0.0, 1.01), fontsize=5.5,
                    handlelength=1.6, handletextpad=0.4, labelspacing=0.25, borderaxespad=0)
    ax.add_artist(leg)
    sizes = [Line2D([], [], ls='', marker='o', ms=np.sqrt(max(n * 0.11, 3.0)), mfc='none', mec=INK2, mew=0.5,
                    label=f'{n}') for n in (25, 100, 400)]
    ax.legend(handles=sizes, ncol=3, loc='lower right', bbox_to_anchor=(1.0, 1.01), fontsize=5, handletextpad=0.6,
              columnspacing=1.0, handlelength=1.2, borderaxespad=0, title='Runs with that many errors',
              title_fontsize=5)
    ax.text(0.02, 0.04, f'At equal error counts, Galaxy runs with errors ended\ncorrect {rec["difference"]:.1f} '
            f'percentage points more often ({fmt_p(rec["p"])})', transform=ax.transAxes, ha='left', va='bottom',
            fontsize=5, color=INK, linespacing=1.25)


def draw_e(fig, H, y0, tab):
    label(fig, 0, y0, 'e', 'Parameter checks on installed-tool jobs', H)
    fig.text(4.4 / W, 1 - (y0 + 4.6) / H, 'The interface compares requested and recorded parameters', fontsize=5,
             color=INK2, va='top')
    ax = axes_mm(fig, 20.0, y0 + 12.0, 54.0, 18.0, H)
    rows = BENCH + ['all']
    ypos = [0, 1, 2, 3.25]
    shares = [100 * tab.loc[b].values / tab.loc[b].sum() for b in rows]
    stacked_rows(ax, ypos, shares, [col for _, _, col in CHECKS], 54.0, last_right=True,
                 dark=(NEUTRAL_DARK, OI_GREEN, OI_PURPLE))
    ax.set_ylim(3.85, -0.6)
    ax.set_yticks(ypos, ['BixBench-\nVerified-50', 'CompBioBench', 'IWC', 'All'], fontsize=5)
    ax.get_yticklabels()[-1].set_fontweight('bold')
    ax.tick_params(axis='y', length=0)
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Installed-tool requests (%)')
    ax.text(1.0, 1.04, f'{int(tab.loc["all"].sum()):,} requests', transform=ax.transAxes, ha='right', va='bottom',
            fontsize=5, color=INK2)
    ax.legend(handles=[Patch(fc=col, ec=NEUTRAL_MID if col == '#E8E8E8' else col, lw=0.3, label=lab)
                       for _, lab, col in CHECKS], loc='upper left', bbox_to_anchor=(-0.30, -0.50), ncol=2,
              fontsize=5.0, handlelength=0.9, handletextpad=0.3, columnspacing=0.8, labelspacing=0.25, borderaxespad=0)


def draw_f(fig, H, y0, tab):
    label(fig, 82.0, y0, 'f', 'What would prevent failed Galaxy requests', H)
    ax = axes_mm(fig, 121.0, y0 + 8.5, 44.0, 33.0, H)
    n = len(tab)
    for i, t in enumerate(tab.itertuples()):
        grey = t.fix in ('Tool runtime error', 'Other or unclassified')
        ax.barh(i, t.requests, height=0.68, color=NEUTRAL_LIGHT if grey else GALAXY, zorder=3)
        ax.text(t.requests + 40, i, f'{t.requests:,} ({t.pct:.0f}%)', ha='left', va='center', fontsize=5)
    ax.set_ylim(n - 0.45, -0.6)
    ax.set_yticks(range(n), tab.fix, fontsize=5.5)
    ax.tick_params(axis='y', length=0)
    ax.axhline(5.5, color=NEUTRAL_MID, lw=0.5, zorder=1)
    ax.set_xlim(0, tab.requests.max() * 1.45)
    ax.set_xticks([0, 500, 1000, 1500])
    grid_x(ax)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel(f'Failed Galaxy requests (of {int(tab.requests.sum()):,})')


# ---------------------------------------------------------------- source data and assembly
def source_data(a_tab, a_t, b_tab, c_tab, c_runs, rec, fine, coef, e_tab, f_tab, f_class):
    rows = []
    for t in a_tab.itertuples():
        rows.append(dict(panel='a', group=t.domain, condition=t.env, measure='runs_correct_pct', value=t.value,
                         ci95_low=t.lo, ci95_high=t.hi, n=t.tasks))
    for t in a_t.itertuples():
        rows.append(dict(panel='a', group=t.domain, condition='galaxy-custom_code', measure='difference_points',
                         value=t.diff, p=t.p, p_holm=t.p_holm))
    for (bm, c), t in b_tab.iterrows():
        for code, lab, _ in ROUTES:
            rows.append(dict(panel='b', benchmark=bm, model=c, condition='galaxy', group=lab, measure='galaxy_runs',
                             value=int(t[code]), n=int(t.sum())))
    for code, name, where in CHANNELS:
        for et, _ in ETYPES:
            rows.append(dict(panel='c', group=f'{name} ({where})', condition=CODE if code == 'code_shell' else GAL,
                             measure=f'errors: {et}', value=int(c_tab.loc[code, et]),
                             n=int(c_runs[CODE if code == 'code_shell' else GAL])))
    for t in fine.itertuples():
        rows.append(dict(panel='d', group=f'errors_{t.bin}', condition=t.env, measure='runs_ending_correct_pct',
                         value=t.value, n=t.n))
        rows.append(dict(panel='d', group=f'errors_{t.bin}', condition=t.env, measure='mean_errors_per_run',
                         value=t.mean_errors, n=t.n))
    for env, c in coef.items():
        rows.append(dict(panel='d', group='logistic fit on ln(1 + errors)', condition=env, measure='slope',
                         value=c['slope'], ci95_low=c['slope_lo'], ci95_high=c['slope_hi'], n=c['runs']))
    rows.append(dict(panel='d', group='runs with errors', condition='galaxy-custom_code',
                     measure='difference_points_adjusted_for_error_bins', value=rec['difference'], p=rec['p'],
                     n=rec['runs_with_errors']))
    rows.append(dict(panel='d', group='runs with errors', condition='galaxy-custom_code',
                     measure='difference_points_unadjusted', value=rec['unadjusted'], p=rec['p_unadjusted'],
                     n=rec['runs_with_errors']))
    for bm, t in e_tab.iterrows():
        for code, lab, _ in CHECKS:
            rows.append(dict(panel='e', benchmark=bm, condition='galaxy', group=lab,
                             measure='installed_tool_requests', value=int(t[code]), n=int(t.sum())))
    for t in f_tab.itertuples():
        rows.append(dict(panel='f', condition='galaxy', group=t.fix, measure=f'failed_requests ({t.classes})',
                         value=t.requests, n=int(f_tab.requests.sum())))
    for t in f_class.itertuples():
        rows.append(dict(panel='f', condition='galaxy', group=t.failure_class, measure='failed_requests_by_class',
                         value=int(t.calls)))
    cols = ['panel', 'benchmark', 'model', 'condition', 'group', 'measure', 'value', 'ci95_low', 'ci95_high', 'n', 'p',
            'p_holm']
    out = pd.DataFrame(rows).reindex(columns=cols)
    out['condition'] = out.condition.str.replace('custom_code', 'custom_code')
    out.round(4).to_csv(HERE / 'source_data.csv', index=False)


def main():
    r = load_runs()
    calls, traced = load_calls()
    m = load_errors(r)
    rec, fine, grid, curves, coef = panel_d(m)
    a_tab, a_t = panel_a(r)
    b_tab = panel_b(calls, traced)
    c_tab, c_runs = panel_c(calls)
    e_tab = panel_e(calls)
    f_tab, f_class = panel_f()
    for name, t in (('a: domains', a_tab), ('a: tests', a_t), ('b: routes', b_tab), ('c: errors', c_tab),
                    ('e: parameter checks', e_tab), ('f: fixes', f_tab)):
        print(name)
        print(t.round(3).to_string())
    print('d:', {k: round(float(v), 4) for k, v in rec.items()})

    H = 170.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    draw_a(fig, H, a_tab, a_t)
    draw_b(fig, H, b_tab)
    draw_c(fig, H, c_tab, c_runs)
    y2 = 62.0
    runs = m.groupby('env').size().to_dict()
    max_errors = m.groupby('env').errors.max().to_dict()
    draw_d(fig, H, y2, rec, fine, grid, curves, runs, max_errors)
    draw_e(fig, H, 119.0, e_tab)
    draw_f(fig, H, 119.0, f_tab)
    enforce_min_font(fig)
    title = 'Fig. 3 | Galaxy provides a structured environment for agent analyses'
    fig.savefig(HERE / f'{FIG_NAME}.svg', metadata={'Title': title})
    fig.savefig(HERE / f'{FIG_NAME}.pdf', metadata={'Title': title})
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(HERE / f'{FIG_NAME}.png', dpi=(600, 600))
    source_data(a_tab, a_t, b_tab, c_tab, c_runs, rec, fine, coef, e_tab, f_tab, f_class)


if __name__ == '__main__':
    main()
