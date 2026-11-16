"""RankRAG Table 3: complete OpenQA EM subset, inference reranking ablation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plotlib import setup, options, read, heading, save, plt, np, GRAY, TEAL, INK, LIGHT


def main():
    setup()
    args = options('R01_rerank_qa')
    rows = read(args, 'rankrag_qa_ablation.csv')
    fig, (ax, gains) = plt.subplots(1, 2, figsize=(10, 5.5),
                                    gridspec_kw={'width_ratios': [5.3, 1]})
    fig.subplots_adjust(left=.17, right=.95, top=.79, bottom=.19, wspace=.09)
    heading(fig, 'Does reranking improve the final answer?',
            'RankRAG-8B inference ablation | All five OpenQA datasets | Exact Match')
    y = np.arange(len(rows))[::-1]
    before = np.array([float(r['without_reranking_em']) for r in rows])
    after = np.array([float(r['with_reranking_em']) for r in rows])
    ax.hlines(y, before, after, color='#C8D4DA', linewidth=3, zorder=2)
    ax.scatter(before, y, color=GRAY, s=58, zorder=3, label='Without reranking')
    ax.scatter(after, y, color=TEAL, s=58, zorder=3, label='With reranking')
    for yi, b, a in zip(y, before, after):
        ax.annotate(f'{b:.1f}', (b, yi), xytext=(-8, 0), textcoords='offset points',
                    ha='right', va='center', fontsize=9, color='#607581')
        ax.annotate(f'{a:.1f}', (a, yi), xytext=(8, 0), textcoords='offset points',
                    ha='left', va='center', fontsize=9, color=TEAL, fontweight='bold')
    ax.set_yticks(y, [r['dataset'] for r in rows])
    ax.tick_params(axis='y', length=0, pad=12)
    ax.set(xlim=(15, 100), ylim=(-.55, len(rows)-.45), xlabel='Exact Match (%)')
    ax.set_xticks([20, 40, 60, 80, 100])
    ax.grid(axis='x')
    ax.spines['left'].set_visible(False)
    ax.legend(loc='lower left', bbox_to_anchor=(-.015, 1.02), ncol=2,
              handletextpad=.4, columnspacing=1.8, fontsize=9)
    gains.set(xlim=(0, 1), ylim=ax.get_ylim())
    gains.axis('off')
    gains.text(.55, 1.06, 'Gain (pp)', transform=gains.transAxes,
               ha='center', color=INK, fontsize=9)
    for yi, b, a in zip(y, before, after):
        gains.text(.55, yi, f'+{a-b:.1f}', ha='center', va='center',
                   color=TEAL, fontsize=12, fontweight='bold')
    save(fig, args, 'R01_rerank_qa', 'RankRAG (2407.02485v1), Table 3, p. 8',
         'Same trained model; reranking removed at inference. Equal token budget is not established by the table.')


if __name__ == '__main__':
    main()
