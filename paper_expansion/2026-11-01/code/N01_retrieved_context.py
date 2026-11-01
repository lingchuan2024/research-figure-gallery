"""A-RAG v1 Table 3: retrieved corpus text, NOT solver input or total cost."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    args=options('N01_retrieved_context');setup();rows=read(args,'arag_context.csv')
    datasets=list(dict.fromkeys(r['dataset']for r in rows));methods=['Naive RAG','A-RAG Naive','A-RAG Full'];colors=[GRAY,ORANGE,GREEN]
    index={(r['dataset'],r['method']):float(r['retrieved_tokens'])for r in rows};y=np.arange(len(datasets))
    fig,(ax,delta)=plt.subplots(1,2,figsize=(11.3,4.8),sharey=True,gridspec_kw={'width_ratios':[2.1,1],'wspace':.16})
    for i,d in enumerate(datasets):ax.plot([index[d,'A-RAG Naive'],index[d,'A-RAG Full']],[i,i],color='#D4DDE2',lw=3,zorder=0)
    for m,c,marker in zip(methods,colors,['D','o','o']):
        ax.scatter([index[d,m]for d in datasets],y,color=c,s=42,marker=marker,label=m,zorder=3)
    ax.set_xscale('log');ax.set(yticks=y,yticklabels=datasets,xlim=(1800,90000),xlabel='Retrieved corpus tokens (log scale)',title='Text exposed through retrieval tools')
    ax.set_xticks([2000,5000,10000,20000,50000],['2k','5k','10k','20k','50k']);ax.grid(axis='x');ax.invert_yaxis()
    reduction=np.array([100*(1-index[d,'A-RAG Full']/index[d,'A-RAG Naive'])for d in datasets])
    delta.hlines(y,0,reduction,color='#CDE4DB',lw=3);delta.scatter(reduction,y,color=GREEN,s=36)
    for i,v in enumerate(reduction):delta.text(v+2,i,f'{v:.1f}%',va='center',fontsize=9)
    delta.set(xlim=(0,110),xticks=[0,25,50,75,100],xlabel='Reduction vs. A-RAG Naive (%)',title='Interface-related reduction');delta.grid(axis='x');delta.tick_params(axis='y',left=False)
    handles,labels=ax.get_legend_handles_labels();fig.legend(handles,labels,ncol=3,loc='lower center',bbox_to_anchor=(.5,.075),fontsize=9)
    fig.suptitle('Hierarchical retrieval exposes less text than the naive agent',fontsize=14);fig.subplots_adjust(left=.10,right=.98,top=.80,bottom=.26)
    save(fig,args,'N01_retrieved_context','A-RAG (2602.03442v1), Table 3; GPT-5-mini; aggregates only, no uncertainty estimates')

if __name__=='__main__':main()
