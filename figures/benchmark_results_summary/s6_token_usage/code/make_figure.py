"""October token footprint and the sequence of historical BixBench measurements."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from plot_style import BENCH, G, GRID, INK, MODELS, MUTED, PALE, Plate, data, xgrid

d=data(__file__)
october=d[d.panel=="main_runs"].set_index(["benchmark","model"])
history=d[d.panel=="historical_rounds"].sort_values("order")
p=Plate(114)
for j,(bench,x) in enumerate(zip(BENCH,[32,83,134])):
    p.heading(2 if j==0 else x-5,4,"abc"[j],bench)
    pooled=october.loc[(bench,"Pooled")]
    direction = "more" if pooled.galaxy_token_change_pct >= 0 else "fewer"
    p.text(6.2 if j==0 else x-.8,9.6,f"{abs(pooled.galaxy_token_change_pct):.0f}% {direction} tokens overall",weight="bold")
    ax=p.axes(x,14.3,39,30)
    ax.set_xscale("log",base=2)
    ax.axhspan(3.5,4.5,color=PALE,zorder=0)
    ax.axvline(1,color=MUTED,lw=.8)
    for y,m in enumerate([*MODELS,"Pooled"]):
        ratio=october.loc[(bench,m),"ratio"]
        ax.hlines(y,min(1,ratio),max(1,ratio),color=MUTED,lw=.7)
        ax.plot(ratio,y,"D" if y==4 else "o",ms=4 if y==4 else 3.7,color=G)
    ax.set(xlim=(.25,8),xticks=[.25,.5,1,2,4,8],xticklabels=["¼","½","1","2","4","8"],ylim=(4.5,-.5),
           yticks=range(5),yticklabels=[*MODELS,"All four models"] if j==0 else [])
    if j==0:
        ax.get_yticklabels()[-1].set_weight("bold")
    xgrid(ax)
p.text(101,53.8,"Galaxy / custom-code tokens (log scale) · 1 means equal use",ha="center",weight="bold")
p.line(2,58.2,178,58.2)

stage_names={"baseline":"Baseline","round1":"Prompts and skills","round1-rerun":"Prompts and skills",
             "round2":"Galaxy MCP server","round2-sol":"Galaxy MCP server","round3a":"Compact replies","round3b":"Compact + longer waits"}
for i,(model,start) in enumerate([("GPT-5.5",2),("GPT-5.6 Sol",93)]):
    block=history[history.model==model]
    p.heading(start,63,"de"[i],f"BixBench campaigns with {model}")
    p.text(start+2,69.8,"Interface stage",weight="bold",fontsize=6.5)
    p.text(start+37,69.8,"Replicates",weight="bold",ha="center",fontsize=6.5)
    p.text(start+65,69.8,"Galaxy / custom code",weight="bold",ha="center",fontsize=6.5)
    ax=p.axes(start+48,74.5,37,24)
    ax.set_xscale("log",base=2)
    for y,r in enumerate(block.itertuples()):
        yy=74.5+(y+.5)*24/4
        p.text(start+2,yy,stage_names[r.slug])
        p.text(start+37,yy,f"{r.runs_per_task:.0f}",ha="center")
        estimated=r.evidence=="author estimate"
        ax.plot(r.ratio,y,"o",ms=3.8,mfc="white" if estimated else G,mec=G,mew=.8)
        # Keep labels inside the frame and separate the text from the point.
        right=r.ratio<12
        ax.annotate(("≈" if estimated else "")+(f"{r.ratio:.0f}" if estimated else f"{r.ratio:.2f}")+"×",
                    (r.ratio,y),xytext=(4 if right else -4,0),textcoords="offset points",
                    va="center",ha="left" if right else "right",fontsize=6.5)
    ax.set(xlim=(.8,24),xticks=[1,2,4,8,16],xticklabels=["1","2","4","8","16"],ylim=(3.5,-.5),yticks=[])
    ax.axvline(1,color=MUTED,lw=.6)
    xgrid(ax)
p.text(4,109,"Open circles, author estimates  ·  Filled circles, ratios from recorded totals",fontsize=6.5)
p.save(__file__)
