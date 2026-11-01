"""Original vector diagram; no measured quantities or external artwork."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from gallerylib import *
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def main():
    args=arguments('18_method_overview');setup();fig,ax=plt.subplots(figsize=(12,5.8));ax.set(xlim=(0,12),ylim=(0,6));ax.axis('off')
    def box(x,y,w,text,color):
        ax.add_patch(FancyBboxPatch((x,y),w,.68,boxstyle='round,pad=0.08,rounding_size=0.1',facecolor=color,edgecolor='none'))
        ax.text(x+w/2,y+.34,text,ha='center',va='center',fontsize=9)
    def arrow(x1,y1,x2,y2,label=None,style='-'):
        ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=12,color='#82939D',lw=1.2,linestyle=style))
        if label:ax.text((x1+x2)/2,(y1+y2)/2+.15,label,ha='center',fontsize=8,color='#657985')
    ax.text(.1,5.65,'Where ranking decisions enter the agent workflow',fontsize=16,weight='bold')
    lanes=[(4.35,'Baseline','#EEF1F4'),(2.75,'Auto rerank','#FFF1D4'),(1.15,'Agent rerank','#DCF0E8')]
    for y,m,color in lanes:
        ax.text(.1,y+.34,m,fontsize=11,weight='bold',va='center',color=COLORS[m]);box(1.85,y,1.15,'Query',color);box(3.5,y,1.35,'Search',color)
        if m=='Baseline':box(5.4,y,1.8,'Original order',color)
        elif m=='Auto rerank':box(5.4,y,1.8,'Fixed reranking',color)
        else:box(5.4,y,1.8,'Optional rerank',color)
        box(7.8,y,1.65,'Read evidence',color);box(10.05,y,1.35,'Answer',color)
        for x1,x2 in [(3.05,3.45),(4.9,5.35),(7.25,7.75),(9.5,10)]:arrow(x1,y+.34,x2,y+.34)
    ax.text(6.3,2.38,'Every search; fixed query and scope',ha='center',fontsize=8,color='#94733C')
    ax.text(6.3,.64,'Choose when, query, candidate scope and snippet',ha='center',fontsize=8,color='#31755E')
    ax.text(.1,.05,'Controlled comparison: search and rerank return the same character budget (e.g. 100 chars).',fontsize=10)
    fig.subplots_adjust(left=.02,right=.98,bottom=.09,top=.98);save(fig,args,'18_method_overview','Illustrative workflow; adapt the boxes to the implemented system',concept=True)

if __name__=='__main__':main()
