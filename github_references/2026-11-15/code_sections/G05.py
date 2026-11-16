# G05: upstream example code excerpt — not executed locally.
# Source: https://github.com/DingWB/PyComplexHeatmap/blob/2db32554c62c99b7e1823f5b2059a8b341ad0a9b/notebooks/clustermap.ipynb
# Local snapshot: sources/efficiency/clustermap.ipynb
# Extraction: zero-based cells 0 (1–16), 2 (1–15), 7 (1–27)
# Adaptations: commented %matplotlib inline; added explicit import pandas as pd absent from saved cell 0; plotting and random-data code unchanged
# This file is provided for offline reading; no original-image reproduction is claimed.
#
# Upstream license retained below:
# MIT License
#
# Copyright (c) 2023 Wubin Ding
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

# Notebook cell 0: imports and display settings
import os,sys
# %matplotlib inline  # Notebook-only magic; commented for Python syntax.
import matplotlib.pylab as plt
import pickle
import numpy as np
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi']=300
plt.rcParams['font.family']='sans serif'
plt.rcParams['font.sans-serif']='Arial'
plt.rcParams['pdf.fonttype']=42
# sys.path.append(os.path.expanduser("~/Projects/Github/PyComplexHeatmap/"))
from PyComplexHeatmap import (
    ClusterMapPlotter,HeatmapAnnotation,anno_simple,anno_scatterplot,anno_lineplot,anno_barplot,
    anno_label,anno_boxplot,anno_img,
)
# plt.rcParams

# Extraction addition: cell 2 uses pd, but saved cell 0 does not import it.
import pandas as pd

# Notebook cell 2, lines 1–15: complete random-data initialization
#Generate example dataset (random)
df = pd.DataFrame(['AAAA1'] * 5 + ['BBBBB2'] * 5, columns=['AB'])
df['CD'] = ['C'] * 3 + ['D'] * 3 + ['G'] * 4
df['EF'] = ['E'] * 6 + ['F'] * 2 + ['H'] * 2
df['F'] = np.random.normal(0, 1, 10)
df.index = ['sample' + str(i) for i in range(1, df.shape[0] + 1)]
df_box = pd.DataFrame(np.random.randn(10, 4), columns=['Gene' + str(i) for i in range(1, 5)])
df_box.index = ['sample' + str(i) for i in range(1, df_box.shape[0] + 1)]
df_bar = pd.DataFrame(np.random.uniform(0, 10, (10, 2)), columns=['TMB1', 'TMB2'])
df_bar.index = ['sample' + str(i) for i in range(1, df_box.shape[0] + 1)]
df_scatter = pd.DataFrame(np.random.uniform(0, 10, 10), columns=['Scatter'])
df_scatter.index = ['sample' + str(i) for i in range(1, df_box.shape[0] + 1)]
df_heatmap = pd.DataFrame(np.random.randn(30, 10), columns=['sample' + str(i) for i in range(1, 11)])
df_heatmap.index = ["Fea" + str(i) for i in range(1, df_heatmap.shape[0] + 1)]
df_heatmap.iloc[1, 2] = np.nan

# Notebook cell 7: the selected original figure
#Annotate the rows with average > 0.3
df_rows = df_heatmap.apply(lambda x:x.name if x.mean() > 0.3 else None,axis=1)
df_rows.name='Selected'

row_ha = HeatmapAnnotation(
            Avg=anno_simple(df_heatmap.mean(axis=1).apply(lambda x:round(x,2)),
                       cmap='jet'), #add_text=True,,text_kws={'rotation':0,'fontsize':10,'color':'black'}
            # Avg=anno_barplot(df_heatmap.mean(axis=1).apply(lambda x:round(x,2)),
            #                height=10,colors='orangered'),
            selected=anno_label(df_rows,colors='red',frac=0.3,rad=0),
            axis=0,verbose=0,label_kws={'rotation':0,'horizontalalignment':'left'})

col_ha = HeatmapAnnotation(
            label=anno_label(df.AB, merge=True,rotation=15),
            AB=anno_simple(df.AB,add_text=True,cmap='Set2'),axis=1,
            Exp=anno_boxplot(df_box, cmap='turbo'),
            verbose=0) #verbose=0 will turn off the log.

plt.figure(figsize=(5.5, 6))
cm = ClusterMapPlotter(
            data=df_heatmap, top_annotation=col_ha,right_annotation=row_ha,
            col_split=2,row_split=2, col_split_gap=0.5,row_split_gap=1,
            label='values',row_dendrogram=True,show_rownames=False,show_colnames=False,
            tree_kws={'row_cmap': 'Set1'},verbose=0,legend_vgap=7,
            #annot=True,linewidths=0.05,linecolor='gold',
            cmap='bwr')
plt.show()
