"""A05: IndexAct accuracy vs. live context and observation-policy ablation (arXiv:2610.07960v1, Tables 1 & 2, pp. 7-8)."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import plotlib as pl


def main():
    pl.setup()
    args = pl.options('A05_indexact_context_tradeoff')
    main_rows = pl.read(args, 'indexact_bcplus_main.csv')
    abl_rows = pl.read(args, 'indexact_observation_ablation.csv')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.2), gridspec_kw={'width_ratios': [1.35, 1.0]})
    fig.subplots_adjust(left=0.07, right=0.97, top=0.78, bottom=0.19, wspace=0.26)

    # Panel (a): Accuracy vs. Avg Live Context (830 BC+ questions), bubble size = Evidence Coverage
    ax1.grid(True, linestyle='-', alpha=0.85)
    cat_colors = {'standard': pl.GRAY, 'interface': pl.BLUE, 'proposed': pl.TEAL}
    label_offsets = {
        'Retrieval Agent (BM25)': (-95, 6),
        'Retrieval Agent (Dense)': (-94, -16),
        'PI-SERINI': (9, -6),
        'SIEVE': (9, -4),
        'DCI-Agent-Lite': (-96, -15),
        'DR-DCI': (-36, -24),
        'RARG': (-34, 9),
        'IndexAct': (10, 4),
    }

    for r in main_rows:
        x = float(r['bc_avg_ctx']) / 1000.0
        y = float(r['bc_acc'])
        cov = float(r['bc_evi_cov'])
        c = cat_colors[r['category']]
        size = (cov - 25.0) * 6.5
        ax1.scatter([x], [y], s=size, color=c, alpha=0.85, edgecolors='white', linewidth=1.1, zorder=4)
        dx, dy = label_offsets.get(r['method'], (8, 4))
        ax1.annotate(
            f"{r['method']}\n({y:.1f}%, cov {cov:.1f}%)",
            (x, y),
            xytext=(dx, dy),
            textcoords='offset points',
            fontsize=7.6,
            color=pl.TEAL if r['category'] == 'proposed' else pl.INK,
            fontweight='bold' if r['category'] == 'proposed' else 'normal',
        )

    ax1.set_xlim(8, 35)
    ax1.set_ylim(25, 80)
    ax1.set_xlabel('Average live context (K tokens, lower is smaller)')
    ax1.set_ylabel('BrowseComp-Plus accuracy (%, n = 830)')
    ax1.set_title('(a) Corpus interfaces: accuracy vs. live context (Table 1)', pad=8)

    # Panel (b): Observation-policy ablation (100q subset, Table 2)
    methods = [r['method'] for r in abl_rows]
    x_pos = np.arange(len(methods))
    w = 0.25
    acc = [float(r['acc']) for r in abl_rows]
    cov = [float(r['evi_cov']) for r in abl_rows]
    src = [float(r['src_tok_k']) for r in abl_rows]

    b1 = ax2.bar(x_pos - w, acc, width=w, color=pl.TEAL, label='Accuracy (%)')
    b2 = ax2.bar(x_pos, cov, width=w, color=pl.BLUE, label='Evidence Coverage (%)')
    b3 = ax2.bar(x_pos + w, src, width=w, color=pl.ORANGE, label='Cumulative Source Tokens (K)')

    for bars, fmt in ((b1, '{:.1f}'), (b2, '{:.1f}'), (b3, '{:.1f}K')):
        for bar in bars:
            h = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2, h + 1.2, fmt.format(h),
                     ha='center', va='bottom', fontsize=7.6, color=pl.INK)

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(methods, fontsize=8.8, fontweight='bold')
    ax2.set_ylim(0, 96)
    ax2.set_ylabel('Percentage (%) or K source tokens')
    ax2.set_title('(b) Observation-policy ablation (Table 2, n = 100)', pad=8)
    ax2.grid(axis='y', alpha=0.85)
    ax2.legend(loc='upper left', ncol=2, fontsize=7.6)

    pl.heading(
        fig,
        'Selective reading & state feedback vs. context size (IndexAct)',
        'GPT-5.4-nano (high effort) on BrowseComp-Plus | Separating candidate-set refinement from text exposure raises accuracy & coverage with less context',
    )
    pl.save(
        fig,
        args,
        'A05_indexact_context_tradeoff',
        'IndexAct (Kim et al., arXiv:2610.07960v1), Table 1 (p. 7) & Table 2 (p. 8)',
        note='Panel (a) uses all 830 BC+ queries (bubble area scales with Evidence Coverage); Panel (b) uses the fixed 100-query ablation subset. SrcTok is cumulative tool-returned text.',
    )


if __name__ == '__main__':
    main()
