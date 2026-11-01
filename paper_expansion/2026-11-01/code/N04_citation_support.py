"""DeepResearch Bench v1 Table 1 FACT scores; original-paper snapshot, not a current leaderboard."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    args=options('N04_citation_support');setup();data=read(args,'deepbench_fact.csv');fig,ax=plt.subplots(figsize=(9.8,5.1))
    short={'Grok Deeper Search':'Grok','Perplexity Deep Research':'Perplexity','Gemini 2.5 Pro Deep Research':'Gemini 2.5 Pro','OpenAI Deep Research':'OpenAI'}
    offsets={'Grok Deeper Search':(12,-3),'Perplexity Deep Research':(12,10),'Gemini 2.5 Pro Deep Research':(-12,12),'OpenAI Deep Research':(12,-5)}
    for r,color in zip(data,[GRAY,BLUE,GREEN,ORANGE]):
        x=float(r['effective_citations_per_task']);y=float(r['citation_accuracy_percent']);ax.scatter(x,y,color=color,s=100,edgecolor='white',lw=1.2,zorder=3);dx,dy=offsets[r['agent']]
        ax.annotate(short[r['agent']]+f'\n{x:.2f} / {y:.2f}%',(x,y),xytext=(dx,dy),textcoords='offset points',ha='left'if dx>0 else 'right',va='bottom',fontsize=10,color=INK)
    ax.set(xlim=(0,125),ylim=(70,100),xlabel='Effective citations per task (FACT E. Cit.)',ylabel='Citation support accuracy (FACT C. Acc., %)',title='Supported information volume and citation accuracy are different axes');ax.grid()
    fig.subplots_adjust(left=.12,right=.98,top=.88,bottom=.20)
    save(fig,args,'N04_citation_support','DeepResearch Bench (2506.11763v1), Table 1; four DR agents; deduplicated statement–URL pairs, not raw URL counts')

if __name__=='__main__':main()
