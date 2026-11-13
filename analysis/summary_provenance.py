"""Verify immutable source fingerprints and inventory the generated publication package.

Run without flags after a rebuild. Use --record-sources only for a reviewed new edition.
"""
import argparse
import csv
from hashlib import sha256
from pathlib import Path

from benchmark_records import BASE, FIGS, ROOT, SITE, URL

IMPORT = "90a55f38c14827a82ab48bb509018a417b796a15"
ARCHIVE_EXPORT = "9165a8eaf50569806fbb8af67cb68633316e7359"
WEBSITE = "804299a12ca57d27c2b08b0f5b2d74153c2acedc"
REPO = "https://github.com/goeckslab/agent-galaxy-benchmark-manuscript/blob/"
GALAXY = "https://usegalaxy.org/api/"
UCSC = "https://api.genome.ucsc.edu/getData/"
REGISTRY = BASE/"sources_manifest.csv"


def rows(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def write(path, records):
    with path.open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=records[0],lineterminator="\n")
        w.writeheader()
        w.writerows(records)


def fingerprint(path, text=False):
    body=path.read_bytes()
    if text:
        body=body.replace(b"\r\n",b"\n")
    return sha256(body).hexdigest()


def register():
    records=[]
    def add(path,url,revision,description,policy="exact bytes",expected=None):
        digest=expected or fingerprint(path,policy=="LF text")
        records.append(dict(path=path.relative_to(ROOT).as_posix(),source_url=url,revision=revision,
                            sha256=digest,hash_policy=policy,source_detail=description))
    for r in rows(SITE/"MANIFEST.csv"):
        add(SITE/r["path"],r["url"],r["source_commit"],"Retrieved "+r["fetched"]+"; "+r["checksum_source"],
            "published bytes or Git LF",r["sha256"])
    for file in ["bixbench_failure_causes","galaxy_failure_classes","galaxy_parameter_checks","galaxy_tool_lookup","galaxy_traced_runs","bixbench_task_clusters"]:
        upstream="run_scores" if file=="bixbench_task_clusters" else file
        detail="Historical archive 0fe43954c77f87dddbaf219c62b48b95c7c9f866 via manuscript export."
        if file=="bixbench_task_clusters":
            detail+=" Filter BixBench-Verified-50, select distinct task_id and cluster, sort task_id."
        add(BASE/"sources"/(file+".csv"),REPO+ARCHIVE_EXPORT+"/data/"+upstream+".csv",ARCHIVE_EXPORT,detail)
    for file,url,ver,detail in [
        ("Rerun_Impact_20261028.pdf","user-supplied:Rerun_Impact_20261028.pdf","2026-10-28","Twenty-page author report; original file retained."),
        ("bixbench_july6_token-drivers_index.html",URL+"bixbench/july6/token-drivers/index.html","July 6 cohort","Public HTML downloaded 2026-11-05; version identified by content hash."),
        ("bixbench_token-optimization-oct2026_summary.json",URL+"bixbench/token-optimization-oct2026/summary.json","HF batch 4def1c34763afd79d6271ffe86663d3d6be2a426","Public results export downloaded 2026-11-05; HF revision applies to linked batch."),
        ("iwc_error-analysis_index.html",URL+"iwc/error-analysis/index.html","October deployment; content hash","Full published explanation page downloaded 2026-11-05."),
        ("bixbench_index.html",URL+"index.html","October deployment; content hash","BixBench results page downloaded 2026-11-06; source of the May 2026 no-UDT baseline card (#no-udt-baseline)."),
        ("bixbench_july6_index.html",URL+"bixbench/july6/index.html","July 6 cohort","Archived four-condition accuracy page downloaded 2026-11-06; version identified by content hash."),
        ("bixbench_july6_tokens_index.html",URL+"bixbench/july6/tokens/index.html","July 6 cohort","Archived four-condition token page downloaded 2026-11-06; version identified by content hash."),
        ("web_pages.csv",URL,"2026-11-05 crawl; link-discovery recrawl 2026-11-06","Per-page URL, retrieval date, Last-Modified, byte count and upstream hash; analysis/catalog_benchmark_pages.py. Unchanged pages keep their first retrieval date."),
        ("hg38_gencode_v49.json",UCSC+"track?genome=hg38;track=wgEncodeGencodeCompV49;chrom=chr17;start=7687488;end=7687490","hg38 / GENCODE V49","Raw UCSC response with provider data timestamp."),
        ("hg38_promoter_sequence.json",UCSC+"sequence?genome=hg38;chrom=chr17;start=7687390;end=7687990","GRCh38 / hg38","Raw UCSC response; coordinates zero-based, half-open."),
        ("wf002_run_deseq2.tsv",GALAXY+"datasets/f9cad7b01a472135e36fdd5973541ade/display","Galaxy HDA f9cad7b01a472135e36fdd5973541ade","Public yeast output, IWC 002, GPT-5.5 Galaxy R1, HID 16."),
        ("wf002_reference_deseq2.tsv",GALAXY+"datasets/f9cad7b01a472135b06810b0a8e4ec07/display","Galaxy HDA f9cad7b01a472135b06810b0a8e4ec07","Public yeast output, curated IWC 002 history, HID 13, before downstream filtering."),
        ("wf002_provenance.json",GALAXY+"jobs/bbd44e69cb8906b5c02fec6133bc0439","2026-11-05 API projection","Job id, tool_id and state joined to public dataset metadata via creating_job; no log or trace content.")]:
        add(BASE/"sources"/file,url,ver,detail)
    add(ROOT/"data/token_optimization_rounds.csv",REPO+IMPORT+"/data/token_optimization_rounds.csv",IMPORT,
        "Historical round estimates and transcribed measurements; see source per row.","LF text")
    add(ROOT/"data/site_token_totals.csv",REPO+IMPORT+"/data/site_token_totals.csv",IMPORT,
        "Token snapshot fetched 2026-10-12; BixBench totals rounded to 0.01M.","LF text")
    write(REGISTRY,records)


