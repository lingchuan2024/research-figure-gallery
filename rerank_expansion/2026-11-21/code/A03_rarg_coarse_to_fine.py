"""A03: RARG coarse-to-fine relevance guidance frontier (arXiv:2607.24223v2, Table 1, p. 7)."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import plotlib as pl

FAM_STYLE = {
    'retrieval': (pl.GRAY, 'o', 'Retrieval-only / NeMo'),
    'dci': (pl.RED, 'D', 'DCI (unbounded grep)'),
    'rise': (pl.BLUE, 's', 'RISE family'),
    'rarg': (pl.TEAL, '*', 'RARG -> RARG+ -> RARG++'),
    'rarg_gen': (pl.ORANGE, '^', 'RARG++ (generative query)'),
}


def main():
    pl.setup()
    args = pl.options('A03_rarg_coarse_to_fine')
    rows = pl.read(args, 'rarg_main_bcplus.csv')

    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.6), sharey=False)
    fig.subplots_adjust(left=0.07, right=0.97, top=0.73, bottom=0.19, wspace=0.22)

    panels = [
        ('GPT-5.4-mini', '(a) GPT-5.4-mini (medium effort)', (10, 108), (50, 88)),
        ('GPT-5.4-nano', '(b) GPT-5.4-nano (high effort)', (20, 138), (45, 84)),
    ]

    offsets = {
        ('GPT-5.4-mini', 'RISE'): (6, 2),
        ('GPT-5.4-mini', 'RISE-BM25'): (6, -9),
        ('GPT-5.4-mini', 'RISE-Q3-Emb-4B'): (-6, -13),
        ('GPT-5.4-mini', 'Retrieval-Agent'): (6, 4),
        ('GPT-5.4-mini', 'Embedding Agent'): (-6, 8),
        ('GPT-5.4-mini', 'NeMo Agent'): (6, -4),
        ('GPT-5.4-mini', 'DCI'): (-22, 8),
        ('GPT-5.4-mini', 'RARG'): (7, -6),
        ('GPT-5.4-mini', 'RARG+'): (7, 5),
        ('GPT-5.4-mini', 'RARG++'): (7, 3),
        ('GPT-5.4-mini', 'RARG++ (gen.)'): (-2, -13),
        ('GPT-5.4-nano', 'RISE'): (6, 2),
        ('GPT-5.4-nano', 'RISE-BM25'): (6, -8),
        ('GPT-5.4-nano', 'Embedding Agent'): (-6, 8),
        ('GPT-5.4-nano', 'NeMo Agent'): (6, -5),
        ('GPT-5.4-nano', 'DCI'): (-26, 8),
        ('GPT-5.4-nano', 'RARG'): (7, -8),
        ('GPT-5.4-nano', 'RARG+'): (7, 5),
        ('GPT-5.4-nano', 'RARG++'): (7, 3),
    }

    seen_legend = set()
    legend_handles = []

    for ax, (model, title, xlim, ylim) in zip(axes, panels):
        sub = [r for r in rows if r['model'] == model]
        ax.grid(True, linestyle='-', alpha=0.85)
        rarg_pts = []
        for r in sub:
            fam = r['family']
            color, marker, leg_label = FAM_STYLE[fam]
            x, y = float(r['tools']), float(r['acc'])
            size = 140 if marker == '*' else 62
            h = ax.scatter([x], [y], color=color, marker=marker, s=size, zorder=4, edgecolors='white', linewidth=0.7)
            if fam not in seen_legend:
                seen_legend.add(fam)
                legend_handles.append(plt.Line2D([0], [0], marker=marker, color='w', markerfacecolor=color,
                                                 markersize=9 if marker == '*' else 7, label=leg_label))
            dx, dy = offsets.get((model, r['method']), (6, 4))
            ax.annotate(
                f"{r['method']} ({int(y)}%)",
                (x, y),
                xytext=(dx, dy),
                textcoords='offset points',
                fontsize=7.8,
                color=pl.INK if fam != 'rarg' else pl.TEAL,
                fontweight='bold' if r['method'] == 'RARG++' else 'normal',
            )
            if r['method'] in {'RARG', 'RARG+', 'RARG++'}:
                rarg_pts.append((r['method'], x, y))

        order = {'RARG': 0, 'RARG+': 1, 'RARG++': 2}
        rarg_pts.sort(key=lambda t: order[t[0]])
        for i in range(len(rarg_pts) - 1):
            _, x1, y1 = rarg_pts[i]
            _, x2, y2 = rarg_pts[i + 1]
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle='->', color=pl.TEAL, lw=1.6, alpha=0.75, shrinkA=5, shrinkB=6))

        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_xlabel('Mean tool calls per query (lower is fewer)')
        ax.set_ylabel('BrowseComp-Plus accuracy (%)')
        ax.set_title(title, pad=8)

    fig.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.52, 0.865), ncol=5, fontsize=8.0, columnspacing=1.0)

    pl.heading(
        fig,
        'Coarse-to-fine relevance guidance vs. tool calls (RARG)',
        '100-query BrowseComp-Plus (100K corpus) | Constructed-query match reranking (RARG++) improves accuracy & cuts tools; generative rerank query drops to 75%',
    )
    pl.save(
        fig,
        args,
        'A03_rarg_coarse_to_fine',
        'RARG (Li et al., arXiv:2607.24223v2), Table 1, p. 7',
        note='RISE/DCI/Retrieval-Agent rows are cited from RISE in RARG Table 1. Tool counts reflect interface actions, not equal wall-clock cost or billing.',
    )


if __name__ == '__main__':
    main()
