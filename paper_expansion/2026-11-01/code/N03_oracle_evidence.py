"""BrowseComp-Plus Table 1 and §4.8.1: an evidence-access diagnostic, not a pure rerank ablation."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    args=options('N03_oracle_evidence');setup();data=read(args,'browse_oracle.csv');models=['GPT-4.1','Qwen3-32B'];settings=['BM25','Dense retrieval','Oracle evidence'];colors=[GRAY,BLUE,GREEN]
    fig,ax=plt.subplots(figsize=(10.3,4.1))
    for i,m in enumerate(models):
        vals=[float(next(r['accuracy_percent']for r in data if r['model']==m and r['setting']==s))for s in settings]
        ax.plot(vals,[i]*3,color='#D2DCE1',lw=3,zorder=0)
        for j,(v,c)in enumerate(zip(vals,colors)):
            ax.scatter(v,i,color=c,s=90,zorder=3,label=settings[j]if i==0 else None);ax.annotate(f'{v:.2f}%',(v,i),xytext=(0,13 if j!=1 else -23),textcoords='offset points',ha='center',fontsize=10,color=c)
    ax.set(yticks=range(2),yticklabels=models,xlim=(-2,103),ylim=(-.6,1.6),xlabel='Answer accuracy (%)',title='What changes when the answer evidence is already available?');ax.invert_yaxis();ax.grid(axis='x')
    ax.legend(ncol=3,loc='upper center',bbox_to_anchor=(.5,-.25),fontsize=9);fig.subplots_adjust(left=.14,right=.98,top=.82,bottom=.31)
    save(fig,args,'N03_oracle_evidence','BrowseComp-Plus (2508.06600v1), Table 1 + §4.8.1; oracle changes access; Qwen includes context-overflow failures')

if __name__=='__main__':main()
