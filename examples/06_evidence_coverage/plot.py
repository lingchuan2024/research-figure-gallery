"""Auditable evidence-stage coverage; answer accuracy is not forced into a funnel."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('06_evidence_coverage');setup();data=rows(args,'questions.csv')
    fig,ax=plt.subplots(figsize=(9.5,4.5));x=np.arange(3);width=.18
    keys=['gold_in_pool','gold_shown','gold_located']
    for i,m in enumerate(METHODS):
        r=subset(data,m);vals=np.array([numbers(r,k)for k in keys])
        if not np.all((vals[0]>=vals[1])&(vals[1]>=vals[2])):raise ValueError('Demo stage definitions require nested evidence states')
        y=vals.mean(axis=1)*100
        ax.bar(x+(i-1.5)*width,y,width,color=COLORS[m],label=m)
        for xx,yy in zip(x+(i-1.5)*width,y):ax.text(xx,yy+1,f'{yy:.0f}',ha='center',fontsize=8)
    ax.set_xticks(x,['In candidate pool','Shown in a snippet','Located in source']);ax.set_ylabel('Questions with known gold evidence (%)');ax.set_ylim(0,105);ax.grid(axis='y');ax.legend(ncol=2,fontsize=9)
    ax.set_title('Where available evidence becomes visible and verifiable')
    fig.tight_layout(rect=[0,.07,1,1]);save(fig,args,'06_evidence_coverage','Stage definitions are explicit; real traces may require additional access paths')

if __name__=='__main__':main()
