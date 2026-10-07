#!/usr/bin/env python3
"""Figure 3: Galaxy provides a structured environment for agent analyses.

Drawing code copied unchanged from the run archive, paulocilasjr/Galaxy_benchmark@0dbf3f443b83a91322098c9918d86a5846129215:figures/make_fig3.py; the panel data are the
values that script computed and passed to its drawing functions (data/figure_panels/fig3.json, written by the
archive's figures/panel_io.py and copied by analysis/export_galaxy_benchmark_tables.py). Nothing is recomputed here:
every number traces to the archive script at that commit. Writes, next to this script, fig3_structured_environment.pdf, .png (600 dpi)
and .svg, and source_data.csv (the archive's fig3_source_data.csv).

Regenerate with: python figures/fig3_structured_environment/make_figure.py
"""
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / 'data'
sys.path.insert(0, str(HERE.parent))
import figure_style as style  # noqa: E402  (the archive's style module; sets rcParams on import)
import panel_io  # noqa: E402
plt = style.plt
OUT = str(HERE)
from PIL import Image
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.transforms import blended_transform_factory
import io
import numpy as np
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})


style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition


W, MM = 180.0, 1 / 25.4


CFG = style.CONFIGS


ENVS = style.ENVS                                    # custom code first, always


CODE, GAL = ENVS


BENCH = style.BENCH


BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}


ROUTES = [('I', 'Installed tools only', style.GALAXY), ('IU', 'Installed tools and UDTs', '#56B4E9'),
          ('U', 'UDTs only', '#CFE3F1'), ('F', 'Jobs submitted, none completed', '#999999'),
          ('', 'No job submitted', style.NEUTRAL_LIGHT)]


EGROUPS = [('Code, parameter or syntax', ('Code, parameter or syntax error',), '#44BB99'),
           ('Missing software or package', ('Missing software, package or container',), '#BBCC33'),
           ('Galaxy job never started', ('Galaxy job never started',), '#AAAA00'),
           ('Other or unclassified', ('File, path or input format', 'Time or memory limit', 'Network or download',
                                      'No or unclassified message'), style.NEUTRAL_LIGHT)]


CHANNELS = [('galaxy_tool', 'Installed-tool jobs', GAL), ('galaxy_udt', 'UDT jobs', GAL),
            ('galaxy_shell', 'Shell commands', GAL), ('code_shell', 'Shell commands', CODE)]


ERROR_BINS = [(0, 0, '0'), (1, 2, '1–2'), (3, 5, '3–5'), (6, 10, '6–10'), (11, 10 ** 9, '>10')]


CHECKS = [('matched', 'Matched', style.NEUTRAL_DARK),
          ('diff_blocked', 'Different value, blocked before the job', style.OI_GREEN),
          ('diff_ran', 'Different value, job ran', style.OI_PURPLE),
          ('unrecorded', 'Requested value not recorded (default or format)', '#BBBBBB'),
          ('none', 'No comparison (no parameters or no result)', '#E8E8E8')]


UNRESOLVED = ('Tool runtime error (not attributable)', 'Other or unclassified')


def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H, note=None):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')
    if note:
        fig.text((x + 4.4) / W, 1 - (y + 4.4) / H, note, fontsize=5, color=style.INK2, va='top', ha='left',
                 linespacing=1.2)


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
                        color='white' if c in dark else style.INK, zorder=4)
            elif i == last and last_right:
                ax.text(101.2, y, txt, ha='left', va='center', fontsize=5, color=style.INK, zorder=4, clip_on=False)
            else:
                out.append([left + v / 2, txt, left + v / 2])
            left += v
        for a_, b_ in zip(out, out[1:]):                    # neighbouring outside labels at least 5 points apart
            if b_[0] - a_[0] < 5.0:
                b_[0] = a_[0] + 5.0
        for xc, txt, seg in out:
            edge, tip = y - bar_h / 2, y - bar_h / 2 - lead     # y axis inverted: smaller y is higher
            ax.plot([seg, xc], [edge, tip], color=style.INK2, lw=0.4, zorder=4, clip_on=False)
            ax.text(xc, tip - 0.04, txt, ha='center', va='bottom', fontsize=5, color=style.INK, zorder=4,
                    clip_on=False)


def cond_marker(ax, x, y, env, ms=3.0, **kw):
    ax.plot(x, y, ls='', marker=style.ENV_MARKER[env], ms=ms, mfc=style.ENV_COLOR[env], mec='white', mew=0.35, **kw)


