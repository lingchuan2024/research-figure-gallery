"""Resolve a single curated catalog against the unchanged source inventories."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def load_catalog():
    return json.loads((ROOT/'catalog.json').read_text())

def expansion_manifests():
    """Find published-data bundles in both generations of the gallery."""
    return sorted(path for name in ('paper_expansion','rerank_expansion')
                  for path in (ROOT/name).glob('*/manifest.json'))

def source_inventory():
    result={}
    def add(raw):
        if raw['id'] in result:
            raise ValueError('Duplicate figure ID across source inventories: '+raw['id'])
        result[raw['id']]=raw
    for raw in json.loads((ROOT/'gallery.json').read_text()):
        add({**raw,'origin':'synthetic','source_label':'图型参考','source_url':raw['reference']})
    for manifest in expansion_manifests():
        folder=manifest.parent;prefix=folder.relative_to(ROOT)
        paper_rows=json.loads((folder/'papers.json').read_text())
        papers={p['id']:p for p in paper_rows}
        if len(papers)!=len(paper_rows):
            raise ValueError('Duplicate paper ID in '+str(folder/'papers.json'))
        for raw in json.loads(manifest.read_text()):
            paper=papers[raw['paper']]
            add({**raw,'origin':'paper','script':str(prefix/raw['script']),'image':str(prefix/raw['image']),'vector':str(prefix/raw['vector']),'data':[str(prefix/raw['data'])],'source_label':paper['title'].split(':',1)[0],'source_url':paper['pdf']+'#page='+str(raw['source_pdf_page']),'paper_version':paper['version']})
    return result

def selected_entries():
    inventory=source_inventory()
    return [{**inventory[item['id']],**item,'number':i}for i,item in enumerate(load_catalog()['selected'],1)]
