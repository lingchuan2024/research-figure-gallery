"""G03: Critical difference diagram of simulated percentile ranks

Extracted upstream example; NOT executed locally and NOT our experiment.
Source: https://github.com/maximtrp/scikit-posthocs/blob/07e4c182b83314785eb879c3046de8ac5cf4febc/docs/source/tutorial.rst
Commit: 07e4c182b83314785eb879c3046de8ac5cf4febc
License notice: MIT
Local license: ../sources/effectiveness/G03_critical_difference_LICENSE.txt
See effectiveness.json for exact extraction and execution requirements.
"""

# Added explicit imports for the aliases used throughout the upstream tutorial.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scikit_posthocs as sp

# Tutorial lines 317-337; only RST indentation and >>> prompts removed.
rng = np.random.default_rng(1)
dict_data = {
    'model1': rng.normal(loc=0.2, scale=0.1, size=30),
    'model2': rng.normal(loc=0.2, scale=0.1, size=30),
    'model3': rng.normal(loc=0.4, scale=0.1, size=30),
    'model4': rng.normal(loc=0.5, scale=0.1, size=30),
    'model5': rng.normal(loc=0.7, scale=0.1, size=30),
    'model6': rng.normal(loc=0.7, scale=0.1, size=30),
    'model7': rng.normal(loc=0.8, scale=0.1, size=30),
    'model8': rng.normal(loc=0.9, scale=0.1, size=30),
}
data = (
  pd.DataFrame(dict_data)
  .rename_axis('cv_fold')
  .melt(
      var_name='estimator',
      value_name='score',
      ignore_index=False,
  )
  .reset_index()
)

# Tutorial line 358. Values are mean PERCENTILE ranks, not ranks 1..8.
# rank(pct=True) uses ascending ranks: larger values mean larger mock scores.
avg_rank = data.groupby('cv_fold').score.rank(pct=True).groupby(data.estimator).mean()

# Tutorial lines 378-379: omnibus test context.
import scipy.stats as ss
ss.friedmanchisquare(*dict_data.values())

# Tutorial lines 386-392: post-hoc matrix; upstream defaults preserved.
test_results = sp.posthoc_conover_friedman(
    data,
    melted=True,
    block_col='cv_fold',
    group_col='estimator',
    y_col='score',
)

# Tutorial lines 402-404, immediately followed by cd_diagram1.png.
plt.figure(figsize=(10, 2), dpi=100)
plt.title('Critical difference diagram of average score ranks')
sp.critical_difference_diagram(avg_rank, test_results)

# Local script export; not part of the tutorial block.
if __name__ == "__main__":
    plt.gcf().savefig("G03_extracted_example.png", dpi=150, bbox_inches="tight")