def draw_a(fig, H, tab, tests):
    label(fig, 0, 0, 'a', 'Correct runs by domain', H)
    ax = axes_mm(fig, 33.0, 12.0, 22.0, 41.0, H)
    gal = tab[tab.env == GAL].set_index('domain')
    comp = [d for d in gal.value.sort_values(ascending=False).index if d not in BENCH_NAME.values()]
    order = comp + ['BixBench-Verified-50', 'IWC']
    ys = {d: i + (0.6 if d in ('BixBench-Verified-50', 'IWC') else 0) for i, d in enumerate(order)}
    for k, env in enumerate(ENVS):
        t = tab[tab.env == env].set_index('domain')
        for d in order:
            y = ys[d] + (k - 0.5) * 0.34
            ax.plot([t.loc[d, 'lo'], t.loc[d, 'hi']], [y, y], color=style.ENV_COLOR[env], lw=0.7, zorder=3,
                    clip_on=False)
            cond_marker(ax, t.loc[d, 'value'], y, env, ms=2.9, zorder=4, clip_on=False)
    ax.set_ylim(max(ys.values()) + 0.6, -0.6)
    ax.set_yticks([ys[d] for d in order], [f'{d} ({int(gal.loc[d, "tasks"])})' for d in order], fontsize=5.5)
    ax.tick_params(axis='y', length=0)
    ax.axhline(len(comp) - 0.2, color=style.NEUTRAL_MID, lw=0.5, zorder=1)
    ax.set_xlim(25, 104)                                 # room past 100% so markers are not clipped
    ax.set_xticks([25, 50, 75, 100])
    ax.spines['bottom'].set_bounds(25, 100)
    style.grid_x(ax)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Runs correct (%)')
    ax.text(-0.04, -0.75, 'CompBioBench domains (tasks)', transform=blended_transform_factory(ax.transAxes, ax.transData),
            ha='right', va='center', fontsize=5.5, fontweight='bold')
    hand = [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=2.9, mfc=style.ENV_COLOR[e], mec='white', mew=0.35,
                   label=style.ENV_LABEL[e]) for e in ENVS]
    ax.legend(handles=hand, loc='lower left', bbox_to_anchor=(-1.35, 1.07), ncol=2, fontsize=5.3, handletextpad=0.2,
              columnspacing=0.8, borderaxespad=0)
    worst = tests.p_holm.min()
    ax.text(1.0, 1.02, f'no domain differs\n(Holm-adjusted {fmt_p(worst).replace("= ", "≥ ")})',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=5, color=style.INK2, linespacing=1.15)


def draw_b(fig, H, tab, acc):
    label(fig, 62.0, 0, 'b', 'How each Galaxy run used Galaxy, and how it ended', H)
    ax = axes_mm(fig, 92.0, 13.0, 62.0, 40.0, H)
    rows = [(bm, c) for bm in BENCH for c in CFG]
    ypos = [i + 0.45 * BENCH.index(bm) for i, (bm, c) in enumerate(rows)]
    shares = [100 * tab.loc[(bm, c)].values / tab.loc[(bm, c)].sum() for bm, c in rows]
    stacked_rows(ax, ypos, shares, [col for _, _, col in ROUTES], 62.0, dark=(style.GALAXY, '#999999'))
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
        ax.text(-0.485, np.mean(ys), BENCH_NAME[bm].replace('-Verified-50', '-\nVerified-50'), transform=tr,
                ha='left', va='center', fontsize=5, fontweight='bold', linespacing=1.1)
    ax.text(1.12, -1.05, 'Runs', transform=tr, ha='right', va='center', fontsize=5, color=style.INK2)
    ax.text(1.28, -1.05, 'Correct', transform=tr, ha='right', va='center', fontsize=5, color=style.INK2)
    for y, (bm, c) in zip(ypos, rows):
        n = int(tab.loc[(bm, c)].sum())
        ax.text(1.12, y, f'{n}', transform=tr, ha='right', va='center', fontsize=5)
        a = acc.loc[(bm, c)]
        ax.text(1.28, y, f'{100 * a["mean"]:.0f}%', transform=tr, ha='right', va='center', fontsize=5)
    ax.text(-0.485, np.mean(ypos[-4:]) + 0.9, '(UDTs not\noffered)', transform=tr, ha='left', va='top',
            fontsize=5, color=style.INK2, linespacing=1.1)
    ax.legend(handles=[Patch(fc=col, ec=style.NEUTRAL_MID if col == '#CFE3F1' else col, lw=0.3, label=lab)
                       for _, lab, col in ROUTES], loc='lower left', bbox_to_anchor=(-0.485, 1.015), ncol=3,
              fontsize=5.0, handlelength=0.9, handletextpad=0.3, columnspacing=0.8, labelspacing=0.2, borderaxespad=0)


