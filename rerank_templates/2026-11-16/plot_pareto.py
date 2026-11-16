"""Mean quality versus cost, with paired-question bootstrap intervals.

The highlighted frontier describes observed means, not statistical superiority.
Run ``python plot_pareto.py --help`` for input/output options.
"""

from math import ceil
from textwrap import fill

from common import (
    np, plt, setup, arguments, load_dataset, select_metric_cohort,
    metric_info, bootstrap_ci, pareto_mask, save_outputs,
)
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.transforms import Bbox


STEM = "pareto"


def _place_labels(ax, points):
    """Choose deterministic label positions using rendered bounding boxes."""
    renderer = ax.figure.canvas.get_renderer()
    occupied = []
    bounds = ax.get_window_extent(renderer).padded(-3)
    point_boxes = [Bbox.from_bounds(*(ax.transData.transform((x, y)) - 5), 10, 10)
                   for x, y, _label, _color, _highlight in points]
    offsets = [(9, 9), (9, -15), (-9, 9), (-9, -15), (9, 24), (-9, 24),
               (9, -30), (-9, -30), (26, 0), (-26, 0), (9, 40), (-9, 40),
               (9, -46), (-9, -46)]
    for distance in range(60, max(80, 22 * len(points)), 20):
        offsets.extend([(9, distance), (-9, distance), (9, -distance), (-9, -distance)])
    for x, y, label, color, highlight in points:
        best = None
        for rank, (dx, dy) in enumerate(offsets):
            annotation = ax.annotate(fill(str(label), width=23), (x, y), xytext=(dx, dy),
                                     textcoords="offset points", fontsize=8.5,
                                     ha="left" if dx > 0 else "right", va="bottom" if dy > 0 else "top",
                                     color=color, weight="bold" if highlight else "normal",
                                     bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 1.0})
            box = annotation.get_window_extent(renderer).padded(2)
            overlap = sum(box.overlaps(other) for other in occupied)
            point_overlap = sum(box.overlaps(other) for other in point_boxes)
            overflow = (max(0, bounds.x0 - box.x0) + max(0, box.x1 - bounds.x1)
                        + max(0, bounds.y0 - box.y0) + max(0, box.y1 - bounds.y1))
            penalty = overlap * 10000 + overflow * 100 + point_overlap * 40 + rank
            annotation.remove()
            if best is None or penalty < best[0]:
                best = (penalty, dx, dy, box)
        _penalty, dx, dy, box = best
        ax.annotate(fill(str(label), width=23), (x, y), xytext=(dx, dy),
                    textcoords="offset points", fontsize=8.5,
                    ha="left" if dx > 0 else "right", va="bottom" if dy > 0 else "top",
                    color=color, weight="bold" if highlight else "normal",
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 1.0},
                    arrowprops={"arrowstyle": "-", "color": color, "lw": 0.55, "alpha": 0.65})
        occupied.append(box)


def _original_tick(value, _position):
    original = max(0.0, float(np.expm1(value)))
    return f"{original:,.0f}" if original >= 100 else f"{original:.3g}"


