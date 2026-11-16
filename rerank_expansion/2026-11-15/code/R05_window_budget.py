"""FIRST reproduction Table 6: fixed window, varied stride, no cross-table joins."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    setup()
    args=options('R05_window_budget')
    rows=read(args,'first_window_budget.csv')
    fig,axes=plt.subplots(1,2,figsize=(11.6,6.0))
    fig.subplots_adjust(left=.09,right=.96,bottom=.24,top=.78,wspace=.25)
    heading(fig,'More overlapping windows: cost rises, gains vary',
            'FIRST window/stride experiment: fixed window = 20, top-100 candidates; one RTX 4090')
    colors={10:TEAL,5:BLUE,2:ORANGE}
    for ax,dataset in zip(axes,['DL19','DL20']):
        selected=sorted([r for r in rows if r['dataset']==dataset and int(r['window'])==20],
                        key=lambda r:float(r['latency_s']))
        x=[float(r['latency_s']) for r in selected]
        y=[float(r['ndcg10'])*100 for r in selected]
        ax.plot(x,y,color='#C5D0D6',lw=1.5,zorder=1)
        for r,xx,yy in zip(selected,x,y):
            stride=int(r['stride']);color=colors[stride]
            ax.scatter(xx,yy,s=90,color=color,edgecolor='white',linewidth=1.1,zorder=3)
            # Label placements are fixed by point, never inferred as another result.
            if dataset=='DL19': offsets={10:(8,-38),5:(8,-34),2:(-9,10)}
            else: offsets={10:(8,-34),5:(9,11),2:(-9,-35)}
            dx,dy=offsets[stride]
            ax.annotate(f"stride {stride} · {r['llm_calls']} calls\n{xx:.2f}s · {yy:.2f}",
                        (xx,yy),xytext=(dx,dy),textcoords='offset points',fontsize=9,
                        color=color,ha='right' if dx<0 else 'left')
        ax.set_title(dataset,loc='left',pad=10)
        ax.set_xlim(.8,9.5)
        ax.set_xticks([1,3,5,7,9])
        ax.set_xlabel('Reranking latency (seconds / query)')
        ax.set_ylabel('nDCG@10 × 100')
        ax.grid(alpha=.9)
        if dataset=='DL19':ax.set_ylim(76.45,77.85)
        else:ax.set_ylim(78.25,79.45)
    save(fig,args,'R05_window_budget','Chen et al., FIRST reproduction, Table 6 (SIGIR 2025)',
         'Panels use different y-ranges. Source naming caveat: caption says RankMistral; Section 5.6 describes FIRST. No cross-table merge.')

if __name__=='__main__':
    main()
