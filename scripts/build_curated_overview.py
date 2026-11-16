"""Show one representative per visual family without rewriting source images."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
sys.path.insert(0,str(ROOT))
from scripts.family_support import load_families
from scripts.render_readme import index_entries
import matplotlib
from PIL import Image,ImageDraw,ImageFont,ImageOps

# Use bundled Latin fonts so the overview renders on a clean checkout without
# depending on a host's Chinese font installation. The README uses full titles.
PREVIEW_LABELS={
    'F01':'Results table',
    'F02':'Paired point comparisons',
    'F03':'Effect estimates and intervals',
    'F04':'Raincloud distributions',
    'F05':'Two-objective scatter plots',
    'F06':'Trend curves',
    'F07':'Matrix heatmaps',
    'F08':'Bars and composition',
    'F09':'Tool trajectories',
    'F10':'Method ranks and statistical tests',
    'F11':'Set intersections',
}

def validate_existing():
    """Check the approved sheet and its inputs without platform-dependent redraw."""
    receipt=json.loads((ROOT/'curation/2026-11-16-families/changes.json').read_text())
    entries={entry['code']:entry for entry in index_entries()}
    expected=[]
    for family in load_families(set(entries)):
        entry=entries[family['representative']]
        expected.append({'family_id':family['id'],'title':family['title'],
                         'code':family['representative'],'image':entry['image'],
                         'sha256':hashlib.sha256((ROOT/entry['image']).read_bytes()).hexdigest(),
                         'members':family['members']})
    if receipt['representatives']!=expected:
        raise ValueError('Overview inputs changed; rebuild and review the overview before recording a new receipt.')
    record=receipt['rebuilt_contact_sheets'][0]
    if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()!=record['sha256_after']:
        raise ValueError('Checked-in overview differs from its approved preservation receipt.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-existing',action='store_true')
    args=parser.parse_args()
    if args.check_existing:
        validate_existing()
        print('Verified approved overview and representative inputs without redrawing.')
        return
    entries=index_entries();by_code={item['code']:item for item in entries}
    families=load_families(set(by_code))
    cols=3;cell_w=720;cell_h=430;rows=(len(families)+cols-1)//cols
    sheet=Image.new('RGB',(cols*cell_w,110+rows*cell_h),'#EFF3F5');draw=ImageDraw.Draw(sheet)
    fontdir=Path(matplotlib.get_data_path())/'fonts/ttf'
    label=ImageFont.truetype(str(fontdir/'DejaVuSans.ttf'),20);small=ImageFont.truetype(str(fontdir/'DejaVuSans.ttf'),16);bold=ImageFont.truetype(str(fontdir/'DejaVuSans-Bold.ttf'),28)
    draw.text((24,17),f'Rerank research | {len(families)} chart families',font=bold,fill='#243746')
    draw.text((24,59),f'One preview per visual encoding; {len(entries)} examples retained as use cases and code variants.',font=small,fill='#657985')
    for n,family in enumerate(families):
        code=family['representative'];item=by_code[code]
        title=family.get('preview_label') or PREVIEW_LABELS[family['id']]
        x=(n%cols)*cell_w+12;y=(n//cols)*cell_h+110
        draw.rounded_rectangle((x,y,x+696,y+408),radius=10,fill='white')
        with Image.open(ROOT/item['image'])as im:thumb=ImageOps.contain(im.convert('RGB'),(674,324))
        sheet.paste(thumb,(x+(696-thumb.width)//2,y+8+(324-thumb.height)//2))
        draw.text((x+12,y+345),f'{n+1:02d}  {title}',font=label,fill='#243746')
        count=len(family['members'])
        draw.text((x+12,y+378),f"Representative {code}  |  {count} source example{'s' if count!=1 else ''}",font=small,fill='#657985')
    folder=ROOT/'docs';folder.mkdir(exist_ok=True);sheet.save(folder/'gallery_overview.png',optimize=True)

if __name__=='__main__':main()
