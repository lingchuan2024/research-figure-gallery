"""Check the rerank bundle's source lineage and preserved, usable deliverables."""
from pathlib import Path
import csv
import hashlib
import json
import re
import sys
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.family_support import load_families
from scripts.render_readme import index_entries
HERE=ROOT/'rerank_expansion/2026-11-15'


@unittest.skipUnless((HERE/'manifest.json').is_file(), 'Rerank bundle not present')
class RerankExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.figures=json.loads((HERE/'manifest.json').read_text())
        cls.paper_rows=json.loads((HERE/'papers.json').read_text())
        cls.papers={p['id']:p for p in cls.paper_rows}
        cls.records=json.loads((HERE/'data_provenance.json').read_text())

    def test_paper_identity_and_source_locators_are_unambiguous(self):
        self.assertEqual(len(self.papers),len(self.paper_rows))
        self.assertEqual(len({f['id'] for f in self.figures}),len(self.figures))
        self.assertGreater(len(self.figures),0)
        for figure in self.figures:
            paper=self.papers[figure['paper']]
            self.assertTrue(paper['title'].strip())
            self.assertTrue(paper['pdf'].startswith('https://'))
            self.assertTrue(paper['version'].strip())
            self.assertTrue(figure['source_locator'].strip())
            self.assertGreaterEqual(figure['source_pdf_page'],1)
            self.assertEqual(figure['origin'],'published_numeric_redraw')

    def test_csvs_match_the_recorded_transcriptions(self):
        by_id={r['figure_id']:r for r in self.records}
        self.assertEqual(len(by_id),len(self.records))
        self.assertEqual(set(by_id),{f['id'] for f in self.figures})
        for figure in self.figures:
            record=by_id[figure['id']]
            self.assertEqual(record['csv'],figure['data'])
            data_path=HERE/record['csv']
            self.assertEqual(hashlib.sha256(data_path.read_bytes()).hexdigest(),record['csv_sha256'])
            self.assertEqual(record['version'],self.papers[figure['paper']]['version'])
            self.assertIn(figure['source_pdf_page'],record['pdf_pages'])
            self.assertTrue(all(isinstance(p,int) and p>0 for p in record['pdf_pages']))
            self.assertRegex(record['inspected_pdf_sha256'],r'^[0-9a-f]{64}$')
            with data_path.open(newline='',encoding='utf-8') as handle:
                reader=csv.DictReader(handle)
                self.assertTrue(reader.fieldnames)
                self.assertEqual(len(reader.fieldnames),len(set(reader.fieldnames)))
                rows=list(reader)
            self.assertGreater(len(rows),0)
            self.assertTrue(all(None not in row and all(v is not None for v in row.values()) for row in rows))

    def test_each_reviewed_figure_is_complete_and_readable(self):
        for figure in self.figures:
            self.assertEqual(figure['aesthetic_status'],'passed')
            for key in ('data','script','image','vector'):
                path=(HERE/figure[key]).resolve()
                self.assertTrue(path.is_relative_to(HERE.resolve()))
                self.assertTrue(path.is_file(),str(path))
            with Image.open(HERE/figure['image']) as image:
                self.assertGreater(min(image.size),500)
                self.assertTrue(any(lo<hi for lo,hi in image.convert('RGB').getextrema()))
            self.assertIn('<svg',(HERE/figure['vector']).read_text())

    def test_rerank_variants_are_indexed_without_duplicate_family_previews(self):
        entries=index_entries();by_script={entry['script']:entry for entry in entries}
        representatives={family['representative']for family in load_families({e['code']for e in entries})}
        content=(ROOT/'README.md').read_text()
        index=(ROOT/'docs/FIGURE_INDEX.md').read_text()
        images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',content)
        prefix=str(HERE.relative_to(ROOT))+'/'
        for figure in self.figures:
            entry=by_script[prefix+figure['script']]
            self.assertEqual(images.count(prefix+figure['image']),int(entry['code']in representatives),figure['id'])
            anchor=f'<a id="variant-{entry["code"].lower()}"></a>'
            self.assertEqual(index.count(anchor),1,figure['id'])
            body=index.split(anchor,1)[1].split('\n<a id=',1)[0]
            for field in ('script','data'):
                self.assertIn('](../'+prefix+figure[field]+')',body,figure['id'])
        self.assertEqual(re.findall(r'!\[[^\]]*\]\(([^)]+)\)',index),[])


if __name__=='__main__':
    unittest.main()
