"""A06: RISE corpus scaling (100K->1M) and BM25 top-K workspace ablation (arXiv:2606.06880v1, Tables 2 & 3, pp. 7-8)."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import plotlib as pl

ARCH_COLORS = {
    'RISE-BM25': pl.TEAL,
    'retrieval-agent': pl.BLUE,
    'DCI': pl.RED,
}
MODEL_COLORS = {
    'mimo-v2.5-pro': pl.TEAL,
    'gpt-5.4-mini': pl.BLUE,
    'gpt-5.4-nano': pl.ORANGE,
}


def main():
    pl.setup()
    args = pl.options('A06_rise_scaling_and_topk')
    scale_rows = pl.read(args, 'rise_scaling_100k_1m.csv')
    topk_rows = pl.read(args, 'rise_topk_ablation.csv')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.2))
    fig.subplots_adjust(left=0.14, right=0.97, top=0.78, bottom=0.19, wspace=0.25)

    # Panel (a): 100K -> 1M shift per (model, architecture)
    y = np.arange(len(scale_rows))[::-1]
    labels = [f"{r['model']} | {r['architecture']}" for r in scale_rows]
    ax1.grid(axis='x', alpha=0.85)
    for yi, r in zip(y, scale_rows):
        a, b = float(r['acc_100k']), float(r['acc_1m'])
        c = ARCH_COLORS[r['architecture']]
        ax1.annotate('', xy=(b, yi), xytext=(a, yi),
                     arrowprops=dict(arrowstyle='->', color=c, lw=2.2, shrinkA=4, shrinkB=4))
        ax1.scatter([a], [yi], color='white', edgecolors=c, s=50, linewidth=1.6, zorder=4)
        ax1.scatter([b], [yi], color=c, s=55, zorder=5)
        delta = b - a
        sign = '+' if delta >= 0 else ''
        ax1.text(max(a, b) + 0.9, yi, f'{int(a)}->{int(b)}% ({sign}{int(delta)})',
                 va='center', ha='left', fontsize=8.0, color=c, fontweight='bold')

    ax1.set_yticks(y)
    ax1.set_yticklabels(labels, fontsize=8.3)
    ax1.set_xlim(55, 96)
    ax1.set_xlabel('BrowseComp-Plus accuracy (%, n = 100)')
    ax1.set_title('(a) 10x corpus expansion: 100K -> 1M docs (Table 2)', pad=8)
    ax1.legend(
        handles=[
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='white', markeredgecolor=pl.INK, lw=0, label='100K corpus'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=pl.INK, lw=0, label='1M corpus (+900K distractors)'),
        ],
        loc='lower right',
        bbox_to_anchor=(1.0, 0.14),
        fontsize=7.8,
    )

    # Panel (b): Top-K ablation (Accuracy vs. mean workspace size in files, log x-axis)
    ax2.grid(True, linestyle='-', alpha=0.85)
    for model in ('mimo-v2.5-pro', 'gpt-5.4-mini', 'gpt-5.4-nano'):
        sub = sorted([r for r in topk_rows if r['model'] == model], key=lambda r: int(r['top_k']))
        xs = [float(r['ws_size']) for r in sub]
        ys = [float(r['acc']) for r in sub]
        c = MODEL_COLORS[model]
        ax2.plot(xs, ys, marker='o', color=c, lw=2.2, markersize=6.5, label=model)
        for r, x, yv in zip(sub, xs, ys):
            k_lbl = f"K={r['top_k']}"
            dy = 7 if not (model == 'gpt-5.4-mini' and r['top_k'] == '100') else -13
            ax2.annotate(f"{k_lbl} ({int(yv)}%)", (x, yv), xytext=(0, dy),
                         textcoords='offset points', ha='center', fontsize=7.6, color=c)

    ax2.set_xscale('log')
    ax2.set_xlim(650, 80000)
    ax2.set_ylim(60, 81)
    ax2.set_xlabel('Mean accumulated workspace size (unique files, log scale)')
    ax2.set_ylabel('RISE-BM25 accuracy on 100K corpus (%)')
    ax2.set_title('(b) Per-sub-query BM25 top-K ablation (Table 3)', pad=8)
    ax2.legend(loc='lower right', fontsize=8.2)

    pl.heading(
        fig,
        'Bounded interaction spaces under 10x scaling & top-K ablation (RISE)',
        '100-query BrowseComp-Plus | RISE-BM25 remains stable at 1M docs while DCI degrades (-11 pp, 33/100 timeouts); K=1000 balances recall & workspace size',
    )
    pl.save(
        fig,
        args,
        'A06_rise_scaling_and_topk',
        'RISE (Zhuang et al., arXiv:2606.06880v1), Table 2 (p. 7) & Table 3 (p. 8)',
        note='At 1M, all RISE rows are RISE-BM25 (boundary-only, no TOC on 900K distractors); DCI is evaluated at 1M only on gpt-5.4-nano.',
    )


if __name__ == '__main__':
    main()
