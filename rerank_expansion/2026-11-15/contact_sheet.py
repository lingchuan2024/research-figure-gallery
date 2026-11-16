"""Compact visual index of the six reranking paper redraws."""
from pathlib import Path
import json
import os
HERE = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(HERE.parents[1] / '.cache/matplotlib'))
import matplotlib
from PIL import Image, ImageDraw, ImageFont, ImageOps

def main():
    entries = json.loads((HERE / 'manifest.json').read_text())
    width, height, columns = 1000, 650, 2
    sheet = Image.new('RGB', (columns * width, 110 + height * ((len(entries)+1)//2)), '#EDF2F4')
    draw = ImageDraw.Draw(sheet)
    fonts = Path(matplotlib.get_data_path()) / 'fonts/ttf'
    title = ImageFont.truetype(str(fonts / 'DejaVuSans-Bold.ttf'), 32)
    label = ImageFont.truetype(str(fonts / 'DejaVuSans.ttf'), 21)
    draw.text((30, 20), 'Reranking | 6 paper-based figure designs', font=title, fill='#203744')
    draw.text((30, 66), 'Exact published table values. Source, code and CSV accompany every figure.', font=label, fill='#607581')
    for i, entry in enumerate(entries):
        x, y = (i % columns)*width+12, (i//columns)*height+110
        draw.rounded_rectangle((x,y,x+width-24,y+height-18),radius=12,fill='white')
        with Image.open(HERE/entry['image']) as source:
            preview = ImageOps.contain(source.convert('RGB'), (width-44,height-72))
        sheet.paste(preview,(x+(width-24-preview.width)//2,y+12+(height-72-preview.height)//2))
        draw.text((x+18,y+height-52),entry['id'].split('_')[0]+'  '+entry['preview_label'],font=label,fill='#203744')
    sheet.save(HERE/'rerank_overview.png',optimize=True)

if __name__ == '__main__': main()
