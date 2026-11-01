"""Sequential action transitions; unobserved rows are masked rather than zero-filled."""
from pathlib import Path
import sys
from collections import defaultdict
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('05_action_transitions');setup();data=rows(args,'actions.csv')
    fig,axs=plt.subplots(2,2,figsize=(9,7));cmap=plt.get_cmap('Blues').copy();cmap.set_bad('#E5E9EC')
    for ax,method in zip(axs.flat,METHODS):
        groups=defaultdict(list)
        for row in subset(data,method):groups[row['question_id']].append(row)
        counts=np.zeros((4,4),dtype=int)
        for seq in groups.values():
            if len({int(r['turn'])for r in seq})!=len(seq):raise ValueError('Parallel actions need an explicit ordering policy')
            seq.sort(key=lambda r:int(r['turn']))
            for a,b in zip(seq,seq[1:]):counts[TOOLS.index(a['tool']),TOOLS.index(b['tool'])]+=1
        prob=normalize_rows(counts)
        im=ax.imshow(np.ma.masked_invalid(prob),vmin=0,vmax=1,cmap=cmap)
        for i in range(4):
            for j in range(4):ax.text(j,i,'-'if np.isnan(prob[i,j])else f'{prob[i,j]:.0%}',ha='center',va='center',color='white'if prob[i,j]>.5 else INK,fontsize=9)
        ax.set_xticks(range(4),TOOLS);ax.set_yticks(range(4),TOOLS);ax.set_title(method);ax.set_xlabel('Next action');ax.set_ylabel('Current action')
    fig.subplots_adjust(wspace=.5,hspace=.6,bottom=.12,right=.9)
    cb=fig.colorbar(im,ax=axs,fraction=.035,pad=.03);cb.set_label('Row-normalized probability')
    save(fig,args,'05_action_transitions','Gray rows = no observed source-state transitions')

if __name__=='__main__':main()
