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
from scripts.catalog_support import load_catalog,expansion_manifests
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
    github_builder=ROOT/'github_references/2026-11-15/build_document.py'
    if github_builder.is_file():command([github_builder])
    template_folder=ROOT/'rerank_templates/2026-11-16'
    if (template_folder/'run_all.py').is_file():command([template_folder/'run_all.py'])
    if (template_folder/'verify.py').is_file():command([template_folder/'verify.py'])
    all_figures_builder=ROOT/'scripts/build_all_figures.py'
    if all_figures_builder.is_file():
        command([all_figures_builder])
        command(['scripts/verify_bundles.py'])
        command([all_figures_builder])
    readme(items)
    test=command(['-m','unittest','discover','-s','tests','-v']);match=re.search(r'Ran (\d+) tests?',test.stderr);test_count=int(match.group(1))if match else None
    paths=[p for p in ROOT.rglob('*')if p.is_file() and not any(s in {'.git','.cache','__pycache__','dist','.venv'}for s in p.relative_to(ROOT).parts)and p.name not in {'verification.json','.DS_Store'}]
    verification={'status':'passed','examples':len(items),'unit_tests':test_count,'image_formats':['png','svg'],'python':platform.python_version(),'dependencies':{'matplotlib':matplotlib.__version__,'numpy':numpy.__version__,'Pillow':PIL.__version__},'checks':['unit tests','all manifest code/data links exist','all example PNG/SVG exist','PNG dimensions and nonconstant pixels'],'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(paths)}}
    additions=[f for path in expansion_manifests()for f in json.loads(path.read_text())]
    verification['paper_redraws']=len(additions);verification['total_figures']=len(items)+len(additions)
    catalog=load_catalog();verification['selected_figures']=len(catalog['selected']);verification['supplement_figures']=len(catalog['supplement'])
    verification['validation_scope']='Rendering, source records, data contracts, README uniqueness and existing-image integrity; not empirical validation of our method'
    if github_builder.is_file():
        github_manifest=json.loads((github_builder.parent/'manifest.json').read_text())
        verification['separate_github_reference_figures']=github_manifest['count']
        verification['checks'].append('GitHub original-image SHA256 and Git blob hashes; separate reference document generated')
    if (template_folder/'verification.json').is_file():
        template_checks=json.loads((template_folder/'verification.json').read_text())
        verification['separate_rerank_templates']=template_checks['templates']
        verification['template_contract_tests']=template_checks['statistical_contract_tests']
        verification['checks'].append('Standalone rerank template contracts and rendered demo artifacts')
    if (ROOT/'dist/all_figures_manifest.json').is_file():
        all_figures_manifest=json.loads((ROOT/'dist/all_figures_manifest.json').read_text())
        verification['single_file_collection_figures']=all_figures_manifest['figures']
        verification['single_file_collection_code_sections']=all_figures_manifest.get('code_sections',0)
        verification['checks'].append('Single-file collection contains unchanged PNG bytes and an embedded verified template ZIP')
    if (ROOT/'dist/figure_code_manifest.json').is_file():
        code_entries=json.loads((ROOT/'dist/figure_code_manifest.json').read_text())['entries']
        verification['independently_run_figure_bundles']=sum(e['execution_status']=='local_bundle_executed' for e in code_entries)
        verification['upstream_source_reference_bundles']=sum(e['execution_status']=='upstream_not_executed' for e in code_entries)
    (ROOT/'dist/verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
    command(['scripts/package_release.py'])
    print(f"Verified {len(catalog['selected'])} selected figures, {len(catalog['supplement'])} supplements and {test_count} tests; release files are in dist/.")

if __name__=='__main__':main()