EPISODE_CHANNEL = {'galaxy_tool': 'Galaxy installed-tool jobs', 'galaxy_udt': 'Galaxy UDT jobs',
                   'galaxy_shell': 'shell (Galaxy runs)', 'code_shell': 'shell (custom code runs)'}


def draw_c(fig, H, y0, rates, burden, tab, fixed=None):
    label(fig, 0, y0, 'c', 'How often execution steps failed, and were fixed later', H)
    ax = axes_mm(fig, 33.0, y0 + 10.0, 26.0, 20.0, H)
    rr = rates.set_index('channel')
    ypos = [0, 1.3, 2.6, 4.1]
    for y, (code, name, env) in zip(ypos, CHANNELS):
        t = rr.loc[code]
        ax.plot([t.lo, t.hi], [y, y], color=style.ENV_COLOR[env], lw=0.8, zorder=3)
        cond_marker(ax, t.value, y, env, ms=3.2, zorder=4)
        ax.text(-0.04, y, f'{name}\n({int(t.steps):,})', transform=blended_transform_factory(ax.transAxes,
                ax.transData), ha='right', va='center', fontsize=5.5, linespacing=1.1)
        ax.text(t.hi + 1.5, y, f'{t.value:.0f}%' if t.value >= 10 else f'{t.value:.1f}%', ha='left', va='center',
                fontsize=5, color=style.INK2)
        if fixed is not None:
            f = fixed.loc[EPISODE_CHANNEL[code]]
            ax.text((62.5 - 33.0) / 26.0 * 60, y, f'{100 * f["mean"]:.0f}%', ha='center', va='center',
                    fontsize=5.5, clip_on=False)
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(-1.25, 1.3, 'Galaxy\nruns', transform=tr, ha='left', va='center', fontsize=5.5, fontweight='bold',
            linespacing=1.1)
    ax.text(-1.25, 4.1, 'Custom-\ncode runs', transform=tr, ha='left', va='center', fontsize=5.5, fontweight='bold',
            linespacing=1.1)
    ax.set_ylim(4.7, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 60)
    ax.set_xticks([0, 20, 40, 60])
    style.grid_x(ax)
    ax.set_xlabel('Steps that failed (%)', labelpad=1.5)
    if fixed is not None:
        ax.text((62.5 - 33.0) / 26.0 * 60, -1.15, 'Fixed\nlater', ha='center', va='center', fontsize=5,
                color=style.INK2, linespacing=1.05, clip_on=False)
    # all execution errors per run
    bx = axes_mm(fig, 33.0, y0 + 38.0, 26.0, 6.0, H)
    bb = burden.set_index('env')
    for y, env in enumerate([GAL, CODE]):
        t = bb.loc[env]
        bx.plot([t.lo, t.hi], [y, y], color=style.ENV_COLOR[env], lw=0.8, zorder=3)
        cond_marker(bx, t.value, y, env, ms=3.2, zorder=4)
        bx.text(-0.04, y, f'{style.ENV_LABEL[env].replace("Custom code", "Custom-code")} runs', transform=blended_transform_factory(bx.transAxes, bx.transData),
                ha='right', va='center', fontsize=5.5)
        bx.text(t.hi + 0.12, y, f'{t.value:.1f}', ha='left', va='center', fontsize=5, color=style.INK2)
    bx.set_ylim(1.6, -0.6)
    bx.set_yticks([])
    bx.spines['left'].set_visible(False)
    bx.set_xlim(0, 5)
    bx.set_xticks([0, 1, 2, 3, 4, 5])
    style.grid_x(bx)
    bx.set_xlabel('All execution errors per run', labelpad=1.5)
    # error types per channel, four groups
    cx = axes_mm(fig, 66.0, y0 + 10.0, 31.0, 20.0, H)
    shares = []
    for code, _, _ in CHANNELS:
        row = tab.loc[code]
        shares.append([100 * row[list(types)].sum() / row.sum() for _, types, _ in EGROUPS])
    stacked_rows(cx, ypos, shares, [c for _, _, c in EGROUPS], 31.0, bar_h=0.66, lead=0.30)
    cx.set_ylim(4.7, -0.6)
    cx.set_yticks([])
    cx.spines['left'].set_visible(False)
    cx.set_xlim(0, 100)
    cx.set_xticks([0, 50, 100])
    cx.set_xlabel('Error types (%)', labelpad=1.5)
    cx.legend(handles=[Patch(fc=c, label=n) for n, _, c in EGROUPS], loc='upper left', bbox_to_anchor=(0.0, -0.40),
              ncol=1, fontsize=5, handlelength=0.9, handletextpad=0.3, labelspacing=0.2, borderaxespad=0)


