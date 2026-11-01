"""Aligned question rows let readers inspect correctness and resource use."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *
from matplotlib.colors import ListedColormap

def main():
    args=arguments('15_question_method_matrix');setup();data=rows(args,'questions.csv');all_ids=sorted({r['question_id']for r in data});ids=all_ids[:24]
    index={(r['question_id'],r['method']):r for r in data}
    correct=np.array([[int(index[q,m]['correct'])for m in METHODS]for q in ids]);tokens=np.array([[float(index[q,m]['main_input_tokens'])for m in METHODS]for q in ids])
    if np.any(tokens<=0):raise ValueError('Log token scale requires strictly positive values')
    fig,axs=plt.subplots(1,2,figsize=(9.4,7),sharey=True,gridspec_kw={'wspace':.28})
    a=axs[0].imshow(correct,aspect='auto',cmap=ListedColormap(['#EEF1F4','#009E73']),vmin=0,vmax=1);b=axs[1].imshow(np.log10(tokens),aspect='auto',cmap='Blues')
    axs[0].set_title('Correctness');axs[1].set_title('Solver input tokens')
    for ax in axs:ax.set_xticks(range(4),METHODS,rotation=22,ha='right');ax.set_yticks(range(len(ids)),ids,fontsize=7);ax.tick_params(length=0)
    cb=fig.colorbar(a,ax=axs[0],fraction=.045,pad=.04,ticks=[0,1]);cb.ax.set_yticklabels(['Wrong','Correct'])
    cb=fig.colorbar(b,ax=axs[1],fraction=.045,pad=.04);cb.set_label('log10(tokens)')
    fig.subplots_adjust(left=.09,right=.96,bottom=.14,top=.92)
    save(fig,args,'15_question_method_matrix',f'First {len(ids)} of {len(all_ids)} question IDs; identical row order in both panels')

if __name__=='__main__':main()
