#!/usr/bin/env python3
"""Figure 5: Galaxy records analyses as structured provenance and uses more input tokens on question-answering tasks.

Drawing code copied unchanged from the run archive, paulocilasjr/Galaxy_benchmark@0dbf3f443b83a91322098c9918d86a5846129215:figures/make_fig5.py; the panel data are the
values that script computed and passed to its drawing functions (data/figure_panels/fig5.json, written by the
archive's figures/panel_io.py and copied by analysis/export_galaxy_benchmark_tables.py). Nothing is recomputed here:
every number traces to the archive script at that commit. Writes, next to this script, fig5_token_cost.pdf, .png (600 dpi)
and .svg, and source_data.csv (the archive's fig5_source_data.csv).

Regenerate with: python figures/fig5_token_cost/make_figure.py
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
from matplotlib.patches import Patch, Rectangle
from matplotlib.transforms import blended_transform_factory
import io
import numpy as np
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})


style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition


W, MM = 180.0, 1 / 25.4


ENVS = style.ENVS                                    # custom code first, always


CODE, GAL = ENVS


BENCH = style.BENCH


BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}


TOKEN_KINDS = [('input_tokens', 'Input, incl. cached'), ('uncached', 'Uncached input'), ('output_tokens', 'Output')]


OPS = [('Finding tools (search, tool descriptions)', ('search_galaxy_tools', 'inspect_galaxy_tool')),
       ('Running installed tools', ('run_galaxy_tool_and_wait',)),
       ('Running agent-written code (UDTs)', ('run_galaxy_udt_and_wait',)),
       ('Reading results (history, datasets)', ('inspect_galaxy_history', 'peek_galaxy_dataset',
                                                 'inspect_archive_inventory')),
       ('Waiting for jobs, uploading files', ('wait_for_galaxy_jobs', 'stage_workspace_file'))]


OP_COLOR = [style.GALAXY, style.NEUTRAL_DARK, '#8a8a8a', '#bdbdbd', '#e3e3e3']


ELEMENTS = [('software', 'Software and version'), ('parameters', 'Parameters'), ('inputs', 'Input data'),
            ('outputs', 'Output data'), ('status', 'Execution status'), ('command', 'Command or code'),
            ('analysis', 'Whole analysis (per run)')]


LEVELS = [('S', 'Structured record', '#3A3A3A'), ('T', 'Free text in the retained trace', '#9A9A9A'),
          ('P', 'Partial: environment image or metadata only', '#D6D6D6'),
          ('N', 'Not retained or not recorded (unknown)', 'white')]


EXAMPLE = ('bix-45-q1', 'galaxy_codex_gpt_5_6_sol_r1', 'open_ended_code_codex_gpt_5_6_sol_r1')


ROUND_HEAD = {'July': 'July 2026 · GPT-5.5 · 3 runs per task and condition',
              'October': 'October 2026 · GPT-5.6 Sol · 3 runs per task'}


def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H, note=None):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')
    if note:
        fig.text((x + 4.4) / W, 1 - (y + 4.4) / H, note, fontsize=5, color=style.INK2, va='top', ha='left',
                 linespacing=1.2)


def log_ratio_axis(ax, lo=0.2, hi=12.0, ticks=(0.25, 0.5, 1, 2, 4, 8)):
    ax.set_xscale('log')
    ax.set_xlim(lo, hi)
    ax.set_xticks(list(ticks), [f'{t:g}' for t in ticks])
    ax.minorticks_off()
    style.grid_x(ax)
    ax.axvline(1, color=style.INK2, lw=0.6, zorder=2)


def forest_point(ax, y, est, lo, hi, primary=True, color=style.INK):
    ax.plot([lo, hi], [y, y], color=color, lw=0.8 if primary else 0.6, zorder=3, solid_capstyle='butt')
    ax.plot(est, y, ls='', marker='D' if primary else 'o', ms=2.8 if primary else 2.4,
            mfc=color if primary else 'white', mec=color, mew=0.6, zorder=4)


def draw_a(fig, H, tok, pooled):
    label(fig, 0, 0, 'a', 'Token use, Galaxy relative to custom code', H,
          'Diamonds, typical paired task (geometric mean of task–model ratios; primary);\n'
          'circles, all tokens summed over the same tasks (aggregate)')
    ax = axes_mm(fig, 33.0, 15.0, 42.0, 34.0, H)
    rows, y = [], 0.0
    for bm in BENCH:
        rows.append(('head', bm, y))
        y += 0.95
        for value, lab in TOKEN_KINDS:
            rows.append(('row', (bm, value, lab), y))
            y += 0.95
        y += 0.35
    t = tok.set_index(['benchmark', 'kind'])
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    for kind, key, yy in rows:
        if kind == 'head':
            ax.text(-0.76, yy, BENCH_NAME[key], transform=tr, ha='left', va='center', fontsize=5.5, fontweight='bold')
            continue
        bm, value, lab = key
        x = t.loc[(bm, value)]
        forest_point(ax, yy - 0.17, x.ratio, x.lo, x.hi, primary=True)
        forest_point(ax, yy + 0.17, x.total_ratio, x.total_lo, x.total_hi, primary=False, color=style.INK2)
        ax.text(-0.04, yy, lab, transform=tr, ha='right', va='center', fontsize=5)
        ax.text(1.02, yy, f'{x.ratio:.1f}×', transform=tr, ha='left', va='center', fontsize=5,
                fontweight='bold' if value == 'input_tokens' else 'normal')
    log_ratio_axis(ax)
    ax.set_ylim(y - 0.35 + 0.1, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Galaxy / custom code (log scale)', labelpad=1.5)
    # incorrect relative to correct runs of the same task and model
    bx = axes_mm(fig, 33.0, 61.0, 42.0, 5.5, H)
    pp = pooled.set_index('env')
    for i, env in enumerate(ENVS):
        x = pp.loc[env]
        forest_point(bx, i, x.ratio, x.lo, x.hi, color=style.ENV_COLOR[env])
        bx.text(-0.04, i, f'{style.ENV_LABEL[env]} ({int(x.sets)} sets)', transform=blended_transform_factory(
            bx.transAxes, bx.transData), ha='right', va='center', fontsize=5)
        bx.text(1.02, i, f'{x.ratio:.2f}×', transform=blended_transform_factory(bx.transAxes, bx.transData),
                ha='left', va='center', fontsize=5)
    log_ratio_axis(bx)
    bx.set_ylim(1.6, -0.6)
    bx.set_yticks([])
    bx.spines['left'].set_visible(False)
    bx.set_xlabel('Incorrect / correct runs of the same task and model', labelpad=1.5)
    fig.text(4.4 / W, 1 - 56.5 / H, 'No clear input-token difference between correct and incorrect siblings',
             fontsize=5.5, fontweight='bold', va='top')


def draw_b(fig, H, act, rep, never, cached):
    label(fig, 92.0, 0, 'b', 'Where the extra input comes from', H,
          'Left, Galaxy / custom code, typical paired task (all runs); right, the text\nGalaxy returned to the agent, '
          'by what the request was for')
    ax = axes_mm(fig, 120.0, 15.0, 22.0, 34.0, H)
    rows, y = [], 0.0
    for bm in BENCH:
        rows.append(('head', bm, y))
        y += 0.95
        for value, lab in (('actions', 'Actions'), ('tokens_per_action', 'Tokens per action')):
            rows.append(('row', (bm, value, lab), y))
            y += 0.95
        y += 0.35
    t = act.set_index(['benchmark', 'kind'])
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    for kind, key, yy in rows:
        if kind == 'head':
            ax.text(-1.05, yy, BENCH_NAME[key], transform=tr, ha='left', va='center', fontsize=5.5, fontweight='bold')
            continue
        bm, value, lab = key
        x = t.loc[(bm, value)]
        forest_point(ax, yy, x.ratio, x.lo, x.hi)
        ax.text(-0.06, yy, lab, transform=tr, ha='right', va='center', fontsize=5)
        ax.text(1.03, yy, f'{x.ratio:.1f}×', transform=tr, ha='left', va='center', fontsize=5)
    log_ratio_axis(ax, 0.25, 8.0, (0.5, 1, 2, 4))
    ax.set_ylim(y - 0.25, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Galaxy / custom code', labelpad=1.5)
    # returned characters by request type, per benchmark
    cx = axes_mm(fig, 155.0, 15.0, 24.0, 34.0, H)
    for i, bm in enumerate(BENCH):
        d = rep[rep.benchmark == bm].set_index('operation')
        bottom = 0.0
        for (name, _), col in zip(OPS, OP_COLOR):
            v = d.loc[name, 'char_pct']
            cx.bar(i, v, bottom=bottom, width=0.72, color=col, ec='white', lw=0.3, zorder=3)
            if v >= 9:
                cx.text(i, bottom + v / 2, f'{v:.0f}', ha='center', va='center', fontsize=5,
                        color='white' if col in (style.GALAXY, style.NEUTRAL_DARK, '#8a8a8a') else style.INK)
            bottom += v
    cx.set_xticks(range(3), ['BixB.', 'CompBio', 'IWC'], fontsize=5, rotation=0)
    cx.tick_params(axis='x', length=0, pad=1.5)
    cx.set_ylim(0, 100)
    cx.set_yticks([0, 50, 100])
    cx.set_ylabel('Returned characters (%)', labelpad=1.0)
    cx.legend(handles=[Patch(fc=c, ec=style.NEUTRAL_MID if c == '#e3e3e3' else c, lw=0.3, label=n)
                       for (n, _), c in zip(OPS, OP_COLOR)], loc='upper left', bbox_to_anchor=(-2.42, -0.21), ncol=2,
              fontsize=5, handlelength=0.9, handletextpad=0.3, columnspacing=0.8, labelspacing=0.2, borderaxespad=0)
    nv = never.percent
    rng_txt = lambda s_: (f'{s_.min():.0f}%' if round(s_.min()) == round(s_.max())   # noqa: E731
                          else f'{s_.min():.0f}–{s_.max():.0f}%')
    fig.text(96.4 / W, 1 - 66.0 / H,
             f'Tools inspected but not executed in the same run: {rng_txt(nv)} by benchmark.\n'
             f'Median share of input that was cached (earlier context reread): Galaxy '
             f'{rng_txt(cached.xs(GAL, level="env"))}, custom code {rng_txt(cached.xs(CODE, level="env"))}.',
             fontsize=5, color=style.INK2, va='top', linespacing=1.25)


def draw_c(fig, H, y0, tr, change):
    label(fig, 0, y0, 'c', 'Reducing Galaxy token use', H,
          'Galaxy / custom-code tokens per complete 50-task run (input, including cached, plus output) on BixBench-Verified-50, '
          'before and after each round of interface changes;\nfilled, three replicates with 95% intervals over source capsules; '
          'open, one replicate (batch summary only). The October rows share one set of custom-code runs.')
    ax = axes_mm(fig, 62.0, y0 + 10.0, 40.0, 17.0, H)
    rows, y = [], 0.0
    for comparison in ('July', 'October'):
        rows.append(('head', comparison, y))
        y += 1.0
        for t in tr[tr.comparison == comparison].itertuples():
            rows.append(('row', t, y))
            y += 1.0
        y += 0.3
    trf = blended_transform_factory(ax.transAxes, ax.transData)
    col = {'galaxy': 59.0 / 40.0, 'code': 72.0 / 40.0, 'correct': 88.0 / 40.0}   # right edges of the table columns
    for name, x in (('Galaxy tokens', col['galaxy']), ('Custom code', col['code']), ('Galaxy correct', col['correct'])):
        ax.text(x, -0.75, name, transform=trf, ha='right', va='center', fontsize=5, fontweight='bold')
    for comparison in ('July', 'October'):
        ys = [yy for kind, t, yy in rows if kind == 'row' and t.comparison == comparison]
        xs = tr[tr.comparison == comparison].ratio.values
        ax.plot(xs, ys, color=style.NEUTRAL_MID, lw=0.6, zorder=2)
    for kind, t, yy in rows:
        if kind == 'head':
            ax.text(-62.0 / 40.0, yy, ROUND_HEAD[t], transform=trf, ha='left', va='center', fontsize=5.5, fontweight='bold')
            continue
        one = np.isnan(t.lo)
        if not one:
            ax.plot([t.lo, t.hi], [yy, yy], color=style.GALAXY, lw=0.8, zorder=3, solid_capstyle='butt')
        ax.plot(t.ratio, yy, ls='', marker='D', ms=2.8, mfc='white' if one else style.GALAXY, mec=style.GALAXY, mew=0.6, zorder=4)
        ax.text(-0.03, yy, t.label, transform=trf, ha='right', va='center', fontsize=5)
        ax.text(1.03, yy, f'{t.ratio:.2f}×', transform=trf, ha='left', va='center', fontsize=5,
                fontweight='bold' if t.stage == 'after' else 'normal')
        gal = f'{t.galaxy_tokens_m:.1f}M'
        if t.stage == 'after':
            gal += f' ({change[t.comparison]["pct"]:+.0f}%)'.replace('-', '−')
        ax.text(col['galaxy'], yy, gal, transform=trf, ha='right', va='center', fontsize=5)
        ax.text(col['code'], yy, f'{t.code_tokens_m:.1f}M', transform=trf, ha='right', va='center', fontsize=5)
        ax.text(col['correct'], yy, '–' if np.isnan(t.galaxy_correct) else f'{t.galaxy_correct:.0f}%', transform=trf,
                ha='right', va='center', fontsize=5)
    log_ratio_axis(ax, 0.5, 8.0, (0.5, 1, 2, 4, 8))
    ax.set_ylim(y - 0.3 + 0.1, -1.3)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Galaxy / custom code (log scale)', labelpad=1.5)


def draw_d(fig, H, y0, ev, counts):
    label(fig, 0, y0, 'd', 'What the retained record holds for each analysis step', H,
          f'{counts["steps"][CODE]:,} custom-code steps (shell commands labelled analysis) and '
          f'{counts["steps"][GAL]:,} Galaxy jobs;\nwhole analysis per run ({counts["runs"][GAL]:,} runs per condition)')
    ax = axes_mm(fig, 40.0, y0 + 12.0, 46.0, 38.0, H)
    ypos, y = [], 0.0
    for k, (code, name) in enumerate(ELEMENTS):
        for env in ENVS:
            ypos.append((code, env, y))
            y += 0.78
        y += 0.5
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    for code, env, yy in ypos:
        d = ev[(ev.env == env) & (ev.element == code)].set_index('level').pct
        left = 0.0
        for lev, _, col in LEVELS:
            v = d.get(lev, 0.0)
            if v <= 0:
                continue
            ax.barh(yy, v, left=left, height=0.62, color=col, ec=style.NEUTRAL_MID if lev == 'N' else 'white',
                    lw=0.4, hatch='/////' if lev == 'N' else None, zorder=3)
            if v >= 12:
                ax.text(left + v / 2, yy, f'{v:.0f}', ha='center', va='center', fontsize=5, zorder=4,
                        color='white' if lev == 'S' else style.INK,
                        bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none') if lev == 'N' else None)
            left += v
        ax.text(-0.02, yy, style.ENV_LABEL[env], transform=tr, ha='right', va='center', fontsize=5)
    for code, name in ELEMENTS:
        ys = [yy for c, _, yy in ypos if c == code]
        ax.text(-13.0 / 46.0, np.mean(ys), name, transform=tr, ha='right', va='center', fontsize=5.5,
                fontweight='bold')
    ax.set_ylim(y - 0.5 + 0.1, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Steps (or runs) (%)', labelpad=1.5)
    ax.legend(handles=[Patch(fc=col, ec=style.NEUTRAL_MID, lw=0.4, hatch='/////' if lev == 'N' else None, label=lab)
                       for lev, lab, col in LEVELS], loc='upper left', bbox_to_anchor=(-0.78, -0.17), ncol=2,
              fontsize=5, handlelength=1.1, handletextpad=0.3, columnspacing=0.8, labelspacing=0.25, borderaxespad=0)


def draw_e(fig, H, y0, rec):
    label(fig, 92.0, y0, 'e', 'One analysis step, recorded both ways', H,
          f'{EXAMPLE[0]}, PhyKIT relative composition variability; GPT-5.6 Sol, replicate 1 (the case in Fig. 2d)')
    x0, w, top, hgt = 96.0, 84.0, y0 + 11.5, 54.0
    ax = axes_mm(fig, x0, top, w, hgt, H)
    ax.set_axis_off()
    ax.set_xlim(0, w)
    ax.set_ylim(hgt, 0)
    c1, c2, cw = 18.5, 51.5, 32.0
    ax.text(c1, 1.2, 'Custom code: retained trace', fontsize=5.5, fontweight='bold', va='top')
    ax.text(c2, 1.2, 'Galaxy: job record', fontsize=5.5, fontweight='bold', va='top')
    rows = [
        ('Software and\nversion', f'PhyKIT 2.4.1 installed, then 2.0.3\ndownloaded and loaded through\n'
                                  f'PYTHONPATH (in command text only)',
         f'{rec["tool"].split("/")[1]} wrapper {rec["wrapper_version"]}\n(Tool Shed ID); library version\n'
         f'not in the job record'),
        ('Parameters', 'In the Python code of the command\n(file suffix, rounding)',
         f'Fields: metric = {rec["metric"].replace("composition_", "composition_" + chr(10))};\n'
         f'mode = {rec["mode"]}; suffix = {rec["suffix"]}'),
        ('Inputs and\noutputs', 'Input archives named in the\ncommand; output files not retained',
         f'{rec["n_in"]} input and {rec["n_out"]} output datasets,\nlinked by ID in the history'),
        ('Status', f'Exit code {", ".join(rec["code_exit"])} for every command', f'Job state "{rec["state"]}", exit code '
                                                                                f'{rec["exit"]}'),
        ('Answer', 'Accepted' if rec['code_ok'] else 'Rejected', ('Accepted' if rec['gal_ok'] else 'Rejected') +
         ': the reference encodes the\nolder PhyKIT value'),
    ]
    y = 6.2
    for name, a, b in rows:
        n = max(a.count('\n'), b.count('\n'), name.count('\n')) + 1
        ax.text(0.5, y, name, fontsize=5, fontweight='bold', va='top', linespacing=1.2)
        ax.text(c1, y, a, fontsize=5, va='top', linespacing=1.2)
        ax.text(c2, y, b, fontsize=5, va='top', linespacing=1.2)
        y += n * 2.25 + 2.0
        ax.plot([0.5, w], [y - 1.1, y - 1.1], color=style.GRID, lw=0.4)
    ax.add_patch(Rectangle((c1 - 1.0, 0), cw, y - 1.1, fc=style.ENV_TINT[CODE], ec='none', zorder=0))
    ax.add_patch(Rectangle((c2 - 1.0, 0), cw, y - 1.1, fc=style.ENV_TINT[GAL], ec='none', zorder=0))
    ax.text(0.5, y + 1.0, 'The Galaxy record keeps fields a reviewer can query; the custom-code trace keeps the code,\n'
            'so the same facts must be read from it. Neither record was rerun to test reproducibility.',
            fontsize=5, color=style.INK2, va='top', linespacing=1.25)


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
    panel_io.replay(DATA / 'figure_panels' / 'fig5.json', globals(), names=['fig5'])
    for ext in ('pdf', 'png', 'svg'):
        os.replace(HERE / f'fig5.{ext}', HERE / f'fig5_token_cost.{ext}')
    shutil.copyfile(DATA / 'figure_panels' / 'fig5_source_data.csv', HERE / 'source_data.csv')


if __name__ == '__main__':
    main()
