"""Question-level paired query metrics and their paired mean difference."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('08_query_paired_comparison');setup();data=rows(args,'query_pairs.csv')
    if len({r['question_id']for r in data})!=len(data):raise ValueError('One paired snapshot per question is required')
    a=numbers(data,'search_ndcg');b=numbers(data,'rerank_ndcg');delta=b-a;order=np.argsort(delta);y=np.arange(len(data))
    fig,axs=plt.subplots(1,2,figsize=(10,7.5),sharey=True,gridspec_kw={'width_ratios':[1.6,1]})
    axs[0].hlines(y,a[order],b[order],color='#CED8DE',lw=1.5)
    axs[0].scatter(a[order],y,color='#4C78A8',s=24,label='Search query',zorder=3)
    axs[0].scatter(b[order],y,color='#009E73',s=24,label='Rerank query',zorder=3)
    axs[0].set_yticks(y,[data[i]['question_id']for i in order]);axs[0].set_xlim(0,1);axs[0].set_xlabel('nDCG@10 (synthetic labels)');axs[0].legend(fontsize=9)
    axs[1].barh(y,delta[order],color=np.where(delta[order]>=0,'#009E73','#D58A45'),height=.65);axs[1].axvline(0,color=INK,lw=.8);axs[1].set_xlabel('Rerank - search')
    for ax in axs:ax.grid(axis='x')
    ci=paired_bootstrap_ci(delta)
    fig.suptitle(f'Query-only change on frozen candidates\nPaired mean delta {delta.mean():+.3f}; bootstrap 95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]',fontsize=12)
    fig.tight_layout(rect=[0,.05,1,.92]);save(fig,args,'08_query_paired_comparison',f'All {len(data)} paired questions shown; intervals resample questions')

if __name__=='__main__':main()
