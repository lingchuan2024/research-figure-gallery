"""Generate demo CSVs, render all six templates (F01/F02/F06/F07/F08/F09), and build overview."""
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
FIG_DIR = HERE / 'figures'

JOBS = [
    ('plot_results_table.py', 'results_table', []),
    ('plot_paired.py', 'paired', []),
    ('plot_budget_curve.py', 'budget_curve', []),
    ('plot_rank_transition.py', 'rank_transition', []),
    ('plot_tool_composition.py', 'tool_composition', []),
    ('plot_trajectory.py', 'trajectory', []),
]


def build_overview():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    fig, axes = plt.subplots(3, 2, figsize=(16, 15.0), facecolor='#F4F6F8')
    fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.02, wspace=0.06, hspace=0.10)
    fig.text(0.02, 0.975, 'Rerank Templates 2026-11-21 | F01, F02, F06, F07, F08, F09',
             fontsize=16, fontweight='bold', color='#243746', va='top')
    fig.text(0.02, 0.948, 'Measured-data-ready CSV + config.json templates (shown with synthetic demo inputs)',
             fontsize=10, color='#5C707B', va='top')

    for ax, (_, stem, _) in zip(axes.flat, JOBS):
        img = mpimg.imread(FIG_DIR / f'{stem}.png')
        ax.imshow(img)
        ax.axis('off')
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('#D8E0E5')

    fig.savefig(HERE / 'templates_overview.png', dpi=180, facecolor='#F4F6F8',
                metadata={'Software': 'rerank-templates-20261121'})
    plt.close(fig)


def main():
    subprocess.run([sys.executable, str(HERE / 'generate_demo.py')], check=True)
    for script, _, extra in JOBS:
        subprocess.run([sys.executable, str(HERE / script), *extra], check=True)
    build_overview()
    print(f'Rendered all {len(JOBS)} templates + templates_overview.png in {HERE}')


if __name__ == '__main__':
    main()
