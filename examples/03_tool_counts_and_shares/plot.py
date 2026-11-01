"""Absolute agent-visible calls and pooled call shares with explicit denominators."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('03_tool_counts_and_shares');setup();data=rows(args,'tool_calls.csv')
    fig,axs=plt.subplots(1,2,figsize=(11,4.3));x=np.arange(4)
    count=np.array([[sum(float(r['calls'])for r in subset(data,m)if r['tool']==t)for t in TOOLS]for m in METHODS])
    n=np.array([len(set(r['question_id']for r in subset(data,m)))for m in METHODS])
    share=normalize_rows(count)*100
    for ax,values in zip(axs,[count/n[:,None],share]):
        bottom=np.zeros(4)
        for j,t in enumerate(TOOLS):
            ax.bar(x,values[:,j],bottom=bottom,color=TOOL_COLORS[t],width=.65,label=t)
            bottom+=values[:,j]
        ax.set_xticks(x,METHODS,rotation=18);ax.grid(axis='y')
    axs[0].set(title='(a) Agent tool calls',ylabel='Calls / question')
    axs[1].set(title='(b) Pooled call composition',ylabel='Share of all calls (%)',ylim=(0,105))
    handles,labels=axs[1].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=4,fontsize=9,loc='lower center',bbox_to_anchor=(.5,.07))
    fig.tight_layout(rect=[0,.17,1,1]);save(fig,args,'03_tool_counts_and_shares','Auto reranking is implicit work; see its scoring ledger in Example 01')

if __name__=='__main__':main()
