"""DRB II v3 Table 4: evaluation cost vs agreement with humans; not agent-inference cost."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    args=options('N08_evaluator_budget');setup();data=read(args,'judge_batch.csv');fig,ax=plt.subplots(figsize=(9.5,4.8));offset={'full':(-12,-20),'80':(-10,12),'50':(12,10),'10':(12,10),'5':(-12,-16)}
    for r in data:
        x=float(r['evaluation_cost_usd_per_task']);y=float(r['human_agreement_f1_percent']);selected=r['batch_size']=='50';color=GREEN if selected else BLUE
        ax.scatter(x,y,s=95 if selected else 65,color=color,edgecolor='white',linewidth=1,zorder=3);dx,dy=offset[r['batch_size']]
        label=('Full batch'if r['batch_size']=='full'else 'Batch '+r['batch_size'])+f'\n${x:.4f}, F1 {y:.2f}'
        ax.annotate(label,(x,y),xytext=(dx,dy),textcoords='offset points',ha='left'if dx>0 else 'right',va='center',fontsize=9,color=color)
    ax.set(xlim=(0,.98),ylim=(83.5,92),xlabel='Evaluator cost per task (USD)',ylabel='Agreement with human labels (F1, %)',title='Budget the evaluator and verify its reliability');ax.grid()
    ax.text(.97,.96,'Green: paper’s chosen default',transform=ax.transAxes,ha='right',va='top',fontsize=9,color=GREEN)
    fig.subplots_adjust(left=.12,right=.98,top=.87,bottom=.21)
    save(fig,args,'N08_evaluator_budget','DeepResearch Bench II (2601.08536v3), Table 4; Gemini-2.5-Pro judge, 10 human-labeled reports; no significance claim')

if __name__=='__main__':main()
