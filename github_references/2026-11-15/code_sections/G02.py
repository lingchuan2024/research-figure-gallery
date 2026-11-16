"""G02: Multi-model grouped forest plot

Extracted upstream example; NOT executed locally and NOT our experiment.
Source: https://github.com/LSYS/forestplot/blob/b7591e3be7004f9962fd7cd7f91aa4cac91c45fc/README.md
Commit: b7591e3be7004f9962fd7cd7f91aa4cac91c45fc
License notice: MIT
Local license: ../sources/effectiveness/G02_multimodel_forest_LICENSE.txt
See effectiveness.json for exact extraction and execution requirements.
"""

# Run from this code bundle's examples/ directory (or an upstream checkout).
# Bundled upstream data: examples/data/sleep-mmodel.csv (see support_files).
# https://github.com/LSYS/forestplot/blob/b7591e3be7004f9962fd7cd7f91aa4cac91c45fc/examples/data/sleep-mmodel.csv
# Added missing import: the README refers to pd without importing it here.
import pandas as pd
# Added for the optional script export below.
import matplotlib.pyplot as plt

# Upstream README lines 267-272: import, full CSV, and model selection.
import forestplot as fp

df_mmodel = pd.read_csv("../examples/data/sleep-mmodel.csv").query(
    "model=='all' | model=='young kids'"
)
df_mmodel.head(3)

# Upstream README lines 282-307: code directly preceding multimodel.png.
fp.mforestplot(
    dataframe=df_mmodel,
    estimate="coef",
    ll="ll",
    hl="hl",
    varlabel="label",
    capitalize="capitalize",
    model_col="model",
    color_alt_rows=True,
    groupvar="group",
    table=True,
    rightannote=["var", "group"],
    right_annoteheaders=["Source", "Group"],
    xlabel="Coefficient (95% CI)",
    modellabels=["Have young kids", "Full sample"],
    xticks=[-1200, -600, 0, 600],
    mcolor=["#CC6677", "#4477AA"],
    # Additional kwargs for customizations
    **{
        "markersize": 30,
        # override default vertical offset between models (0.0 to 1.0)
        "offset": 0.35,  
        "xlinestyle": (0, (10, 5)),  # long dash for x-reference line
        "xlinecolor": ".8",  # gray color for x-reference line
    },
)

# Local script export; not part of the README example.
if __name__ == "__main__":
    plt.gcf().savefig("G02_extracted_example.png", dpi=150, bbox_inches="tight")
