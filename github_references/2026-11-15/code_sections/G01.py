"""G01: Paired Gardner-Altman mean-difference plot

Extracted upstream example; NOT executed locally and NOT our experiment.
Source: https://github.com/ACCLAB/DABEST-python/blob/ec6172724e0397bf0546863c76949d40da9c5457/nbs/tests/mpl_image_tests/test_03_plotting.py
Commit: ec6172724e0397bf0546863c76949d40da9c5457
License notice: Apache-2.0 in LICENSE; README badge says BSD-3-Clause-Clear (conflicting repository notices).
Local license: ../sources/effectiveness/G01_paired_estimation_LICENSE.txt
See effectiveness.json for exact extraction and execution requirements.
"""

# Necessary upstream imports: G01_source.py lines 2-5, 9, 11, 13.
import numpy as np
from scipy.stats import norm
import pandas as pd
import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from dabest._api import load

# Upstream lines 16-64: synthetic data generator and initialization.
def create_demo_dataset(seed=9999, N=20):
    import numpy as np
    import pandas as pd
    from scipy.stats import norm  # Used in generation of populations.

    np.random.seed(9999)  # Fix the seed so the results are replicable.
    # pop_size = 10000 # Size of each population.

    # Create samples
    c1 = norm.rvs(loc=3, scale=0.4, size=N)
    c2 = norm.rvs(loc=3.5, scale=0.75, size=N)
    c3 = norm.rvs(loc=3.25, scale=0.4, size=N)

    t1 = norm.rvs(loc=3.5, scale=0.5, size=N)
    t2 = norm.rvs(loc=2.5, scale=0.6, size=N)
    t3 = norm.rvs(loc=3, scale=0.75, size=N)
    t4 = norm.rvs(loc=3.5, scale=0.75, size=N)
    t5 = norm.rvs(loc=3.25, scale=0.4, size=N)
    t6 = norm.rvs(loc=3.25, scale=0.4, size=N)

    # Add a `gender` column for coloring the data.
    females = np.repeat("Female", N / 2).tolist()
    males = np.repeat("Male", N / 2).tolist()
    gender = females + males

    # Add an `id` column for paired data plotting.
    id_col = pd.Series(range(1, N + 1))

    # Combine samples and gender into a DataFrame.
    df = pd.DataFrame(
        {
            "Control 1": c1,
            "Test 1": t1,
            "Control 2": c2,
            "Test 2": t2,
            "Control 3": c3,
            "Test 3": t3,
            "Test 4": t4,
            "Test 5": t5,
            "Test 6": t6,
            "Gender": gender,
            "ID": id_col,
        }
    )

    return df


df = create_demo_dataset()

# Upstream lines 68-70: pair observations by ID, against the baseline.
two_groups_paired = load(
    df, idx=("Control 1", "Test 1"), paired="baseline", id_col="ID"
)

# Upstream lines 153-155: matching PNG-baseline test function.
# The pytest image-comparison decorator on line 152 is omitted.
def test_04_gardner_altman_paired_meandiff():
    plt.rcdefaults()
    return two_groups_paired.mean_diff.plot()

# Local script entry point, not part of the upstream test.
if __name__ == "__main__":
    fig = test_04_gardner_altman_paired_meandiff()
    fig.savefig("G01_extracted_example.png", dpi=150, bbox_inches="tight")
