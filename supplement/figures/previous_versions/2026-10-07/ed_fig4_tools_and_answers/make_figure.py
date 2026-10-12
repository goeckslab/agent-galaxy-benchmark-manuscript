#!/usr/bin/env python3
"""Extended Data Fig. 4: Tool inventory, route similarity, answer matching, difficulty and UDT methods.

Drawing code copied unchanged from the run archive, paulocilasjr/Galaxy_benchmark@b3cbb944648a57104a6837d1640b255854dd7e3e:figures/make_fig4.py; the panel data are the
values that script computed and passed to its drawing functions (data/figure_panels/ed_fig4.json, written by the
archive's figures/panel_io.py and copied by analysis/export_galaxy_benchmark_tables.py). Nothing is recomputed here:
every number traces to the archive script at that commit. Writes, next to this script, ed_fig4_tools_and_answers.pdf, .png (600 dpi)
and .svg, and source_data.csv (the archive's ed_fig4_source_data.csv).

Regenerate with: python figures/ed_fig4_tools_and_answers/make_figure.py
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
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
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


BENCH = style.BENCH


QA = ['BixBench50', 'CompBio']                       # benchmarks with a submitted answer


BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}


BENCH_SHORT = {'BixBench50': 'BixBench', 'CompBio': 'CompBio', 'IWC': 'IWC'}


MODEL_COLOR = dict(zip(CFG, ['#117733', '#AA4499', '#DDCC77', '#332288']))


MODEL_SHORT = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'Sol', 'GPT-5.6 Luna': 'Luna', 'DeepSeek V4 Pro': 'DeepSeek'}


TOOL_LABEL = {
    'toolshed.g2.bx.psu.edu/repos/iuc/filter_tabular/filter_tabular': 'Filter tabular', 'Cut1': 'Cut columns',
    'toolshed.g2.bx.psu.edu/repos/iuc/datamash_ops/datamash_ops': 'Datamash',
    'toolshed.g2.bx.psu.edu/repos/devteam/column_maker/Add_a_column1': 'Compute column',
    'toolshed.g2.bx.psu.edu/repos/ufz/xlsx2tsv/xlsx2tsv': 'XLSX to TSV', 'Filter1': 'Filter rows',
    'csv_to_tabular': 'CSV to tabular', 'Grep1': 'Select lines',
    'toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem': 'BWA-MEM',
    'toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_grep_tool': 'Search text (grep)',
    'toolshed.g2.bx.psu.edu/repos/goeckslab/phykit_metrics/phykit_metrics': 'PhyKIT metrics',
    'toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_sort_header_tool': 'Sort with header',
    'toolshed.g2.bx.psu.edu/repos/iuc/anndata_inspect/anndata_inspect': 'Inspect AnnData', 'Grouping1': 'Group',
    'join1': 'Join datasets', 'toolshed.g2.bx.psu.edu/repos/iuc/bedtools/bedtools_intersectbed': 'Bedtools intersect',
    'toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_head_tool': 'Select first lines',
    'CONVERTER_gz_to_uncompressed': 'Uncompress', 'Summary_Statistics1': 'Summary statistics',
    'toolshed.g2.bx.psu.edu/repos/devteam/samtools_idxstats/samtools_idxstats': 'Samtools idxstats',
    'toolshed.g2.bx.psu.edu/repos/iuc/deseq2/deseq2': 'DESeq2',
    'toolshed.g2.bx.psu.edu/repos/iuc/anndata_export/anndata_export': 'Export AnnData',
}


N_TOOLS = 15


MATCH_RULES = [('exact', 'Exact text (trimmed, lower case)'), ('3sig', 'Numbers to 3 significant digits'),
               ('2sig', 'Numbers to 2 significant digits'),
               ('task', 'Task-aware: benchmark tolerance, lists as sets (primary)')]


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


def signed(x, nd=2):
    return f'{x:.{nd}f}'.replace('-', '−')


def ed_tools(fig, H, top, per, runs):
    label(fig, 0, 0, 'a', f'Installed tools with completed jobs in the most Galaxy runs ({N_TOOLS})', H)
    x0, pw, gap = 30.0, 16.0, 1.8
    labels = [TOOL_LABEL.get(t, t.split('/')[-1]) for t in top.index]
    for j, c in enumerate(CFG):
        ax = axes_mm(fig, x0 + j * (pw + gap), 13.0, pw, 40.0, H)
        ax.barh(range(N_TOOLS), per[c].values, height=0.68, color=MODEL_COLOR[c],
                ec=style.INK if c == 'GPT-5.6 Luna' else 'none', lw=0.3, zorder=3)
        ax.set_ylim(N_TOOLS - 0.5, -0.5)
        ax.set_xlim(0, 25)
        ax.set_xticks([0, 10, 20])
        style.grid_x(ax)
        ax.tick_params(axis='y', length=0)
        if j == 0:
            ax.set_yticks(range(N_TOOLS), labels, fontsize=5)
        else:
            ax.set_yticks(range(N_TOOLS), [''] * N_TOOLS)
            ax.spines['left'].set_visible(False)
        ax.set_title(c, fontsize=5.5, fontweight='bold', pad=7.0, loc='left')
        ax.text(0.0, 1.015, f'{int(runs[c])} runs', transform=ax.transAxes, ha='left', va='bottom', fontsize=5,
                color=style.INK2)
        if j == 1:
            ax.text(1 + gap / pw / 2, -0.10, 'Galaxy runs with a completed job of the tool (%)',
                    transform=ax.transAxes, ha='center', va='top', fontsize=5.5)


def ed_similarity(fig, H, sim, sim_t, sens):
    label(fig, 108.0, 0, 'b', 'Tool-set similarity by model', H)
    ax = axes_mm(fig, 118.0, 13.0, 60.0, 26.0, H)
    for g, bm in enumerate(BENCH):
        for j, c in enumerate(CFG):
            t = sim[(sim.benchmark == bm) & (sim.cfg == c)].iloc[0]
            x = g * 1.2 + (j - 1.5) * 0.22
            ax.errorbar(x, t.value, yerr=[[t.value - t.lo], [t.hi - t.value]], fmt='o', ms=3.0, mfc=MODEL_COLOR[c],
                        mec=style.INK, mew=0.35, elinewidth=0.8, capsize=0, ecolor=MODEL_COLOR[c])
    ax.set_xticks([g * 1.2 for g in range(3)], [BENCH_NAME[b] for b in BENCH], fontsize=5)
    ax.tick_params(axis='x', length=0)
    ax.set_ylim(0, 1)
    style.grid_y(ax)
    ax.set_ylabel('Mean tool-set similarity')
    st = sim_t.set_index('benchmark')
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for g, bm in enumerate(BENCH):
        ax.text(g * 1.2, -0.17, f'models differ {fmt_p(st.loc[bm, "p"])}', transform=tr, ha='center', va='top',
                fontsize=5, color=style.INK2)
    ax.legend(handles=[Line2D([], [], ls='', marker='o', ms=3.0, mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35, label=c)
                       for c in CFG], ncol=2, loc='lower left', bbox_to_anchor=(0.0, 1.02), fontsize=5,
              handletextpad=0.2, columnspacing=0.6, borderaxespad=0, labelspacing=0.2)
    # sensitivity of the panel c correlation (Spearman rho across tasks; tasks in parentheses)
    x0, y = 112.4, 52.0
    cols = [x0 + 44.0, x0 + 56.0, x0 + 66.0]
    fig.text(x0 / W, 1 - y / H, 'Task similarity against task accuracy, Spearman ρ (tasks)', fontsize=5,
             fontweight='bold', va='top')
    y += 3.4
    for xc, bm in zip(cols, BENCH):
        fig.text(xc / W, 1 - y / H, BENCH_SHORT[bm], fontsize=5, va='top', ha='right', color=style.INK2)
    names = {'primary': 'Panel c (installed tools + one UDT item)',
             'installed tools only (UDTs dropped)': 'UDT items dropped',
             'cells whose runs used installed tools only': 'Cells using installed tools only',
             'cells with any UDT': 'Cells with any UDT',
             'ordered steps (edit distance)': 'Ordered steps (edit distance)',
             'tool versions distinguished': 'Tool versions distinguished',
             'tools with identical parameters': 'Tools with identical parameters'}
    for variant in names:
        y += 3.0
        fig.text(x0 / W, 1 - y / H, names[variant], fontsize=5, va='top')
        for xc, bm in zip(cols, BENCH):
            t = sens[(sens.variant == variant) & (sens.benchmark == bm)]
            txt = f'{signed(t.rho.iloc[0])} ({int(t.tasks.iloc[0])})' if len(t) else '–'
            fig.text(xc / W, 1 - y / H, txt, fontsize=5, va='top', ha='right')


def ed_matching(fig, H, mr):
    label(fig, 0, 88.0, 'c', 'Answer agreement under four answer-matching rules', H)
    ax = axes_mm(fig, 62.0, 97.0, 40.0, 14.0, H)
    for i, (k, lab) in enumerate(MATCH_RULES):
        for env in ENVS:
            t = mr[(mr.rule == k) & (mr.env == env)].iloc[0]
            ax.plot(t.value, i, ls='', marker=style.ENV_MARKER[env], ms=3.2, mfc=style.ENV_COLOR[env], mec='white',
                    mew=0.35)
    ax.set_yticks(range(len(MATCH_RULES)), [lab for _, lab in MATCH_RULES], fontsize=5)
    ax.set_ylim(len(MATCH_RULES) - 0.5, -0.5)
    ax.set_xlim(70, 95)
    style.grid_x(ax)
    ax.tick_params(axis='y', length=0)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Replicate sets with the same answer in all three runs (%)')
    ax.legend(handles=[Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.2, mfc=style.ENV_COLOR[e], mec='white',
                              mew=0.35, label=style.ENV_LABEL[e]) for e in ENVS], loc='lower right',
              bbox_to_anchor=(1.0, 1.02), ncol=2, fontsize=5, borderaxespad=0)


UDT_CLASSES = ['Statistics, machine learning and enrichment', 'Single-cell and spatial analysis',
               'Variant calling and annotation', 'Peak calling and epigenomics', 'Genomic intervals and sequence features',
               'Read processing and alignment', 'Expression and differential testing', 'Phylogenetics',
               'Sequence search, taxonomy and assembly', 'Tables and text', 'Script supplied as a dataset',
               'Environment probe or set-up', 'Other methods']


def ed_udt(fig, H, y0, pct, n):
    label(fig, 0, y0, 'e', 'What completed UDT jobs computed', H,
          'Share of each model\'s completed UDT jobs by method class (rules on the UDT definition: code first, '
          'then a tool-specific container)')
    ax = axes_mm(fig, 58.0, y0 + 12.0, 76.0, 30.0, H)
    m = pct.values
    cmap = LinearSegmentedColormap.from_list('blues', ['#FFFFFF', '#CFE3F1', style.GALAXY, '#063B5E'])
    ax.imshow(m, aspect='auto', cmap=cmap, vmin=0, vmax=100, interpolation='nearest')
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            if not np.isnan(m[i, j]):
                ax.text(j, i, f'{m[i, j]:.0f}', ha='center', va='center', fontsize=5,
                        color='white' if m[i, j] >= 45 else style.INK)
    ax.set_yticks(range(len(UDT_CLASSES)), UDT_CLASSES, fontsize=5)
    ax.set_xticks(range(m.shape[1]), [f'{MODEL_SHORT[c]}\n({int(n[(b, c)])})' for b, c in pct.columns], fontsize=5)
    ax.tick_params(length=0, pad=1.5)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.axvline(3.5, color='white', lw=1.6)
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for b, bm in enumerate(QA):
        ax.text(b * 4 + 1.5, 1.01, BENCH_SHORT[bm], transform=tr, ha='center', va='bottom', fontsize=5.5,
                fontweight='bold')


def ed_difficulty(fig, H, y0, ds):
    label(fig, 108.0, y0, 'd', 'Same rejected answer by held-out difficulty, two definitions', H)
    ax = axes_mm(fig, 120.0, y0 + 9.0, 58.0, 20.0, H)
    for k, (name, col, mk) in enumerate((('other 21 runs', style.INK, 'o'), ('other models (18 runs)', '#888888', 's'))):
        d = ds[ds.definition == name].reset_index(drop=True)
        x = np.arange(len(d)) + (k - 0.5) * 0.18
        ax.errorbar(x, d.value, yerr=[d.value - d.lo, d.hi - d.value], fmt=mk, ms=3.0, color=col, mfc=col if k == 0
                    else 'white', mec=col, elinewidth=0.7, capsize=0, label=f'Incorrect runs among the task\'s {name}')
    ax.set_xticks(range(4), ['None', 'Few', 'Some', 'Most'])
    ax.tick_params(axis='x', length=0)
    ax.set_ylim(0, 60)
    ax.set_yticks([0, 20, 40, 60])
    style.grid_y(ax)
    ax.set_ylabel('Replicate sets (%)')
    ax.set_xlabel('Held-out task difficulty', labelpad=1.5)
    ax.legend(loc='upper left', fontsize=5, borderaxespad=0.2, handletextpad=0.3)


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
    panel_io.replay(DATA / 'figure_panels' / 'fig4.json', globals(), names=['ed_fig4'])
    for ext in ('pdf', 'png', 'svg'):
        os.replace(HERE / f'ed_fig4.{ext}', HERE / f'ed_fig4_tools_and_answers.{ext}')
    shutil.copyfile(DATA / 'figure_panels' / 'ed_fig4_source_data.csv', HERE / 'source_data.csv')


if __name__ == '__main__':
    main()