def verify():
    for r in rows(REGISTRY):
        path=ROOT/r["path"]
        if r["source_url"].startswith("user-supplied:") and not path.exists():
            # Author-held and not redistributed; its committed transcription stands in (see .gitignore).
            print(f"Author-held source absent, checksum not checked: {r['path']}")
            continue
        hashes=[fingerprint(path,r["hash_policy"]=="LF text")]
        if r["hash_policy"]=="published bytes or Git LF":
            hashes.append(fingerprint(path,True))
        if r["sha256"] not in hashes:
            raise ValueError(f"Source has changed: {path}")


def figure_inputs():
    registry=rows(REGISTRY)
    primary=["bixbench/data/results.json","compbiobench/data/paper_results.json","iwc/data/results.json"]
    by_figure=[
        [*primary,"bixbench_task_clusters.csv","web_pages.csv"],
        [*primary,"bixbench_failure_causes.csv","galaxy_failure_classes.csv","Rerun_Impact_20261028.pdf",
         "bixbench_token-optimization-oct2026_summary.json","token_optimization_rounds.csv",
         "site_token_totals.csv","bixbench_july6_token-drivers_index.html"],
        [*primary,"public_udt_usage.tsv","wf002_provenance.json","wf002_reference_deseq2.tsv","wf002_run_deseq2.tsv",
         "bixbench_index.html"],
        [*primary,"Rerun_Impact_20261028.pdf","hg38_gencode_v49.json","hg38_promoter_sequence.json"],
        [*primary,"bixbench_failure_causes.csv","hg38_gencode_v49.json","hg38_promoter_sequence.json"],
        [primary[2],"iwc_error-analysis_index.html"],
        ["galaxy_failure_classes.csv","galaxy_parameter_checks.csv","galaxy_tool_lookup.csv","galaxy_traced_runs.csv"],
        [primary[0],"public_token_usage.tsv","iwc/data/token_usage.tsv","token_optimization_rounds.csv",
         "bixbench_july6_token-drivers_index.html","bixbench_token-optimization-oct2026_summary.json"],
        ["bixbench_july6_token-drivers_index.html","bixbench_july6_tokens_index.html","bixbench_july6_index.html",
         "token_optimization_rounds.csv"]]
    for f,inputs in zip(FIGS,by_figure,strict=True):
        subset=[r for r in registry if any(r["path"].endswith("/"+suffix) for suffix in inputs)]
        assert len(subset)==len(inputs),f
        write(BASE/f/"dataset/inputs.csv",subset)


def outputs():
    paths=[p for p in BASE.rglob("*") if p.is_file() and "__pycache__" not in p.parts and
           ".gitattributes" != p.name and p.name!="artifact_manifest.csv" and BASE/"sources" not in p.parents]
    paths.extend(ROOT/"analysis"/name for name in ["benchmark_records.py","build_benchmark_summary.py","catalog_benchmark_pages.py",
                 "check_workflow_output.py","extract_rerun_report.py","fetch_verified50_key.py","summary_provenance.py",
                 "verify_benchmark_package.py","assemble_supplement.py","build_results_manifest.py",
                 "site_data.py","accuracy.py","token_usage.py"])
    paths.extend(ROOT/p for p in ("data/results_manifest.csv","data/accuracy_by_model.csv"))
    paths.extend(ROOT/"manuscript"/name for name in ["index.qmd","brief-communication.qmd","outline-brief-communication.md",
                                                     "references.bib","_quarto.yml","_quarto-nmeth.yml","figure-formats.lua"])
    paths.extend(ROOT/p for p in ("figures/figures.csv","figures/README.md","analysis/README.md","supplement/README.md"))
    records=[]
    for p in sorted(paths):
        txt=p.suffix.lower() not in (".pdf",".png")
        records.append(dict(path=p.relative_to(ROOT).as_posix(),hash_policy="LF text" if txt else "exact bytes",
                            sha256=fingerprint(p,txt)))
    write(BASE/"artifact_manifest.csv",records)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--record-sources",action="store_true")
    p.add_argument("--inventory",action="store_true")
    args=p.parse_args()
    if args.record_sources:
        register()
    verify()
    if args.inventory:
        outputs()
    print("Source checksums verified.")
