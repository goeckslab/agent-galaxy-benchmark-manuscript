#!/usr/bin/env python3
"""Extended Data Fig. 7: Verification, recovery and selected cases.

Drawing code copied unchanged from the run archive, paulocilasjr/Galaxy_benchmark@0dbf3f443b83a91322098c9918d86a5846129215:figures/make_ed_validation.py; the panel data are the
values that script computed and passed to its drawing functions (data/figure_panels/ed_fig7.json, written by the
archive's figures/panel_io.py and copied by analysis/export_galaxy_benchmark_tables.py). Nothing is recomputed here:
every number traces to the archive script at that commit. Writes, next to this script, ed_fig7_verification_recovery.pdf, .png (600 dpi)
and .svg, and source_data.csv (the archive's ed_fig7_source_data.csv).

Regenerate with: python figures/ed_fig7_verification_recovery/make_figure.py
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
from matplotlib.patches import Rectangle
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


CODE, GAL = ENVS


CFG = style.CONFIGS


CHECKS = [('V1', 'Count or denominator'), ('V2', 'Independent recomputation'), ('V3', 'Sensitivity analysis'),
          ('V4', 'Assumption check on inputs'), ('V5', 'Plausibility'), ('V6', 'Domain diagnostic'),
          ('any', 'Any check')]


def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H, note=None):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')
    if note:
        fig.text((x + 4.4) / W, 1 - (y + 4.4) / H, note, fontsize=5, color=style.INK2, va='top', ha='left',
                 linespacing=1.2)


def ed7(ver, changed, eps, ex, case):
    H = 150.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    label(fig, 0, 0, 'a', 'Verification checks in 80 coded runs (coder blind to the grade)', H,
          '10 runs per benchmark × condition × outcome; 95% Wilson intervals')
    for j, (by, groups, title) in enumerate((('ok', [(1, 'Correct', style.INK), (0, 'Incorrect', '#999999')],
                                               'By outcome'),
                                              ('env', [(CODE, 'Custom code', style.CODE), (GAL, 'Galaxy', style.GALAXY)],
                                               'By condition'))):
        ax = axes_mm(fig, 40.0 + j * 50.0, 14.0, 40.0, 32.0, H)
        for k, (val, lab, col) in enumerate(groups):
            d = ver[(ver.by == by) & (ver.group == val)].set_index('check').reindex([c for c, _ in CHECKS])
            y = np.arange(len(CHECKS)) + (k - 0.5) * 0.3
            ax.errorbar(d.value, y, xerr=[d.value - d.lo, d.hi - d.value], fmt='o' if k == 0 else 's', ms=2.8,
                        color=col, mfc=col, mec='white', mew=0.3, elinewidth=0.7, capsize=0, label=lab)
        ax.set_yticks(range(len(CHECKS)), [l for _, l in CHECKS] if j == 0 else [''] * len(CHECKS), fontsize=5)
        ax.set_ylim(len(CHECKS) - 0.4, -0.6)
        ax.set_xlim(0, 100)
        style.grid_x(ax)
        ax.tick_params(axis='y', length=0)
        ax.set_xlabel('Runs with the check (%)', labelpad=1.5)
        ax.set_title(title, fontsize=5.5, fontweight='bold', pad=3, loc='left')
        ax.legend(loc='lower right', bbox_to_anchor=(1.0, 1.0), ncol=2, fontsize=5, borderaxespad=0.2,
                  handletextpad=0.2, columnspacing=0.8)
    yes = changed.get('yes', pd.Series(0, index=changed.index))
    fig.text(142.0 / W, 1 - 16.0 / H, 'A check changed the method\nor answer in\n'
             f'{int(yes.get(1, 0))} of {int(changed.loc[1].sum())} correct runs\n'
             f'{int(yes.get(0, 0))} of {int(changed.loc[0].sum())} incorrect runs', fontsize=5, va='top',
             linespacing=1.3)

    label(fig, 0, 56.0, 'b', 'Failed steps later re-run without error in the same run', H,
          'Galaxy jobs by tool; shell commands by the analysis program or script they ran (inline code excluded)')
    bx = axes_mm(fig, 40.0, 70.0, 50.0, 20.0, H)
    for i, t in enumerate(eps.itertuples()):
        bx.barh(i, t.resolved, height=0.6, color=style.ENV_COLOR[t.env], zorder=3, alpha=0.85)
        bx.plot([t.lo, t.hi], [i, i], color=style.INK, lw=0.7, zorder=4)
        bx.text(-1.5, i, f'{t.channel.replace("shell", "Shell commands").replace("custom code", "custom-code")} ({t.episodes:,})', ha='right', va='center',
                fontsize=5)
        bx.text(101.5, i, f'{t.correct_resolved:.0f}% / {t.correct_unresolved:.0f}%', ha='left', va='center',
                fontsize=5)
    bx.text(101.5, -1.0, 'Runs correct: re-run / not', ha='left', va='center', fontsize=5, color=style.INK2)
    bx.set_ylim(len(eps) - 0.4, -0.6)
    bx.set_yticks([])
    bx.spines['left'].set_visible(False)
    bx.set_xlim(0, 100)
    style.grid_x(bx)
    bx.set_xlabel('Failed steps later re-run without error (%)', labelpad=1.5)

    label(fig, 0, 100.0, 'c', 'A parameter check that stopped a job', H)
    cx = axes_mm(fig, 4.0, 108.0, 84.0, 36.0, H)
    cx.set_axis_off()
    cx.set_xlim(0, 84)
    cx.set_ylim(36, 0)
    cx.add_patch(Rectangle((0, 0), 84, 36, fc=style.LIGHT, ec='none'))
    lines = [('Task', 'bix-43-q4, GPT-5.5, Galaxy, replicate 1 (Reactome enrichment)'),
             ('Tool', ex['tool']),
             ('First request', ex['first_form']),
             ('Interface check', f'{ex["path"]}: requested {ex["requested"]},\nGalaxy would bind {ex["resolved"]}; '
                                 'the job was not submitted'),
             ('Agent response', 'Resubmitted with flat parameter keys'),
             ('Second request', ex['fixed_form'] + '; parameters matched; job ran')]
    y = 2.5
    for k, v in lines:
        cx.text(1.5, y, k, fontsize=5, fontweight='bold', va='top')
        cx.text(20.0, y, v, fontsize=5, va='top', linespacing=1.2)
        y += 4.6 + 2.2 * v.count('\n')

    label(fig, 92.0, 100.0, 'd', 'A selected case: variant-status-q1 (CompBioBench)', H,
          'Read-end artefacts mimic an alternate allele; answers are not shown')
    dx = axes_mm(fig, 96.0, 112.0, 84.0, 32.0, H)
    dx.set_axis_off()
    dx.set_xlim(0, 84)
    dx.set_ylim(32, 0)
    xs = {CODE: 36.0, GAL: 58.0}
    for env in ENVS:
        dx.text(xs[env] + 2.6, 1.0, style.ENV_LABEL[env], fontsize=5, ha='center', va='top', fontweight='bold')
    for i, c in enumerate(CFG):
        y = 6.5 + i * 3.4
        dx.text(1.0, y, c, fontsize=5, va='center')
        for env in ENVS:
            for rep in (1, 2, 3):
                row = case[(case.cfg == c) & (case.env == env) & (case.replicate == rep)]
                ok = bool(row.ok.iloc[0]) if len(row) else False
                dg = bool(row.diagnostic.iloc[0]) if len(row) else False
                x = xs[env] + (rep - 1) * 2.6
                dx.plot(x, y, ls='', marker='o', ms=2.8, mfc=style.INK if ok else 'white', mec=style.INK, mew=0.5)
                if dg:
                    dx.add_patch(Rectangle((x - 1.1, y - 1.1), 2.2, 2.2, fill=False, ec=style.OI_VERMILLION
                                           if env == CODE else style.GALAXY, lw=0.6))
    n_ok = int(case.ok.sum())
    n_dg = int(case.diagnostic.sum())
    cc = case[(case.env == CODE) & case.diagnostic]
    dx.text(1.0, 22.0, f'● accepted   ○ rejected   □ ran a read-position diagnostic ({n_dg} runs)\n'
            f'{n_ok} of {len(case)} runs accepted. GPT-5.6 Sol in Galaxy ran the diagnostic as a UDT in\n'
            f'replicates 2 and 3, and both were accepted; {len(cc)} custom-code runs also ran it '
            f'({int(cc.ok.sum())} accepted).', fontsize=5, va='top', linespacing=1.3)
    save(fig, 'ed_fig7', 'Extended Data Fig. 7 | Verification, recovery and selected cases')


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
    panel_io.replay(DATA / 'figure_panels' / 'ed_validation.json', globals(), names=['ed_fig7'])
    for ext in ('pdf', 'png', 'svg'):
        os.replace(HERE / f'ed_fig7.{ext}', HERE / f'ed_fig7_verification_recovery.{ext}')
    shutil.copyfile(DATA / 'figure_panels' / 'ed_fig7_source_data.csv', HERE / 'source_data.csv')


if __name__ == '__main__':
    main()
