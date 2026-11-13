"""Link a published Galaxy DESeq2 job to its table and a raw curated-workflow output."""
import json
import pandas as pd

from benchmark_records import SOURCES, save


def compare():
    p = json.loads((SOURCES/"wf002_provenance.json").read_text(encoding="utf-8-sig"))
    assert p["job_state"] == p["data_state"] == "ok"
    fields = ["gene","base_mean","log2_fold_change","se","wald_stat","p","adjusted_p"]
    tables = [pd.read_csv(SOURCES/f"wf002_{name}_deseq2.tsv",sep="\t",names=fields).set_index("gene")
              for name in ("run","reference")]
    a,b = tables
    assert a.index.is_unique and b.index.is_unique
    common = a.index.intersection(b.index)
    calls = [set(t.index[t.adjusted_p < .05]) for t in tables]
    evidence = dict(**p, run_genes=len(a), reference_genes=len(b), shared_genes=len(common),
                    run_significant=len(calls[0]), reference_significant=len(calls[1]),
                    shared_significant=len(calls[0]&calls[1]),
                    shared_gene_fc_pearson=a.loc[common,"log2_fold_change"].corr(b.loc[common,"log2_fold_change"]))
    save(pd.DataFrame([evidence]),"s1_execution","workflow_check.csv")
    return evidence
