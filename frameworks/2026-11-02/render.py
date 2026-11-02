"""Render framework specifications to PNG/SVG and an uncompressed editable draw.io file."""
from pathlib import Path
import argparse
import json
from html import escape
import os
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'.cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch,Polygon
from matplotlib.path import Path as MplPath

INK='#233747'
BLUE='#4C78A8'
ORANGE='#C78B43'

def options(identifier):
    p=argparse.ArgumentParser(description=identifier+' — structural framework illustration, not experimental results')
    p.add_argument('--data-dir',type=Path,default=HERE/'specs',help='Directory of editable structure/layout JSON files')
    p.add_argument('--output-dir',type=Path,default=HERE/'figures')
    p.add_argument('--formats',nargs='+',choices=['png','svg'],default=['png','svg'])
    return p.parse_args()

def export_drawio(spec,path):
    mxfile=ET.Element('mxfile',{'host':'app.diagrams.net','type':'device','version':'24.7.17'})
    diagram=ET.SubElement(mxfile,'diagram',{'id':spec['id'],'name':spec['title']})
    model=ET.SubElement(diagram,'mxGraphModel',{'dx':str(spec['width']),'dy':str(spec['height']),'grid':'1','gridSize':'10','page':'1','pageScale':'1','pageWidth':str(spec['width']),'pageHeight':str(spec['height'])})
    root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',{'id':'0'});ET.SubElement(root,'mxCell',{'id':'1','parent':'0'})
    # Diagram geometry uses pixels at 100 dpi; convert typographic points to pixels.
    def vertex(node):
        kind=node.get('kind','card');size=round(node.get('font',15)*100/72,2)
        style='rounded=1;arcSize=12;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacing=8;'
        if kind=='label':style='text;whiteSpace=wrap;html=1;align='+node.get('align','center')+';verticalAlign=middle;'
        if kind=='document':style+='shape=note;size=18;'
        if kind=='panel':style+='align=left;verticalAlign=top;spacingLeft=18;spacingTop=10;'
        fill=node.get('fill','#FFFFFF');stroke=node.get('stroke','#D2DDE3');color=node.get('color',INK)
        style+=f'fillColor={fill};strokeColor={stroke};fontColor={color};fontFamily=Helvetica;fontSize={size};'
        if kind=='label':style+='fillColor='+node.get('background','none')+';strokeColor=none;'
        if node.get('dashed'):style+='dashed=1;dashPattern=5 4;'
        title=escape(node.get('title','')).replace('\n','<br>')
        if node.get('body'):
            body=escape(node['body']).replace('\n','<br>');body_size=round(node.get('body_font',12)*100/72,2)
            value=f'<b>{title}</b><br><br><span style="font-size:{body_size}px;color:{node.get("body_color","#5C7280")}">{body}</span>'
        else:value=('<b>'+title+'</b>')if node.get('bold',kind!='label')else title
        cell=ET.SubElement(root,'mxCell',{'id':node['id'],'value':value,'style':style,'vertex':'1','parent':'1'})
        ET.SubElement(cell,'mxGeometry',{'x':str(node['x']),'y':str(node['y']),'width':str(node['w']),'height':str(node['h']),'as':'geometry'})
    # Panels below routes, cards and annotation backgrounds above routes.
    for node in spec['nodes']:
        if node.get('kind')=='panel':vertex(node)
    for n,edge in enumerate(spec['edges']):
        points=edge['points'];color=edge.get('color',BLUE);style=f'endArrow=block;endFill=1;strokeWidth=1.8;strokeColor={color};rounded=0;'
        if edge.get('dashed'):style+='dashed=1;dashPattern=5 4;'
        cell=ET.SubElement(root,'mxCell',{'id':'edge_'+str(n),'value':'','style':style,'edge':'1','parent':'1'})
        geometry=ET.SubElement(cell,'mxGeometry',{'relative':'1','as':'geometry'})
        ET.SubElement(geometry,'mxPoint',{'x':str(points[0][0]),'y':str(points[0][1]),'as':'sourcePoint'})
        ET.SubElement(geometry,'mxPoint',{'x':str(points[-1][0]),'y':str(points[-1][1]),'as':'targetPoint'})
        if len(points)>2:
            waypoints=ET.SubElement(geometry,'Array',{'as':'points'})
            for x,y in points[1:-1]:ET.SubElement(waypoints,'mxPoint',{'x':str(x),'y':str(y)})
    for node in spec['nodes']:
        if node.get('kind')!='panel':vertex(node)
    # Source and scope remain attached when the file is edited in diagrams.net.
    for identifier,text,x,y,w,h,size in [('heading',spec['title'],35,18,spec['width']-70,40,30.56),('subtitle',spec['subtitle'],35,65,spec['width']-70,30,14),('source_note',spec['footer'],35,spec['height']-36,spec['width']-70,24,10)]:
        cell=ET.SubElement(root,'mxCell',{'id':identifier,'value':text,'style':f'text;html=0;whiteSpace=wrap;fontSize={size};fontColor={INK};align=left;','vertex':'1','parent':'1'})
        ET.SubElement(cell,'mxGeometry',{'x':str(x),'y':str(y),'width':str(w),'height':str(h),'as':'geometry'})
    ET.indent(mxfile);ET.ElementTree(mxfile).write(path,encoding='utf-8',xml_declaration=True)

