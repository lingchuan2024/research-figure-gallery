"""Render all six 2026 agentic-search reranking figures, build overview contact sheet, and write provenance."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CODE_DIR = HERE / 'code'
DATA_DIR = HERE / 'data'
FIG_DIR = HERE / 'figures'
PAPERS_DIR = HERE.parents[2] / 'DCI后续论文'

SCRIPTS = [
    'A01_iter_query_ablation.py',
    'A02_iter_cross_agent.py',
    'A03_rarg_coarse_to_fine.py',
    'A04_rarg_scope_heatmap.py',
    'A05_indexact_context_tradeoff.py',
    'A06_rise_scaling_and_topk.py',
]

SOURCES = [
    {
        'id': 'A01_iter_query_ablation',
        'paper': 'ITER: Interaction-Aware Retrieval for Agentic Search',
        'arxiv': '2608.27912v2',
        'local_pdf': 'ITER_Interaction-Aware_Retrieval_2608.27912.pdf',
        'location': 'Table 3, p. 15',
        'csv_files': ['iter_query_ablation.csv'],
    },
    {
        'id': 'A02_iter_cross_agent',
        'paper': 'ITER: Interaction-Aware Retrieval for Agentic Search',
        'arxiv': '2608.27912v2',
        'local_pdf': 'ITER_Interaction-Aware_Retrieval_2608.27912.pdf',
        'location': 'Table 2, p. 14',
        'csv_files': ['iter_cross_agent.csv'],
    },
    {
        'id': 'A03_rarg_coarse_to_fine',
        'paper': 'A New Role for Relevance: Guiding Corpus Interaction in Agentic Search (RARG)',
        'arxiv': '2607.24223v2',
        'local_pdf': 'RARG_A_New_Role_for_Relevance_2607.24223.pdf',
        'location': 'Table 1, p. 7',
        'csv_files': ['rarg_main_bcplus.csv'],
    },
    {
        'id': 'A04_rarg_scope_heatmap',
        'paper': 'A New Role for Relevance: Guiding Corpus Interaction in Agentic Search (RARG)',
        'arxiv': '2607.24223v2',
        'local_pdf': 'RARG_A_New_Role_for_Relevance_2607.24223.pdf',
        'location': 'Figure 3 (exact printed cell values), p. 9',
        'csv_files': ['rarg_scope_rank_heatmap.csv'],
    },
    {
        'id': 'A05_indexact_context_tradeoff',
        'paper': 'From Delivery to Stateful Exploration: Rethinking the Index for Agentic Search (IndexAct)',
        'arxiv': '2610.07960v1',
        'local_pdf': 'IndexAct_From_Delivery_to_Stateful_Exploration_2610.07960.pdf',
        'location': 'Table 1 (p. 7) & Table 2 (p. 8)',
        'csv_files': ['indexact_bcplus_main.csv', 'indexact_observation_ablation.csv'],
    },
    {
        'id': 'A06_rise_scaling_and_topk',
        'paper': 'Towards Retrieving Interaction Spaces for Agentic Search (RISE)',
        'arxiv': '2606.06880v1',
        'local_pdf': 'RISE_Towards_Retrieving_Interaction_Spaces_2606.06880.pdf',
        'location': 'Table 2 (p. 7) & Table 3 (p. 8)',
        'csv_files': ['rise_scaling_100k_1m.csv', 'rise_topk_ablation.csv'],
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_overview():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    fig, axes = plt.subplots(3, 2, figsize=(16, 15.5), facecolor='#F4F6F8')
    fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.02, wspace=0.06, hspace=0.10)
    fig.text(0.02, 0.975, '2026 Agentic Search & Reranking | 6 Published-Data Redraws (A01-A06)',
             fontsize=16, fontweight='bold', color='#203744', va='top')
    fig.text(0.02, 0.948, 'Exact published table/cell values from ITER, RARG, IndexAct, and RISE | Not our experimental results',
             fontsize=10, color='#5E727D', va='top')

    for ax, script in zip(axes.flat, SCRIPTS):
        stem = Path(script).stem
        img = mpimg.imread(FIG_DIR / f'{stem}.png')
        ax.imshow(img)
        ax.axis('off')
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('#D8E0E5')

    fig.savefig(HERE / 'agentic_overview.png', dpi=180, facecolor='#F4F6F8',
                metadata={'Software': 'research-figure-gallery'})
    plt.close(fig)


def write_provenance():
    entries = []
    for item in SOURCES:
        pdf_path = PAPERS_DIR / item['local_pdf']
        entry = {
            'id': item['id'],
            'paper': item['paper'],
            'arxiv': item['arxiv'],
            'location': item['location'],
            'local_pdf': item['local_pdf'],
            'local_pdf_sha256': sha256(pdf_path) if pdf_path.is_file() else None,
            'csv_sha256': {f: sha256(DATA_DIR / f) for f in item['csv_files']},
            'figure_png_sha256': sha256(FIG_DIR / f"{item['id']}.png"),
            'figure_svg_sha256': sha256(FIG_DIR / f"{item['id']}.svg"),
        }
        entries.append(entry)
    payload = {
        'created_on': '2026-11-21',
        'scope': 'Exact published table/cell values from 2026 agentic-search papers; no pixel-estimated curves; not our experimental results.',
        'figures': entries,
    }
    (HERE / 'data_provenance.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    for script in SCRIPTS:
        subprocess.run([sys.executable, str(CODE_DIR / script), '--formats', 'png', 'svg'], check=True)
    build_overview()
    write_provenance()
    print(f'Built {len(SCRIPTS)} figures + agentic_overview.png + data_provenance.json in {HERE}')


if __name__ == '__main__':
    main()
