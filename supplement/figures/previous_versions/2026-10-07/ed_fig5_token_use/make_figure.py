#!/usr/bin/env python3
"""Extended Data Fig. 5: Token use by model, outcome and action count.

Drawing code copied unchanged from the run archive, paulocilasjr/Galaxy_benchmark@b3cbb944648a57104a6837d1640b255854dd7e3e:figures/make_fig5.py; the panel data are the
values that script computed and passed to its drawing functions (data/figure_panels/ed_fig5.json, written by the
archive's figures/panel_io.py and copied by analysis/export_galaxy_benchmark_tables.py). Nothing is recomputed here:
every number traces to the archive script at that commit. Writes, next to this script, ed_fig5_token_use.pdf, .png (600 dpi)
and .svg, and source_data.csv (the archive's ed_fig5_source_data.csv).

Regenerate with: python figures/ed_fig5_token_use/make_figure.py
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
import io
import numpy as np
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})


style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition


B, SEED, B_PERM, B_MEDIAN = 20000, 20261002, 200000, 2000


W, MM = 180.0, 1 / 25.4


CFG = style.CONFIGS


ENVS = style.ENVS                                    # custom code first, always


BENCH = style.BENCH


BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}


TICK = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6\nSol', 'GPT-5.6 Luna': 'GPT-5.6\nLuna',
        'DeepSeek V4 Pro': 'DeepSeek\nV4 Pro'}


MODEL_COLOR = dict(zip(CFG, ['#117733', '#AA4499', '#DDCC77', '#332288']))


def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H, note=None):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')
    if note:
        fig.text((x + 4.4) / W, 1 - (y + 4.4) / H, note, fontsize=5, color=style.INK2, va='top', ha='left',
                 linespacing=1.2)


def ed_trade(fig, H, tt):
    label(fig, 0, 0, 'a', 'Score and input tokens per model and condition', H,
          'Points, mean score (IWC, output agreement) and median input tokens per run, with 95% intervals')
    for j, bm in enumerate(BENCH):
        ax = axes_mm(fig, 12.0 + j * 57.0, 13.0, 48.0, 32.0, H)
        d = tt[tt.benchmark == bm]
        for t in d.itertuples():
            ax.plot([t.t_lo / 1e6, t.t_hi / 1e6], [t.score, t.score], color=MODEL_COLOR[t.cfg], lw=0.6, zorder=2)
            ax.plot([t.tokens / 1e6] * 2, [t.s_lo, t.s_hi], color=MODEL_COLOR[t.cfg], lw=0.6, zorder=2)
            ax.plot(t.tokens / 1e6, t.score, ls='', marker=style.ENV_MARKER[t.env], ms=3.4, mfc=MODEL_COLOR[t.cfg],
                    mec=style.INK, mew=0.35, zorder=3)
        ax.set_xscale('log')
        ax.set_xlim(0.1, 40)
        ax.set_xticks([0.1, 1, 10], ['0.1', '1', '10'])
        ax.minorticks_off()
        ax.set_ylim(60, 101)
        style.grid_y(ax)
        ax.set_xlabel('Median input tokens per run (millions)')
        if j == 0:
            ax.set_ylabel('Score (%)')
        ax.set_title(BENCH_NAME[bm] + (' (agreement × 100)' if bm == 'IWC' else ''), fontsize=5.5, fontweight='bold',
                     loc='left', pad=3)
    hand = [Line2D([], [], ls='', marker='o', ms=3.2, mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35, label=c) for c in CFG]
    hand += [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.2, mfc=style.NEUTRAL_MID, mec=style.INK, mew=0.35,
                    label=style.ENV_LABEL[e]) for e in ENVS]
    fig.legend(handles=hand, ncol=6, loc='upper right', bbox_to_anchor=(1.0, 1 - 0.6 / H), fontsize=5,
               handletextpad=0.2, columnspacing=0.8, borderaxespad=0, frameon=False)


def box(ax, x, values, color, tint, solid, width=0.34):
    """Box (middle 50%, median), whiskers to 1.5 x IQR, and every run as a dot."""
    v = np.asarray(values, float)
    v = v[np.isfinite(v) & (v > 0)]
    lv = np.log10(v)
    q1, med, q3 = np.percentile(lv, [25, 50, 75])
    lo_w, hi_w = lv[lv >= q1 - 1.5 * (q3 - q1)].min(), lv[lv <= q3 + 1.5 * (q3 - q1)].max()
    ax.scatter(x + rng.uniform(-width * 0.38, width * 0.38, len(v)), v, s=0.6, color=style.INK, alpha=0.22, lw=0,
               zorder=2, rasterized=True)
    ax.add_patch(plt.Rectangle((x - width / 2, 10 ** q1), width, 10 ** q3 - 10 ** q1, fc=color if solid else tint,
                               ec=color, lw=0.6, alpha=0.85, zorder=3))
    ax.plot([x - width / 2, x + width / 2], [10 ** med] * 2, color='white' if solid else style.INK, lw=0.9, zorder=4,
            solid_capstyle='butt')
    for a_, b_ in ((10 ** lo_w, 10 ** q1), (10 ** q3, 10 ** hi_w)):
        ax.plot([x, x], [a_, b_], color=color, lw=0.6, zorder=3)


def ed_siblings(fig, H, y0, r, per):
    label(fig, 0, y0, 'b', 'Input tokens of correct (light) and incorrect (solid) runs', H)
    for j, env in enumerate(ENVS):
        ax = axes_mm(fig, 12.0 + j * 46.0, y0 + 9.0, 42.0, 28.0, H)
        ax.set_yscale('log')
        ax.set_ylim(0.01, 1000)
        ax.set_yticks([0.01, 0.1, 1, 10, 100], ['0.01', '0.1', '1', '10', '100'] if j == 0 else [''] * 5)
        ax.minorticks_off()
        style.grid_y(ax)
        if j == 0:
            ax.set_ylabel('Input tokens per run (millions)')
        for i, c in enumerate(CFG):
            d = r[(r.cfg == c) & (r.env == env)]
            box(ax, i - 0.21, d[d.ok].input_tokens / 1e6, style.ENV_COLOR[env], style.ENV_TINT[env], solid=False)
            box(ax, i + 0.21, d[~d.ok].input_tokens / 1e6, style.ENV_COLOR[env], style.ENV_TINT[env], solid=True)
            t = per[(per.env == env) & (per.cfg == c)].iloc[0]
            ax.text(i, 400, f'{t.ratio:.2f}×', ha='center', va='center', fontsize=5, color=style.INK2)
        ax.set_xticks(range(len(CFG)), [TICK[c] for c in CFG], fontsize=5)
        ax.tick_params(axis='x', length=0, pad=2)
        ax.set_xlim(-0.6, len(CFG) - 0.4)
        ax.set_title(style.ENV_LABEL[env], fontsize=5.5, fontweight='bold', loc='left', pad=3)


def ed_actions(fig, H, y0, r):
    label(fig, 96.0, y0, 'c', 'Input tokens against actions (all runs)', H)
    ax = axes_mm(fig, 108.0, y0 + 9.0, 70.0, 28.0, H)
    d = r.dropna(subset=['input_tokens', 'actions'])
    d = d[d.actions > 0]
    for env in ENVS:
        e = d[d.env == env]
        ax.scatter(e.actions, e.input_tokens / 1e6, s=1.0, marker=style.ENV_MARKER[env], color=style.ENV_COLOR[env],
                   alpha=0.25, lw=0, zorder=2, rasterized=True, label=style.ENV_LABEL[env])
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1, 2000)
    ax.set_ylim(0.005, 300)
    ax.set_xticks([1, 10, 100, 1000], ['1', '10', '100', '1,000'])
    ax.set_yticks([0.01, 0.1, 1, 10, 100], ['0.01', '0.1', '1', '10', '100'])
    ax.minorticks_off()
    style.grid_y(ax)
    style.grid_x(ax)
    ax.set_xlabel('Actions per run')
    ax.set_ylabel('Input tokens (millions)')
    ax.legend(markerscale=4, loc='upper left', fontsize=5, borderaxespad=0.3)


def save(fig, name, title):
    style.enforce_min_font(fig)
    fig.savefig(os.path.join(OUT, f'{name}.svg'), metadata={'Title': title}, dpi=600)
    fig.savefig(os.path.join(OUT, f'{name}.pdf'), metadata={'Title': title}, dpi=600)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(os.path.join(OUT, f'{name}.png'), dpi=(600, 600))
    plt.close(fig)

rng = np.random.default_rng(0)   # the archive script's jitter generator; replay restores its state before each call


def main():
    panel_io.replay(DATA / 'figure_panels' / 'fig5.json', globals(), names=['ed_fig5'])
    for ext in ('pdf', 'png', 'svg'):
        os.replace(HERE / f'ed_fig5.{ext}', HERE / f'ed_fig5_token_use.{ext}')
    shutil.copyfile(DATA / 'figure_panels' / 'ed_fig5_source_data.csv', HERE / 'source_data.csv')


if __name__ == '__main__':
    main()
