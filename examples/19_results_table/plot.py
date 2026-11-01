"""Minimal-rule results table, generated as a reproducible vector figure."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('19_results_table');setup();data=rows(args,'questions.csv');calls=rows(args,'tool_calls.csv');fig,ax=plt.subplots(figsize=(11.5,4.2));ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
    xs=[.02,.32,.55,.74,.92];headers=['Method','Accuracy [95% CI]','Input / question','Calls / question','Wall time']
    ax.text(.02,.93,'Main comparison under a shared evaluation protocol',fontsize=14,weight='bold')
    for x,label in zip(xs,headers):ax.text(x,.75,label,ha='left'if x==.02 else 'center',fontsize=10,weight='bold')
    for y in [.84,.68,.10]:ax.hlines(y,.02,.99,color=INK,lw=1.1 if y!=.68 else .6)
    scores=[numbers(subset(data,m),'correct').mean()for m in METHODS]
    for i,m in enumerate(METHODS):
        rr=subset(data,m);n=len(rr);s=sum(int(r['correct'])for r in rr);lo,hi=wilson_interval(s,n);y=.58-i*.14
        vals=[m,f'{100*s/n:.1f}% [{100*lo:.1f}, {100*hi:.1f}]',f"{numbers(rr,'main_input_tokens').mean()/1e6:.2f} M",f"{numbers(subset(calls,m),'calls').sum()/n:.1f}",f"{np.median(numbers(rr,'wall_seconds'))/60:.1f} min"]
        if i==np.argmax(scores):ax.axhspan(y-.055,y+.07,xmin=.015,xmax=.995,color='#E7F3ED',zorder=-1)
        for j,(x,value)in enumerate(zip(xs,vals)):ax.text(x,y,value,ha='left'if j==0 else 'center',va='center',fontsize=10,color=COLORS[m]if j==0 else INK,weight='bold'if j==1 and i==np.argmax(scores)else 'normal')
    fig.subplots_adjust(left=.02,right=.98,top=.98,bottom=.13);save(fig,args,'19_results_table','Wilson intervals; solver input mean; explicit calls mean; wall time median')

if __name__=='__main__':main()
