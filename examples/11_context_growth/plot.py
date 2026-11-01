"""Per-turn context distribution with the number of surviving trajectories."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('11_context_growth');setup();data=rows(args,'context.csv')
    fig,axs=plt.subplots(2,1,figsize=(9.3,5.7),sharex=True,gridspec_kw={'height_ratios':[2.1,1],'hspace':.12})
    for m in METHODS:
        group=subset(data,m);turns=sorted({int(r['turn']) for r in group});quant=[];counts=[]
        for t in turns:
            values=np.array([int(r['input_tokens'])for r in group if int(r['turn'])==t])/1000
            quant.append(np.quantile(values,[.25,.5,.75]));counts.append(len(values))
        q=np.array(quant);axs[0].plot(turns,q[:,1],color=COLORS[m],label=m);axs[0].fill_between(turns,q[:,0],q[:,2],color=COLORS[m],alpha=.12,lw=0)
        axs[1].plot(turns,counts,color=COLORS[m])
    axs[0].set(title='Context grows while the active question cohort changes',ylabel='Input tokens per turn (thousand)');axs[0].legend(ncol=2,fontsize=8)
    axs[1].set(xlabel='Model turn',ylabel='Active questions');axs[1].set_ylim(bottom=0)
    for ax in axs:ax.grid(axis='y')
    fig.subplots_adjust(left=.13,right=.98,bottom=.16,top=.91)
    save(fig,args,'11_context_growth','Median and IQR among questions still running at each turn')

if __name__=='__main__':main()
