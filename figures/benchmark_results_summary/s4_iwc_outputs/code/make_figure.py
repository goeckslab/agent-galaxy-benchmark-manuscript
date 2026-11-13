"""One cell per IWC run, preserving the individual model and replicate identity."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from plot_style import G, INK, MODELS, MUTED, Plate, data

d=data(__file__)
bands=d[d.panel=="individual_run"].set_index(["task","condition","model","replicate"]).score_band
summary=d[d.panel=="workflow_summary"].set_index(["task","condition"])
labels={"001":"Read QC and trimming", "002":"RNA-seq differential expression","003":"Host-read filtering",
        "005":"Amplicon denoising","006":"ATAC-seq accessibility","007":"Mitogenome assembly",
        "008":"AMR gene detection","009":"Peptide verification","010":"Pseudobulk differential expression",
        "011":"BioProject data retrieval"}
colors=["#EDF2F1","#C4DEDA","#8AB8B5","#427E80","#183F46"]
shades={"exact":0, "near":1, "high":2, "partial":3, "zero":4}

p=Plate(105)
p.heading(2,4,"a","Output agreement in each workflow, model and replicate")
p.heading(137,4,"b","Workflow summaries")
p.text(3,11,"Agreement (%)",weight="bold",fontsize=6.5)
for left,key,lab in [(24,0,"100"),(40,1,"99 to <100"),(65,2,"90 to <99"),(89,3,">0 to <90"),(114,4,"0")]:
    p.box(left,9,4.3,4,colors[key])
    if key==4:
        p.text(left+2.15,11,"×",ha="center",color="white",fontsize=6.5)
    p.text(left+5.8,11,lab,fontsize=6.5)
p.text(3,23.5,"IWC workflow",weight="bold")
for start,cond in [(48,"Galaxy"),(93,"Custom code")]:
    p.text(start+21,17.8,cond,weight="bold",ha="center")
    for mi,m in enumerate(["5.5","Sol","Luna","DeepSeek"]):
        p.text(start+mi*10.9+5,23.5,m,ha="center",fontsize=6.5)
        for rep in range(3):
            p.text(start+mi*10.9+rep*3.25+1.6,28,str(rep+1),ha="center",fontsize=6.5)
p.text(157.5,17.8,"Mean % (runs <99%)",ha="center",fontsize=6.5)
p.text(146.5,25,"Galaxy",ha="center",weight="bold",fontsize=6.5)
p.text(168,25,"Custom code",ha="center",weight="bold",fontsize=6.5)
p.line(2,31,177,31,color=MUTED)
for i,task in enumerate(sorted(summary.index.get_level_values("task").unique())):
    y=35+i*5.9
    ident=task.split("_")[1]
    p.text(2.5,y,f"{ident}  {labels[ident]}",fontsize=6.5)
    for start,cond,sx in [(48,"Galaxy",146.5),(93,"custom code",168)]:
        for mi,model in enumerate(MODELS):
            for rep in range(1,4):
                band=bands.loc[(task,cond,model,rep)]
                x=start+mi*10.9+(rep-1)*3.25
                col=shades[band]
                p.box(x,y-2.1,3.08,4.2,colors[col])
                if col==4:
                    p.text(x+1.54,y,"×",ha="center",color="white",fontsize=6.5)
        r=summary.loc[(task,cond)]
        p.text(sx,y,f"{r.mean_agreement_pct:.2f} ({r.below_099:.0f})",ha="center",weight="bold",fontsize=6.5)
p.line(2,91.5,177,91.5,color=MUTED)
p.text(3,96,"Columns 1–3 are replicates. Models are GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro.",fontsize=6.5)
p.text(3,101,"Each workflow mean uses 12 runs per policy. A cross marks zero agreement.",fontsize=6.5)
p.save(__file__)
