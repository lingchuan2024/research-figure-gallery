"""F02: Per-question paired comparison (bounded dumbbell+delta or binary flip+subset delta)."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
import common


def main(argv=None):
    common.setup()
    parser = common.base_parser('paired', 'observations.csv')
    parser.add_argument('--method', default=None, help='Candidate method ID (default: last configured non-baseline method).')
    parser.add_argument('--baseline', default=None, help='Reference method ID (default: config.baseline).')
    parser.add_argument('--max-rows', type=int, default=30, help='Max individual questions displayed for bounded scores.')
    args = common.finalize_args(parser, 'observations.csv', argv)

    config = common.load_config(args.config)
    rows = common.validate_observations(common.read_csv_rows(args.data), config)
    baseline_id = args.baseline or config['baseline']
    method_map = {m['id']: m for m in config['methods']}
    if baseline_id not in method_map:
        raise ValueError(f'Unknown --baseline {baseline_id}.')
    if args.method:
        cand_id = args.method
    else:
        non_base = [m['id'] for m in config['methods'] if m['id'] != baseline_id]
        cand_id = non_base[-1]
    if cand_id not in method_map or cand_id == baseline_id:
        raise ValueError('Candidate --method must be a configured method distinct from --baseline.')

    base_meta, cand_meta = method_map[baseline_id], method_map[cand_id]
    scale = float(config['score']['scale'])
    d_unit = config['score']['delta_unit']
    is_binary = config['score']['kind'] == 'binary'

    # Pair within each benchmark (use first benchmark if multiple, and audit all in summary)
    benchmarks = sorted({r['benchmark'] for r in rows})
    bm = benchmarks[0]
    bm_rows = [r for r in rows if r['benchmark'] == bm]
    left = {r['question_id']: r for r in bm_rows if r['method'] == baseline_id}
    right = {r['question_id']: r for r in bm_rows if r['method'] == cand_id}
    qids = sorted(left.keys())
    a_vals = np.array([left[q]['score'] for q in qids], dtype=float)
    b_vals = np.array([right[q]['score'] for q in qids], dtype=float)
    deltas = b_vals - a_vals
    mean_delta = float(deltas.mean())
    ci_lo, ci_hi = common.bootstrap_ci(deltas, draws=args.bootstrap, seed=args.seed)

    summary_rows = [{
        'benchmark': bm, 'baseline': baseline_id, 'candidate': cand_id,
        'n_paired': len(qids),
        'baseline_mean': round(float(a_vals.mean()) * scale, 4),
        'candidate_mean': round(float(b_vals.mean()) * scale, 4),
        'paired_mean_delta': round(mean_delta * scale, 4),
        'delta_ci_low': round(ci_lo * scale, 4),
        'delta_ci_high': round(ci_hi * scale, 4),
        'improved_count': int(np.sum(deltas > 1e-12)),
        'tied_count': int(np.sum(np.abs(deltas) <= 1e-12)),
        'regressed_count': int(np.sum(deltas < -1e-12)),
    }]

    if is_binary:
        # Left panel: 2x2 paired outcome counts; Right panel: per-subset paired delta with bootstrap CI
        both_ok = int(np.sum((a_vals == 1) & (b_vals == 1)))
        gained = int(np.sum((a_vals == 0) & (b_vals == 1)))
        lost = int(np.sum((a_vals == 1) & (b_vals == 0)))
        both_no = int(np.sum((a_vals == 0) & (b_vals == 0)))

        subsets = sorted({left[q]['subset'] for q in qids})
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.6), gridspec_kw={'width_ratios': [1.05, 1.25]})
        fig.subplots_adjust(left=0.08, right=0.96, top=0.77, bottom=0.20, wspace=0.30)

        cats = ['Both correct', f'Gained\n({cand_meta["label"]} only)', f'Lost\n({base_meta["label"]} only)', 'Both wrong']
        cnts = [both_ok, gained, lost, both_no]
        cols = ['#6E8494', cand_meta['color'], '#B75A53', '#C9D3D9']
        bars = ax1.bar(np.arange(4), cnts, color=cols, width=0.62)
        for bar, cnt in zip(bars, cnts):
            ax1.text(bar.get_x() + bar.get_width() / 2, cnt + max(cnts) * 0.025,
                     f'{cnt}\n({cnt / len(qids) * 100:.1f}%)', ha='center', va='bottom', fontsize=8.0, color=common.INK)
        ax1.set_xticks(np.arange(4))
        ax1.set_xticklabels(cats, fontsize=8.0)
        ax1.set_ylim(0, max(cnts) * 1.25 + 2)
        ax1.set_ylabel('Paired questions (count)')
        ax1.set_title(f'(a) Paired outcome flips (n = {len(qids)})', pad=8)
        ax1.grid(axis='y')

        groups = ['All'] + subsets
        y_pos = np.arange(len(groups))[::-1]
        ax2.axvline(0.0, color='#8B9AA4', ls='--', lw=1.0)
        ax2.grid(axis='x')
        for yi, grp in zip(y_pos, groups):
            if grp == 'All':
                d_sub = deltas
            else:
                idx = [i for i, q in enumerate(qids) if left[q]['subset'] == grp]
                d_sub = deltas[idx]
            md = float(d_sub.mean()) * scale
            lo, hi = common.bootstrap_ci(d_sub, draws=args.bootstrap, seed=args.seed)
            lo, hi = lo * scale, hi * scale
            col = cand_meta['color'] if md >= 0 else '#B75A53'
            ax2.errorbar([md], [yi], xerr=[[md - lo], [hi - md]], fmt='o', color=col,
                         ecolor=col, elinewidth=2.0, capsize=3.5, markersize=6.5, zorder=4)
            ax2.text(hi + 1.2, yi, f'{md:+.1f} [{lo:+.1f}, {hi:+.1f}] (n={len(d_sub)})',
                     va='center', ha='left', fontsize=8.0, color=common.INK)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(groups, fontsize=8.8, fontweight='bold')
        ax2.set_xlim(-22, 42)
        ax2.set_xlabel(f'Paired delta: {cand_meta["label"]} - {base_meta["label"]} ({d_unit})')
        ax2.set_title('(b) Paired mean delta with 95% bootstrap CI', pad=8)

        fig.text(0.08, 0.93, f'Paired comparison: {cand_meta["label"]} vs. {base_meta["label"]} ({bm})',
                 fontsize=13.2, fontweight='bold', color=common.INK)
        fig.text(0.08, 0.875,
                 f'Overall paired delta = {mean_delta * scale:+.2f} {d_unit} (95% bootstrap CI [{ci_lo * scale:+.2f}, {ci_hi * scale:+.2f}]) | Gained {gained}, Lost {lost}',
                 fontsize=8.8, color=common.MUTED)
        note = f'Strictly paired question IDs (n={len(qids)}). Bootstrap resamples paired questions ({args.bootstrap} draws); subset intervals are not multiplicity-adjusted.'
    else:
        # Bounded continuous scores: dumbbell + sorted delta bars (show up to max_rows evenly sampled across sorted deltas if n > max_rows)
        order = np.argsort(deltas)
        if len(order) > args.max_rows:
            pick = np.linspace(0, len(order) - 1, args.max_rows, dtype=int)
            shown = order[pick]
            trunc_msg = f'Displaying {len(shown)} rank-spaced questions of {len(qids)}; CI uses all {len(qids)} paired questions.'
        else:
            shown = order
            trunc_msg = f'All {len(qids)} paired questions displayed.'

        y = np.arange(len(shown))
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, max(4.8, 0.23 * len(shown) + 1.8)),
                                       sharey=True, gridspec_kw={'width_ratios': [1.35, 1.0]})
        fig.subplots_adjust(left=0.10, right=0.96, top=0.80, bottom=0.15, wspace=0.12)

        for yi, idx in zip(y, shown):
            a, b = a_vals[idx] * scale, b_vals[idx] * scale
            d = deltas[idx] * scale
            c = cand_meta['color'] if d >= 0 else '#B75A53'
            ax1.plot([a, b], [yi, yi], color=c, lw=1.3, alpha=0.65)
            ax1.scatter([a], [yi], color=base_meta['color'], s=24, zorder=3, label=base_meta['label'] if yi == 0 else None)
            ax1.scatter([b], [yi], color=cand_meta['color'], s=28, zorder=4, label=cand_meta['label'] if yi == 0 else None)
            ax2.barh(yi, d, color=c, height=0.68, alpha=0.85)

        ax1.set_yticks(y)
        ax1.set_yticklabels([qids[i] for i in shown], fontsize=7.2)
        ax1.set_xlabel(f"{config['score']['label']} ({config['score']['unit']})")
        ax1.set_title('(a) Per-question paired scores', pad=8)
        ax1.grid(axis='x')
        ax1.legend(loc='lower right', fontsize=8.3)

        ax2.axvline(0.0, color='#7E8E98', lw=1.0)
        ax2.set_xlabel(f'Delta: {cand_meta["label"]} - {base_meta["label"]} ({d_unit})')
        ax2.set_title('(b) Sorted paired differences', pad=8)
        ax2.grid(axis='x')

        fig.text(0.10, 0.94, f'Paired per-question comparison: {cand_meta["label"]} vs. {base_meta["label"]} ({bm})',
                 fontsize=13.0, fontweight='bold', color=common.INK)
        fig.text(0.10, 0.885,
                 f'Mean delta = {mean_delta * scale:+.3f} {d_unit} (95% bootstrap CI [{ci_lo * scale:+.3f}, {ci_hi * scale:+.3f}]) | {trunc_msg}',
                 fontsize=8.6, color=common.MUTED)
        note = f'{trunc_msg} Bootstrap resamples paired questions ({args.bootstrap} draws).'

    common.save_outputs(
        fig, args, 'paired', config, note, summary_rows,
        extra_provenance={'baseline_id': baseline_id, 'candidate_id': cand_id},
    )


if __name__ == '__main__':
    main()
