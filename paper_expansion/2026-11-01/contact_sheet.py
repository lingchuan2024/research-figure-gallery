"""Overview for the new published-data redraws, leaving assets/overview.png intact."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont,ImageOps
from plotlib import HERE
import matplotlib

def main():
    items=json.loads((HERE/'manifest.json').read_text());cols=2;cell_w=720;cell_h=385
    sheet=Image.new('RGB',(cols*cell_w,100+((len(items)+1)//2)*cell_h),'#EEF3F5');draw=ImageDraw.Draw(sheet)
    fontdir=Path(matplotlib.get_data_path())/'fonts/ttf'
    font=ImageFont.truetype(str(fontdir/'DejaVuSans.ttf'),18);bold=ImageFont.truetype(str(fontdir/'DejaVuSans-Bold.ttf'),26)
    draw.text((22,16),'New Deep Research figures | published numeric data',font=bold,fill='#243746')
    draw.text((22,57),'Original redraws with sources and code. Existing gallery images are unchanged.',font=font,fill='#657985')
    for n,item in enumerate(items):
        x=(n%2)*cell_w+12;y=(n//2)*cell_h+100
        draw.rounded_rectangle((x,y,x+696,y+365),radius=10,fill='white')
        with Image.open(HERE/item['image'])as im:thumb=ImageOps.contain(im.convert('RGB'),(674,320))
        sheet.paste(thumb,(x+(696-thumb.width)//2,y+8+(320-thumb.height)//2))
        draw.text((x+13,y+338),item['id'].replace('_',' '),font=font,fill='#243746')
    sheet.save(HERE/'new_figures_overview.png',optimize=True)

if __name__=='__main__':main()
