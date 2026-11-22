"""F09: Turn-aligned multi-method tool trajectory timeline from trajectories.csv."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
import common


def main(argv=None):
    common.setup()
    parser = common.base_parser('trajectory', 'trajectories.csv')
    parser.add_argument('--case-id', default=None, help='Case ID to render (default: first case_id in CSV).')
    args = common.finalize_args(parser, 'trajectories.csv', argv)

    config = common.load_config(args.config)
    rows = common.validate_trajectories(common.read_csv_rows(args.data), config)
    case_ids = sorted({r['case_id'] for r in rows})
    case_id = args.case_id or case_ids[0]
    sub = [r for r in rows if r['case_id'] == case_id]
    if not sub:
        raise ValueError(f'No trajectory rows found for case_id={case_id}.')

    method_order = [m for m in config['methods'] if any(r['method'] == m['id'] for r in sub)]
    pref_tools = ['search', 'bash', 'read', 'rerank', 'answer']
    found_tools = sorted({r['tool'] for r in sub})
    tools = [t for t in pref_tools if t in found_tools] + [t for t in found_tools if t not in pref_tools]
    tool_y = {t: len(tools) - 1 - i for i, t in enumerate(tools)}
    max_turn = max(r['turn'] for r in sub)

    fig, axes = plt.subplots(len(method_order), 1, figsize=(10.6, max(4.2, 1.95 * len(method_order) + 1.2)),
                             sharex=True, squeeze=False)
    fig.subplots_adjust(left=0.11, right=0.96, top=0.80, bottom=0.17, hspace=0.38)

    summary_rows = []
    for ax, m in zip(axes[:, 0], method_order):
        m_rows = sorted([r for r in sub if r['method'] == m['id']], key=lambda r: r['turn'])
        turns = [r['turn'] for r in m_rows]
        ys = [tool_y[r['tool']] for r in m_rows]
        ax.plot(turns, ys, color='#B8C5CC', lw=1.6, zorder=1)
        ax.grid(axis='y', alpha=0.7)

        first_ev = None
        outcome = 'unknown'
        for r in m_rows:
            t, yv = r['turn'], tool_y[r['tool']]
            tc = common.DEFAULT_TOOL_COLORS.get(r['tool'], m['color'])
            flag = r['event_flag']
            if flag == 'first_evidence':
                first_ev = t
                ax.scatter([t], [yv], marker='*', s=190, color='#E6A817', edgecolors=common.INK, lw=0.8, zorder=5)
                ax.annotate('first evidence', (t, yv), xytext=(0, 10), textcoords='offset points',
                            ha='center', fontsize=7.6, fontweight='bold', color='#8C6200')
            elif flag == 'rerank_hit':
                ax.scatter([t], [yv], marker='D', s=72, color='#E09A42', edgecolors=common.INK, lw=0.8, zorder=4)
                ax.annotate('rerank hit', (t, yv), xytext=(0, -13), textcoords='offset points',
                            ha='center', fontsize=7.4, color='#9E5E10')
            elif flag == 'final_correct':
                outcome = 'correct'
                ax.scatter([t], [yv], marker='o', s=84, color='#157E82', edgecolors='white', lw=1.0, zorder=5)
                ax.annotate('correct', (t, yv), xytext=(8, 0), textcoords='offset points',
                            va='center', fontsize=8.0, fontweight='bold', color='#157E82')
            elif flag == 'final_wrong':
                outcome = 'wrong'
                ax.scatter([t], [yv], marker='X', s=84, color='#B75A53', edgecolors='white', lw=0.8, zorder=5)
                ax.annotate('wrong', (t, yv), xytext=(8, 0), textcoords='offset points',
                            va='center', fontsize=8.0, fontweight='bold', color='#B75A53')
            else:
                ax.scatter([t], [yv], marker='o', s=46, color=tc, edgecolors='white', lw=0.7, zorder=3)

        ax.set_yticks(list(tool_y.values()))
        ax.set_yticklabels(list(tool_y.keys()), fontsize=8.5)
        ax.set_ylim(-0.65, len(tools) - 0.35)
        ax.set_title(f"{m['label']}  ({len(m_rows)} turns)", loc='left', fontsize=10.0, color=m['color'], pad=5)
        summary_rows.append({
            'case_id': case_id, 'method_id': m['id'], 'method_label': m['label'],
            'total_turns': len(m_rows), 'first_evidence_turn': '' if first_ev is None else first_ev,
            'rerank_turns': sum(1 for r in m_rows if r['tool'] == 'rerank'),
            'outcome': outcome,
        })

    axes[-1, 0].set_xlim(0.4, max_turn + 1.5)
    axes[-1, 0].set_xticks(np.arange(1, max_turn + 1))
    axes[-1, 0].set_xlabel('Agent turn')

    fig.text(0.11, 0.94, f'Turn-aligned tool trajectories (case: {case_id})',
             fontsize=13.2, fontweight='bold', color=common.INK)
    fig.text(0.11, 0.885, 'Star = first answer-bearing evidence observed | Diamond = rerank hit | Single-question case study only',
             fontsize=8.6, color=common.MUTED)
    note = f'Case-study illustration for {case_id}. Single-question traces diagnose mechanism and cannot establish aggregate superiority.'
    common.save_outputs(fig, args, 'trajectory', config, note, summary_rows, extra_provenance={'case_id': case_id})


if __name__ == '__main__':
    main()
