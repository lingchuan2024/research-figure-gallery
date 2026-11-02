"""Create a new unified contact sheet without rewriting existing images."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gallerylib import ROOT
from scripts.catalog_support import selected_entries
import matplotlib
from PIL import Image,ImageDraw,ImageFont,ImageOps

def main():
    items=selected_entries();cols=3;cell_w=720;cell_h=380;rows=(len(items)+cols-1)//cols
    sheet=Image.new('RGB',(cols*cell_w,100+rows*cell_h),'#EFF3F5');draw=ImageDraw.Draw(sheet)
    fontdir=Path(matplotlib.get_data_path())/'fonts/ttf'
    label=ImageFont.truetype(str(fontdir/'DejaVuSans.ttf'),19);small=ImageFont.truetype(str(fontdir/'DejaVuSans.ttf'),16);bold=ImageFont.truetype(str(fontdir/'DejaVuSans-Bold.ttf'),28)
    draw.text((24,17),f'Agentic Search | {len(items)} selected figures',font=bold,fill='#243746')
    draw.text((24,59),'Organized by experiment purpose. Paper data and synthetic templates are labeled separately.',font=small,fill='#657985')
    for n,item in enumerate(items):
        x=(n%cols)*cell_w+12;y=(n//cols)*cell_h+100
        draw.rounded_rectangle((x,y,x+696,y+359),radius=10,fill='white')
        with Image.open(ROOT/item['image'])as im:thumb=ImageOps.contain(im.convert('RGB'),(674,310))
        sheet.paste(thumb,(x+(696-thumb.width)//2,y+8+(310-thumb.height)//2))
        draw.text((x+12,y+330),f"{item['number']:02d}  {item['preview_label']}",font=label,fill='#243746')
        origin='PAPER DATA'if item['origin']=='paper'else'TEMPLATE'
        draw.text((x+684-draw.textlength(origin,font=small),y+331),origin,font=small,fill='#32856F'if item['origin']=='paper'else'#6B8191')
    folder=ROOT/'docs';folder.mkdir(exist_ok=True);sheet.save(folder/'gallery_overview.png',optimize=True)

if __name__=='__main__':main()
