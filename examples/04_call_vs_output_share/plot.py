"""Call composition and returned-character composition have different denominators."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('04_call_vs_output_share');setup();data=rows(args,'tool_calls.csv')
    fig,axs=plt.subplots(1,2,figsize=(10.6,4.2),sharey=True)
    for ax,key,title in zip(axs,['calls','returned_chars'],['(a) Share of agent tool calls','(b) Share of returned characters']):
        matrix=np.array([[sum(float(r[key])for r in subset(data,m)if r['tool']==t)for t in TOOLS]for m in METHODS])
        matrix=normalize_rows(matrix)*100;left=np.zeros(4)
        for j,t in enumerate(TOOLS):
            ax.barh(np.arange(4),matrix[:,j],left=left,color=TOOL_COLORS[t],height=.60,label=t)
            for i,v in enumerate(matrix[:,j]):
                if v>=8:ax.text(left[i]+v/2,i,f'{v:.0f}%',ha='center',va='center',fontsize=8)
            left+=matrix[:,j]
        ax.set_xlim(0,100);ax.set_xlabel('Pooled share (%)');ax.set_title(title);ax.grid(axis='x')
    axs[0].set_yticks(range(4),METHODS);axs[0].invert_yaxis()
    fig.legend(*axs[1].get_legend_handles_labels(),loc='lower center',ncol=4,bbox_to_anchor=(.55,.06))
    fig.tight_layout(rect=[0,.14,1,1]);save(fig,args,'04_call_vs_output_share','Returned characters are not billed input tokens')

if __name__=='__main__':main()
