"""RankRAG Table 8: answer Recall@5 before and after reranking."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plotlib import setup, options, read, heading, save, plt, np, GRAY, TEAL, INK, LIGHT


def main():
    setup()
    args = options('R02_answer_recall')
    source = read(args, 'rankrag_answer_recall.csv')
    rows = [r for retriever in ['DPR', 'Contriever'] for r in source
            if r['retriever'] == retriever and int(r['cutoff_k']) == 5]
    fig, (ax, gains) = plt.subplots(1, 2, figsize=(10, 5.8),
                                    gridspec_kw={'width_ratios': [5.3, 1]})
    fig.subplots_adjust(left=.245, right=.95, top=.79, bottom=.19, wspace=.09)
    heading(fig, 'Bring answer-bearing passages into the top five',
            'RankRAG-8B | Both retrievers and all three datasets in Table 8 | Answer Recall@5')
    y = np.arange(len(rows))[::-1]
    before = np.array([float(r['before_recall_pct']) for r in rows])
    after = np.array([float(r['after_recall_pct']) for r in rows])
    ax.axhline(2.5, color=LIGHT, lw=1)
    ax.hlines(y, before, after, color='#C8D4DA', linewidth=3, zorder=2)
    ax.scatter(before, y, color=GRAY, s=58, zorder=3, label='Before reranking')
    ax.scatter(after, y, color=TEAL, s=58, zorder=3, label='After reranking')
    for yi, b, a in zip(y, before, after):
        ax.annotate(f'{b:.2f}', (b, yi), xytext=(-8, 0), textcoords='offset points',
                    ha='right', va='center', fontsize=9, color='#607581')
        ax.annotate(f'{a:.2f}', (a, yi), xytext=(8, 0), textcoords='offset points',
                    ha='left', va='center', fontsize=9, color=TEAL, fontweight='bold')
    ax.set_yticks(y, [f"{r['retriever']} / {r['dataset']}" for r in rows])
    ax.tick_params(axis='y', length=0, pad=12)
    ax.set(xlim=(32, 100), ylim=(-.55, len(rows)-.45), xlabel='Answer Recall@5 (%)')
    ax.set_xticks([40, 60, 80, 100])
    ax.grid(axis='x')
    ax.spines['left'].set_visible(False)
    ax.legend(loc='lower left', bbox_to_anchor=(-.015, 1.02), ncol=2,
              handletextpad=.4, columnspacing=1.8, fontsize=9)
    gains.set(xlim=(0, 1), ylim=ax.get_ylim())
    gains.axis('off')
    gains.text(.55, 1.06, 'Gain (pp)', transform=gains.transAxes,
               ha='center', color=INK, fontsize=9)
    for yi, b, a in zip(y, before, after):
        gains.text(.55, yi, f'+{a-b:.2f}', ha='center', va='center',
                   color=TEAL, fontsize=12, fontweight='bold')
    save(fig, args, 'R02_answer_recall', 'RankRAG (2407.02485v1), Table 8, p. 21',
         'The cutoff is five retrieved ranks, not five reranker candidates. R@10 and R@20 remain in the source CSV.')


if __name__ == '__main__':
    main()
