"""Separate solver and reranker token accounting; all demo data are synthetic."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('01_token_breakdown');setup()
    data=rows(args,'questions.csv');x=np.arange(len(METHODS))
    fig,axs=plt.subplots(1,2,figsize=(10.5,4.1),gridspec_kw={'width_ratios':[1.3,1]})
    bottom=np.zeros(len(METHODS))
    for key,label,color in [('main_uncached_tokens','Uncached input','#567FA3'),('main_cached_tokens','Cached input','#ACCADB'),('main_output_tokens','Output','#E6AB63')]:
        values=np.array([numbers(subset(data,m),key).mean()/1e6 for m in METHODS])
        axs[0].bar(x,values,bottom=bottom,label=label,color=color,width=.62)
        bottom+=values
    for i,v in enumerate(bottom):axs[0].text(i,v,f'{v:.2f}',ha='center',va='bottom',fontsize=9)
    rr=[numbers(subset(data,m),'reranker_input_tokens').mean()/1e6 for m in METHODS]
    axs[1].bar(x,rr,color=[COLORS[m]for m in METHODS],width=.62)
    for i,v in enumerate(rr):axs[1].text(i,v,f'{v:.2f}',ha='center',va='bottom',fontsize=9)
    for ax in axs:
        ax.set_xticks(x,METHODS,rotation=18);ax.set_ylabel('Million tokens / question');ax.grid(axis='y');ax.margins(y=.15)
    axs[0].set_title('(a) Solver token ledger');axs[0].legend(fontsize=8)
    axs[1].set_title('(b) Reranker input ledger')
    fig.tight_layout(rect=[0,.08,1,1]);save(fig,args,'01_token_breakdown','Different model tokens are not a common compute-cost unit')

if __name__=='__main__':main()
