"""ResearchRubrics Figure 6 printed labels; different task strata, not paired interventions."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    args=options('N05_task_complexity');setup();data=read(args,'rubric_complexity.csv');dimensions=list(dict.fromkeys(r['dimension']for r in data));models=['Gemini DR','OpenAI DR','Perplexity DR']
    fig,axs=plt.subplots(1,3,figsize=(12,4.7),sharey=True,gridspec_kw={'wspace':.12})
    for ax,dimension in zip(axs,dimensions):
        rr=[r for r in data if r['dimension']==dimension];levels=list(dict.fromkeys(r['level']for r in rr));x=np.arange(3)
        for model,color in zip(models,[GREEN,BLUE,ORANGE]):
            vals=[float(next(r['compliance_percent']for r in rr if r['level']==lv and r['model']==model))for lv in levels];ax.plot(x,vals,'o-',ms=5,lw=2,color=color,label=model)
        ax.set(title=dimension,xticks=x,xticklabels=levels,ylim=(40,80),xlim=(-.15,2.15));ax.tick_params(axis='x',labelsize=8);ax.grid(axis='y')
    axs[0].set_ylabel('Ternary rubric compliance (%)');handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,ncol=3,loc='lower center',bbox_to_anchor=(.5,.08))
    fig.suptitle('Stratify results by the kind of difficulty, not just an overall average',fontsize=14);fig.subplots_adjust(left=.075,right=.98,top=.79,bottom=.27)
    save(fig,args,'N05_task_complexity','ResearchRubrics (2511.07685), Figure 6 labels; observational task groups; no paired effects or uncertainty claimed')

if __name__=='__main__':main()
