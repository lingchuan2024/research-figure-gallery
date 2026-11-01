"""Observed configurations, Wilson intervals and a nondominated cost frontier."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('12_accuracy_cost_frontier');setup();data=rows(args,'budget_runs.csv')
    fig,ax=plt.subplots(figsize=(8.8,5.2));all_x=[];all_y=[]
    for m in METHODS:
        group=subset(data,m);xx=[];yy=[];ci=[]
        for b in sorted({int(r['budget']) for r in group}):
            rr=[r for r in group if int(r['budget'])==b];s=sum(int(r['correct']) for r in rr);n=len(rr)
            xx.append(numbers(rr,'cost_units').mean());yy.append(100*s/n);ci.append(np.array(wilson_interval(s,n))*100)
        xx=np.array(xx);yy=np.array(yy);ci=np.array(ci)
        ax.errorbar(xx,yy,yerr=[yy-ci[:,0],ci[:,1]-yy],fmt='o',ms=6,capsize=2,color=COLORS[m],elinewidth=.7,label=m)
        all_x.extend(xx);all_y.extend(yy)
    xx=np.array(all_x);yy=np.array(all_y);idx=pareto_frontier(xx,yy);idx=idx[np.argsort(xx[idx])]
    ax.plot(xx[idx],yy[idx],ls='--',color=INK,lw=1.1,zorder=0,label='Observed Pareto frontier')
    ax.set(title='Accuracy versus mean resource cost',xlabel='Mean cost per question (synthetic units)',ylabel='Correct answers (%)',ylim=(0,100));ax.grid();ax.legend(ncol=2,fontsize=8,loc='lower right')
    fig.tight_layout(rect=(0,.10,1,1));save(fig,args,'12_accuracy_cost_frontier','95% Wilson intervals; cost units are not dollars or mixed-model token counts')

if __name__=='__main__':main()
