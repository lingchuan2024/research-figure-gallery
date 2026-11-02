"""Resolve a single curated catalog against the unchanged source inventories."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def load_catalog():
    return json.loads((ROOT/'catalog.json').read_text())

def source_inventory():
    result={}
    for raw in json.loads((ROOT/'gallery.json').read_text()):
        result[raw['id']]={**raw,'origin':'synthetic','source_label':'图型参考','source_url':raw['reference']}
    for manifest in sorted((ROOT/'paper_expansion').glob('*/manifest.json')):
        folder=manifest.parent;prefix=folder.relative_to(ROOT)
        papers={p['id']:p for p in json.loads((folder/'papers.json').read_text())}
        for raw in json.loads(manifest.read_text()):
            paper=papers[raw['paper']]
            result[raw['id']]={**raw,'origin':'paper','script':str(prefix/raw['script']),'image':str(prefix/raw['image']),'vector':str(prefix/raw['vector']),'data':[str(prefix/raw['data'])],'source_label':paper['title'].split(':',1)[0],'source_url':paper['pdf']+'#page='+str(raw['source_pdf_page']),'paper_version':paper['version']}
    for manifest in sorted((ROOT/'frameworks').glob('*/manifest.json')):
        folder=manifest.parent;prefix=folder.relative_to(ROOT)
        sources={p['id']:p for p in json.loads((folder/'sources.json').read_text())}
        for raw in json.loads(manifest.read_text()):
            item={**raw,**{key:str(prefix/raw[key])for key in ['script','image','vector','editable','spec']},'data':[str(prefix/raw['spec'])]}
            if raw.get('source'):
                source=sources[raw['source']]
                item.update(source_label=source['title'].split(':',1)[0],source_url=source['pdf']+'#page='+str(source['pdf_page']),paper_version=source['version'],source_locator=f"{source['figure']}，PDF p{source['pdf_page']}；{source['methods']}")
            result[raw['id']]=item
    return result

def selected_entries():
    inventory=source_inventory()
    return [{**inventory[item['id']],**item,'number':i}for i,item in enumerate(load_catalog()['selected'],1)]
