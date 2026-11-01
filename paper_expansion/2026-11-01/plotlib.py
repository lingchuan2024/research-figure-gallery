"""Only the new paper-derived figures; does not import or write old assets."""
from pathlib import Path
import argparse
import csv
import os

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(REPO/'.cache/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(REPO/'.cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

INK='#243746'
BLUE='#4C78A8'
GREEN='#009E73'
ORANGE='#D99442'
GRAY='#9DAAB3'

def setup():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#9AA9B2','axes.labelcolor':INK,'text.color':INK,'xtick.color':INK,'ytick.color':INK,'axes.axisbelow':True,'grid.color':'#E8EEF1','grid.linewidth':.7,'legend.frameon':False,'svg.fonttype':'none','svg.hashsalt':'paper-expansion-2026-11-01','figure.facecolor':'white','axes.facecolor':'white','savefig.dpi':190})

def options(identifier):
    p=argparse.ArgumentParser(description=identifier+' — published numeric data, original redraw')
    p.add_argument('--data-dir',type=Path,default=HERE/'data')
    p.add_argument('--output-dir',type=Path,default=HERE/'figures')
    p.add_argument('--formats',nargs='+',choices=['png','svg','pdf'],default=['png','svg'])
    return p.parse_args()

def read(args,name):
    with (args.data_dir/name).open(newline='',encoding='utf-8')as f:return list(csv.DictReader(f))

def save(fig,args,identifier,citation):
    fig.text(.5,.016,'PUBLISHED DATA REDRAW | '+citation,ha='center',va='bottom',fontsize=8,color='#657985')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    for fmt in args.formats:
        meta={'Date':None}if fmt=='svg'else({'CreationDate':None,'ModDate':None}if fmt=='pdf'else{'Software':'research-figure-gallery'})
        fig.savefig(args.output_dir/(identifier+'.'+fmt),dpi=190,bbox_inches='tight',metadata=meta,facecolor='white')
    plt.close(fig)
