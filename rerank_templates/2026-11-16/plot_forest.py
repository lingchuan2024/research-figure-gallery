"""Plot question-paired quality changes, with one block per benchmark and subset.

This is an original Matplotlib implementation of a grouped forest layout.
It uses the shared input contract in common.py and does not depend on forestplot.
"""
from __future__ import annotations

import textwrap

from common import (
    np, plt, setup, arguments, load_dataset, groups, paired_differences,
    bootstrap_ci, save_outputs,
)


STEM = "forest"
INK = "#203744"
MUTED = "#627884"
PALE = "#F1F5F6"
MARKERS = ("o", "s", "D", "^", "v", "P", "X")


def _wrapped(value, width):
    return "\n".join(textwrap.wrap(str(value), width=width,
                                    break_long_words=False,
                                    break_on_hyphens=False))


def _signed(value):
    """Avoid a displayed negative zero after rounding."""
    value = 0.0 if abs(value) < .005 else value
    return f"{value:+.2f}"


def main(argv=None):
    setup()
    args = arguments(STEM, argv)
    rows, cfg = load_dataset(args)
    baseline_id = cfg["baseline"]
    baseline_label = next(m["label"] for m in cfg["methods"] if m["id"] == baseline_id)
    methods = [m for m in cfg["methods"] if m["id"] != baseline_id]
    if not methods:
        raise ValueError("A forest plot requires at least one non-baseline method.")
    scale = float(cfg["score"]["scale"])
    delta_unit = cfg["score"]["delta_unit"]
    score_label = cfg["score"]["label"]
    group_data = groups(rows, include_all=True)
    if not group_data:
        raise ValueError("No benchmark/subset groups are available to plot.")

    # Keep a whole benchmark together while retaining the common helper's order.
    benchmark_order = list(dict.fromkeys(g[1][0]["benchmark"] for g in group_data))
    ordered_groups = [g for benchmark in benchmark_order for g in group_data
                      if g[1][0]["benchmark"] == benchmark]
    label_lines = max(len(_wrapped(m["label"], 20).splitlines()) for m in methods)
    row_step = max(1.0, .7 * label_lines)
    plotted = []
    group_blocks = []
    benchmark_headers = []
    cursor = 0.0
    previous_benchmark = None

    for gi, (group_label, group_rows) in enumerate(ordered_groups):
        benchmark = group_rows[0]["benchmark"]
        if any(r["benchmark"] != benchmark for r in group_rows):
            raise ValueError("A forest plot group cannot pool multiple benchmarks.")
        if benchmark != previous_benchmark:
            if previous_benchmark is not None:
                cursor += .45
            benchmark_headers.append((cursor, benchmark))
            cursor += .95
            previous_benchmark = benchmark
        block_start = cursor
        subset_label = str(group_label)
        prefix = f"{benchmark} / "
        if subset_label.startswith(prefix):
            subset_label = subset_label[len(prefix):]
        for mi, method in enumerate(methods):
            differences = np.asarray(
                paired_differences(group_rows, baseline_id, method["id"]),
                dtype=float,
            ) * scale
            if differences.ndim != 1 or not len(differences) or not np.all(np.isfinite(differences)):
                raise ValueError(f"Invalid paired differences for {group_label}: {method['id']}")
            # This offset is deterministic across processes; Python hash() is not.
            seed = int(args.seed) + gi * 1009 + mi * 37
            low, high = bootstrap_ci(differences, draws=args.bootstrap, seed=seed)
            estimate = float(differences.mean())
            plotted.append({
                "benchmark": benchmark,
                "subset": subset_label,
                "group": group_label,
                "method": method["id"],
                "method_label": method["label"],
                "baseline": baseline_id,
                "n": len(differences),
                "mean_delta": estimate,
                "ci_low": float(low),
                "ci_high": float(high),
                "delta_unit": delta_unit,
                "bootstrap_draws": int(args.bootstrap),
                "bootstrap_seed": seed,
                "interval_status": "single_pair_degenerate" if len(differences) == 1 else "estimated",
                "y": cursor,
                "method_index": mi,
            })
            cursor += row_step
        block_end = cursor - row_step
        group_blocks.append((block_start, block_end, subset_label, gi))
        cursor += .65

    height = max(5.2, 2.0 + .31 * cursor)
    fig = plt.figure(figsize=(12.8, height))
    grid = fig.add_gridspec(1, 3, width_ratios=[1.85, 3.4, 3.7],
                            left=.045, right=.985,
                            top=1 - 1.18 / height, bottom=.92 / height,
                            wspace=.045)
    labels = fig.add_subplot(grid[0, 0])
    ax = fig.add_subplot(grid[0, 1])
    table = fig.add_subplot(grid[0, 2])
    ymin, ymax = -.45, max(cursor - .30, 1)
    for panel in (labels, ax, table):
        panel.set_ylim(ymax, ymin)
    for panel in (labels, table):
        panel.set_xlim(0, 1)
        panel.axis("off")

    fig.text(.045, 1 - .19 / height,
             f"Quality change relative to {baseline_label}",
             ha="left", va="top", fontsize=16, fontweight="bold", color=INK)
    fig.text(.045, 1 - .54 / height,
             f"{score_label} | Strictly paired question IDs within each benchmark | 95% bootstrap intervals",
             ha="left", va="top", fontsize=9.5, color=MUTED)

    for start, end, label, gi in group_blocks:
        if gi % 2 == 0:
            for panel in (labels, ax, table):
                panel.axhspan(start - .42, end + .42, color=PALE, zorder=0)
        labels.text(.03, (start + end) / 2, _wrapped(label, 22),
                    va="center", ha="left", fontsize=10, color=INK)
    for y, benchmark in benchmark_headers:
        labels.text(.02, y, _wrapped(benchmark, 22), va="center", ha="left",
                    fontsize=10.5, color=INK, fontweight="bold")
        for panel in (labels, ax, table):
            panel.axhline(y - .32, color="#D1DDE2", lw=.8, zorder=1)

    extrema = [0.0]
    for item in plotted:
        mi = item["method_index"]
        method = methods[mi]
        color = method["color"]
        y = item["y"]
        low, high, mean = item["ci_low"], item["ci_high"], item["mean_delta"]
        # Draw interval and point independently: percentile intervals need not
        # contain the sample mean for every tiny or very skewed sample.
        ax.hlines(y, low, high, color=color, lw=1.6, zorder=3)
        ax.vlines([low, high], y - .10, y + .10, color=color, lw=1.1, zorder=3)
        ax.scatter(mean, y, marker=MARKERS[mi % len(MARKERS)], s=35,
                   color=color, edgecolors="white", linewidths=.4, zorder=4)
        table.text(.01, y, _wrapped(method["label"], 20), ha="left", va="center",
                   fontsize=9, color=color)
        n_label = f"{item['n']}\u2020" if item["n"] == 1 else str(item["n"])
        table.text(.48, y, n_label, ha="right", va="center", fontsize=9)
        table.text(.99, y,
                   f"{_signed(mean)} [{_signed(low)}, {_signed(high)}]",
                   ha="right", va="center", fontsize=9, fontfamily="DejaVu Sans Mono")
        extrema.extend([low, high, mean])

    extent = max(extrema) - min(extrema)
    pad = max(extent * .10, abs(scale) * .005, .1)
    ax.set_xlim(min(extrema) - pad, max(extrema) + pad)
    ax.axvline(0, ls=(0, (4, 4)), color="#80929D", lw=1, zorder=1)
    ax.grid(axis="x", color="#E5ECEF", linewidth=.7)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel(f"Candidate minus baseline ({delta_unit})", labelpad=7)
    table.text(.01, 1.035, "Method", transform=table.transAxes,
               fontsize=9, fontweight="bold", color=INK)
    table.text(.48, 1.035, "n", transform=table.transAxes,
               ha="right", fontsize=9, fontweight="bold", color=INK)
    table.text(.99, 1.035, f"Delta ({delta_unit}) [95% CI]", transform=table.transAxes,
               ha="right", fontsize=9, fontweight="bold", color=INK)
    handles = [plt.Line2D([], [], color=m["color"], marker=MARKERS[i % len(MARKERS)],
                          linewidth=1.5, markersize=5, label=m["label"])
               for i, m in enumerate(methods)]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.045, 1 - .78 / height),
               borderaxespad=0, ncol=min(4, len(methods)), fontsize=9,
               handlelength=1.8, columnspacing=1.5, frameon=False)

    summaries = [{k: v for k, v in row.items() if k not in ("y", "method_index")}
                 for row in plotted]
    note = (f"Paired-question percentile bootstrap ({args.bootstrap:,} draws); intervals are not "
            "multiplicity-adjusted. All includes its subsets; benchmarks are never pooled.")
    if any(item["n"] == 1 for item in plotted):
        note += " \u2020 n=1: the degenerate interval cannot estimate population uncertainty."
    audit = {
        "pairing": "strict question-ID pairing within benchmark, validated by shared loader",
        "aggregation": "one benchmark and subset per estimate; All overlaps its subsets",
        "effect": "candidate score minus baseline score, multiplied by score.scale",
        "ci": "95% percentile bootstrap over paired-question differences",
        "multiple_comparisons_adjusted": False,
        "benchmark_count": len(benchmark_order),
        "group_count": len(ordered_groups),
        "method_count_excluding_baseline": len(methods),
    }
    save_outputs(fig, args, STEM, cfg, note, summaries, audit=audit)


if __name__ == "__main__":
    main()
