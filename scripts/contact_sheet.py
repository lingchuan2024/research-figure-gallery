"""Create the README overview from the same manifest as the individual figures."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
from gallerylib import ROOT
import matplotlib
from PIL import Image, ImageDraw, ImageFont, ImageOps

def main():
    items=json.loads((ROOT/'gallery.json').read_text());cols=2;width=1200;cell_h=365;rows=(len(items)+cols-1)//cols
    sheet=Image.new('RGB',(width,rows*cell_h+100),'#F0F4F6');draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(str(Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf'),17)
    large=ImageFont.truetype(str(Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans-Bold.ttf'),25)
    draw.text((24,18),f'Research Figure Gallery | {len(items)} curated examples',fill='#243746',font=large)
    draw.text((24,57),'All quantitative examples use synthetic data.',fill='#657985',font=font)
    for n,item in enumerate(items):
        x=(n%cols)*600+12;y=(n//cols)*cell_h+100
        draw.rounded_rectangle((x,y,x+576,y+343),radius=9,fill='white')
        with Image.open(ROOT/item['image'])as im:thumb=ImageOps.contain(im.convert('RGB'),(552,300))
        sheet.paste(thumb,(x+(576-thumb.width)//2,y+8+(300-thumb.height)//2))
        draw.text((x+12,y+317),item['id'].replace('_',' '),font=font,fill='#243746')
    (ROOT/'assets').mkdir(exist_ok=True);sheet.save(ROOT/'assets/overview.png',optimize=True)

if __name__=='__main__':main()
