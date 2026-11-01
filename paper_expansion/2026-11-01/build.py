"""Build only new figures; refresh README through a mode that preserves old images."""
from pathlib import Path
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]

def main():
    manifest=json.loads((HERE/'manifest.json').read_text())
    for item in manifest:
        if item['aesthetic_status']!='passed':raise ValueError('Figure has not passed manual review: '+item['id'])
        subprocess.run([sys.executable,str(HERE/item['script'])],cwd=REPO,check=True)
        print('Rendered '+item['id'],flush=True)
    subprocess.run([sys.executable,str(HERE/'contact_sheet.py')],cwd=REPO,check=True)
    subprocess.run([sys.executable,str(REPO/'scripts/build_gallery.py'),'--keep-existing-images'],cwd=REPO,check=True)

if __name__=='__main__':main()
