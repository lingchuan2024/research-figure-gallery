"""Budget sweep with an explicit uncertainty convention."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('14_budget_accuracy');setup();data=rows(args,'budget_runs.csv');fig,ax=plt.subplots(figsize=(8.8,5))
    for m in METHODS:
        group=subset(data,m);xx=[];yy=[];interval=[]
        for budget in sorted({int(r['budget'])for r in group}):
            rr=[r for r in group if int(r['budget'])==budget];n=len(rr);s=sum(int(r['correct']) for r in rr)
            xx.append(budget);yy.append(100*s/n);interval.append(np.array(wilson_interval(s,n))*100)
        ci=np.array(interval);ax.plot(xx,yy,'o-',ms=4,color=COLORS[m],label=m);ax.fill_between(xx,ci[:,0],ci[:,1],color=COLORS[m],alpha=.10,lw=0)
    ax.set(xlabel='Maximum model turns',ylabel='Correct answers (%)',ylim=(0,100),title='How much budget is enough?',xticks=[10,20,40,60,100]);ax.grid();ax.legend(ncol=2,loc='lower right',fontsize=9)
    fig.tight_layout(rect=(0,.10,1,1));save(fig,args,'14_budget_accuracy','Shading: pointwise 95% Wilson intervals; demo budget runs, not truncated traces')

if __name__=='__main__':main()
