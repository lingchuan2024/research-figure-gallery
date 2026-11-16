"""Per-question cost distributions, with raw observations and shared KDE bandwidth.

Run ``python plot_raincloud.py --help`` for the common input/output options.
No distribution is inferred from published aggregate statistics.
"""

from math import ceil

from common import (
    np, plt, setup, arguments, load_dataset, select_metric_cohort, groups,
    metric_info, save_outputs,
)
from matplotlib.ticker import FuncFormatter, MaxNLocator


STEM = "raincloud"


def _order(row):
    return (str(row["benchmark"]), str(row["question_id"]), str(row["method"]))


def _bandwidth(values):
    """One bandwidth per facet, in the actual plotted coordinate system."""
    values = np.asarray(values, dtype=float)
    if len(values) < 2 or np.ptp(values) == 0:
        return None
    sd = float(np.std(values, ddof=1))
    q25, q75 = np.quantile(values, [0.25, 0.75])
    robust_sd = float((q75 - q25) / 1.349)
    spread = min(sd, robust_sd) if robust_sd > 0 else sd
    return max(0.9 * spread * len(values) ** -0.2, np.ptp(values) * 1e-6)


def _density(grid, values, bandwidth):
    """Gaussian KDE, reflected at zero; chunking bounds working memory."""
    result = np.zeros_like(grid, dtype=float)
    for start in range(0, len(values), 2048):
        block = values[start:start + 2048]
        z = (grid[:, None] - block[None, :]) / bandwidth
        reflected = (grid[:, None] + block[None, :]) / bandwidth
        result += np.exp(-0.5 * z * z).sum(axis=1)
        result += np.exp(-0.5 * reflected * reflected).sum(axis=1)
    return result / (len(values) * bandwidth * np.sqrt(2 * np.pi))


def _original_tick(value, _position):
    original = max(0.0, float(np.expm1(value)))
    return f"{original:,.0f}" if original >= 100 else f"{original:.3g}"


