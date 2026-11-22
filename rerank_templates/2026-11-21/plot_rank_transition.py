"""F07: Rank transition heatmap (before vs. after reranking) from rank_transitions.csv."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
import common


def bin_index(rank, bins):
    if rank is None:
        return None
    for idx, (_, lo, hi) in enumerate(bins):
        if lo <= rank <= hi:
            return idx
    return None


def main(argv=None):
    common.setup()
    parser = common.base_parser('rank_transition', 'rank_transitions.csv')
    parser.add_argument('--method', default=None, help='Method ID to visualize (default: first method present in CSV).')
    parser.add_argument('--relevant-only', action='store_true', default=True, help='Restrict to is_relevant=1 rows (default: True).')
    args = common.finalize_args(parser, 'rank_transitions.csv', argv)

    config = common.load_config(args.config)
    rows = common.validate_rank_transitions(common.read_csv_rows(args.data), config)
    if args.relevant_only:
        rows = [r for r in rows if r['is_relevant']]
    if not rows:
        raise ValueError('No rows remain after filtering.')

    methods_in_csv = sorted({r['method'] for r in rows})
    target_method = args.method or methods_in_csv[0]
    sub = [r for r in rows if r['method'] == target_method]
    if not sub:
        raise ValueError(f'No rank transition rows for method={target_method}.')

    bins = common.DEFAULT_RANK_BINS
    k = len(bins)
    counts = np.zeros((k, k), dtype=int)
    outside_before = 0
    outside_after = 0
    in_pool = 0

    for r in sub:
        bi = bin_index(r['rank_before'], bins)
        ai = bin_index(r['rank_after'], bins)
        if bi is None:
            outside_before += 1
        elif ai is None:
            outside_after += 1
        else:
            counts[bi, ai] += 1
            in_pool += 1

    probs = common.normalize_rows(counts)
    bin_labels = [b[0] for b in bins]
    summary_rows = []
    for i, bl in enumerate(bin_labels):
        for j, al in enumerate(bin_labels):
            p = probs[i, j]
            summary_rows.append({
                'method': target_method, 'rank_before_bin': bl, 'rank_after_bin': al,
                'count': int(counts[i, j]),
                'row_share': '' if np.isnan(p) else round(float(p), 4),
            })

    fig, ax = plt.subplots(figsize=(7.6, 5.8))
    fig.subplots_adjust(left=0.16, right=0.86, top=0.80, bottom=0.19)

    cmap = plt.cm.Blues.copy()
    cmap.set_bad(color='#F2F4F6')
    im = ax.imshow(np.ma.masked_invalid(probs), cmap=cmap, vmin=0.0, vmax=1.0, aspect='equal')

    for i in range(k):
        for j in range(k):
            p = probs[i, j]
            c = counts[i, j]
            if np.isnan(p):
                ax.text(j, i, 'n/a', ha='center', va='center', fontsize=8.0, color=common.MUTED)
            else:
                txt_c = 'white' if p >= 0.55 else common.INK
                ax.text(j, i, f'{c}\n{p * 100:.0f}%', ha='center', va='center', fontsize=8.3, color=txt_c,
                        fontweight='bold' if i == j or (j < i and p >= 0.25) else 'normal')

    ax.set_xticks(np.arange(k))
    ax.set_xticklabels(bin_labels, fontsize=9.0)
    ax.set_yticks(np.arange(k))
    ax.set_yticklabels(bin_labels, fontsize=9.0)
    ax.set_xlabel('Rank after reranking (lower is better)')
    ax.set_ylabel('Rank before reranking')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#CBD5DC')

    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label('Row-normalized transition share', fontsize=8.8)

    label_map = {m['id']: m['label'] for m in config['methods']}
    fig.text(0.16, 0.935, f"Known-evidence rank transitions ({label_map.get(target_method, target_method)})",
             fontsize=13.0, fontweight='bold', color=common.INK)
    fig.text(0.16, 0.88,
             f'{in_pool} in-pool transitions | Reported separately: {outside_before} outside before, {outside_after} outside after',
             fontsize=8.6, color=common.MUTED)
    note = 'Each row sums to 100% over observed in-pool transitions; unobserved source rows stay n/a (not 0%). Cells left of diagonal indicate rank promotion.'
    common.save_outputs(
        fig, args, 'rank_transition', config, note, summary_rows,
        extra_provenance={'method': target_method, 'in_pool': in_pool, 'outside_before': outside_before, 'outside_after': outside_after},
    )


if __name__ == '__main__':
    main()
