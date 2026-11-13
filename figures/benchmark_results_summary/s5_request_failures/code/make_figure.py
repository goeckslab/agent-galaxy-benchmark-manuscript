"""Historical trace coverage, stage totals and exact failure-class counts."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from plot_style import BENCH, INK, MUTED, Plate, data

d=data(__file__)
trace=data(__file__,"historical_trace_coverage.csv")
trace["benchmark"]=trace.benchmark.replace({"BixBench-Verified-50":"BixBench"})
trace=trace.set_index("benchmark")
d["code"]=d.failure_class.str.split().str[0]
codes={"A1":"Tool schema needs history context", "A2":"Tool identifier missing or guessed",
       "A3":"Nested parameter structure", "A4":"Parameter value or datatype", "A5":"Invalid or foreign identifier",
       "A6":"User-defined tool schema", "A7":"Upload or datatype registry", "A8":"Server, transport or rate limit",
       "B1":"Missing container dependency", "B2":"Job error without diagnostic", "B3":"Tool runtime error",
       "B4":"Input format, compression or index", "B5":"Memory or resource limit", "X":"Additional exceptions", "Z":"Unclassified"}
stages=["Request rejected before a job ran","Job failed during execution","Other exception"]
counts=d.pivot(index="code",columns="benchmark",values="requests").reindex(index=codes,columns=BENCH).fillna(0)
shares=d.pivot(index="code",columns="benchmark",values="class_pct").reindex(index=codes,columns=BENCH).fillna(0)
by_stage=d.groupby(["benchmark","failure_stage"]).requests.sum().unstack(fill_value=0)
p=Plate(135)
p.heading(2,4,"a","Coverage and stage of historical Galaxy request failures")
for x,label in [(4,"Benchmark"),(45,"Traced runs"),(78,"Before a job ran"),(113,"During execution"),(141,"Other"),(164,"All failures")]:
    p.text(x,10.5,label,ha="left" if x==4 else "center",weight="bold",fontsize=6.5)
p.line(3,13.5,177,13.5,color=MUTED)
for i,bench in enumerate(BENCH):
    y=17+i*5.3
    p.text(4,y,bench)
    for x,count in zip([45,78,113,141,164],
                       [trace.loc[bench,"traced_runs"], *by_stage.loc[bench,stages],counts[bench].sum()]):
        p.text(x,y,f"{count:,.0f}",ha="center")
p.line(3,31.2,177,31.2)
p.heading(2,36.4,"b","Failed requests by class and benchmark")
p.text(6.2,42,"Counts are printed in each cell. Shading shows the share of failures within a benchmark.",fontsize=6.5)
swatches=["#FAFBFB","#E1ECEC","#BCD6D5","#75A8A8","#245F62"]
for j,label in enumerate(["0%",">0–<5%","5–<10%","10–<20%","≥20%"]):
    x=55+j*24
    p.box(x,45.8,4.8,3.2,swatches[j])
    p.text(x+6,47.4,label,fontsize=6.5)
for x,label in [(4,"Stage"),(36,"Failure class"),(103,"BixBench"),(133,"CompBioBench"),(162,"IWC")]:
    p.text(x,54,label,ha="left" if x<90 else "center",weight="bold")
p.line(3,57,177,57,color=MUTED)
for i,(code,label) in enumerate(codes.items()):
    y=60.3+4.8*i + (1.6 if i>=8 else 0)+(1.6 if i>=13 else 0)
    if i in (0,8,13):
        p.text(4,y,{0:"Before job",8:"During job",13:"Other"}[i],weight="bold")
        if i:
            p.line(3,y-3.8,177,y-3.8)
    p.text(36,y,label)
    for j,bench in enumerate(BENCH):
        number=counts.loc[code,bench]
        pct=shares.loc[code,bench]
        shade=0 if not number else 1 + sum(pct >= t for t in [5,10,20])
        x=103+29.5*j
        p.box(x-13.4,y-2.1,26.8,4.2,swatches[shade])
        p.text(x,y,f"{number:,.0f}",ha="center",color="white" if shade==4 else INK)
p.save(__file__)
