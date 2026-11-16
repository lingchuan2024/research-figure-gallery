"""G04: Faceted raincloud plot, Figure P13

Extracted upstream example; NOT executed locally and NOT our experiment.
Source: https://github.com/RainCloudPlots/RainCloudPlots/blob/4ceeb06dc5bd5b9911e7147d1b0b452c4c2f9b1d/tutorial_python/raincloud_tutorial_python.ipynb
Commit: 4ceeb06dc5bd5b9911e7147d1b0b452c4c2f9b1d
License notice: MIT
Local license: ../sources/effectiveness/G04_faceted_raincloud_LICENSE.txt
See effectiveness.json for exact extraction and execution requirements.
"""

# Run from this code bundle's tutorial_python/ directory (or an upstream checkout).
# Bundled input: tutorial_python/simdat.csv (see support_files).
# This preserves the notebook's original figureP13.png save location.
# Therefore execution can replace that output in the bundle or upstream checkout.

# Upstream notebook cell 1 (zero-based index 0): imports and global plot style.
import pandas as pd
import seaborn as sns
import os
import matplotlib.pyplot as plt
#sns.set(style="darkgrid")
#sns.set(style="whitegrid")
#sns.set_style("white")
sns.set(style="whitegrid",font_scale=2)
import matplotlib.collections as clt


import ptitprince as pt

# Upstream notebook cell 4 (zero-based index 3): savefigs flag and output-directory setup.
savefigs = True
figs_dir = '../figs/tutorial_python'

if savefigs:
    # Make the figures folder if it doesn't yet exist
    if not os.path.isdir('../figs/tutorial_python'):
        os.makedirs('../figs/tutorial_python')

# Upstream notebook cell 7 (zero-based index 6): simdat.csv source dataframe.
df = pd.read_csv ("simdat.csv", sep= ",")
df.head()

# Upstream notebook cell 31 (zero-based index 30): FacetGrid + RainCloud + figureP13.png export.
# Rainclouds with FacetGrid
g = sns.FacetGrid(df, col = "gr2", height = 6)
g = g.map_dataframe(pt.RainCloud, x = "group", y = "score", data = df,
                    orient = "h")

g.fig.subplots_adjust(top=0.75)
g.fig.suptitle("Figure P13\n Using FacetGrid for More Complex Designs",  fontsize=26)
if savefigs:
    plt.savefig('../figs/tutorial_python/figureP13.png', bbox_inches='tight')