def draw_d(fig, H, y0, rec, bins_):
    label(fig, 103.0, y0, 'd', 'Final correctness among runs with execution errors', H)
    ax = axes_mm(fig, 113.0, y0 + 10.0, 66.0, 22.0, H)
    labs = [b[2] for b in ERROR_BINS]
    for k, env in enumerate(ENVS):
        t = bins_[(bins_.scope == 'all') & (bins_.env == env)].set_index('bin').reindex(labs)
        x = np.arange(len(labs)) + (k - 0.5) * 0.22
        ax.plot(x, t.value, color=style.ENV_COLOR[env], lw=0.5, zorder=2, alpha=0.6)
        for xi, (_, row) in zip(x, t.iterrows()):
            ax.plot([xi, xi], [row.lo, row.hi], color=style.ENV_COLOR[env], lw=0.8, zorder=3)
            cond_marker(ax, xi, row.value, env, ms=3.2, zorder=4)
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for i, lab in enumerate(labs):
        n = bins_[(bins_.scope == 'all') & (bins_.bin == lab)].set_index('env').n
        ax.text(i, -0.42, f'{int(n[CODE]):,}\n{int(n[GAL]):,}', transform=tr, ha='center', va='top', fontsize=5,
                color=style.INK2, linespacing=1.15)
    ax.text(-0.75, -0.42, 'Runs, custom code\nGalaxy', transform=tr, ha='right', va='top', fontsize=5,
            color=style.INK2, linespacing=1.15)
    ax.set_xticks(range(len(labs)), labs)
    ax.tick_params(axis='x', length=0, pad=1.5)
    ax.set_xlim(-0.6, len(labs) - 0.4)
    ax.set_ylim(40, 100)
    ax.set_yticks([40, 60, 80, 100])
    style.grid_y(ax)
    ax.set_xlabel('Execution errors in the run', labelpad=1.5)
    ax.set_ylabel('Runs correct (%)')
    hand = [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.2, mfc=style.ENV_COLOR[e], mec='white', mew=0.35,
                   label=style.ENV_LABEL[e]) for e in ENVS]
    ax.legend(handles=hand, ncol=2, loc='lower right', bbox_to_anchor=(1.0, 1.02), fontsize=5.3, handletextpad=0.2,
              columnspacing=0.8, borderaxespad=0)
    ax.text(0.02, 0.05, f'Runs with errors, Galaxy − custom code:\n'
            f'unadjusted {rec["unadjusted"]:+.1f} points ({fmt_p(rec["p_unadjusted"])})\n'
            f'adjusted for error bin, exploratory {rec["difference"]:+.1f} ({fmt_p(rec["p"])})',
            transform=ax.transAxes, ha='left', va='bottom', fontsize=5, linespacing=1.25)


