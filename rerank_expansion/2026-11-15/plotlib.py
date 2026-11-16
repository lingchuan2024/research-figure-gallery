"""Consistent publication-oriented plotting for the reranking paper collection."""
from pathlib import Path
import argparse
import csv
import os

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

INK = '#203744'
TEAL = '#157E82'
BLUE = '#4C78A8'
ORANGE = '#D4943B'
GRAY = '#8A99A3'
RED = '#B75A53'
LIGHT = '#E9EFF2'

def setup():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 10,
        'axes.titlesize': 12, 'axes.titleweight': 'bold', 'axes.labelsize': 10,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.edgecolor': '#B8C5CC', 'axes.labelcolor': INK, 'text.color': INK,
        'xtick.color': INK, 'ytick.color': INK, 'xtick.labelsize': 9, 'ytick.labelsize': 9,
        'axes.axisbelow': True, 'grid.color': LIGHT, 'grid.linewidth': .8,
        'legend.frameon': False, 'svg.fonttype': 'none',
        'svg.hashsalt': 'rerank-expansion-2026-11-15',
        'figure.facecolor': 'white', 'axes.facecolor': 'white', 'savefig.dpi': 200,
    })

def options(identifier):
    p = argparse.ArgumentParser(description=identifier + ' | exact published table data')
    p.add_argument('--data-dir', type=Path, default=HERE / 'data')
    p.add_argument('--output-dir', type=Path, default=HERE / 'figures')
    p.add_argument('--formats', nargs='+', choices=['png', 'svg'], default=['png', 'svg'])
    return p.parse_args()

def read(args, filename):
    with (args.data_dir / filename).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))

def heading(fig, title, subtitle):
    fig.text(.065, .96, title, va='top', fontsize=17, fontweight='bold', color=INK)
    fig.text(.065, .91, subtitle, va='top', fontsize=10, color='#607581')

def save(fig, args, identifier, citation, note=''):
    if note:
        fig.text(.065, .065, note, fontsize=8.5, color='#607581', va='bottom')
    fig.text(.065, .025, 'PUBLISHED DATA REDRAW | ' + citation + ' | Not our experimental results',
             fontsize=7.5, color='#607581', va='bottom')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for fmt in args.formats:
        metadata = {'Date': None} if fmt == 'svg' else {'Software': 'research-figure-gallery'}
        fig.savefig(args.output_dir / (identifier + '.' + fmt), dpi=200,
                    bbox_inches='tight', facecolor='white', metadata=metadata)
    plt.close(fig)
