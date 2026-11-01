"""A-RAG v1 Tables 7–8. The two panels deliberately have different denominators."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    args=options('N02_failure_hierarchy');setup();data=read(args,'arag_failures.csv')
    fig,axs=plt.subplots(1,2,figsize=(12,4.7),gridspec_kw={'wspace':.70})
    for ax,pop,title,color in zip(axs,['all_errors','reasoning_chain_errors'],['All reviewed errors','Within reasoning-chain errors'],[BLUE,ORANGE]):
        rr=sorted([r for r in data if r['population']==pop],key=lambda r:float(r['percent']),reverse=True)
        y=np.arange(len(rr));v=np.array([float(r['percent'])for r in rr]);ax.barh(y,v,color=color,alpha=.85,height=.56)
        for i,x in enumerate(v):ax.text(x+1.8,i,f'{x:.0f}%',va='center',fontsize=10)
        ax.set(yticks=y,yticklabels=[r['category']for r in rr],xlim=(0,100),xlabel='Share of this panel’s population (%)',title=title);ax.invert_yaxis();ax.grid(axis='x')
    fig.suptitle('A failure taxonomy separates bad retrieval from bad use of evidence',fontsize=14)
    fig.subplots_adjust(left=.17,right=.96,top=.78,bottom=.24)
    save(fig,args,'N02_failure_hierarchy','A-RAG (2602.03442v1), Tables 7–8; MuSiQue, first 100 incorrect cases; subgroup percentages are rounded')

if __name__=='__main__':main()
