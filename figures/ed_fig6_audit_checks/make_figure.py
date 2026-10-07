#!/usr/bin/env python3
"""Extended Data Fig. 6: Independent checks of the audits and of benchmark integrity.

Drawing code copied unchanged from the run archive, paulocilasjr/Galaxy_benchmark@b3cbb944648a57104a6837d1640b255854dd7e3e:figures/make_ed_validation.py; the panel data are the
values that script computed and passed to its drawing functions (data/figure_panels/ed_fig6.json, written by the
archive's figures/panel_io.py and copied by analysis/export_galaxy_benchmark_tables.py). Nothing is recomputed here:
every number traces to the archive script at that commit. Writes, next to this script, ed_fig6_audit_checks.pdf, .png (600 dpi)
and .svg, and source_data.csv (the archive's ed_fig6_source_data.csv).

Regenerate with: python figures/ed_fig6_audit_checks/make_figure.py
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
from matplotlib.patches import Patch
from matplotlib.transforms import blended_transform_factory
import io
import numpy as np
import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})


style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}


W, MM, B, SEED = 180.0, 1 / 25.4, 20000, 20261002


ENVS = style.ENVS


BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}


TIERS = [('verified', 'Answers seen in the trace', '#882255'), ('probable', 'Opened a page with answers', '#CC6677'),
         ('attempted', 'Searched for the benchmark', '#DDCC77'), ('none', 'No benchmark search', '#E8E8E8')]


GROUPS = ['Validation', 'Benchmark', 'Knowledge', 'Galaxy', 'No answer']


def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H, note=None):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')
    if note:
        fig.text((x + 4.4) / W, 1 - (y + 4.4) / H, note, fontsize=5, color=style.INK2, va='top', ha='left',
                 linespacing=1.2)


def ed6(counts, sens, acc, tab, cinfo, per, ainfo):
    H = 112.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    label(fig, 0, 0, 'a', 'Runs that reached benchmark answers during the run', H,
          'Highest tier per run, from the traces (web pages themselves are not logged)')
    ax = axes_mm(fig, 40.0, 14.0, 44.0, 20.0, H)
    rows = [(bm, env) for bm in ('BixBench50', 'CompBio', 'IWC') for env in ENVS]
    ypos = [0, 1, 2.4, 3.4, 4.8, 5.8]
    for (bm, env), y in zip(rows, ypos):
        t = counts.loc[(bm, env)] if (bm, env) in counts.index else pd.Series(0, index=[x for x, _, _ in TIERS])
        n, left = t.sum(), 0
        for code, _, col in TIERS:
            v = 100 * t[code] / n
            ax.barh(y, v, left=left, height=0.7, color=col, ec='white', lw=0.3, zorder=3)
            left += v
        exposed = int(t['verified'] + t['probable'])
        ax.text(101.5, y, f'{exposed} / {int(n):,}', ha='left', va='center', fontsize=5)
        ax.text(-1.5, y, style.ENV_LABEL[env], ha='right', va='center', fontsize=5)
    for bm, y in (('BixBench50', 0.5), ('CompBio', 2.9), ('IWC', 5.3)):
        ax.text(-0.42, y, BENCH_NAME[bm].replace('-Verified-50', '-\nVerified-50'),
                transform=blended_transform_factory(ax.transAxes, ax.transData), ha='right', va='center', fontsize=5,
                fontweight='bold', linespacing=1.1)
    ax.text(101.5, -1.0, 'Exposed / runs', ha='left', va='center', fontsize=5, color=style.INK2)
    ax.set_ylim(6.4, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Runs (%)', labelpad=1.5)
    ax.legend(handles=[Patch(fc=c, ec=style.NEUTRAL_MID if c == '#E8E8E8' else c, lw=0.3, label=l) for _, l, c in TIERS],
              loc='upper left', bbox_to_anchor=(-0.85, -0.32), ncol=2, fontsize=5, handlelength=0.9,
              columnspacing=0.8, labelspacing=0.25, borderaxespad=0)

    label(fig, 100.0, 0, 'b', 'Galaxy minus custom code without exposed runs', H)
    bx = axes_mm(fig, 146.0, 12.0, 32.0, 26.0, H)
    y = 0
    for bm in ('BixBench50', 'CompBio'):
        bx.text(-1.38, y, BENCH_NAME[bm], transform=blended_transform_factory(bx.transAxes, bx.transData), ha='left',
                va='center', fontsize=5, fontweight='bold')
        y += 0.9
        for t in sens[sens.benchmark == bm].itertuples():
            bx.plot([t.lo, t.hi], [y, y], color=style.INK, lw=0.7)
            bx.plot(t.diff, y, ls='', marker='D' if t.population == 'All runs' else 'o', ms=2.6,
                    mfc=style.INK if t.population == 'All runs' else 'white', mec=style.INK, mew=0.6)
            bx.text(-0.04, y, f'{t.population} ({t.runs:,})', transform=blended_transform_factory(bx.transAxes,
                    bx.transData), ha='right', va='center', fontsize=5)
            y += 0.9
        y += 0.4
    bx.axvline(0, color=style.INK2, lw=0.6)
    bx.set_ylim(y - 0.4, -0.6)
    bx.set_yticks([])
    bx.spines['left'].set_visible(False)
    bx.set_xlim(-8, 8)
    style.grid_x(bx)
    bx.set_xlabel('Runs correct, percentage points', labelpad=1.5)

    label(fig, 0, 54.0, 'c', 'Second rater for the failure-cause audit (BixBench-Verified-50)', H,
          f'{cinfo["items"]} incorrect runs; agreement {100 * cinfo["agree"]:.0f}%, Cohen\'s κ = {cinfo["kappa"]:.2f}; '
          f'{100 * cinfo["either"]:.0f}% counting secondary causes')
    cx = axes_mm(fig, 30.0, 66.0, 32.0, 32.0, H)
    m = tab.values.astype(float)
    cx.imshow(m, cmap='Greys', vmin=0, vmax=m.max() * 1.3)
    for i in range(len(GROUPS)):
        for j in range(len(GROUPS)):
            cx.text(j, i, f'{int(m[i, j])}', ha='center', va='center', fontsize=5,
                    color='white' if m[i, j] > m.max() * 0.6 else style.INK, fontweight='bold' if i == j else 'normal')
    cx.set_xticks(range(len(GROUPS)), GROUPS, fontsize=5, rotation=45, ha='right')
    cx.set_yticks(range(len(GROUPS)), GROUPS, fontsize=5)
    cx.tick_params(length=0, pad=1.5)
    for s in cx.spines.values():
        s.set_visible(False)
    cx.set_xlabel('Second rater', labelpad=1.5)
    cx.set_ylabel('Original audit', labelpad=1.5)

    label(fig, 100.0, 54.0, 'd', 'Second rater for the failure classes of failed requests', H,
          f'{ainfo["items"]} requests, 10 per class; agreement {100 * ainfo["agree_classified"]:.0f}% for classified '
          f'requests\n(κ = {ainfo["kappa_classified"]:.2f}); the rule\'s improvement group was among the rater\'s in '
          f'{100 * ainfo["fix_supported"]:.0f}%')
    dx = axes_mm(fig, 108.0, 70.0, 70.0, 22.0, H)
    order = [c for c in ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'B1', 'B2', 'B3', 'B4', 'B5', 'X', 'Z']
             if c in per.index]
    vals = [100 * per.loc[c, 'sum'] / per.loc[c, 'size'] for c in order]
    dx.bar(range(len(order)), vals, width=0.7, color=style.NEUTRAL_DARK, zorder=3)
    dx.set_xticks(range(len(order)), order, fontsize=5)
    dx.tick_params(axis='x', length=0)
    dx.set_ylim(0, 100)
    dx.set_yticks([0, 50, 100])
    style.grid_y(dx)
    dx.set_ylabel('Same class (%)')
    dx.text(1.0, -0.22, f'Rater judged the failure an agent error only in {100 * ainfo["agent_only"]:.0f}%; more than '
            f'one improvement plausible in {100 * ainfo["multiple"]:.0f}%', transform=dx.transAxes, ha='right',
            va='top', fontsize=5, color=style.INK2)
    save(fig, 'ed_fig6', 'Extended Data Fig. 6 | Independent checks of the audits and of benchmark integrity')


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
    panel_io.replay(DATA / 'figure_panels' / 'ed_validation.json', globals(), names=['ed_fig6'])
    for ext in ('pdf', 'png', 'svg'):
        os.replace(HERE / f'ed_fig6.{ext}', HERE / f'ed_fig6_audit_checks.{ext}')
    shutil.copyfile(DATA / 'figure_panels' / 'ed_fig6_source_data.csv', HERE / 'source_data.csv')


if __name__ == '__main__':
    main()
