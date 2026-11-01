"""A fictional case study: actions, evidence and completion on one axis."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *
from matplotlib.lines import Line2D

def main():
    args=arguments('16_trajectory_timeline');setup();data=rows(args,'timeline.csv');tools=TOOLS+['answer'];palette={**TOOL_COLORS,'answer':'#009E73'}
    fig,axs=plt.subplots(2,1,figsize=(9.5,6),sharex=True,gridspec_kw={'hspace':.42})
    for ax,m in zip(axs,['Baseline','Agent rerank']):
        rr=sorted(subset(data,m),key=lambda r:int(r['turn']));x=numbers(rr,'turn');y=[tools.index(r['tool'])for r in rr]
        ax.plot(x,y,color='#D0DADF',lw=1.3,zorder=0)
        for r,xx,yy in zip(rr,x,y):
            ax.scatter(xx,yy,s=90,color=palette[r['tool']],edgecolors='white',linewidths=1)
            if int(r['evidence']):ax.scatter(xx,yy,s=210,marker='*',facecolor='#F2C25B',edgecolor=INK,linewidth=.6,zorder=4)
        ax.set(yticks=range(5),yticklabels=tools,title=m,ylim=(-.65,4.65));ax.grid(axis='x');ax.invert_yaxis()
    axs[1].set(xlabel='Model turn',xticks=np.arange(1,21,2),xlim=(0,20));axs[0].legend(handles=[Line2D([],[],marker='*',color='#F2C25B',markeredgecolor=INK,linestyle='',markersize=12,label='Answer-bearing evidence observed')],loc='upper right',fontsize=8)
    fig.subplots_adjust(left=.10,right=.98,bottom=.15,top=.92)
    save(fig,args,'16_trajectory_timeline','Fictional DEMO-CASE; an illustrative trace, not a representative real case')

if __name__=='__main__':main()
