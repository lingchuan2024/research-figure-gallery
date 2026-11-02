"""Render the checked-in examples and regenerate the usage-oriented README."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import hashlib
import json
import platform
import re
import subprocess
from gallerylib import ROOT
from scripts.catalog_support import load_catalog
from scripts.render_readme import write_documents
import matplotlib
import numpy
import PIL
from PIL import Image

def command(argv):
    result=subprocess.run([sys.executable,*map(str,argv)],cwd=ROOT,text=True,capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {argv}\n{result.stdout}\n{result.stderr}")
    return result

def readme(items):
    # Source inventory remains unchanged; editorial selection has one renderer.
    write_documents()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--only',nargs='+');p.add_argument('--keep-existing-images',action='store_true',help='Validate existing images and update docs without rendering or changing them');args=p.parse_args()
    items=json.loads((ROOT/'gallery.json').read_text());known={i['id']for i in items}
    if args.only and not set(args.only)<=known:p.error('Unknown example IDs: '+str(set(args.only)-known))
    if not args.keep_existing_images:
        for i in items:
            if args.only and i['id']not in args.only:continue
            command([i['script']]);print('Rendered '+i['id'],flush=True)
    for i in items:
        for key in ['image','vector']:
            if not (ROOT/i[key]).is_file():raise FileNotFoundError(i[key])
        with Image.open(ROOT/i['image'])as im:
            rgb=im.convert('RGB');extrema=rgb.getextrema()
            if min(im.size)<300 or all(lo==hi for lo,hi in extrema):raise ValueError('Empty or undersized image: '+i['image'])
    if not args.keep_existing_images:command(['scripts/contact_sheet.py'])
    command(['scripts/build_curated_overview.py'])
    readme(items)
    test=command(['-m','unittest','discover','-s','tests','-v']);match=re.search(r'Ran (\d+) tests?',test.stderr);test_count=int(match.group(1))if match else None
    paths=[p for p in ROOT.rglob('*')if p.is_file() and not any(s in {'.git','.cache','__pycache__','dist','.venv'}for s in p.relative_to(ROOT).parts)and p.name!='verification.json']
    verification={'status':'passed','examples':len(items),'unit_tests':test_count,'image_formats':['png','svg'],'python':platform.python_version(),'dependencies':{'matplotlib':matplotlib.__version__,'numpy':numpy.__version__,'Pillow':PIL.__version__},'checks':['unit tests','all manifest code/data links exist','all example PNG/SVG exist','PNG dimensions and nonconstant pixels'],'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(paths)}}
    additions=[f for path in (ROOT/'paper_expansion').glob('*/manifest.json')for f in json.loads(path.read_text())]
    verification['paper_redraws']=len(additions);verification['total_figures']=len(items)+len(additions)
    catalog=load_catalog();verification['selected_figures']=len(catalog['selected']);verification['supplement_figures']=len(catalog['supplement'])
    verification['validation_scope']='Rendering, source records, data contracts, README uniqueness and existing-image integrity; not empirical validation of our method'
    (ROOT/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n');print(f"Verified {len(catalog['selected'])} selected figures, {len(catalog['supplement'])} supplements and {test_count} tests; README updated.")

if __name__=='__main__':main()
