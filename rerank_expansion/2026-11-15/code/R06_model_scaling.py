from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    setup(); args = options('R06_model_scaling'); rows = read(args, 'qwen3_scaling.csv')
    fig, axes = plt.subplots(2, 3, figsize=(11.6, 7.2))
    fig.subplots_adjust(left=.075, right=.97, top=.80, bottom=.17, hspace=.55, wspace=.28)
    heading(fig, 'Model size does not improve every ranking task',
            'Qwen3 rerankers | Identical top-100 candidates from Qwen3-Embedding-0.6B')
    for ax, task in zip(axes.flat, dict.fromkeys(r['benchmark'] for r in rows)):
        subset = [r for r in rows if r['benchmark'] == task]
        baseline = float(subset[0]['score']); vals = [float(r['score']) for r in subset[1:]]
        ax.axhline(baseline, color=GRAY, ls=(0,(4,3)), lw=1.4)
        ax.plot(range(3), vals, color=TEAL, lw=1.8, marker='o', ms=6)
        lo, hi = min([baseline]+vals), max([baseline]+vals); span = max(hi-lo, 4)
        ax.set_ylim(lo-.22*span, hi+.33*span); ax.set_xlim(-.3,2.3)
        for x, val in enumerate(vals):
            ax.annotate(f'{val:.2f}', (x,val), xytext=(0,9), textcoords='offset points',
                        ha='center', fontsize=9, fontweight='bold')
        ax.text(.02,.04,f'Retriever: {baseline:.2f}',transform=ax.transAxes,fontsize=8,color=GRAY)
        ax.set_title(task,loc='left',pad=12); ax.set_xticks(range(3),['0.6B','4B','8B'])
        ax.set_xlabel('Reranker parameters'); ax.grid(axis='y')
        ax.set_ylabel('Reported benchmark score')
    save(fig,args,'R06_model_scaling','Qwen3 Embedding (2025), Table 4, p. 8',
         'Each panel uses its native benchmark score and a separate y-scale; do not average across panels. Parameters are not latency.')

if __name__ == '__main__': main()
