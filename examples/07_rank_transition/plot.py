"""Full candidate ranking transitions, retaining evidence that falls outside top-K."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('07_rank_transition');setup();data=rows(args,'ranks.csv');counts=np.zeros((5,5),int);outside=0
    for r in data:
        if int(r['in_candidates'])==0:outside+=1;continue
        a,b=int(r['before_rank']),int(r['after_rank'])
        if not(1<=a<=1000 and 1<=b<=1000):raise ValueError('Ranks must be in the declared 1..1000 candidate universe')
        counts[np.searchsorted([1,5,10,100,1000],a),np.searchsorted([1,5,10,100,1000],b)]+=1
    prob=normalize_rows(counts);fig,ax=plt.subplots(figsize=(7,5.6))
    im=ax.imshow(np.ma.masked_invalid(prob),cmap='Blues',vmin=0,vmax=1)
    for i in range(5):
        for j in range(5):
            label=f'{counts[i,j]}\n{prob[i,j]:.0%}' if np.isfinite(prob[i,j]) else '-'
            ax.text(j,i,label,ha='center',va='center',fontsize=9,color='white'if prob[i,j]>.45 else INK)
    bins=['1','2-5','6-10','11-100','101-1000'];ax.set_xticks(range(5),bins);ax.set_yticks(range(5),bins)
    ax.set(xlabel='Rank after reranking',ylabel='Rank before reranking',title='Known-evidence rank transitions')
    fig.colorbar(im,ax=ax,label='Share within the original-rank bin',fraction=.05)
    fig.tight_layout(rect=[0,.08,1,1]);save(fig,args,'07_rank_transition',f'{len(data)-outside} scored snapshots; {outside} outside candidates reported separately')

if __name__=='__main__':main()
