"""Consistent publication-oriented plotting for the 2026 agentic-search reranking paper collection."""
from pathlib import Path
import argparse
import csv
import os

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', str(ROOT / '.cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

INK = '#203744'
MUTED = '#5E727D'
TEAL = '#157E82'
BLUE = '#4C78A8'
ORANGE = '#D4943B'
GRAY = '#8A99A3'
RED = '#B75A53'
PURPLE = '#7A68A6'
LIGHT = '#E9EFF2'


def setup():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 9.5,
        'axes.titlesize': 11.5,
        'axes.titleweight': 'bold',
        'axes.labelsize': 9.5,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.edgecolor': '#B8C5CC',
        'axes.labelcolor': INK,
        'text.color': INK,
        'xtick.color': INK,
        'ytick.color': INK,
        'xtick.labelsize': 8.5,
        'ytick.labelsize': 8.5,
        'axes.axisbelow': True,
        'grid.color': LIGHT,
        'grid.linewidth': 0.8,
        'legend.frameon': False,
        'svg.fonttype': 'none',
        'svg.hashsalt': 'rerank-expansion-2026-11-21',
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'savefig.dpi': 240,
    })


def options(identifier):
    p = argparse.ArgumentParser(description=identifier + ' | exact published table data')
    p.add_argument('--data-dir', type=Path, default=HERE / 'data')
    p.add_argument('--output-dir', type=Path, default=HERE / 'figures')
    p.add_argument('--formats', nargs='+', choices=['png', 'svg', 'pdf'], default=['png', 'svg'])
    return p.parse_args()


def read(args, filename):
    with (args.data_dir / filename).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def heading(fig, title, subtitle):
    fig.text(0.055, 0.965, title, va='top', fontsize=15.5, fontweight='bold', color=INK)
    fig.text(0.055, 0.915, subtitle, va='top', fontsize=9.5, color=MUTED)


def save(fig, args, identifier, citation, note=''):
    if note:
        fig.text(0.055, 0.058, note, fontsize=8.0, color=MUTED, va='bottom')
    fig.text(
        0.055,
        0.020,
        'PUBLISHED DATA REDRAW | ' + citation + ' | Not our experimental results',
        fontsize=7.3,
        color=MUTED,
        va='bottom',
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for fmt in args.formats:
        if fmt == 'svg':
            metadata = {'Date': None}
        elif fmt == 'pdf':
            metadata = {'CreationDate': None, 'ModDate': None}
        else:
            metadata = {'Software': 'research-figure-gallery'}
        fig.savefig(
            args.output_dir / f'{identifier}.{fmt}',
            dpi=240,
            bbox_inches='tight',
            facecolor='white',
            metadata=metadata,
        )
    plt.close(fig)
