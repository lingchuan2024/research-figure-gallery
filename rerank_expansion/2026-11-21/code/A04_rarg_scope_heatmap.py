"""A04: RARG relevant-document hits over scope rank bins (arXiv:2607.24223v2, Figure 3 exact values, p. 9)."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import plotlib as pl


def main():
    pl.setup()
    args = pl.options('A04_rarg_scope_heatmap')
    rows = pl.read(args, 'rarg_scope_rank_heatmap.csv')

    methods = [r['method'] for r in rows]
    bin_cols = [c for c in rows[0].keys() if c not in {'method', 'out_of_scope'}]
    main_mat = np.array([[float(r[c]) for c in bin_cols] for r in rows], dtype=float)
    oos_vec = np.array([[float(r['out_of_scope'])] for r in rows], dtype=float)

    # Mask zeros for log scale while showing explicit 0 text
    vmin, vmax = 0.25, 230.0
    norm = LogNorm(vmin=vmin, vmax=vmax)
    cmap = plt.cm.YlGnBu.copy()
    cmap.set_bad(color='#F4F6F8')

    fig = plt.figure(figsize=(14.0, 4.9))
    gs = fig.add_gridspec(1, 3, width_ratios=[20, 1.35, 0.55], wspace=0.06,
                          left=0.10, right=0.94, top=0.77, bottom=0.26)
    ax_main = fig.add_subplot(gs[0, 0])
    ax_oos = fig.add_subplot(gs[0, 1], sharey=ax_main)
    ax_cb = fig.add_subplot(gs[0, 2])

    im = ax_main.imshow(np.ma.masked_less_equal(main_mat, 0), aspect='auto', cmap=cmap, norm=norm)
    ax_oos.imshow(np.ma.masked_less_equal(oos_vec, 0), aspect='auto', cmap=cmap, norm=norm)

    for i in range(main_mat.shape[0]):
        for j in range(main_mat.shape[1]):
            v = main_mat[i, j]
            txt_c = 'white' if v >= 12.0 else pl.INK
            ax_main.text(j, i, f'{v:.1f}', ha='center', va='center', fontsize=6.8, color=txt_c)
        vo = oos_vec[i, 0]
        txt_c = 'white' if vo >= 12.0 else pl.INK
        ax_oos.text(0, i, '0' if vo == 0 else f'{vo:.1f}', ha='center', va='center', fontsize=7.5,
                    color=txt_c, fontweight='bold' if vo > 0 else 'normal')

    ax_main.set_yticks(np.arange(len(methods)))
    ax_main.set_yticklabels(methods, fontsize=9.0, fontweight='bold')
    ax_main.set_xticks(np.arange(len(bin_cols)))
    ax_main.set_xticklabels([c.replace('-', '–') for c in bin_cols], rotation=40, ha='right', fontsize=7.4)
    ax_main.set_xlabel('Document rank bin within 10K retrieval scope')
    ax_main.set_title('In-scope relevant-document hits per query', pad=8, fontsize=10.5)

    ax_oos.set_xticks([0])
    ax_oos.set_xticklabels(['Out of\nscope'], fontsize=8.0)
    plt.setp(ax_oos.get_yticklabels(), visible=False)
    ax_oos.tick_params(axis='y', length=0)
    ax_oos.set_title('OOS', pad=8, fontsize=10.5)

    for ax in (ax_main, ax_oos):
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('#CBD5DC')

    cb = fig.colorbar(im, cax=ax_cb)
    cb.set_label('Hits per query (log scale)', fontsize=8.5)

    pl.heading(
        fig,
        'Where corpus-interaction agents hit relevant documents (RARG)',
        'BrowseComp-Plus (100K) | DCI probes flatly across 223.8 out-of-scope hits; RARG++ recovers lower-ranked in-scope evidence via match reranking',
    )
    pl.save(
        fig,
        args,
        'A04_rarg_scope_heatmap',
        'RARG (Li et al., arXiv:2607.24223v2), Figure 3 exact cell values, p. 9',
        note='Non-scope methods are projected onto RARG scope_1.txt rank bins. Zeros in out-of-scope cells are shown in light gray.',
    )


if __name__ == '__main__':
    main()
