"""Half violin + quartiles + points, computed in log-token space."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('02_token_raincloud');setup();data=rows(args,'questions.csv')
    fig,ax=plt.subplots(figsize=(8.8,4.8));rng=np.random.default_rng(21);omitted=0
    for i,m in enumerate(METHODS):
        raw=numbers(subset(data,m),'main_input_tokens');omitted+=int(np.sum(raw<=0));values=np.log10(raw[raw>0])
        if len(values)<2 or np.ptp(values)==0:raise ValueError('Violin needs at least two distinct positive values')
        part=ax.violinplot([values],positions=[i],widths=.7,showextrema=False)
        body=part['bodies'][0];vertices=body.get_paths()[0].vertices
        vertices[:,0]=np.maximum(vertices[:,0],i)
        body.set_facecolor(COLORS[m]);body.set_alpha(.35);body.set_edgecolor('none')
        ax.scatter(i-.12-rng.uniform(0,.15,len(values)),values,s=10,color=COLORS[m],alpha=.55,edgecolors='none')
        q1,med,q3=np.quantile(values,[.25,.5,.75])
        ax.vlines(i-.035,q1,q3,color=INK,lw=4);ax.scatter([i-.035],[med],s=23,color='white',edgecolors=INK,zorder=4)
    positive=numbers(data,'main_input_tokens');positive=positive[positive>0]
    ticks=np.arange(np.floor(np.log10(positive).min()),np.ceil(np.log10(positive).max())+.1)
    ax.set_yticks(ticks,[rf'$10^{{{int(t)}}}$'for t in ticks]);ax.set_ylabel('Solver input tokens / question (log scale)')
    ax.set_xticks(range(4),METHODS);ax.set_xlim(-.55,3.65);ax.grid(axis='y');ax.set_title('Typical volume, distribution shape, and individual questions')
    fig.tight_layout(rect=[0,.07,1,1]);save(fig,args,'02_token_raincloud',f'Each dot is one question; nonpositive values omitted: {omitted}')

if __name__=='__main__':main()
