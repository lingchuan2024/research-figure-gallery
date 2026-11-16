# G06: upstream example code excerpt — not executed locally.
# Source: https://github.com/tommyod/paretoset/blob/6f2803057085a696cbe10118ca3164d993cee175/scripts/examples.py
# Local snapshot: sources/efficiency/paretoset_examples.py
# Extraction: lines 1–2 and 103–153 (EXAMPLE 3: OPTIMIZATION)
# Adaptations: Examples 1 and 2 omitted; upstream PLOT=False changed to True only to enable plotting; numeric and plotting statements unchanged
# This file is provided for offline reading; no original-image reproduction is claimed.
#
# Upstream license retained below:
# MIT License
#
# Copyright (c) 2018 Tommy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Extraction adaptation: upstream PLOT=False is changed to True so this selected example renders.
# Only the plotting switch changed; random values and plotting statements are unchanged.
if __name__ == "__main__":
    PLOT = True  # Upstream: False. Enabled only for this standalone selected example.

    # ==========================================================================================
    # =============================== EXAMPLE 3: OPTIMIZATION ==================================
    # ==========================================================================================

    from paretoset import paretoset
    import numpy as np
    from collections import namedtuple

    np.random.seed(2)

    # Create Solution objects holding the problem solution and objective values
    Solution = namedtuple("Solution", ["solution", "objective_values"])
    solutions = [Solution(solution=object, objective_values=np.random.randn(2)) for _ in range(999)]

    # Create an array of shape (solutions, objectives) and compute the non-dominated set
    objective_values_array = np.vstack([s.objective_values for s in solutions])
    mask = paretoset(objective_values_array, sense=["min", "max"])

    # Filter the list of solutions, keeping only the non-dominated solutions
    efficient_solutions = [solution for (solution, m) in zip(solutions, mask) if m]

    # ==================================================
    if PLOT:
        import matplotlib.pyplot as plt

        plt.figure(figsize=(6, 2.5))

        plt.title("Objective value space and the Pareto set (efficient solutions)")

        plt.scatter(
            objective_values_array[:, 0], objective_values_array[:, 1], zorder=10, label="Solutions", s=10, alpha=0.8
        )

        plt.scatter(
            objective_values_array[mask, 0],
            objective_values_array[mask, 1],
            zorder=5,
            label="Efficient solutions",
            s=50,
            alpha=1,
        )

        plt.legend(loc="upper right").set_zorder(50)
        plt.xlabel("Objective 1 (min.)")
        plt.ylabel("Objective 2 (max.)")
        plt.xticks(fontsize=0)
        plt.yticks(fontsize=0)
        plt.grid(True, alpha=0.5, ls="--", zorder=0)
        plt.tight_layout()
        plt.savefig("example_optimization.png", dpi=100)
        plt.show()
