"""Build only the new reranking figures; existing gallery images are untouched."""
from pathlib import Path
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent

def main():
    for item in json.loads((HERE / 'manifest.json').read_text()):
        subprocess.run([sys.executable, str(HERE / item['script'])], check=True)
        print('Rendered ' + item['id'], flush=True)
    subprocess.run([sys.executable, str(HERE / 'contact_sheet.py')], check=True)

if __name__ == '__main__': main()
