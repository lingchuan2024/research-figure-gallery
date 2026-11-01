"""Shared style, data contracts and statistics for the figure examples."""
from pathlib import Path
import argparse
import csv
import os
import re

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

METHODS = ["Baseline", "Paging", "Auto rerank", "Agent rerank"]
COLORS = dict(zip(METHODS, ["#7A8693", "#4C78A8", "#E69F00", "#009E73"]))
TOOLS = ["search", "bash", "read", "rerank"]
TOOL_COLORS = dict(zip(TOOLS, ["#4C78A8", "#B3BAC5", "#72B7B2", "#F2AA5E"]))
INK = "#243746"

def setup():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.titlesize": 12, "axes.labelsize": 10,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#8B9AA4", "axes.labelcolor": INK,
        "text.color": INK, "xtick.color": INK, "ytick.color": INK,
        "axes.axisbelow": True, "grid.color": "#E4EAEE",
        "grid.linewidth": 0.7, "lines.linewidth": 1.8,
        "legend.frameon": False, "savefig.dpi": 180,
        "svg.fonttype": "none", "svg.hashsalt": "research-figure-gallery",
        "figure.facecolor": "white", "axes.facecolor": "white",
    })

def arguments(example_id):
    p = argparse.ArgumentParser(description=f"Render {example_id}")
    p.add_argument("--data-dir", type=Path, default=ROOT / "data" / "demo")
    p.add_argument("--output-dir", type=Path, default=ROOT / "assets")
    p.add_argument("--formats", nargs="+", choices=["png", "svg", "pdf"], default=["png", "svg"])
    return p.parse_args()

def rows(args, filename):
    path = args.data_dir / filename
    if not path.is_file():
        raise FileNotFoundError(f"{path}: run python scripts/generate_demo_data.py first")
    with path.open(newline="", encoding="utf-8") as f:
        result = list(csv.DictReader(f))
    if not result:
        raise ValueError(f"{path}: empty input table")
    return result

def numbers(records, key):
    return np.array([float(r[key]) for r in records], dtype=float)

def subset(records, method):
    return [r for r in records if r["method"] == method]

def save(fig, args, example_id, note="", concept=False):
    title = "CONCEPTUAL DIAGRAM - not a measured result" if concept else "SYNTHETIC DEMO - not experimental results"
    fig.text(0.5, 0.018, title + (" | " + note if note else ""), ha="center", va="bottom", fontsize=8, color="#657985")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for fmt in args.formats:
        metadata = {"Date": None} if fmt == "svg" else ({"CreationDate": None, "ModDate": None} if fmt == "pdf" else {"Software": "research-figure-gallery"})
        fig.savefig(args.output_dir / f"{example_id}.{fmt}", bbox_inches="tight", facecolor="white", metadata=metadata)
    plt.close(fig)

def normalize_rows(matrix):
    """Return probabilities; an unobserved source state remains NaN, not 0."""
    a = np.asarray(matrix, dtype=float)
    if a.ndim != 2 or np.any(a < 0):
        raise ValueError("Expected a nonnegative two-dimensional count matrix")
    denominator = a.sum(axis=1, keepdims=True)
    return np.divide(a, denominator, out=np.full_like(a, np.nan), where=denominator > 0)

def wilson_interval(successes, total, z=1.959963984540054):
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("Require 0 <= successes <= total and total > 0")
    p = successes / total
    den = 1 + z*z / total
    mid = (p + z*z/(2*total)) / den
    half = z * np.sqrt(p*(1-p)/total + z*z/(4*total*total)) / den
    return max(0.0, mid-half), min(1.0, mid+half)

def paired_bootstrap_ci(differences, seed=20261101, draws=3000):
    a = np.asarray(differences, dtype=float)
    if a.ndim != 1 or len(a) == 0 or not np.all(np.isfinite(a)):
        raise ValueError("Expected a nonempty finite vector of paired differences")
    rng = np.random.default_rng(seed)
    means = a[rng.integers(0, len(a), size=(draws, len(a)))].mean(axis=1)
    return np.quantile(means, [0.025, 0.975])

def pair_by_id(left, right, key="question_id"):
    def index(items):
        result = {}
        for item in items:
            k = item[key]
            if k in result:
                raise ValueError(f"Duplicate pairing key: {k}")
            result[k] = item
        return result
    a, b = index(left), index(right)
    if a.keys() != b.keys():
        raise ValueError("Pairing requires exactly the same question IDs in both groups")
    return [(a[k], b[k]) for k in sorted(a)]

def pareto_frontier(x, y):
    """Minimize x and maximize y; ties retain the point with highest y."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.shape != y.shape or x.ndim != 1 or not np.all(np.isfinite(x+y)):
        raise ValueError("Expected matching finite vectors")
    return np.array([i for i in range(len(x)) if not np.any((x <= x[i]) & (y >= y[i]) & ((x < x[i]) | (y > y[i])))], dtype=int)

