"""A02: ITER cross-agent transfer vs. LRAT (0.6B) and AgentIR (4B) (arXiv:2608.27912v2, Table 2, p. 14)."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
import plotlib as pl


def main():
    pl.setup()
    args = pl.options('A02_iter_cross_agent')
    rows = pl.read(args, 'iter_cross_agent.csv')

    backbones = list(dict.fromkeys(r['backbone'] for r in rows))
    r06 = {r['backbone']: r for r in rows if r['scale'] == '0.6B'}
    r4b = {r['backbone']: r for r in rows if r['scale'] == '4B'}

    y = np.arange(len(backbones))[::-1]
    off = 0.16

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.4), sharey=True)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.78, bottom=0.18, wspace=0.16)

    for yi, bb in zip(y, backbones):
        # 0.6B pair (top track)
        a, b = float(r06[bb]['baseline_bcp_sr']), float(r06[bb]['iter_bcp_sr'])
        ax1.plot([a, b], [yi + off, yi + off], color=pl.BLUE, lw=2.2, alpha=0.8)
        ax1.scatter([a], [yi + off], color=pl.GRAY, s=46, zorder=3, label='LRAT (0.6B)' if yi == y[0] else None)
        ax1.scatter([b], [yi + off], color=pl.BLUE, s=52, zorder=4, label='ITER (0.6B)' if yi == y[0] else None)
        sig = '*' if r06[bb]['bcp_sr_sig'] == '*' else ''
        ax1.text(max(a, b) + 0.8, yi + off, f'{b:.1f}{sig}', va='center', ha='left', fontsize=7.8, color=pl.BLUE)

        # 4B pair (bottom track)
        c, d = float(r4b[bb]['baseline_bcp_sr']), float(r4b[bb]['iter_bcp_sr'])
        ax1.plot([c, d], [yi - off, yi - off], color=pl.TEAL, lw=2.2, alpha=0.8)
        ax1.scatter([c], [yi - off], color=pl.ORANGE, marker='s', s=42, zorder=3, label='AgentIR (4B)' if yi == y[0] else None)
        ax1.scatter([d], [yi - off], color=pl.TEAL, marker='s', s=46, zorder=4, label='ITER (4B)' if yi == y[0] else None)
        ax1.text(max(c, d) + 0.8, yi - off, f'{d:.1f}', va='center', ha='left', fontsize=7.8, color=pl.TEAL)

        # Right panel: Visit-to-Search recall ratio (%) at 4B and 0.6B
        va, vb = float(r06[bb]['baseline_vs_ratio']), float(r06[bb]['iter_vs_ratio'])
        ax2.plot([va, vb], [yi + off, yi + off], color=pl.BLUE, lw=2.2, alpha=0.8)
        ax2.scatter([va], [yi + off], color=pl.GRAY, s=46, zorder=3)
        ax2.scatter([vb], [yi + off], color=pl.BLUE, s=52, zorder=4)
        ax2.text(max(va, vb) + 0.7, yi + off, f'{vb:.1f}%', va='center', ha='left', fontsize=7.8, color=pl.BLUE)

        vc, vd = float(r4b[bb]['baseline_vs_ratio']), float(r4b[bb]['iter_vs_ratio'])
        ax2.plot([vc, vd], [yi - off, yi - off], color=pl.TEAL, lw=2.2, alpha=0.8)
        ax2.scatter([vc], [yi - off], color=pl.ORANGE, marker='s', s=42, zorder=3)
        ax2.scatter([vd], [yi - off], color=pl.TEAL, marker='s', s=46, zorder=4)
        ax2.text(max(vc, vd) + 0.7, yi - off, f'{vd:.1f}%', va='center', ha='left', fontsize=7.8, color=pl.TEAL)

    ax1.set_yticks(y)
    ax1.set_yticklabels(backbones, fontsize=9.0, fontweight='bold')
    ax1.set_xlim(22, 59)
    ax1.set_xlabel('BrowseComp-Plus task success rate (%)')
    ax1.set_title('(a) End-to-end task success (BCP)', pad=8)
    ax1.grid(axis='x')

    ax2.set_xlim(47, 81)
    ax2.set_xlabel('Visit-to-Search recall ratio V/S (%)')
    ax2.set_title('(b) Retrieved-to-visited evidence conversion (BCP)', pad=8)
    ax2.grid(axis='x')

    for ax in (ax1, ax2):
        for sep in np.arange(0.5, len(backbones) - 0.5, 1.0):
            ax.axhline(sep, color='#EEF3F5', lw=1.0)

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(0.97, 0.89), ncol=4, fontsize=8.5)

    pl.heading(
        fig,
        'Cross-agent transfer of interaction-aware retrieval (ITER)',
        'Six agent backbones (4B-120B) on BrowseComp-Plus | 0.6B ITER beats LRAT on all 6; 4B ITER raises V/S ratio over AgentIR on all 6',
    )
    pl.save(
        fig,
        args,
        'A02_iter_cross_agent',
        'ITER (Chen et al., arXiv:2608.27912v2), Table 2, p. 14',
        note='* indicates two-sided exact McNemar p < .05 vs. scale-matched baseline (0.6B vs. LRAT, 4B vs. AgentIR). Top track = 0.6B; bottom track = 4B.',
    )


if __name__ == '__main__':
    main()
