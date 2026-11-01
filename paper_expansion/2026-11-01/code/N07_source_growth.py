"""FS-Researcher v2 Tables 8 and 10: compare aggregate budgets, not individual-query novelty."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    args=options('N07_source_growth');setup();data=read(args,'fs_scaling.csv');data.sort(key=lambda r:int(r['rounds']));rounds=np.array([int(r['rounds'])for r in data]);search=np.array([float(r['search_calls'])for r in data]);readcalls=np.array([float(r['read_calls'])for r in data]);urls=np.array([float(r['unique_urls'])for r in data])
    fig,(ax,ratio)=plt.subplots(1,2,figsize=(11,4.8),gridspec_kw={'width_ratios':[1.5,1],'wspace':.30})
    for values,label,color in [(search,'Search calls',BLUE),(readcalls,'Page reads',ORANGE),(urls,'Unique URLs',GREEN)]:ax.plot(rounds,values,'o-',label=label,color=color,ms=6,lw=2)
    ax.set(xlabel='Context-building rounds',ylabel='Mean count per query',xticks=rounds,ylim=(0,75),title='More search does not scale sources one-for-one');ax.grid(axis='y');ax.legend(fontsize=9,loc='upper left')
    values=np.diff(urls)/np.diff(search);y=np.arange(2);ratio.hlines(y,0,values,color='#BBDDCF',lw=4);ratio.scatter(values,y,color=GREEN,s=60,zorder=3)
    for i,v in enumerate(values):ratio.text(v+.035,i,f'{v:.2f}',va='center',fontsize=11)
    ratio.set(yticks=y,yticklabels=['3 → 5 rounds','5 → 10 rounds'],xlim=(0,1.40),ylim=(-.55,1.55),xlabel='Δ unique URLs / Δ search calls',title='Ratio of aggregate differences');ratio.invert_yaxis();ratio.grid(axis='x')
    fig.subplots_adjust(left=.08,right=.98,top=.83,bottom=.21)
    save(fig,args,'N07_source_growth','FS-Researcher (2602.01566v2), Tables 8 + 10; n=10 queries; ratio of mean differences, not mean per-query novelty')

if __name__=='__main__':main()
