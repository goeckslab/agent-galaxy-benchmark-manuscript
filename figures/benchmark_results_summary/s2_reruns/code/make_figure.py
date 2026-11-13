"""Distinguish selected replacements from regrading and show each reported effect."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from plot_style import BENCH, C, G, INK, MODELS, MUTED, PALE, Plate, data, xgrid

d = data(__file__)
effects = d[d.panel == "release_scores"]
selection = d[d.panel == "selection"].pivot_table(index="reason_class",columns="benchmark",values="selected",aggfunc="sum")
reasons = {"prior-run access":"Access to an earlier run", "direct copying":"Direct copying", "exposure unconfirmed":"Exposure unconfirmed",
           "scientific follow-up":"Scientific follow-up", "reference access":"Reference output access"}
p = Plate(125)
p.heading(2,4,"a",f"Why {selection.sum().sum():.0f} runs were selected for replacement")
p.text(5.5,12,"Reported reason",weight="bold")
for i,bench in enumerate(BENCH):
    p.text(81+38*i,12,bench,weight="bold",ha="center")
p.line(4,15.5,175,15.5,color=MUTED)
for row,(key,label) in enumerate(reasons.items()):
    y=18.8+row*4.9
    p.text(5.5,y,label)
    for i,bench in enumerate(BENCH):
        count=selection.loc[key,bench]
        if count==count:
            p.box(68+38*i,y-2.05,26,4.1,PALE)
        p.text(81+38*i,y,str(int(count)) if count==count else "0",ha="center")
p.line(4,41.6,175,41.6)
p.text(5.5,45.2,"Replacement runs",weight="bold")
for i,bench in enumerate(BENCH):
    p.text(81+38*i,45.2,f"{selection[bench].sum():.0f}",ha="center",weight="bold")

p.heading(2,52,"b","CompBioBench · change in official score")
p.text(6.2,57.4,"Percentage points per 100-answer submission")
comp=effects[effects.benchmark=="CompBioBench"].set_index(["model","condition","replicate"])
for start,cond in [(38,"Galaxy"),(66,"Custom code")]:
    p.text(start+6,63.5,cond,ha="center",weight="bold")
    for rep in range(3):
        p.text(start+6.8*rep,68,f"R{rep+1}",ha="center",fontsize=6.5)
p.line(3.5,71,87.5,71,color=MUTED)
def signed(value):
    return f"{value:+.0f}".replace("-","−") if value else "0"
for i,model in enumerate(MODELS):
    y=74.5+i*5.5
    p.text(4,y,model)
    for start,cond in [(38,"Galaxy"),(66,"custom code")]:
        for rep in [1,2,3]:
            x=start+(rep-1)*6.8
            if (model,cond,rep) in comp.index:
                val=comp.loc[(model,cond,rep),"reported_delta_pp"]
                p.box(x-3.15,y-2.6,6.3,5.2,PALE)
                p.text(x,y,signed(val),ha="center")
            else:
                p.text(x,y,"–",ha="center",color=MUTED)
p.text(4,96.8,"R, replicate · dash, no selected replacement",fontsize=6.5)
change_pct = (comp.changed_answer_pct * comp.reruns).sum() / comp.reruns.sum()
p.text(4,102.5,f"{change_pct:.0f}% of {comp.reruns.sum():.0f} replacement answers changed.",weight="bold")

p.heading(92,52,"c","BixBench · change in acceptance")
p.text(96.2,57.4,"150 runs per model and policy")
bix=effects[effects.benchmark=="BixBench"].set_index(["model","condition"])
ax=p.axes(122,63.5,48,23)
for i,model in enumerate(MODELS):
    for cond,col,m,dy in [("Galaxy",G,"o",-.18),("custom code",C,"s",.18)]:
        row=bix.loc[(model,cond)]
        ax.plot(row.reported_delta_pp,i+dy,marker=m,ms=3.7,mec=col,mew=.85,
                mfc=col if row.reruns else "white",linestyle="none")
ax.set(xlim=(-1,2.4),xticks=[-1,0,1,2],yticks=range(4),yticklabels=MODELS,ylim=(3.55,-.55),
       xlabel="Change (percentage points)")
ax.axvline(0,color=MUTED,lw=.7)
xgrid(ax)
p.text(96.2,98.2,"Circle, Galaxy · square, custom code",fontsize=6.5)
p.text(96.2,103,"Filled, includes reruns · open, scoring rule only",fontsize=6.5)

p.line(3,108,176,108)
p.heading(2,113,"d","IWC · DeepSeek V4 Pro mean output agreement")
iwc=effects[effects.benchmark=="IWC"].set_index("condition")
for x,cond in [(6.2,"Galaxy"),(93,"custom code")]:
    r=iwc.loc[cond]
    noun = "run" if r.reruns == 1 else "runs"
    p.text(x,119.7,f"{cond.capitalize()}   {r.before_pct:.2f}% → {r.after_pct:.2f}%    ({r.reruns:.0f} {noun} replaced out of 30)")
p.save(__file__)