def main(argv=None):
    args = arguments(STEM, argv)
    setup()
    rows, cfg = load_dataset(args)
    rows, audit = select_metric_cohort(rows, args.metric, args.missing_cost)
    methods = cfg["methods"]
    benchmarks = sorted({str(row["benchmark"]) for row in rows})
    if not benchmarks or not methods:
        raise ValueError("No complete paired observations remain for the requested cost metric.")
    scale = float(cfg["score"].get("scale", 100))
    metric_label, _unit = metric_info(args.metric)
    score_label = cfg["score"]["label"]
    if cfg["score"].get("unit"):
        score_label += f" ({cfg['score']['unit']})"
    transformed = args.scale == "log1p"
    transform = np.log1p if transformed else np.asarray
    ncols = min(2, len(benchmarks))
    nrows = ceil(len(benchmarks) / ncols)
    facet_height = max(4.3, 0.24 * len(methods) + 2.5)
    fig, axes = plt.subplots(nrows, ncols, figsize=(6.8 * ncols, facet_height * nrows + 1.8), squeeze=False)
    fig.suptitle("Observed quality–cost trade-offs", x=0.08, y=1 - 0.14 / fig.get_figheight(),
                 ha="left", va="top", fontsize=16, weight="bold")
    summary = []
    labels_by_axis = []
    for benchmark_index, benchmark in enumerate(benchmarks):
        ax = axes.flat[benchmark_index]
        selected = [row for row in rows if str(row["benchmark"]) == benchmark]
        by_method = {method["id"]: sorted(
            [row for row in selected if row["method"] == method["id"]],
            key=lambda row: str(row["question_id"])) for method in methods}
        reference_ids = [str(row["question_id"]) for row in by_method[methods[0]["id"]]]
        if not reference_ids or any([str(row["question_id"]) for row in observations] != reference_ids
                                    for observations in by_method.values()):
            raise ValueError(f"{benchmark}: every method must use the same nonempty set of questions.")
        means_cost, means_score, intervals_cost, intervals_score = [], [], [], []
        # Identical seeds and question ordering share bootstrap draws across all
        # methods and both coordinates. Intervals remain marginal, not joint.
        seed = args.seed + benchmark_index * 1009
        for method in methods:
            observations = by_method[method["id"]]
            costs = np.asarray([float(row[args.metric]) for row in observations])
            scores = np.asarray([float(row["score"]) for row in observations]) * scale
            if not np.isfinite(costs).all() or (costs < 0).any():
                raise ValueError("Cost values must be finite and nonnegative.")
            means_cost.append(float(np.mean(costs)))
            means_score.append(float(np.mean(scores)))
            intervals_cost.append(bootstrap_ci(costs, args.bootstrap, seed))
            intervals_score.append(bootstrap_ci(scores, args.bootstrap, seed))
        means_cost, means_score = np.asarray(means_cost), np.asarray(means_score)
        intervals_cost, intervals_score = np.asarray(intervals_cost), np.asarray(intervals_score)
        frontier = pareto_mask(means_cost, means_score)
        plot_costs = transform(means_cost)
        plot_intervals = transform(intervals_cost)
        points = []
        for index, method in enumerate(methods):
            x, y = plot_costs[index], means_score[index]
            color, highlight = method["color"], bool(frontier[index])
            # Draw CI bounds directly: percentile intervals need not enclose the
            # observed mean, so using unsigned errorbar widths can be incorrect.
            ax.plot(plot_intervals[index], [y, y], color=color, lw=1.0, alpha=0.7, zorder=2)
            ax.plot([x, x], intervals_score[index], color=color, lw=1.0, alpha=0.7, zorder=2)
            ax.scatter([x], [y], s=78 if highlight else 48,
                       facecolors=color if highlight else "white", edgecolors=color,
                       linewidths=1.7 if highlight else 1.2, zorder=4)
            if highlight:
                ax.scatter([x], [y], s=135, facecolors="none", edgecolors=color, lw=0.6, zorder=3)
            points.append((x, y, method["label"], color, highlight))
            dominates = (means_cost <= means_cost[index]) & (means_score >= means_score[index])
            strict = (means_cost < means_cost[index]) | (means_score > means_score[index])
            dominated_by = [methods[j]["id"] for j in np.flatnonzero(dominates & strict)]
            summary.append({
                "benchmark": benchmark, "method": method["id"], "method_label": method["label"],
                "metric": args.metric, "n": len(reference_ids),
                "mean_cost": float(means_cost[index]), "cost_ci_low": float(intervals_cost[index, 0]),
                "cost_ci_high": float(intervals_cost[index, 1]),
                "mean_score": float(means_score[index]), "score_ci_low": float(intervals_score[index, 0]),
                "score_ci_high": float(intervals_score[index, 1]), "score_unit": cfg["score"].get("unit", ""),
                "nondominated": highlight, "dominated_by": " | ".join(dominated_by),
                "bootstrap_draws": args.bootstrap, "bootstrap_seed": seed,
                "plot_scale": args.scale,
            })
        xmin = float(min(plot_intervals[:, 0].min(), plot_costs.min()))
        xmax = float(max(plot_intervals[:, 1].max(), plot_costs.max()))
        ymin = float(min(intervals_score[:, 0].min(), means_score.min()))
        ymax = float(max(intervals_score[:, 1].max(), means_score.max()))
        xrange = max(xmax - xmin, abs(xmax) * 0.15, 0.1 if transformed else 1.0)
        yrange = max(ymax - ymin, scale * 0.04)
        ax.set_xlim(max(-0.04 * xrange, xmin - 0.18 * xrange), xmax + 0.30 * xrange)
        ax.set_ylim(max(-0.02 * yrange, ymin - 0.20 * yrange), min(scale + 0.02 * yrange, ymax + 0.25 * yrange))
        ax.set_title(f"{benchmark}  ·  n={len(reference_ids):,} paired questions", loc="left", fontsize=11, weight="bold", pad=12)
        ax.set_xlabel(metric_label + ("\nlog1p positions; ticks in original units" if transformed else ""), labelpad=8)
        ax.set_ylabel(score_label)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=3))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=3))
        if transformed:
            ax.xaxis.set_major_formatter(FuncFormatter(_original_tick))
        ax.grid(alpha=0.17, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        labels_by_axis.append((ax, points))
    for ax in axes.flat[len(benchmarks):]:
        ax.set_visible(False)
    fig.subplots_adjust(left=0.11 if ncols == 1 else 0.07, right=0.97,
                        top=1 - 0.90 / fig.get_figheight(), bottom=(1.65 if transformed else 1.45) / fig.get_figheight(),
                        hspace=0.52, wspace=0.30)
    fig.canvas.draw()
    for ax, points in labels_by_axis:
        _place_labels(ax, points)
    note = ("Filled double-ring points: nondominated observed means (lower cost, higher quality); hollow: dominated. "
            "Bars: 95% marginal percentile bootstrap CIs, resampling the same questions within each benchmark. "
            "All methods and both coordinates use the same retained question cohort. "
            "No connecting frontier is drawn; nondominance does not establish statistical superiority. "
            + ("log1p changes cost positions only; summaries and tick labels retain original units."
               if transformed else ""))
    save_outputs(fig, args, STEM, cfg, note, summary, audit=audit)
    plt.close(fig)
    return summary


if __name__ == "__main__":
    main()
