"""Package portable sources, demo data and rendered examples; exclude caches/git."""
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    folder=ROOT/'dist';folder.mkdir(exist_ok=True);target=folder/'research-figure-gallery.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=8)as z:
        for p in sorted(ROOT.rglob('*')):
            rel=p.relative_to(ROOT)
            if not p.is_file()or any(s in {'.git','.cache','dist','__pycache__','.venv'}for s in rel.parts)or p.name=='.DS_Store':continue
            z.write(p,Path(ROOT.name)/rel)
        # Ship the offline document and verified runnable bundles with sources.
        for p in sorted(folder.rglob('*')):
            if p.is_file() and p != target and p.suffix in {'.html','.json','.zip'}:
                z.write(p,Path(ROOT.name)/p.relative_to(ROOT))
    print(f'{target} ({target.stat().st_size/1024/1024:.2f} MiB)')

if __name__=='__main__':main()
