#!/usr/bin/env python3
"""Extended Data Fig. 3: Task status, execution errors and final correctness.

Drawing code copied unchanged from the run archive, paulocilasjr/Galaxy_benchmark@b3cbb944648a57104a6837d1640b255854dd7e3e:figures/make_fig3.py; the panel data are the
values that script computed and passed to its drawing functions (data/figure_panels/ed_fig3.json, written by the
archive's figures/panel_io.py and copied by analysis/export_galaxy_benchmark_tables.py). Nothing is recomputed here:
every number traces to the archive script at that commit. Writes, next to this script, ed_fig3_execution_errors.pdf, .png (600 dpi)
and .svg, and source_data.csv (the archive's ed_fig3_source_data.csv).

Regenerate with: python figures/ed_fig3_execution_errors/make_figure.py
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


ETYPES = [('Code, parameter or syntax error', '#44BB99'), ('Missing software, package or container', '#BBCC33'),
          ('File, path or input format', '#EEDD88'), ('Time or memory limit', '#FFAABB'),
          ('Network or download', '#99DDFF'), ('Galaxy job never started', '#AAAA00'),
          ('No or unclassified message', style.NEUTRAL_LIGHT)]


CHANNELS = [('galaxy_tool', 'Installed-tool jobs', GAL), ('galaxy_udt', 'UDT jobs', GAL),
            ('galaxy_shell', 'Shell commands', GAL), ('code_shell', 'Shell commands', CODE)]


ERROR_BINS = [(0, 0, '0'), (1, 2, '1–2'), (3, 5, '3–5'), (6, 10, '6–10'), (11, 10 ** 9, '>10')]


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


def ed_status(fig, H, y0, status):
    label(fig, 0, y0, 'a', 'Correct runs of three for every task, model and condition', H)
    cols = [(c, e) for c in CFG for e in ENVS]
    m = status[[f'{c}|{e}' for c, e in cols]].values.T.astype(float)   # rows: model x condition; columns: tasks
    ax = axes_mm(fig, 33.0, y0 + 8.0, 146.0, 17.0, H)
    cmap = plt.matplotlib.colors.ListedColormap(['#F2F1EE', '#C9C8C3', '#8A8A8A', '#1A1A1A'])
    ax.imshow(m, aspect='auto', cmap=cmap, vmin=-0.5, vmax=3.5, interpolation='nearest')
    ax.set_yticks(range(len(cols)), [f'{c} · {style.ENV_LABEL[e]}' for c, e in cols], fontsize=5)
    ax.tick_params(length=0, pad=1.5)
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    for y in np.arange(1.5, len(cols) - 1, 2):
        ax.axhline(y, color='white', lw=0.8)
    groups = status.domain.values
    start = 0
    for i in range(1, len(groups) + 1):
        if i == len(groups) or groups[i] != groups[start]:
            name = groups[start]
            ax.axvline(i - 0.5, color='white', lw=0.8) if i < len(groups) else None
            ax.plot([start - 0.3, i - 0.7], [len(cols) - 0.2] * 2, color=style.INK2, lw=0.5, clip_on=False)
            short = {'BixBench-Verified-50': 'BixBench-Verified-50', 'Population genetics': 'Pop. gen.',
                     'Machine learning': 'ML', 'Spatial and structure': 'Sp.', 'Transcriptomics': 'Transcript.',
                     'Epigenomics': 'Epigenomics', 'Single-cell': 'Single-cell', 'Genomics': 'Genomics', 'IWC': 'IWC'}
            ax.text((start + i - 1) / 2, len(cols) + 0.4, short.get(name, name), ha='center', va='top', fontsize=5,
                    rotation=0)
            start = i
    ax.text(0.5, len(cols) + 2.2, 'CompBioBench domains between BixBench-Verified-50 and IWC; tasks sorted by '
            'correct runs within each group', transform=blended_transform_factory(ax.transAxes, ax.transData),
            ha='center', va='top', fontsize=5, color=style.INK2)
    ax.legend(handles=[Patch(fc=cmap(k), ec=style.NEUTRAL_MID, lw=0.3, label=f'{k} of 3') for k in range(4)],
              loc='lower right', bbox_to_anchor=(1.0, 1.02), ncol=4, fontsize=5, handlelength=0.9, borderaxespad=0,
              title='Correct runs', title_fontsize=5)


def ed_types(fig, H, y0, tab, runs):
    label(fig, 0, y0, 'b', 'Execution errors by type and channel (all seven types)', H)
    ax = axes_mm(fig, 30.0, y0 + 9.0, 70.0, 22.0, H)
    shares = [100 * tab.loc[c].values / tab.loc[c].sum() for c, _, _ in CHANNELS]
    ypos = [0, 1.6, 3.2, 5.0]
    stacked_rows(ax, ypos, shares, [col for _, col in ETYPES], 70.0, bar_h=0.78)
    ax.set_ylim(5.6, -1.2)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Errors (%)')
    for y, (c, name, env) in zip(ypos, CHANNELS):
        ax.text(-1.5, y, f'{name} ({"Galaxy" if env == GAL else "custom-code"} runs)', ha='right', va='center', fontsize=5)
        n = int(tab.loc[c].sum())
        ax.text(101.5, y, f'{n:,} ({n / runs[env]:.1f}/run)', ha='left', va='center', fontsize=5, color=style.INK2)
    ax.legend(handles=[Patch(fc=col, label=lab) for lab, col in ETYPES], loc='upper left', bbox_to_anchor=(1.25, 1.0),
              ncol=1, fontsize=5.0, handlelength=0.9, handletextpad=0.3, labelspacing=0.25, borderaxespad=0)


def ed_recovery(fig, H, y0, bins_, by_bm):
    label(fig, 0, y0, 'c', 'Final correctness by execution errors, per benchmark', H)
    labs = [b[2] for b in ERROR_BINS]
    for j, bm in enumerate(BENCH):
        ax = axes_mm(fig, 14.0 + j * 56.0, y0 + 10.0, 48.0, 24.0, H)
        for k, env in enumerate(ENVS):
            t = bins_[(bins_.scope == bm) & (bins_.env == env)].set_index('bin').reindex(labs)
            x = np.arange(len(labs)) + (k - 0.5) * 0.22
            for xi, (_, row) in zip(x, t.iterrows()):
                if np.isnan(row.value):
                    continue
                ax.plot([xi, xi], [row.lo, row.hi], color=style.ENV_COLOR[env], lw=0.8, zorder=3)
                cond_marker(ax, xi, row.value, env, ms=3.0, zorder=4)
        ax.set_xticks(range(len(labs)), labs)
        ax.tick_params(axis='x', length=0, pad=1.5)
        ax.set_xlim(-0.6, len(labs) - 0.4)
        ax.set_ylim(0, 104)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.spines['left'].set_bounds(0, 100)
        style.grid_y(ax)
        ax.set_xlabel('Execution errors in the run')
        if j == 0:
            ax.set_ylabel('Runs correct (%)')
        t = by_bm.set_index('benchmark').loc[bm]
        ax.set_title(f'{BENCH_NAME[bm]}: {t.unadjusted:+.1f} points, unadjusted ({fmt_p(t.p_unadjusted)})', fontsize=5.5,
                     fontweight='bold', loc='left', pad=3)


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
    panel_io.replay(DATA / 'figure_panels' / 'fig3.json', globals(), names=['ed_fig3'])
    for ext in ('pdf', 'png', 'svg'):
        os.replace(HERE / f'ed_fig3.{ext}', HERE / f'ed_fig3_execution_errors.{ext}')
    shutil.copyfile(DATA / 'figure_panels' / 'ed_fig3_source_data.csv', HERE / 'source_data.csv')


if __name__ == '__main__':
    main()
