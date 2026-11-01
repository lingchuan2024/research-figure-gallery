"""Paired question bootstrap for an ablation forest plot."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('17_ablation_forest');setup();data=rows(args,'ablations.csv');full=[r for r in data if r['variant']=='Full system'];variants=list(dict.fromkeys(r['variant']for r in data if r['variant']!='Full system'))
    fig,(ax,table)=plt.subplots(1,2,figsize=(9.4,4.8),sharey=True,gridspec_kw={'width_ratios':[2.5,1.2],'wspace':.05})
    all_limits=[]
    for i,v in enumerate(variants):
        paired=pair_by_id(full,[r for r in data if r['variant']==v]);diff=np.array([int(b['correct'])-int(a['correct'])for a,b in paired])*100;mean=diff.mean();lo,hi=paired_bootstrap_ci(diff)
        ax.errorbar(mean,i,xerr=[[mean-lo],[hi-mean]],fmt='o',color='#C08057',ms=7,capsize=4,lw=2)
        table.text(.08,i,f'{mean:+.1f} [{lo:+.1f}, {hi:+.1f}]',va='center',fontsize=9);all_limits.extend([lo,hi])
    ax.axvline(0,color='#6E808B',ls='--',lw=1)
    ax.set(yticks=range(len(variants)),yticklabels=variants,xlabel='Accuracy change vs. full system (pp)',xlim=(min(-1,min(all_limits))-2,max(1,max(all_limits))+2),ylim=(-.85,len(variants)-.5));ax.invert_yaxis();ax.grid(axis='x')
    table.axis('off');table.text(.08,-.65,'Delta [95% CI]',fontsize=9,weight='bold')
    fig.suptitle('Which components explain the gain?',fontsize=13);fig.subplots_adjust(left=.17,right=.98,bottom=.19,top=.85)
    save(fig,args,'17_ablation_forest','Question-paired bootstrap, 3,000 resamples; intervals are not multiplicity-adjusted')

if __name__=='__main__':main()
