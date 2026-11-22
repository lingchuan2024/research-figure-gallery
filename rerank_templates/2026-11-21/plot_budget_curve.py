"""F06: Budget / turn sensitivity curves with 95% confidence bands from budget_runs.csv."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
import common


def main(argv=None):
    common.setup()
    parser = common.base_parser('budget_curve', 'budget_runs.csv')
    args = common.finalize_args(parser, 'budget_runs.csv', argv)

    config = common.load_config(args.config)
    rows = common.validate_budget_runs(common.read_csv_rows(args.data), config)
    scale = float(config['score']['scale'])
    unit = config['score']['unit']
    is_binary = config['score']['kind'] == 'binary'
    budget_cfg = config.get('budget', {'label': 'Budget', 'unit': ''})

    benchmarks = sorted({r['benchmark'] for r in rows})
    n_bm = len(benchmarks)
    fig, axes = plt.subplots(1, n_bm, figsize=(max(6.8, 5.8 * n_bm), 4.6), squeeze=False)
    fig.subplots_adjust(left=0.09, right=0.96, top=0.77, bottom=0.20, wspace=0.22)

    summary_rows = []
    for ax, bm in zip(axes[0], benchmarks):
        bm_rows = [r for r in rows if r['benchmark'] == bm]
        budgets = sorted({r['budget_value'] for r in bm_rows})
        ax.grid(True, alpha=0.85)

        for m in config['methods']:
            xs, ys, los, his = [], [], [], []
            for bval in budgets:
                sub = [r['score'] for r in bm_rows if r['method'] == m['id'] and r['budget_value'] == bval]
                arr = np.asarray(sub, dtype=float)
                mean_v = float(arr.mean())
                if is_binary:
                    lo, hi = common.wilson_interval(int(round(arr.sum())), len(arr))
                else:
                    lo, hi = common.bootstrap_ci(arr, draws=args.bootstrap, seed=args.seed)
                xs.append(bval)
                ys.append(mean_v * scale)
                los.append(lo * scale)
                his.append(hi * scale)
                summary_rows.append({
                    'benchmark': bm, 'method_id': m['id'], 'method_label': m['label'],
                    'budget_value': bval, 'n': len(arr),
                    'score_mean': round(mean_v * scale, 4),
                    'ci_low': round(lo * scale, 4),
                    'ci_high': round(hi * scale, 4),
                })
            ax.fill_between(xs, los, his, color=m['color'], alpha=0.14)
            ax.plot(xs, ys, marker='o', color=m['color'], lw=2.2, markersize=5.5, label=m['label'])
            ax.text(xs[-1] + (xs[-1] - xs[0]) * 0.025, ys[-1], f'{ys[-1]:.1f}{unit}' if unit == '%' else f'{ys[-1]:.3f}',
                    va='center', ha='left', fontsize=8.0, color=m['color'], fontweight='bold')

        span = max(budgets) - min(budgets) if len(budgets) > 1 else 1.0
        ax.set_xlim(min(budgets) - span * 0.04, max(budgets) + span * 0.14)
        ax.set_xticks(budgets)
        ax.set_xlabel(f"{budget_cfg['label']} ({budget_cfg['unit']})" if budget_cfg.get('unit') else budget_cfg['label'])
        ax.set_ylabel(f"{config['score']['label']} ({unit})")
        ax.set_title(bm, pad=8)
        ax.legend(loc='lower right', fontsize=8.4)

    fig.text(0.09, 0.93, f"Quality across {budget_cfg['label'].lower()} budgets", fontsize=13.2, fontweight='bold', color=common.INK)
    fig.text(0.09, 0.875, f"{config['experiment']} | Shaded bands show pointwise 95% {'Wilson' if is_binary else 'bootstrap'} intervals",
             fontsize=8.6, color=common.MUTED)
    note = 'Each budget point represents a dedicated run under that cap (not post-hoc trajectory truncation). Pointwise bands are not simultaneous confidence bands.'
    common.save_outputs(fig, args, 'budget_curve', config, note, summary_rows)


if __name__ == '__main__':
    main()