def draw_e(fig, H, y0, tab, follow):
    label(fig, 0, y0, 'e', 'Parameter checks on installed-tool requests', H,
          'The interface compares the requested parameters with those Galaxy validated or recorded')
    ax = axes_mm(fig, 20.0, y0 + 12.0, 60.0, 19.0, H)
    rows = BENCH + ['all']
    ypos = [0, 1.3, 2.6, 4.0]
    shares = [100 * tab.loc[b].values / tab.loc[b].sum() for b in rows]
    stacked_rows(ax, ypos, shares, [col for _, _, col in CHECKS], 60.0, last_right=True,
                 dark=(style.NEUTRAL_DARK, style.OI_GREEN, style.OI_PURPLE))
    ax.set_ylim(4.55, -0.75)
    ax.set_yticks(ypos, ['BixBench-\nVerified-50', 'CompBioBench', 'IWC', 'All'], fontsize=5)
    ax.get_yticklabels()[-1].set_fontweight('bold')
    ax.tick_params(axis='y', length=0)
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Installed-tool requests (%)', labelpad=1.5)
    ax.text(1.0, 1.04, f'{int(tab.loc["all"].sum()):,} requests', transform=ax.transAxes, ha='right', va='bottom',
            fontsize=5, color=style.INK2)
    ax.legend(handles=[Patch(fc=col, ec=style.NEUTRAL_MID if col == '#E8E8E8' else col, lw=0.3, label=lab)
                       for _, lab, col in CHECKS], loc='upper left', bbox_to_anchor=(-0.28, -0.42), ncol=2,
              fontsize=5.0, handlelength=0.9, handletextpad=0.3, columnspacing=0.8, labelspacing=0.25, borderaxespad=0)
    f = follow.loc['diff_blocked']
    fig.text(4.4 / W, 1 - (y0 + 49.5) / H, f'After a request was blocked for a different value, the run later completed '
             f'a job of the same tool in {100 * f.completed:.0f}% of {int(f.requests):,} cases\n(with matching '
             f'parameters in {100 * f.matched:.0f}%). Matching parameters do not show that the settings were '
             f'scientifically appropriate.', fontsize=5, color=style.INK2, va='top', linespacing=1.25)


def draw_f(fig, H, y0, tab, runs_any, ainfo):
    label(fig, 90.0, y0, 'f', 'Failed requests and candidate infrastructure improvements', H,
          'Failure classes grouped by the change most likely to help (codebook in Source Data); an independent rater\n'
          f'reproduced {100 * ainfo["agree_classified"]:.0f}% of the classes and named the same improvement for '
          f'{100 * ainfo["fix_supported"]:.0f}% of requests')
    ax = axes_mm(fig, 133.0, y0 + 12.5, 28.0, 33.0, H)
    n = len(tab)
    ypos = [i + (0.4 if t.fix in UNRESOLVED else 0) for i, t in enumerate(tab.itertuples())]
    for y, t in zip(ypos, tab.itertuples()):
        grey = t.fix in UNRESOLVED
        ax.barh(y, t.requests, height=0.68, color=style.NEUTRAL_LIGHT if grey else style.GALAXY, zorder=3)
        ax.text(t.requests + 40, y, f'{t.requests:,} ({t.pct:.0f}%)', ha='left', va='center', fontsize=5)
        ax.text(1.62, y, f'{t.runs:,}', transform=blended_transform_factory(ax.transAxes, ax.transData), ha='right',
                va='center', fontsize=5)
    ax.text(1.62, -1.1, 'Runs', transform=blended_transform_factory(ax.transAxes, ax.transData), ha='right',
            va='center', fontsize=5, color=style.INK2)
    ax.set_ylim(max(ypos) + 0.6, -0.6)
    ax.set_yticks(ypos, tab.fix, fontsize=5.5)
    ax.tick_params(axis='y', length=0)
    ax.axhline(ypos[n - 3] + 0.7, color=style.NEUTRAL_MID, lw=0.5, zorder=1)
    ax.set_xlim(0, tab.requests.max() * 1.45)
    ax.set_xticks([0, 500, 1000, 1500])
    style.grid_x(ax)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel(f'Failed requests (of {int(tab.requests.sum()):,}; {runs_any:,} runs)', labelpad=1.5)


def save(fig, name, title):
    style.enforce_min_font(fig)
    fig.savefig(os.path.join(OUT, f'{name}.svg'), metadata={'Title': title})
    fig.savefig(os.path.join(OUT, f'{name}.pdf'), metadata={'Title': title})
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(os.path.join(OUT, f'{name}.png'), dpi=(600, 600))
    plt.close(fig)

rng = np.random.default_rng(0)   # the archive script's jitter generator; replay restores its state before each call


def main():
    panel_io.replay(DATA / 'figure_panels' / 'fig3.json', globals(), names=['fig3'])
    for ext in ('pdf', 'png', 'svg'):
        os.replace(HERE / f'fig3.{ext}', HERE / f'fig3_structured_environment.{ext}')
    shutil.copyfile(DATA / 'figure_panels' / 'fig3_source_data.csv', HERE / 'source_data.csv')


if __name__ == '__main__':
    main()
