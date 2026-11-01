"""Keep answer outcomes and termination reasons in separate denominators."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *

def main():
    args=arguments('10_outcomes_and_stops');setup();data=rows(args,'questions.csv')
    fig,axs=plt.subplots(1,2,figsize=(10.8,4),sharey=True)
    panels=[('outcome',['Correct','Wrong answer','Abstain','No final'],['#009E73','#CC7964','#E9BE6A','#BEC8CD'],'Answer quality'),('stop_reason',['Completed','Turn limit','Timeout'],['#6C99B8','#E9BE6A','#CC7964'],'Why execution stopped')]
    for ax,(key,labels,colors,title) in zip(axs,panels):
        left=np.zeros(len(METHODS))
        for label,color in zip(labels,colors):
            values=np.array([sum(r[key]==label for r in subset(data,m))/len(subset(data,m))*100 for m in METHODS])
            ax.barh(METHODS,values,left=left,color=color,height=.6,label=label)
            for i,v in enumerate(values):
                if v>=7:ax.text(left[i]+v/2,i,f'{v:.0f}%',ha='center',va='center',fontsize=8)
            left+=values
        ax.set(xlim=(0,100),xlabel='Questions (%)',title=title);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=2,fontsize=8)
    axs[0].invert_yaxis();fig.subplots_adjust(left=.13,right=.98,bottom=.27,wspace=.15,top=.87)
    save(fig,args,'10_outcomes_and_stops','Completed does not imply a correct answer')

if __name__=='__main__':main()
