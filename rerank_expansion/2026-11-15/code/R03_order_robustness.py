"""RankZephyr Table 7: original vs shuffled top-100 candidate order."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    setup()
    args = options('R03_order_robustness')
    rows = read(args, 'rankzephyr_order_robustness.csv')
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.8), sharey=True)
    fig.subplots_adjust(left=.20, right=.97, bottom=.21, top=.76, wspace=.14)
    heading(fig, 'How much does the starting order matter?',
            'Same top-100 candidates; original retrieval order versus six shuffled orders')
    order = [('RankGPT-3.5', 'BM25'), ('RankGPT-3.5', 'SPLADE++ ED'),
             ('RankZephyr', 'BM25'), ('RankZephyr', 'SPLADE++ ED')]
    for ax, dataset in zip(axes, ['DL19', 'DL20']):
        for index, (model, retriever) in enumerate(order):
            row = next(r for r in rows if r['dataset'] == dataset and r['model'] == model
                       and r['retriever'] == retriever)
            y = 3-index
            original = float(row['original_ndcg10'])
            shuffled = float(row['shuffled_mean_ndcg10'])
            ci = float(row['shuffled_ci99_halfwidth'])
            ax.plot([shuffled, original], [y,y], color='#C5D0D6', lw=2.5, zorder=1)
            ax.plot(original, y, 'o', ms=7, mfc='white', mec=BLUE, mew=2,
                    label='Original order' if index == 0 else None, zorder=3)
            ax.errorbar(shuffled, y, xerr=ci, fmt='s', markersize=6, color=TEAL,
                        capsize=3, lw=1.4, label='Shuffled mean (99% CI)' if index == 0 else None,
                        zorder=4)
            ax.text(.875, y, f'{(shuffled-original)*100:+.2f}', ha='right', va='center',
                    fontsize=9, color=RED if original-shuffled > .04 else INK)
        ax.set_title(dataset, loc='left', pad=12)
        ax.text(.875,3.53,'Δ nDCG ×100', ha='right', fontsize=8.5, color=GRAY)
        ax.set_xlim(.52,.89)
        ax.set_xticks([.55,.60,.65,.70,.75,.80])
        ax.set_ylim(-.5,3.8)
        ax.set_yticks([3,2,1,0])
        ax.set_yticklabels([f'{m}\n{r}' for m,r in order])
        ax.tick_params(axis='y',length=0,pad=10)
        ax.grid(axis='x')
        ax.spines['left'].set_visible(False)
        ax.set_xlabel('nDCG@10')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(.20,.865),
               ncol=2, fontsize=9, handletextpad=.7, columnspacing=2)
    save(fig,args,'R03_order_robustness','Pradeep et al., RankZephyr, Table 7 (2023)',
         'Intervals describe six input-order shuffles; original-order scores have no reported interval. Change = (shuffled - original) × 100.')

if __name__ == '__main__':
    main()
