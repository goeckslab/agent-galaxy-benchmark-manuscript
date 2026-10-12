#!/usr/bin/env python3
"""Figure 4: Answer agreement and tool use vary across model configurations.

Drawing code copied unchanged from the run archive, paulocilasjr/Galaxy_benchmark@0dbf3f443b83a91322098c9918d86a5846129215:figures/make_fig4.py; the panel data are the
values that script computed and passed to its drawing functions (data/figure_panels/fig4.json, written by the
archive's figures/panel_io.py and copied by analysis/export_galaxy_benchmark_tables.py). Nothing is recomputed here:
every number traces to the archive script at that commit. Writes, next to this script, fig4_solution_variability.pdf, .png (600 dpi)
and .svg, and source_data.csv (the archive's fig4_source_data.csv).

Regenerate with: python figures/fig4_solution_variability/make_figure.py
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
from matplotlib.patches import Patch
from matplotlib.transforms import blended_transform_factory
import io
import numpy as np
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})


style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition


B, SEED, B_PERM = 20000, 20261002, 20000


W, MM = 180.0, 1 / 25.4


CFG = style.CONFIGS


ENVS = style.ENVS                                    # custom code first, always


CODE, GAL = ENVS


BENCH = style.BENCH


QA = ['BixBench50', 'CompBio']                       # benchmarks with a submitted answer


BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}


BENCH_SHORT = {'BixBench50': 'BixBench', 'CompBio': 'CompBio', 'IWC': 'IWC'}


BENCH_MARK = {'BixBench50': ('^', '#E69F00'), 'CompBio': ('D', '#56B4E9'), 'IWC': ('v', '#FFAABB')}


MODEL_COLOR = dict(zip(CFG, ['#117733', '#AA4499', '#DDCC77', '#332288']))


MODEL_SHORT = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'Sol', 'GPT-5.6 Luna': 'Luna', 'DeepSeek V4 Pro': 'DeepSeek'}


DATA_FAMILIES = ['Tables and text', 'Format conversion and upload', 'Inspection and quality control',
                 'Data retrieval']


FAMILY_RULES = [
    ('Data retrieval', r'ncbi_datasets|ncbi_acc_download|pysradb|fasterq_dump|sra_tools|seurat_data|snpeff_databases|'
                       r'snpeff_download|ucsc_table_direct|get_online_data|get_pdb|ctb_online'),
    ('Inspection and quality control', r'anndata_inspect|scanpy_inspect|inspect_eset|fastqc|samtools_flagstat|'
                                       r'samtools_idxstats|samtools_stats|fasta_stats|fastq_stats|fastq_info|'
                                       r'seq_composition|fasta_compute_length|gfastats|seqtk_comp|seqtk_fqchk|'
                                       r'bcftools_stats|multiqc|plotqualityprofile|summarize'),
    ('Format conversion and upload', r'^converter_|xlsx2tsv|csv_to_tabular|tabular_to_csv|unzip|^upload1$|__data_fetch__|'
                                     r'rds_to_tabular|anndata_import|anndata_export|sceasy|fasta2tab|tab2fasta|'
                                     r'fasta_to_tabular|fastq_to_tabular|fastq_to_fasta|fastqtofasta|bam_to_sam|'
                                     r'gff2bed|gtftobed12|bigbedtobed|bigwigtowig|wiggle2simple|biom_convert|'
                                     r'maf_to_fasta|lped2pbed|gfa_to_fa|samtools_fastx|bamtofastq|twobittofa|'
                                     r'wigtobigwig|qiime2_core__tools__(import|export)|mcmicro_to_anndata|'
                                     r'mtx_to_10x|read10x|read_10x|seqret|imagemagick|interval2maf|archive|'
                                     r'compress_file|fasta_formatter|interlacer'),
    ('Read processing and alignment', r'fastp|trim|cutadapt|umi_tools|bwa|bowtie|minimap2|hisat2|rna_star|picard|'
                                      r'samtools_view|samtools_sort|samtools_merge|samtools_collate|samtool_filter|'
                                      r'samtools_slice|samtools_phase|sambamba|bamtools|ngsutils|sinto|seqtk|seqkit|'
                                      r'sample_seqs|crossmap|liftover|fastx_|fasta_nucleotide_changer'),
    ('Variant calling and annotation', r'freebayes|bcftools|snpeff|snpsift|samtools_mpileup|lofreq|varscan|gatk|plink|'
                                       r'vcf|ivar_|arriba'),
    ('Expression and differential testing', r'deseq2|edger|limma|featurecounts|salmon|kallisto|alevin|stringtie|'
                                            r'isoformswitch|decoupler|music_|rseqc|gffcompare|htseq|cuffdiff|pizzly'),
    ('Single-cell and spatial analysis', r'scanpy|anndata|seurat|snapatac2|squidpy|scimap|dropletutils|harmony'),
    ('Genomic intervals and sequence features', r'bedtools|bedops|extract genomic dna|gene2exon|flanking|get_flanks|'
                                                r'gtf_filter|gff_filter|extract_features|emboss|orfipy|transdecoder|'
                                                r'fasta_regex|find_subsequences|filter_by_length|filter_by_fasta_ids|'
                                                r'seq_filter_by_id|translate|mosdepth|samtools_depth|'
                                                r'samtools_coverage|samtools_bedcov|deeptools|agat|gffread|splitfasta|'
                                                r'fasta_merge|createinterval|gtf2gene_list|gops_|count_gff|chainswap'),
    ('Phylogenetics', r'phykit|mafft|iqtree|raxml|clustal|muscle'),
    ('Sequence search, taxonomy and assembly', r'blast|kraken|staramr|meme|vsearch|mothur|dada2|qiime2|diamond|hmmer|'
                                               r'mitohifi|flye|hifiasm|trinity|spades|busco|quast|meryl|megahit|weblogo'),
    ('Peak calling and epigenomics', r'macs2|genrich|chipseeker|homer'),
    ('Statistics, machine learning and enrichment', r'correlation|rank_tests|gseapy|kegg|gprofiler|univariate|'
                                                    r'multivariate|transformation|summary_statistics|sklearn|'
                                                    r'model_prediction|scipy|pca|calculate_numeric|annotatemyids|'
                                                    r'scatterplot|ggplot'),
    ('Tables and text', r'^cut1$|^filter1$|^grep1$|^join1$|^sort1$|grouping1|count1|paste1|^comp1$|^cat1$|wc_gnu|'
                        r'remove beginning|show beginning|show tail|convert characters|addvalue|datamash|filter_tabular|'
                        r'column_maker|add_a_column|text_processing|table_compute|query_tabular|regex|changecase|'
                        r'mergecols|random_lines|column_remove|replace_column|split_file|unique|diff|add_line_to_file|'
                        r'collapse|cat_multi|^__|table_pandas|collection_|secure_hash|^tp_|datamash_transpose|melt|'
                        r'subtract_query'),
    ('Other methods', r'.'),
]


METHOD_FAMILIES = [f for f, _ in FAMILY_RULES if f not in DATA_FAMILIES]


FAMILIES = DATA_FAMILIES + METHOD_FAMILIES


DIFF_BINS = [(0, 0, '0'), (1, 2, '1–2'), (3, 10, '3–10'), (11, 21, '11–21')]


OUTCOMES = [('same_rejected', 'Same rejected answer in all three runs', '#CC79A7'),
            ('rejected_differ', 'All rejected, answers differ', '#009E73'),
            ('mixed', 'Mixed: one or two accepted', '#88CCEE'),
            ('missing', 'Missing submission', style.NEUTRAL_DARK),
            ('all_accepted', 'All three accepted', '#E8E8E8')]


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


def draw_a(fig, H, pct, runs):
    label(fig, 0, 0, 'a', 'What each model ran in Galaxy', H,
          'Galaxy runs with at least one completed job in each family (%); UDTs were not offered on IWC')
    rows = FAMILIES + ['UDT (agent-written code)']
    ax = axes_mm(fig, 45.0, 13.0, 60.0, 37.0, H)
    m = pct.values
    cmap = LinearSegmentedColormap.from_list('blues', ['#FFFFFF', '#CFE3F1', style.GALAXY, '#063B5E'])
    ax.imshow(m, aspect='auto', cmap=cmap, vmin=0, vmax=100, interpolation='nearest')
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m[i, j]
            if np.isnan(v):
                continue
            ax.text(j, i, f'{v:.0f}', ha='center', va='center', fontsize=5, color='white' if v >= 45 else style.INK)
    ax.set_yticks(range(len(rows)), rows, fontsize=5)
    ax.set_xticks(range(m.shape[1]), [MODEL_SHORT[c] for _, c in pct.columns], fontsize=5, rotation=90)
    ax.tick_params(axis='x', pad=1.0)
    ax.tick_params(length=0, pad=1.5)
    for s in ax.spines.values():
        s.set_visible(False)
    for j in (4, 8):
        ax.axvline(j - 0.5, color='white', lw=1.6)
    for i in (len(DATA_FAMILIES), len(FAMILIES)):
        ax.axhline(i - 0.5, color='white', lw=1.6)
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for b, bm in enumerate(BENCH):
        ax.text(b * 4 + 1.5, 1.01, BENCH_SHORT[bm], transform=tr, ha='center', va='bottom', fontsize=5.5,
                fontweight='bold')
    tr2 = blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(-0.71, (len(DATA_FAMILIES) - 1) / 2, 'Data\nhandling', transform=tr2, ha='center', va='center',
            fontsize=5.5, fontweight='bold', rotation=90, linespacing=1.0)
    ax.text(-0.71, len(DATA_FAMILIES) + (len(METHOD_FAMILIES) - 1) / 2, 'Scientific methods', transform=tr2,
            ha='center', va='center', fontsize=5.5, fontweight='bold', rotation=90)


def draw_b(fig, H, agree, tests):
    label(fig, 112.0, 0, 'b', 'Same answer in all three runs', H,
          'Replicate sets (one task, model and condition)')
    ax = axes_mm(fig, 122.0, 17.0, 57.0, 27.0, H)
    a = agree.set_index(['benchmark', 'cfg', 'env'])
    for g, bm in enumerate(QA):
        for j, c in enumerate(CFG):
            pts = []
            for k, env in enumerate(ENVS):
                t = a.loc[(bm, c, env)]
                x = g * 1.15 + (j - 1.5) * 0.24 + (k - 0.5) * 0.10
                ax.errorbar(x, t.value, yerr=[[t.value - t.lo], [t.hi - t.value]], fmt=style.ENV_MARKER[env], ms=3.0,
                            mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35, elinewidth=0.8, capsize=0, zorder=3,
                            ecolor=MODEL_COLOR[c] if c != 'GPT-5.6 Luna' else '#A8994A')
                pts.append((x, t.value))
            ax.plot(*zip(*pts), color=style.NEUTRAL_MID, lw=0.4, zorder=2)
        if g:
            ax.axvline(g * 1.15 - 0.575, color=style.GRID, lw=0.6, zorder=1)
    ax.set_ylim(55, 101.5)
    ax.spines['left'].set_bounds(55, 100)
    ax.set_yticks([60, 70, 80, 90, 100])
    style.grid_y(ax)
    ax.set_xticks([g * 1.15 for g in range(len(QA))], [BENCH_NAME[b] for b in QA], fontsize=5.5)
    ax.tick_params(axis='x', length=0, pad=2)
    ax.set_xlim(-0.55, (len(QA) - 1) * 1.15 + 0.55)
    ax.set_ylabel('Sets with the same answer (%)')
    at = tests.set_index(['benchmark', 'env'])
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for g, bm in enumerate(QA):
        ax.text(g * 1.15, -0.13, f'custom code {fmt_p(at.loc[(bm, CODE), "p_holm"])}\n'
                f'Galaxy {fmt_p(at.loc[(bm, GAL), "p_holm"])}', transform=tr, ha='center', va='top', fontsize=5,
                color=style.INK2, linespacing=1.2)
    ax.text(0.5, -0.36, f'Models differ, both benchmarks: custom code {fmt_p(at.loc[("both", CODE), "p_holm"])};\n'
            f'Galaxy {fmt_p(at.loc[("both", GAL), "p_holm"])}', transform=ax.transAxes, ha='center', va='top',
            fontsize=5, color=style.INK, fontweight='bold', linespacing=1.2)
    models = [Line2D([], [], ls='', marker='o', ms=3.0, mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35, label=c)
              for c in CFG]
    shapes = [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.0, mfc=style.NEUTRAL_MID, mec=style.INK, mew=0.35,
                     label=style.ENV_LABEL[e]) for e in ENVS]
    ax.add_artist(ax.legend(handles=models, ncol=2, loc='lower left', bbox_to_anchor=(0.0, 1.02), fontsize=5,
                            handletextpad=0.2, columnspacing=0.6, borderaxespad=0, labelspacing=0.2))
    ax.legend(handles=shapes, ncol=1, loc='lower right', bbox_to_anchor=(1.0, 1.02), fontsize=5, handletextpad=0.2,
              borderaxespad=0, labelspacing=0.2)


def draw_c(fig, H, y0, task, per, within, elig):
    label(fig, 0, y0, 'c', 'Tool-set similarity and task accuracy', H,
          'Galaxy; 1 = the same set of tools in all three runs (any UDT counted as one item; order, versions and\n'
          f'parameters ignored). Models compared on the same task: Spearman ρ = {signed(within["rho"])}, '
          f'{fmt_p(within["p"])}')
    for j, bm in enumerate(BENCH):
        ax = axes_mm(fig, 11.0 + j * 40.5, y0 + 21.0, 35.0, 20.0, H)
        t = task[task.benchmark == bm]
        m, col = BENCH_MARK[bm]
        jitter = rng.uniform(-1.2, 1.2, len(t))
        iwc = bm == 'IWC'
        ax.scatter(t.correct + jitter, t.sim, s=9 if iwc else 7, marker=m, facecolor=col,
                   edgecolor=style.INK2 if iwc else 'white', lw=0.3, zorder=3)
        ax.set_xlim(-4, 104)
        ax.set_ylim(-0.03, 1.03)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0], ['0', '0.25', '0.5', '0.75', '1'] if j == 0 else [''] * 5)
        style.grid_y(ax)
        ax.set_xlabel('Runs correct on the task (%)', labelpad=1.5)
        if j == 0:
            ax.set_ylabel('Tool-set similarity')
        p = per[bm]
        e = elig.loc[bm]
        ax.text(0.0, 1 + 5.9 / 20.0, BENCH_NAME[bm], transform=ax.transAxes, ha='left', va='bottom', fontsize=5.5,
                fontweight='bold')
        ax.text(0.0, 1 + 1.0 / 20.0, f'ρ = {signed(p["rho"])}, {fmt_p(p["p"])}\n{p["tasks"]} tasks; {int(e["sum"])} of '
                f'{int(e["size"])} cells eligible', transform=ax.transAxes, ha='left', va='bottom', fontsize=5,
                color=style.INK2, linespacing=1.2)


VER_LABEL = [('V1', 'Counts or denominators'), ('V2', 'Second method'), ('V3', 'Sensitivity analysis'),
             ('V4', 'Input assumption'), ('V5', 'Plausibility'), ('V6', 'Domain diagnostic'), ('any', 'Any check')]


def draw_d(fig, H, y0, ver):
    """Verification checks in correct and incorrect runs (Extended Data Fig. 7a, by outcome)."""
    label(fig, 131.0, y0, 'd', 'Verification checks', H, '80 coded runs (coder blind\nto the grade); 95% intervals')
    ax = axes_mm(fig, 154.0, y0 + 17.0, 22.0, 24.0, H)
    for k, (val, lab, col, mk) in enumerate(((1, 'Correct', style.INK, 'o'), (0, 'Incorrect', '#999999', 's'))):
        d = ver[(ver.by == 'ok') & (ver.group == val)].set_index('check').reindex([c for c, _ in VER_LABEL])
        y = np.arange(len(VER_LABEL)) + (k - 0.5) * 0.3
        ax.errorbar(d.value, y, xerr=[d.value - d.lo, d.hi - d.value], fmt=mk, ms=2.6, color=col, mfc=col, mec='white',
                    mew=0.3, elinewidth=0.6, capsize=0, label=lab)
    ax.set_yticks(range(len(VER_LABEL)), [l for _, l in VER_LABEL], fontsize=5)
    ax.get_yticklabels()[-1].set_fontweight('bold')
    ax.set_ylim(len(VER_LABEL) - 0.4, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 50, 100])
    style.grid_x(ax)
    ax.tick_params(axis='y', length=0)
    ax.set_xlabel('Runs with the check (%)', labelpad=1.5)
    ax.legend(loc='lower right', bbox_to_anchor=(1.05, 1.0), ncol=2, fontsize=5, borderaxespad=0.2, handletextpad=0.1,
              columnspacing=0.6, handlelength=1.0)


def draw_e(fig, H, y0, tab, ci, counts):
    label(fig, 0, y0, 'e', 'Replicate outcomes by held-out task difficulty', H,
          'BixBench-Verified-50 and CompBioBench, both conditions; difficulty from the task\'s other 21 runs, so a '
          'set\'s own runs never define it')
    labs = [b[2] for b in DIFF_BINS]
    for j, c in enumerate(CFG):
        ax = axes_mm(fig, 11.0 + j * 33.5, y0 + 13.0, 28.0, 27.0, H)
        t = tab.loc[c].reindex(labs)
        tot = t.sum(axis=1).values
        bottom = np.zeros(len(labs))
        for code, lab, col in OUTCOMES:
            v = 100 * t[code].values / tot
            ax.bar(range(len(labs)), v, bottom=bottom, width=0.72, color=col, ec='white', lw=0.3, zorder=3)
            bottom += v
        q = ci[ci.cfg == c].set_index('diff_bin').reindex(labs)
        ax.errorbar(range(len(labs)), q.value, yerr=[q.value - q.lo, q.hi - q.value], fmt='none', ecolor=style.INK,
                    elinewidth=0.6, capsize=1.2, capthick=0.6, zorder=4)
        for x, n in enumerate(tot):
            ax.text(x, 101.5, f'{int(n)}', ha='center', va='bottom', fontsize=5, color=style.INK2)
        ax.set_xticks(range(len(labs)), labs, fontsize=5)
        ax.tick_params(axis='x', length=0, pad=1.5)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100], ['0', '25', '50', '75', '100'] if j == 0 else [''] * 5)
        ax.set_xlim(-0.55, len(labs) - 0.45)
        ax.set_title(c, fontsize=5.5, fontweight='bold', color=style.INK, pad=8.0)
        if j == 0:
            ax.set_ylabel('Replicate sets (%)')
        if j == 1:
            ax.text(1.12, -0.17, 'Incorrect runs among the task\'s other 21 runs', transform=ax.transAxes, ha='center',
                    va='top', fontsize=5.5)
    handles = [Patch(fc=col, ec=style.NEUTRAL_MID if col == '#E8E8E8' else col, lw=0.3, label=lab)
               for _, lab, col in OUTCOMES[::-1]]
    handles.append(Line2D([], [], color=style.INK, lw=0.6, marker='_', ms=2.4, label='95% interval, same rejected answer'))
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(146.0 / W, 1 - (y0 + 12.0) / H), ncol=1, fontsize=5,
               handlelength=0.9, handletextpad=0.4, labelspacing=0.45, borderaxespad=0, frameon=False,
               title='Replicate set', title_fontsize=5, alignment='left')
    fig.text(146.0 / W, 1 - (y0 + 37.5) / H, 'Numbers above bars: sets', fontsize=5, color=style.INK2, va='top')


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
    panel_io.replay(DATA / 'figure_panels' / 'fig4.json', globals(), names=['fig4'])
    for ext in ('pdf', 'png', 'svg'):
        os.replace(HERE / f'fig4.{ext}', HERE / f'fig4_solution_variability.{ext}')
    shutil.copyfile(DATA / 'figure_panels' / 'fig4_source_data.csv', HERE / 'source_data.csv')


if __name__ == '__main__':
    main()
