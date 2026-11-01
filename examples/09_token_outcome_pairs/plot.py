"""SIEVE-inspired layout; original implementation with paired synthetic data."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('09_token_outcome_pairs');setup();data=rows(args,'questions.csv')
    paired=pair_by_id(subset(data,'Baseline'),subset(data,'Agent rerank'))
    delta=np.array([float(b['main_input_tokens'])-float(a['main_input_tokens'])for a,b in paired])/1e6
    flip=np.array([int(b['correct'])-int(a['correct'])for a,b in paired]);order=np.argsort(delta);x=np.arange(len(paired))
    fig,axs=plt.subplots(2,1,figsize=(9.6,5.7),sharex=True,gridspec_kw={'height_ratios':[1,1.7],'hspace':.12})
    for value,color,label in [(1,'#009E73','Wrong to correct'),(-1,'#D58A45','Correct to wrong')]:
        xx=x[flip[order]==value];axs[0].vlines(xx,0,value,color=color,lw=1.3,label=label)
    axs[0].scatter(x[flip[order]==0],np.zeros(np.sum(flip==0)),s=5,color='#A9B5BD')
    axs[0].axhline(0,color=INK,lw=.5);axs[0].set_yticks([-1,0,1],['Lost','Same','Gained']);axs[0].set_ylim(-1.25,1.3);axs[0].legend(ncol=2,fontsize=8,loc='upper left')
    axs[1].bar(x,delta[order],color=np.where(delta[order]<=0,'#6E9AB2','#D6A174'),width=1)
    axs[1].axhline(0,color=INK,lw=.8);axs[1].set(ylabel='Input token delta (million)',xlabel='Same questions, sorted by token change')
    axs[1].grid(axis='y');axs[0].set_title('Per-question outcome changes aligned with token changes')
    fig.subplots_adjust(bottom=.15,left=.12,right=.98,top=.92)
    save(fig,args,'09_token_outcome_pairs','Agent rerank minus Baseline; all paired questions, no clipping')

if __name__=='__main__':main()
