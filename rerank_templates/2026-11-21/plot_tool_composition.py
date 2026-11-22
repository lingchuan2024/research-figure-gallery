"""F08: Pooled tool-call share vs. returned-text share stacked horizontal bars from tool_calls.csv."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import matplotlib.pyplot as plt
import common


def main(argv=None):
    common.setup()
    parser = common.base_parser('tool_composition', 'tool_calls.csv')
    args = common.finalize_args(parser, 'tool_calls.csv', argv)

    config = common.load_config(args.config)
    rows = common.validate_tool_calls(common.read_csv_rows(args.data), config)
    benchmarks = sorted({r['benchmark'] for r in rows})
    bm = benchmarks[0]
    bm_rows = [r for r in rows if r['benchmark'] == bm]

    pref_order = ['search', 'bash', 'read', 'rerank']
    found_tools = sorted({r['tool'] for r in bm_rows})
    tools = [t for t in pref_order if t in found_tools] + [t for t in found_tools if t not in pref_order]
    fallback_palette = ['#6E8494', '#8A79AF', '#C26A63', '#5A9E7D']
    tool_colors = {}
    fi = 0
    for t in tools:
        if t in common.DEFAULT_TOOL_COLORS:
            tool_colors[t] = common.DEFAULT_TOOL_COLORS[t]
        else:
            tool_colors[t] = fallback_palette[fi % len(fallback_palette)]
            fi += 1

    methods = config['methods']
    y = np.arange(len(methods))[::-1]
    n_q = len({r['question_id'] for r in bm_rows})

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, max(3.6, 0.72 * len(methods) + 1.8)), sharey=True)
    fig.subplots_adjust(left=0.14, right=0.95, top=0.75, bottom=0.22, wspace=0.16)

    summary_rows = []
    for yi, m in zip(y, methods):
        sub = [r for r in bm_rows if r['method'] == m['id']]
        tot_calls = sum(r['calls'] for r in sub)
        tot_chars = sum(r['returned_chars'] for r in sub)
        left_c, left_ch = 0.0, 0.0
        for t in tools:
            c_val = sum(r['calls'] for r in sub if r['tool'] == t)
            ch_val = sum(r['returned_chars'] for r in sub if r['tool'] == t)
            sh_c = (c_val / tot_calls * 100.0) if tot_calls > 0 else 0.0
            sh_ch = (ch_val / tot_chars * 100.0) if tot_chars > 0 else 0.0
            summary_rows.append({
                'benchmark': bm, 'method_id': m['id'], 'method_label': m['label'], 'tool': t,
                'pooled_calls': c_val, 'calls_share_pct': round(sh_c, 2),
                'pooled_returned_chars': ch_val, 'chars_share_pct': round(sh_ch, 2),
            })
            if sh_c > 0:
                ax1.barh(yi, sh_c, left=left_c, color=tool_colors[t], height=0.56, edgecolor='white', lw=0.8)
                if sh_c >= 9.0:
                    ax1.text(left_c + sh_c / 2, yi, f'{sh_c:.0f}%', ha='center', va='center', fontsize=8.0,
                             color='white' if t in {'search', 'rerank'} else common.INK, fontweight='bold')
                left_c += sh_c
            if sh_ch > 0:
                ax2.barh(yi, sh_ch, left=left_ch, color=tool_colors[t], height=0.56, edgecolor='white', lw=0.8)
                if sh_ch >= 9.0:
                    ax2.text(left_ch + sh_ch / 2, yi, f'{sh_ch:.0f}%', ha='center', va='center', fontsize=8.0,
                             color='white' if t in {'search', 'rerank'} else common.INK, fontweight='bold')
                left_ch += sh_ch
        ax1.text(101.5, yi, f'{tot_calls / n_q:.1f}/q', va='center', ha='left', fontsize=8.0, color=common.MUTED)
        ax2.text(101.5, yi, f'{tot_chars / n_q / 1000:.1f}k/q', va='center', ha='left', fontsize=8.0, color=common.MUTED)

    ax1.set_yticks(y)
    ax1.set_yticklabels([m['label'] for m in methods], fontsize=9.0, fontweight='bold')
    ax1.set_xlim(0, 114)
    ax1.set_xticks([0, 20, 40, 60, 80, 100])
    ax1.set_xlabel('Pooled share of tool calls (%)')
    ax1.set_title('(a) Tool-call mix (right: mean calls/q)', pad=8)

    ax2.set_xlim(0, 118)
    ax2.set_xticks([0, 20, 40, 60, 80, 100])
    ax2.set_xlabel('Pooled share of returned characters (%)')
    ax2.set_title('(b) Returned-text mix (right: mean chars/q)', pad=8)

    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=tool_colors[t], label=t) for t in tools]
    fig.legend(handles=handles, loc='upper right', bbox_to_anchor=(0.95, 0.87), ncol=len(tools), fontsize=8.6)

    fig.text(0.14, 0.94, f'Tool calls vs. returned text exposure ({bm}, n = {n_q} paired questions)',
             fontsize=13.0, fontweight='bold', color=common.INK)
    note = 'Pooled shares sum across all paired questions before dividing. Returned tool characters are not billed model input tokens.'
    common.save_outputs(fig, args, 'tool_composition', config, note, summary_rows)


if __name__ == '__main__':
    main()
