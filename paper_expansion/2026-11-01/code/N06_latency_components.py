"""FS-Researcher v2 Table 15; separate I/O scale prevents invisible segments."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plotlib import *

def main():
    args=options('N06_latency_components');setup();data=read(args,'fs_latency.csv');stages=['Context building','Report writing'];idx={(r['stage'],r['component']):float(r['seconds'])for r in data}
    fig,(ax,io)=plt.subplots(1,2,figsize=(11.1,4.2),sharey=True,gridspec_kw={'width_ratios':[3,1],'wspace':.17});y=np.arange(2);left=np.zeros(2)
    for comp,color in [('LLM',BLUE),('Web tools',ORANGE)]:
        vals=np.array([idx[s,comp]for s in stages]);ax.barh(y,vals,left=left,color=color,height=.50,label=comp)
        for i,v in enumerate(vals):
            if v>0:ax.text(left[i]+v/2,i,f'{v:.2f} s',ha='center',va='center',fontsize=10,color='white')
        left+=vals
    vals=np.array([idx[s,'File I/O']*1000 for s in stages]);io.hlines(y,0,vals,color='#CFDCD8',lw=3);io.scatter(vals,y,color=GREEN,s=50)
    for i,v in enumerate(vals):io.text(v+9,i,f'{v:.0f} ms',va='center',fontsize=10)
    ax.set(yticks=y,yticklabels=stages,xlim=(0,510),ylim=(-.55,1.55),xlabel='Average wall-clock time (seconds)',title='Inference and browsing');io.set(xlim=(0,265),xticks=[0,100,200],xlabel='Milliseconds',title='File I/O (separate scale)');ax.invert_yaxis();io.tick_params(axis='y',left=False)
    ax.grid(axis='x');io.grid(axis='x');ax.legend(ncol=2,loc='upper center',bbox_to_anchor=(.5,-.25),fontsize=9)
    fig.suptitle('Attribute latency to stages and components',fontsize=14);fig.subplots_adjust(left=.15,right=.98,top=.78,bottom=.32)
    save(fig,args,'N06_latency_components','FS-Researcher (2602.01566v2), Table 15; means over 10 sampled queries; no tail-latency estimates available')

if __name__=='__main__':main()