def main(argv=None):
    args = arguments(STEM, argv)
    setup()
    rows, cfg = load_dataset(args)
    rows, audit = select_metric_cohort(rows, args.metric, args.missing_cost)
    rows = sorted(rows, key=_order)
    facets = list(groups(rows, include_all=False))
    if not facets:
        raise ValueError("No complete observations remain for the requested cost metric.")
    methods = cfg["methods"]
    if not methods:
        raise ValueError("At least one method is required.")
    transformed = args.scale == "log1p"
    transform = np.log1p if transformed else np.asarray
    all_values = np.asarray([float(row[args.metric]) for row in rows])
    if not np.isfinite(all_values).all() or (all_values < 0).any():
        raise ValueError("Cost values must be finite and nonnegative.")
    max_position = float(np.max(transform(all_values)))
    span = max_position if max_position > 0 else (float(np.log(2)) if transformed else 1.0)
    ncols = min(2, len(facets))
    nrows = ceil(len(facets) / ncols)
    facet_height = max(3.3, 0.62 * len(methods) + 1.4)
    fig, axes = plt.subplots(nrows, ncols, figsize=(6.4 * ncols, facet_height * nrows + 1.8),
                             squeeze=False, sharex=True)
    fig.suptitle("Per-question cost distributions", x=0.08, y=1 - 0.14 / fig.get_figheight(),
                 ha="left", va="top", fontsize=16, weight="bold")
    summary = []
    metric_label, _unit = metric_info(args.metric)
    x_label = metric_label + ("\nlog1p positions; ticks in original units" if transformed else "")
    for facet_index, (label, facet_rows) in enumerate(facets):
        ax = axes.flat[facet_index]
        facet_rows = sorted(facet_rows, key=_order)
        pooled = np.asarray([float(row[args.metric]) for row in facet_rows])
        bandwidth = _bandwidth(transform(pooled))
        ax.set_title(str(label), loc="left", fontsize=12, weight="bold", pad=12)
        for method_index, method in enumerate(methods):
            observations = [row for row in facet_rows if row["method"] == method["id"]]
            values = np.asarray([float(row[args.metric]) for row in observations])
            if not len(values):
                continue
            positions = np.asarray(transform(values), dtype=float)
            color = method["color"]
            # Constant and singleton groups deliberately have no artificial density.
            if len(values) > 1 and np.ptp(positions) > 0 and bandwidth is not None:
                endpoint = min(span * 1.06, float(np.max(positions)) + 3 * bandwidth)
                grid = np.linspace(0.0, endpoint, 240)
                density = _density(grid, positions, bandwidth)
                density = density / density.max() * 0.32
                ax.fill_between(grid, method_index - 0.10, method_index - 0.10 - density,
                                color=color, alpha=0.32, linewidth=0)
                ax.plot(grid, method_index - 0.10 - density, color=color, lw=0.9)
            q25, median, q75 = np.quantile(values, [0.25, 0.5, 0.75])
            q25p, medianp, q75p = transform(np.asarray([q25, median, q75]))
            ax.plot([q25p, q75p], [method_index, method_index], color=color,
                    lw=6, solid_capstyle="butt", zorder=4)
            ax.scatter([medianp], [method_index], marker="|", s=110,
                       color="white" if q75 > q25 else color, linewidths=1.5, zorder=5)
            # Every observation is retained, including failures and structural zeros.
            rng = np.random.default_rng(args.seed + facet_index * 1009 + method_index)
            jitter = rng.uniform(-0.055, 0.055, len(values))
            ax.scatter(positions, method_index + 0.18 + jitter, s=9,
                       color=color, alpha=0.35, linewidths=0, zorder=3,
                       rasterized=len(values) > 5000)
            ax.text(0.99, method_index + 0.20, f"n={len(values):,}",
                    transform=ax.get_yaxis_transform(), ha="right", va="center",
                    fontsize=8, color="#555555", bbox={"fc": "white", "ec": "none", "alpha": 0.8, "pad": 1})
            benchmarks = sorted({str(row["benchmark"]) for row in observations})
            summary.append({
                "facet": str(label), "benchmark": " | ".join(benchmarks),
                "method": method["id"], "method_label": method["label"],
                "metric": args.metric, "n": len(values), "mean": float(np.mean(values)),
                "p50": float(median), "p90": float(np.quantile(values, 0.9)),
                "p95": float(np.quantile(values, 0.95)), "zero_count": int(np.sum(values == 0)),
                "plot_scale": args.scale, "facet_kde_bandwidth": bandwidth,
            })
        ax.set_yticks(range(len(methods)), [method["label"] for method in methods])
        ax.set_ylim(len(methods) - 0.5, -0.60)
        ax.set_xlim(-0.025 * span, 1.08 * span)
        ax.set_xlabel(x_label, labelpad=8)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=3))
        if transformed:
            ax.xaxis.set_major_formatter(FuncFormatter(_original_tick))
        ax.grid(axis="x", alpha=0.2, linewidth=0.6)
        ax.set_axisbelow(True)
        for edge in ("top", "right", "left"):
            ax.spines[edge].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=8)
        ax.tick_params(axis="x", labelbottom=True)
    for ax in axes.flat[len(facets):]:
        ax.set_visible(False)
    fig.subplots_adjust(left=0.16 if ncols == 1 else 0.12, right=0.97,
                        top=1 - 0.90 / fig.get_figheight(), bottom=(1.65 if transformed else 1.45) / fig.get_figheight(),
                        hspace=0.62, wspace=0.42)
    note = ("Dots: all retained questions, including structural zeros. Bar: IQR; white tick: median. "
            "KDE uses a fixed pooled bandwidth within each facet and reflection at zero; "
            "each cloud is height-normalized (not sample size). Constant/singleton groups show dots and IQR only. "
            + ("log1p changes plotted positions only; summary statistics and ticks retain original units. "
               if transformed else "Summary statistics retain original units. "))
    save_outputs(fig, args, STEM, cfg, note, summary, audit=audit)
    plt.close(fig)
    return summary


if __name__ == "__main__":
    main()
