"""F01: Publication-ready main results table from paired observations.csv."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
import common


def fmt_tokens(val):
    if val is None:
        return '—'
    return f'{val / 1000:.1f}k' if val >= 1000 else f'{val:.0f}'


def main(argv=None):
    common.setup()
    parser = common.base_parser('results_table', 'observations.csv')
    args = common.finalize_args(parser, 'observations.csv', argv)

    config = common.load_config(args.config)
    rows = common.validate_observations(common.read_csv_rows(args.data), config)
    scale = float(config['score']['scale'])
    unit = config['score']['unit']
    is_binary = config['score']['kind'] == 'binary'

    benchmarks = sorted({r['benchmark'] for r in rows})
    summary_rows = []
    table_blocks = []

    for bm in benchmarks:
        bm_rows = [r for r in rows if r['benchmark'] == bm]
        block = []
        for m in config['methods']:
            sub = [r for r in bm_rows if r['method'] == m['id']]
            scores = np.array([r['score'] for r in sub], dtype=float)
            n = len(sub)
            n_comp = sum(1 for r in sub if r['status'] == 'complete')
            mean_s = float(scores.mean())
            if is_binary:
                lo, hi = common.wilson_interval(int(round(scores.sum())), n)
                ci_kind = 'Wilson 95% CI'
            else:
                lo, hi = common.bootstrap_ci(scores, draws=args.bootstrap, seed=args.seed)
                ci_kind = 'Bootstrap 95% CI'

            toks = [r['main_input_tokens'] for r in sub if r['main_input_tokens'] is not None]
            rev = [r['rerank_events'] for r in sub if r['rerank_events'] is not None]
            wall = [r['wall_seconds'] for r in sub if r['wall_seconds'] is not None]

            mean_tok = float(np.mean(toks)) if len(toks) == n else None
            mean_rev = float(np.mean(rev)) if len(rev) == n else None
            med_wall = float(np.median(wall)) if len(wall) == n else None
            q25_wall, q75_wall = (float(np.percentile(wall, 25)), float(np.percentile(wall, 75))) if len(wall) == n else (None, None)

            summary_rows.append({
                'benchmark': bm, 'method_id': m['id'], 'method_label': m['label'],
                'n': n, 'n_complete': n_comp,
                'score_mean': round(mean_s * scale, 4),
                'score_ci_low': round(lo * scale, 4),
                'score_ci_high': round(hi * scale, 4),
                'ci_method': ci_kind,
                'mean_main_input_tokens': '' if mean_tok is None else round(mean_tok, 1),
                'mean_rerank_events': '' if mean_rev is None else round(mean_rev, 2),
                'median_wall_seconds': '' if med_wall is None else round(med_wall, 2),
                'iqr_wall_low': '' if q25_wall is None else round(q25_wall, 2),
                'iqr_wall_high': '' if q75_wall is None else round(q75_wall, 2),
            })
            block.append((m, mean_s * scale, lo * scale, hi * scale, mean_tok, mean_rev, med_wall, q25_wall, q75_wall, n_comp, n))
        table_blocks.append((bm, block))

    total_rows = sum(len(b) for _, b in table_blocks) + len(table_blocks)
    fig_h = max(3.0, 1.55 + 0.44 * total_rows)
    fig, ax = plt.subplots(figsize=(10.6, fig_h))
    ax.axis('off')
    fig.subplots_adjust(left=0.03, right=0.97, top=0.82, bottom=0.17)

    cols = [
        ('Method', 0.01, 'left'),
        (f"{config['score']['label']} [95% CI]", 0.20, 'left'),
        ('Main input tok/q', 0.56, 'right'),
        ('Rerank events/q', 0.70, 'right'),
        ('Wall time med [IQR]', 0.87, 'right'),
        ('Complete', 0.99, 'right'),
    ]

    y = 1.0
    step = 1.0 / (total_rows + 1.8)
    ax.plot([0.0, 1.0], [y, y], color=common.INK, lw=1.4, transform=ax.transAxes, clip_on=False)
    y -= step * 0.62
    for label, x, ha in cols:
        ax.text(x, y, label, transform=ax.transAxes, ha=ha, va='center', fontsize=8.8, fontweight='bold', color=common.INK)
    y -= step * 0.48
    ax.plot([0.0, 1.0], [y, y], color='#7E8E98', lw=0.9, transform=ax.transAxes, clip_on=False)

    for bm, block in table_blocks:
        best_score = max(item[1] for item in block)
        if len(table_blocks) > 1:
            y -= step * 0.72
            ax.text(0.01, y, bm, transform=ax.transAxes, ha='left', va='center',
                    fontsize=8.6, fontweight='bold', color=common.MUTED)
        for m, ms, lo, hi, mtok, mrev, mwall, q25, q75, nc, n in block:
            y -= step * 0.92
            is_best = abs(ms - best_score) < 1e-9
            if is_best:
                ax.add_patch(plt.Rectangle((0.0, y - step * 0.42), 1.0, step * 0.84,
                                           transform=ax.transAxes, facecolor='#EDF6F5', edgecolor='none', zorder=0))
            weight = 'bold' if is_best else 'normal'
            score_str = f'{ms:.1f}{unit} [{lo:.1f}, {hi:.1f}]' if unit == '%' else f'{ms:.3f} [{lo:.3f}, {hi:.3f}]'
            wall_str = '—' if mwall is None else f'{mwall:.1f}s [{q25:.1f}, {q75:.1f}]'
            rev_str = '—' if mrev is None else f'{mrev:.2f}'
            vals = [
                (m['label'], 0.01, 'left', m['color'], 'bold' if is_best else 'semibold'),
                (score_str, 0.20, 'left', common.INK, weight),
                (fmt_tokens(mtok), 0.56, 'right', common.INK, weight),
                (rev_str, 0.70, 'right', common.INK, weight),
                (wall_str, 0.87, 'right', common.INK, weight),
                (f'{nc}/{n}', 0.99, 'right', common.MUTED, 'normal'),
            ]
            for txt, x, ha, col_c, fw in vals:
                ax.text(x, y, txt, transform=ax.transAxes, ha=ha, va='center', fontsize=8.6, color=col_c, fontweight=fw)

    y -= step * 0.55
    ax.plot([0.0, 1.0], [y, y], color=common.INK, lw=1.4, transform=ax.transAxes, clip_on=False)

    fig.text(0.03, 0.93, 'Main comparison under a shared evaluation protocol', fontsize=13.5, fontweight='bold', color=common.INK)
    fig.text(0.03, 0.875, f"{config['experiment']} | Shading marks highest point-estimate row only (not statistical superiority)",
             fontsize=8.6, color=common.MUTED)

    note = (
        f"Score CIs are {'Wilson 95%' if is_binary else f'bootstrap 95% ({args.bootstrap} draws)'} per method (not paired difference CIs). "
        f"Token/rerank columns report means when complete across all n questions; wall time reports median [IQR]."
    )
    common.save_outputs(fig, args, 'results_table', config, note, summary_rows)


if __name__ == '__main__':
    main()
