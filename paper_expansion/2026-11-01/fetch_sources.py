"""Optional: download pinned paper versions and verify their exact inspected hashes."""
from pathlib import Path
import argparse
import hashlib
import json
from urllib.request import Request,urlopen

HERE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=HERE/'sources');args=p.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    for paper in json.loads((HERE/'papers.json').read_text()):
        if paper['status']!='selected':continue
        path=args.output_dir/(paper['version']+'.pdf')
        if not path.exists():
            request=Request(paper['pdf'],headers={'User-Agent':'research-figure-gallery/1.0 academic source verification'})
            with urlopen(request,timeout=60)as response:payload=response.read()
            if not payload.startswith(b'%PDF'):raise ValueError('Not a PDF: '+paper['pdf'])
            path.write_bytes(payload)
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=paper['sha256']:raise ValueError('Source hash differs; inspect before use: '+str(path))
        print('Verified '+paper['version'])

if __name__=='__main__':main()
