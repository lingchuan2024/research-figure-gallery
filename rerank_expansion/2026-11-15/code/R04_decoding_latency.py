"""FIRST reproduction Table 5: decoding latency without cross-table quality joins."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    setup()
    args = options('R04_decoding_latency')
    rows = read(args, 'first_decoding_latency.csv')
    fig, axes = plt.subplots(1,2,figsize=(11.6,5.9),sharex=True,sharey=True)
    fig.subplots_adjust(left=.10,right=.96,bottom=.22,top=.75,wspace=.19)
    heading(fig,'Shorter decoding lowers reranker latency',
            'Average seconds per query on one RTX 4090; two decoding modes within each table-labeled model')
    for ax, model in zip(axes,['RankZephyr','RankMistral']):
        for index,dataset in enumerate(['DL19','DL20','DL21','DL22','DL23']):
            r=next(x for x in rows if x['dataset']==dataset and x['model_table_label']==model)
            y=4-index
            full=float(r['full_generation_latency_s'])
            first=float(r['first_identifier_latency_s'])
            ax.plot([first,full],[y,y],color='#C5D0D6',lw=2.5,zorder=1)
            ax.plot(full,y,'o',ms=7,mfc='white',mec=BLUE,mew=2,
                    label='Full permutation' if index==0 else None,zorder=3)
            ax.plot(first,y,'s',ms=6,color=TEAL,
                    label='First-identifier logits' if index==0 else None,zorder=3)
            ax.text(first,y+.19,f'{first:.2f}',ha='center',va='bottom',fontsize=9,color=TEAL)
            ax.text(full,y+.19,f'{full:.2f}',ha='center',va='bottom',fontsize=9,color=BLUE)
            ax.text(3.68,y,f"−{float(r['reported_latency_reduction_pct']):.1f}%",
                    ha='right',va='center',fontsize=9,color=INK)
        ax.set_title(model,loc='left',pad=12)
        ax.text(3.68,4.60,'Latency change',ha='right',fontsize=8,color=GRAY)
        ax.set_yticks([4,3,2,1,0]);ax.set_yticklabels(['DL19','DL20','DL21','DL22','DL23'])
        ax.set_ylim(-.45,4.95);ax.set_xlim(0,3.80)
        ax.set_xticks([0,1,2,3]);ax.set_xlabel('Reranking latency (seconds / query)')
        ax.tick_params(axis='y',length=0,pad=8)
        ax.grid(axis='x');ax.spines['left'].set_visible(False)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper left',bbox_to_anchor=(.10,.86),ncol=2,fontsize=9)
    save(fig,args,'R04_decoding_latency','Chen et al., FIRST reproduction, Table 5 (SIGIR 2025)',
         'Top 100; window 20 / stride 10; nine calls per query. Output tokens: 711 vs. 18. Reranker latency only; accuracy is not plotted.')

if __name__=='__main__':
    main()
