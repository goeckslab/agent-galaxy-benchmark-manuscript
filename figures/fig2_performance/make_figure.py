#!/usr/bin/env python3
"""Figure 2: Agents show similar observed benchmark performance in Galaxy and custom code.

Drawing code copied unchanged from the run archive, paulocilasjr/Galaxy_benchmark@b3cbb944648a57104a6837d1640b255854dd7e3e:figures/make_fig2.py; the panel data are the
values that script computed and passed to its drawing functions (data/figure_panels/fig2.json, written by the
archive's figures/panel_io.py and copied by analysis/export_galaxy_benchmark_tables.py). Nothing is recomputed here:
every number traces to the archive script at that commit. Writes, next to this script, fig2_performance.pdf, .png (600 dpi)
and .svg, and source_data.csv (the archive's fig2_source_data.csv).

Regenerate with: python figures/fig2_performance/make_figure.py
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
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.transforms import blended_transform_factory
import io
import numpy as np
import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})


style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition


W, MM = 180.0, 1 / 25.4


CFG = style.CONFIGS


ENVS = style.ENVS                                    # custom code first, always


CODE, GAL = ENVS


BENCH = style.BENCH


TICK = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6\nSol', 'GPT-5.6 Luna': 'GPT-5.6\nLuna',
        'DeepSeek V4 Pro': 'DeepSeek\nV4 Pro'}


BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}


CONTRACT = {'BixBench50': 'evaluator acceptance', 'CompBio': 'reconstructed-key agreement',
            'IWC': 'workflow-output agreement (0–1)'}


CAUSES = ['No answer validation', 'Benchmark specification or scoring', 'Lacking biological knowledge',
          'Not able to use Galaxy', 'No answer submitted']


CAUSE_COLOR = dict(zip(CAUSES, [style.NEUTRAL_DARK, style.OI_GREEN, style.OI_YELLOW, style.OI_PURPLE,
                                style.NEUTRAL_LIGHT]))


EXAMPLE = 'bix-45-q1'                                 # traced discordant case: PhyKIT version


PAIR_TYPES = [('galaxy_higher', CODE, 'Galaxy higher'), ('code_higher', GAL, 'Custom code higher'),
              ('equal', CODE, 'Same count'), ('equal', GAL, None)]


def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H, note=None):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')
    if note:
        fig.text((x + 4.4) / W, 1 - (y + 4.4) / H, note, fontsize=5, color=style.INK2, va='top', ha='left',
                 linespacing=1.2)


def cond_marker(ax, x, y, env, ms=3.4, **kw):
    ax.plot(x, y, ls='', marker=style.ENV_MARKER[env], ms=ms, mfc=style.ENV_COLOR[env], mec='white', mew=0.4, **kw)


def draw_a(fig, H, tab, reps):
    label(fig, 0, 0, 'a', 'Scores by benchmark, model and condition', H)
    specs = [('BixBench50', 12.0), ('CompBio', 66.0), ('IWC', 128.0)]
    for bm, x0 in specs:
        ax = axes_mm(fig, x0, 14.0, 48.0, 28.0, H)
        iwc = bm == 'IWC'
        k = 0.01 if iwc else 1.0                      # IWC on its own agreement scale, 0-1
        for i, c in enumerate(CFG):
            pts = {}
            for j, env in enumerate(ENVS):
                t = tab[(tab.benchmark == bm) & (tab.cfg == c) & (tab.env == env)].iloc[0]
                x = i + (j - 0.5) * 0.36
                ax.plot([x, x], [t.lo * k, t.hi * k], color=style.ENV_COLOR[env], lw=0.8, zorder=3,
                        solid_capstyle='butt')
                cond_marker(ax, x, t.value * k, env, zorder=5)
                pts[env] = (x, t.value * k)
                v = reps[(reps.benchmark == bm) & (reps.cfg == c) & (reps.env == env)].value.values * k
                ax.plot(np.full(len(v), x + (j - 0.5) * 0.30), v, ls='', marker='o', ms=1.4, mfc='white',
                        mec=style.INK2, mew=0.4, zorder=4)
            ax.plot([pts[CODE][0], pts[GAL][0]], [pts[CODE][1], pts[GAL][1]], color=style.NEUTRAL_MID, lw=0.5,
                    zorder=2)
        if iwc:
            ax.set_ylim(0.6, 1.02)
            ax.set_yticks([0.6, 0.7, 0.8, 0.9, 1.0], ['0.6', '0.7', '0.8', '0.9', '1.0'])
            ax.set_ylabel('Mean output agreement')
        else:
            ax.set_ylim(60, 102)
            ax.set_yticks([60, 70, 80, 90, 100])
            if bm == 'BixBench50':
                ax.set_ylabel('Runs accepted (%)')
            else:
                ax.set_yticklabels([])
        style.grid_y(ax)
        ax.set_xlim(-0.6, len(CFG) - 0.4)
        ax.set_xticks(range(len(CFG)), [TICK[c] for c in CFG])
        ax.tick_params(axis='x', length=0, pad=2, labelsize=5.5)
        ntask = int(tab[tab.benchmark == bm].tasks.iloc[0])
        ax.text(0.0, 1 + 5.6 / 28.0, f'{BENCH_NAME[bm]} · {ntask} tasks', transform=ax.transAxes, ha='left',
                va='bottom', fontsize=6, fontweight='bold')
        ax.text(0.0, 1 + 1.6 / 28.0, CONTRACT[bm], transform=ax.transAxes, ha='left', va='bottom', fontsize=5,
                color=style.INK2)
    hand = [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.4, mfc=style.ENV_COLOR[e], mec='white', mew=0.4,
                   label=style.ENV_LABEL[e]) for e in ENVS]
    hand.append(Line2D([], [], ls='', marker='o', ms=1.4, mfc='white', mec=style.INK2, mew=0.4,
                       label='Replicate (one run per task)'))
    fig.legend(handles=hand, ncol=3, loc='upper right', bbox_to_anchor=(1.0, 1 - 0.6 / H), fontsize=5.3,
               handletextpad=0.3, columnspacing=1.0, borderaxespad=0, frameon=False)


def draw_b(fig, H, y0, fr, exp_sens=None, n_exposed=0):
    label(fig, 0, y0, 'b', 'Paired differences: Galaxy minus custom code', H)
    rows, y = [], 0.0
    for bm in BENCH:
        rows.append((bm, None, y))
        y += 1.0
        for c in CFG + ['all four']:
            rows.append((bm, c, y))
            y += 1.0
        y += 0.45
    ymax = y - 0.45
    h = 42.0
    cols = [('mean_score', 'Mean score', 34.0, (-15, 25), [-10, 0, 10, 20]),
            ('all_three', 'All three runs correct', 67.0, (-45, 70), [-40, 0, 40])]
    for k, (grp, title, x0, xlim, ticks) in enumerate(cols):
        ax = axes_mm(fig, x0, y0 + 13.0, 29.0, h, H)
        g = fr[fr.group == grp].set_index(['benchmark', 'cfg'])
        for bm, c, yy in rows:
            if c is None:
                continue
            t = g.loc[(bm, c)]
            pooled = c == 'all four'
            lo, hi = max(t.lo, xlim[0]), min(t.hi, xlim[1])
            ax.plot([lo, hi], [yy, yy], color=style.INK, lw=0.9 if pooled else 0.6, zorder=3, solid_capstyle='butt')
            for edge, lim, sgn in ((t.lo, xlim[0], -1), (t.hi, xlim[1], 1)):
                if (edge < lim) if sgn < 0 else (edge > lim):     # interval runs past the axis
                    ax.plot(lim, yy, ls='', marker='<' if sgn < 0 else '>', ms=2.2, color=style.INK, zorder=3,
                            clip_on=False)
            ax.plot(t['diff'], yy, ls='', marker='D' if pooled else 'o', ms=3.0 if pooled else 2.3,
                    mfc=style.INK if pooled else 'white', mec=style.INK, mew=0.6, zorder=4)
        ax.axvline(0, color=style.INK2, lw=0.6, zorder=2)
        ax.set_ylim(ymax - 0.4, -0.6)
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.set_xlim(*xlim)
        ax.set_xticks(ticks)
        style.grid_x(ax)
        ax.set_title(title, fontsize=5.5, fontweight='bold', pad=3)
        ax.set_xlabel('Percentage points', labelpad=1.5)
        if k == 0:
            tr = blended_transform_factory(ax.transAxes, ax.transData)
            for bm, c, yy in rows:
                if c is None:
                    ax.text(-(x0 - 1.0) / 29.0, yy, BENCH_NAME[bm] + (' (agreement × 100)' if bm == 'IWC' else ''),
                            transform=tr, ha='left', va='center', fontsize=5.5, fontweight='bold')
                else:
                    ax.text(-0.05, yy, 'All four models' if c == 'all four' else c, transform=tr, ha='right',
                            va='center', fontsize=5.5, fontweight='bold' if c == 'all four' else 'normal')
    note = '← custom code higher · Galaxy higher →  (95% intervals)'
    if exp_sens is not None:
        e = exp_sens[exp_sens.population == 'Without verified or probable exposure'].set_index('benchmark')['diff']
        note += (f'\nWithout the {n_exposed} runs that reached benchmark answers: BixBench-Verified-50 '
                 f'{e["BixBench50"]:+.1f}, CompBioBench {e["CompBio"]:+.1f} points').replace('-', '\u2212') \
            .replace('BixBench\u2212Verified\u221250', 'BixBench-Verified-50')
    fig.text((0 + 4.4) / W, 1 - (y0 + 4.6) / H, note, fontsize=5, color=style.INK2, va='top', linespacing=1.25)


def draw_c(fig, H, y0, grids, summ):
    label(fig, 100.0, y0, 'c', 'Correct runs of three, same task and model', H)
    vmax = max(g.values.max() for g in grids.values())
    norm = LogNorm(vmin=1, vmax=vmax * 1.6)
    side, xs = 20.0, (112.0, 135.5, 159.0)
    for k, (bm, x0) in enumerate(zip(BENCH, xs)):
        ax = axes_mm(fig, x0, y0 + 14.0, side, side, H)
        m = grids[bm].values.astype(float)
        im = ax.imshow(np.where(m > 0, m, np.nan), origin='lower', cmap='Greys', norm=norm,
                       extent=(-0.5, 3.5, -0.5, 3.5), zorder=1)
        for gg in range(4):
            for cc in range(4):
                v = int(m[gg, cc])
                ax.text(cc, gg, f'{v}', ha='center', va='center', fontsize=5,
                        color='white' if v >= 0.18 * vmax else style.INK, fontweight='bold' if gg == cc else 'normal',
                        zorder=3)
                if gg == cc:
                    ax.add_patch(Rectangle((cc - 0.5, gg - 0.5), 1, 1, fill=False, ec=style.INK, lw=0.7, zorder=2))
        ax.set_xticks(range(4))
        ax.set_yticks(range(4), [str(i) for i in range(4)] if k == 0 else [''] * 4)
        ax.tick_params(length=0, pad=1.5, labelsize=5)
        for s in ax.spines.values():
            s.set_visible(False)
        name = {'BixBench50': 'BixBench-V-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC (≥ 0.99)'}[bm]
        ax.set_title(name, fontsize=5, fontweight='bold', pad=2.5)
        s = summ[bm]
        ax.text(0.5, -0.30, f'{s["pairs"]} pairs\nSame count {s["equal"]}\nGalaxy higher {s["galaxy_higher"]}\n'
                f'Custom code higher {s["code_higher"]}', transform=ax.transAxes, ha='center', va='top', fontsize=5,
                linespacing=1.2)
        if k == 0:
            ax.set_ylabel('Galaxy', labelpad=1.5)
        if k == 1:
            ax.set_xlabel('Custom code', labelpad=1.5)
    fig.text(104.4 / W, 1 - (y0 + 4.6) / H, 'Outlined diagonal, same count; above it, Galaxy had more correct runs;\n'
             'below it, custom code had more', fontsize=5, color=style.INK2, va='top', linespacing=1.2)
    cax = axes_mm(fig, 112.0, y0 + 50.5, 20.0, 1.4, H)
    cb = fig.colorbar(im, cax=cax, orientation='horizontal', ticks=[1, 10, 100])
    cb.ax.set_xticklabels(['1', '10', '100'])
    cb.ax.minorticks_off()
    cb.ax.tick_params(labelsize=5, length=1.5, pad=1)
    cb.outline.set_linewidth(0.4)
    fig.text(134.0 / W, 1 - (y0 + 50.1) / H, 'Task–model pairs per cell (log scale)', fontsize=5, color=style.INK2,
             va='top')


def stacked_causes(ax, yy, counts, over, width_mm, bar_h=0.66, outside=False, below=False):
    n = int(counts.sum())
    left, out = 0.0, []
    for cause in CAUSES:
        v = 100 * counts[cause] / n if n else 0
        if not v:
            continue
        ax.barh(yy, v, left=left, height=bar_h, color=CAUSE_COLOR[cause], ec='white', lw=0.4, zorder=3)
        o = over.get(cause, 0)
        if o:
            ax.barh(yy, 100 * o / n, left=left, height=bar_h, fill=False, hatch='////', ec='white', lw=0, zorder=4)
        txt = f'{int(counts[cause])}'
        if v / 100 * width_mm >= 1.25 * len(txt) + 0.8:
            ax.text(left + v / 2, yy, txt, ha='center', va='center', fontsize=5, zorder=5,
                    color='white' if cause in ('No answer validation', 'Benchmark specification or scoring',
                                               'Not able to use Galaxy') else style.INK,
                    bbox=dict(boxstyle='square,pad=0.08', fc=CAUSE_COLOR[cause], ec='none') if o else None)
        elif outside:
            out.append([left + v / 2, txt])
        left += v
    for a_, b_ in zip(out, out[1:]):                    # neighbouring outside counts at least 4 points apart
        if b_[0] - a_[0] < 4.0:
            b_[0] = a_[0] + 4.0
    for xc, txt in out:                                 # narrow segments: count just above (or below) the bar
        ax.text(xc, yy + (bar_h / 2 + 0.05) * (1 if below else -1), txt, ha='center', va='top' if below else 'bottom',
                fontsize=5, color=style.INK, zorder=5)
    return n


def draw_d(fig, H, y0, tab, over, cover, pairs, sets, r, cinfo=None):
    note = 'Incorrect runs by primary cause (AI-assisted audit), for task–model pairs whose conditions differ or agree'
    if cinfo:
        note += (f'\nAn independent second rater agreed on the cause for {round(cinfo["agree"] * cinfo["items"])} of '
                 f'{cinfo["items"]} sampled runs (κ = {cinfo["kappa"]:.2f})')
    label(fig, 0, y0, 'd', 'Why the conditions disagree (BixBench-Verified-50)', H, note)
    ax = axes_mm(fig, 43.0, y0 + 12.0, 54.0, 19.0, H)
    ypos = [0.0, 1.45, 3.05, 4.1]
    for (ptype, env, lab), yy in zip(PAIR_TYPES, ypos):
        counts = tab.loc[(ptype, env)] if (ptype, env) in tab.index else pd.Series(0, index=CAUSES)
        o = {c: int(over.get((ptype, env, c), 0)) for c in CAUSES}
        n = stacked_causes(ax, yy, counts, o, 54.0, outside=True, below=yy == ypos[-1])
        cv = cover.loc[(ptype, env)]
        ax.text(101.5, yy, f'{n} runs · {int(cv.tasks)} tasks', ha='left', va='center', fontsize=5, color=style.INK2)
        ax.text(-1.0, yy, f'{style.ENV_LABEL[env].replace("Custom code", "Custom-code")} runs', ha='right', va='center', fontsize=5)
        if lab:
            npairs = int(pairs.get(ptype, 0)) if ptype != 'equal' else int(
                (sets[sets.benchmark == 'BixBench50'].pivot_table(index=['task', 'cfg'], columns='env',
                                                                  values='n_correct').min(axis=1) < 3).sum() -
                pairs.get('galaxy_higher', 0) - pairs.get('code_higher', 0))
            mid = yy if ptype != 'equal' else (ypos[2] + ypos[3]) / 2
            ax.text(-0.335, mid, f'{lab}\n({npairs} pairs)', transform=blended_transform_factory(ax.transAxes, ax.transData),
                    ha='right', va='center', fontsize=5, fontweight='bold', linespacing=1.1)
    ax.set_ylim(ypos[-1] + 0.95, -0.95)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Incorrect runs (%)', labelpad=1.5)
    style.grid_x(ax)
    handles = [Patch(fc=CAUSE_COLOR[c], label=c) for c in CAUSES]
    handles.append(Patch(fc=style.NEUTRAL_MID, hatch='////', ec='white', lw=0, label='Validation and specification\n'
                         'both implicated'))
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(-0.77, -0.50), ncol=3, fontsize=5, handlelength=1.0,
              handletextpad=0.3, columnspacing=0.8, labelspacing=0.3, borderaxespad=0)
    draw_example(fig, H, y0, r)


def draw_example(fig, H, y0, r):
    """Traced discordant case: run outcome of every model and replicate on bix-45-q1, in both conditions."""
    x0, w = 122.0, 58.0
    ax = axes_mm(fig, x0, y0 + 1.0, w, 40.0, H)
    ax.set_axis_off()
    ax.set_xlim(0, w)
    ax.set_ylim(40.0, 0)
    ax.add_patch(Rectangle((0, 0), w, 40.0, fc=style.LIGHT, ec='none', zorder=0))
    ax.text(1.5, 1.6, f'Traced case: {EXAMPLE} (relative composition variability)', fontsize=5.5, fontweight='bold',
            va='top')
    d = r[r.task == EXAMPLE]
    gx = {CODE: 25.0, GAL: 44.0}
    for env in ENVS:
        ax.text(gx[env] + 2.4, 6.0, style.ENV_LABEL[env], fontsize=5, ha='center', va='top', fontweight='bold')
    for i, c in enumerate(CFG):
        yy = 10.4 + i * 2.6
        ax.text(1.5, yy, c, fontsize=5, va='center')
        for env in ENVS:
            v = d[(d.cfg == c) & (d.env == env)].sort_values('replicate').ok.values
            for j, ok in enumerate(v):
                ax.plot(gx[env] + j * 2.4, yy, ls='', marker='o', ms=2.6, mfc=style.INK if ok else 'white',
                        mec=style.INK, mew=0.5, zorder=3)
    for env in ENVS:
        n = int(d[d.env == env].ok.sum())
        ax.text(gx[env] + 2.4, 21.4, f'{n} of {len(d[d.env == env])} correct', fontsize=5, ha='center', va='center',
                color=style.INK2)
    ax.plot([], [], ls='', marker='o', ms=2.6, mfc=style.INK, mec=style.INK, mew=0.5)
    ax.text(1.5, 24.6, 'Successful custom-code runs matched the PhyKIT version to the\n'
            'date of the input archive. The Galaxy PhyKIT wrapper, like current\n'
            'PhyKIT, returned a different value, and the wrapper version was not\n'
            'shown to the agent; the reference encodes the older value.',
            fontsize=5, va='top', linespacing=1.25)
    ax.text(1.5, 37.6, '●  correct    ○  incorrect (one run each)', fontsize=5, va='center', color=style.INK2)


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
    panel_io.replay(DATA / 'figure_panels' / 'fig2.json', globals(), names=['fig2'])
    for ext in ('pdf', 'png', 'svg'):
        os.replace(HERE / f'fig2.{ext}', HERE / f'fig2_performance.{ext}')
    shutil.copyfile(DATA / 'figure_panels' / 'fig2_source_data.csv', HERE / 'source_data.csv')


if __name__ == '__main__':
    main()