def render(identifier,args):
    spec=json.loads((args.data_dir/(identifier+'.json')).read_text());w,h=spec['width'],spec['height']
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','svg.hashsalt':'framework-gallery-2026-11-02','figure.facecolor':'white','savefig.dpi':180})
    fig=plt.figure(figsize=(w/100,h/100));ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,w),ylim=(h,0));ax.axis('off')
    text_artists=[]
    # Container panels below edges; foreground cards above them.
    for node in spec['nodes']:
        if node.get('kind')!='panel':continue
        ax.add_patch(FancyBboxPatch((node['x'],node['y']),node['w'],node['h'],boxstyle='round,pad=0,rounding_size=14',facecolor=node.get('fill','#F5F8FA'),edgecolor=node.get('stroke','#D2DDE3'),lw=1,zorder=0))
    for edge in spec['edges']:
        points=edge['points'];path=MplPath(points,[MplPath.MOVETO]+[MplPath.LINETO]*(len(points)-1))
        ax.add_patch(FancyArrowPatch(path=path,arrowstyle='-|>',mutation_scale=14,lw=1.6,color=edge.get('color',BLUE),linestyle=(0,(5,4))if edge.get('dashed')else '-',zorder=1))
    for node in spec['nodes']:
        x,y,nw,nh=node['x'],node['y'],node['w'],node['h'];kind=node.get('kind','card');fill=node.get('fill','#FFFFFF');color=node.get('color',INK)
        if kind not in {'label','panel'}:
            ax.add_patch(FancyBboxPatch((x,y),nw,nh,boxstyle='round,pad=0,rounding_size='+str(18 if kind=='pill'else 10),facecolor=fill,edgecolor=node.get('stroke','#BCCCD5'),lw=1.1,linestyle=(0,(5,4))if node.get('dashed')else '-',zorder=2))
            if kind=='document':
                ax.add_patch(Polygon([(x+nw-22,y),(x+nw,y+22),(x+nw-22,y+22)],closed=True,facecolor='#E9EFF2',edgecolor=node.get('stroke','#BCCCD5'),lw=.8,zorder=3))
        if kind=='panel':
            text_artists.append((node,ax.text(x+18,y+20,node.get('title',''),ha='left',va='center',fontsize=node.get('font',14),color=color,weight='bold',zorder=4)))
        elif kind=='label':
            align=node.get('align','center');xx=x if align=='left'else(x+nw if align=='right'else x+nw/2)
            background={'facecolor':node['background'],'edgecolor':'none','pad':2} if node.get('background') else None
            text_artists.append((node,ax.text(xx,y+nh/2,node.get('title',''),ha=align,va='center',fontsize=node.get('font',13),linespacing=1.35,color=color,weight='bold'if node.get('bold')else 'normal',bbox=background,zorder=5)))
        else:
            title=node.get('title','');body=node.get('body','');font=node.get('font',15)
            if body:
                text_artists.append((node,ax.text(x+nw/2,y+27,title,ha='center',va='center',fontsize=font,color=color,weight='bold',zorder=4)))
                text_artists.append((node,ax.text(x+nw/2,y+nh*.66,body,ha='center',va='center',fontsize=node.get('body_font',12),linespacing=1.35,color=node.get('body_color','#5C7280'),zorder=4)))
            else:text_artists.append((node,ax.text(x+nw/2,y+nh/2,title,ha='center',va='center',fontsize=font,linespacing=1.35,color=color,weight='bold'if node.get('bold',True)else 'normal',zorder=4)))
    ax.text(35,37,spec['title'],fontsize=22,weight='bold',color=INK,va='center')
    ax.text(35,78,spec['subtitle'],fontsize=12,color='#667D8A',va='center')
    ax.text(w/2,h-20,spec['footer'],fontsize=9,color='#667D8A',ha='center',va='center')
    # Verify actual text widths, so exported small labels do not overflow their blocks.
    fig.canvas.draw();renderer=fig.canvas.get_renderer();overflow=[]
    for node,artist in text_artists:
        if node.get('kind')=='panel':continue
        bounds=artist.get_window_extent(renderer=renderer).transformed(ax.transData.inverted());width=abs(bounds.x1-bounds.x0)
        if width>node['w']-8:overflow.append({'node':node['id'],'text':artist.get_text(),'width':round(width,1),'available':node['w']-8})
    if overflow:raise ValueError('Text overflows: '+json.dumps(overflow,ensure_ascii=False))
    args.output_dir.mkdir(parents=True,exist_ok=True)
    for fmt in args.formats:fig.savefig(args.output_dir/(identifier+'.'+fmt),dpi=180,metadata={'Date':None}if fmt=='svg'else{'Software':'research-figure-gallery'},facecolor='white')
    plt.close(fig);export_drawio(spec,args.output_dir/(identifier+'.drawio'))
    return spec
