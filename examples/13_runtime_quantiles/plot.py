"""Show latency tails without hiding capped runs."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('13_runtime_quantiles');setup();data=rows(args,'questions.csv')
    fig,ax=plt.subplots(figsize=(9,4.8));x=np.arange(4);width=.18
    for j,(q,color) in enumerate(zip([.25,.50,.75,.95],['#D8E4EC','#9FBDC9','#5689A7','#204A66'])):
        values=[np.quantile(numbers(subset(data,m),'wall_seconds')/60,q) for m in METHODS]
        ax.bar(x+(j-1.5)*width,values,width,color=color,label=f'P{int(q*100)}')
    for i,m in enumerate(METHODS):
        rr=subset(data,m);cap=sum(float(r['wall_seconds'])>=3600 for r in rr)/len(rr)*100
        ax.text(i,63,f'60-min cap: {cap:.0f}%',ha='center',fontsize=8,color=COLORS[m])
    ax.axhline(60,color='#A5B3BC',ls=':',lw=1);ax.set(xticks=x,xticklabels=METHODS,ylabel='Wall time (minutes)',title='Latency distribution: median and tail',ylim=(0,69));ax.legend(ncol=4,loc='upper center',bbox_to_anchor=(.5,-.12));ax.grid(axis='y')
    fig.tight_layout(rect=(0,.10,1,1));save(fig,args,'13_runtime_quantiles','All runs included; capped times do not estimate uncensored completion time')

if __name__=='__main__':main()
