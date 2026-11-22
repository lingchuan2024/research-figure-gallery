"""A01: ITER query-input ablation (arXiv:2608.27912v2, Table 3, p. 15)."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import plotlib as pl

GROUP_COLORS = {
    'baseline': pl.GRAY,
    'history': pl.BLUE,
    'visited_content': pl.RED,
    'reasoning': pl.TEAL,
}


def main():
    pl.setup()
    args = pl.options('A01_iter_query_ablation')
    rows = pl.read(args, 'iter_query_ablation.csv')

    labels = [f"{r['variant']}  ({r['input_components']})" for r in rows]
    y = np.arange(len(rows))[::-1]
    colors = [GROUP_COLORS[r['group']] for r in rows]

    fig, axes = plt.subplots(1, 3, figsize=(13.4, 5.8), sharey=True)
    fig.subplots_adjust(left=0.24, right=0.97, top=0.74, bottom=0.18, wspace=0.18)

    specs = [
        ('infoseek_sr', 'infoseek_sig', 'InfoSeek-Eval SR (%)', (68, 83), 72.0, '{:.1f}'),
        ('bcp_sr', 'bcp_sr_sig', 'BrowseComp-Plus SR (%)', (39, 53), 43.7, '{:.1f}'),
        ('bcp_recall', 'bcp_recall_sig', 'BCP Evidence Search Recall', (0.50, 0.71), 0.596, '{:.3f}'),
    ]

    for ax, (col, sig_col, title, xlim, ref_val, fmt) in zip(axes, specs):
        vals = [float(r[col]) for r in rows]
        ax.axvline(ref_val, color=pl.GRAY, linestyle='--', linewidth=1.1, zorder=1)
        ax.grid(axis='x', linestyle='-', alpha=0.8)
        for yi, val, col_c, r in zip(y, vals, colors, rows):
            ax.plot([ref_val, val], [yi, yi], color=col_c, linewidth=2.4, alpha=0.75, zorder=2)
            ax.scatter([val], [yi], color=col_c, s=56, zorder=3, edgecolors='white', linewidth=0.8)
            sig = r[sig_col]
            txt = fmt.format(val) + (f' ({sig})' if sig else '')
            offset = (xlim[1] - xlim[0]) * 0.025
            ha = 'left' if val >= ref_val else 'right'
            x_txt = val + offset if val >= ref_val else val - offset
            ax.text(x_txt, yi, txt, va='center', ha=ha, fontsize=8.0, color=pl.INK,
                    fontweight='bold' if r['variant'] == 'i7' else 'normal')
        ax.set_xlim(*xlim)
        ax.set_title(title, pad=8)
        ax.set_xlabel('Dashed line = LRAT (0.6B, SQ only)')

    axes[0].set_yticks(y)
    axes[0].set_yticklabels(labels, fontsize=8.5)
    # Group separators between LRAT/history, visited_content, and reasoning
    for ax in axes:
        ax.axhline(7.5, color='#D4DDE2', linewidth=0.9)
        ax.axhline(4.5, color='#D4DDE2', linewidth=0.9)
        ax.axhline(1.5, color='#D4DDE2', linewidth=0.9)

    legend_handles = [
        plt.Line2D([0], [0], marker='o', color=pl.GRAY, lw=2, label='LRAT baseline'),
        plt.Line2D([0], [0], marker='o', color=pl.BLUE, lw=2, label='Structured history (MQ/PSQ)'),
        plt.Line2D([0], [0], marker='o', color=pl.RED, lw=2, label='Visited docs / interpretations (i3-i5)'),
        plt.Line2D([0], [0], marker='o', color=pl.TEAL, lw=2, label='With pre-search reasoning (i6-i7)'),
    ]
    fig.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.58, 0.865), ncol=4, fontsize=8.0, columnspacing=1.1)

    pl.heading(
        fig,
        'Query-input ablation in interaction-aware retrieval (ITER)',
        'Tongyi-DeepResearch-30B with 0.6B dense retriever | Adding visited docs/interpretations (i3-i5) lowers BCP SR and recall vs. MQ+SQ+PSQ',
    )
    pl.save(
        fig,
        args,
        'A01_iter_query_ablation',
        'ITER (Chen et al., arXiv:2608.27912v2), Table 3, p. 15',
        note='(a) p < .05 vs. LRAT; (b) p < .05 vs. default i7 (exact McNemar for SR, paired t-test for recall, Bonferroni-corrected). docs = 64-token snippets; DI = post-visit notes.',
    )


if __name__ == '__main__':
    main()
