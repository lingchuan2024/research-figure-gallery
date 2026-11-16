"""Protect existing assets and validate the new paper-data gallery's provenance."""
from pathlib import Path
import csv
import hashlib
import json
import math
import re
import unittest
from PIL import Image
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.curation_audit import assert_preserved_images,deleted_paths
from scripts.family_support import load_families
from scripts.render_readme import index_entries
HERE=ROOT/'paper_expansion/2026-11-01'

def read(name):
    with (HERE/'data'/name).open(newline='')as f:return list(csv.DictReader(f))

class PaperExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.figures=json.loads((HERE/'manifest.json').read_text());cls.papers={p['id']:p for p in json.loads((HERE/'papers.json').read_text())}

    def test_existing_images_are_byte_identical(self):
        baseline=json.loads((HERE/'preservation-baseline.json').read_text())
        self.assertEqual(set(baseline)-deleted_paths(),{str(p.relative_to(ROOT))for p in (ROOT/'assets').iterdir()if p.is_file()})
        assert_preserved_images(baseline)

    def test_new_sources_do_not_reuse_indexed_papers(self):
        excluded=set(json.loads((HERE/'excluded_papers.json').read_text())['excluded_arxiv_ids'])
        for paper in self.papers.values():self.assertNotIn(paper['version'].split('v')[0],excluded)

    def test_every_new_figure_has_review_source_code_and_outputs(self):
        ids=[f['id']for f in self.figures];self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual({f['script']for f in self.figures},{str(p.relative_to(HERE))for p in (HERE/'code').glob('*.py')})
        for f in self.figures:
            self.assertEqual(f['origin'],'published_numeric_redraw');self.assertEqual(f['aesthetic_status'],'passed');self.assertIn(f['paper'],self.papers)
            for key in ['script','data','image','vector']:self.assertTrue((HERE/f[key]).is_file(),f[key])
            with Image.open(HERE/f['image'])as im:
                self.assertGreater(min(im.size),500);self.assertTrue(any(lo<hi for lo,hi in im.convert('RGB').getextrema()))

    def test_transcribed_data_hashes_match_source_registry(self):
        records=json.loads((HERE/'data_provenance.json').read_text());self.assertEqual({r['figure_id']for r in records},{f['id']for f in self.figures})
        for record in records:
            self.assertEqual(hashlib.sha256((HERE/record['csv']).read_bytes()).hexdigest(),record['csv_sha256'])
            self.assertEqual(len(record['inspected_pdf_sha256']),64);self.assertTrue(record['pdf_pages']);self.assertIn('v',record['version'])

    def test_failure_population_denominators_are_separate(self):
        data=read('arag_failures.csv');groups={r['population']for r in data};self.assertEqual(groups,{'all_errors','reasoning_chain_errors'})
        for group in groups:self.assertAlmostEqual(sum(float(r['percent'])for r in data if r['population']==group),100)
        self.assertEqual(len(data),8)

    def test_complexity_strata_are_complete_and_unique(self):
        data=read('rubric_complexity.csv');keys={(r['dimension'],r['level'],r['model'])for r in data};self.assertEqual(len(data),len(keys));self.assertEqual(len(data),27)
        for r in data:self.assertTrue(0<=float(r['compliance_percent'])<=100)
        for dim in {r['dimension']for r in data}:
            rr=[r for r in data if r['dimension']==dim];self.assertEqual(len({r['level']for r in rr}),3);self.assertEqual(len({r['model']for r in rr}),3)

    def test_scaling_derivatives_and_latency_units(self):
        data=sorted(read('fs_scaling.csv'),key=lambda r:int(r['rounds']))
        for left,right in zip(data,data[1:]):
            ds=float(right['search_calls'])-float(left['search_calls']);self.assertGreater(ds,0)
            value=(float(right['unique_urls'])-float(left['unique_urls']))/ds;self.assertTrue(math.isfinite(value));self.assertGreaterEqual(value,0)
        timing=read('fs_latency.csv');self.assertTrue(all(float(r['seconds'])>=0 for r in timing));self.assertEqual(len(timing),6)
        self.assertLess(sum(float(r['seconds'])for r in timing if r['component']=='File I/O'),1)

    def test_paper_variants_keep_source_access_with_only_family_representatives_shown(self):
        readme=(ROOT/'README.md').read_text()
        index=(ROOT/'docs/FIGURE_INDEX.md').read_text()
        entries=index_entries();by_script={entry['script']:entry for entry in entries}
        representatives={family['representative']for family in load_families({e['code']for e in entries})}
        images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',readme)
        prefix=str(HERE.relative_to(ROOT))+'/'
        for f in self.figures:
            entry=by_script[prefix+f['script']]
            self.assertEqual(images.count(prefix+f['image']),int(entry['code']in representatives),f['id'])
            anchor=f'<a id="variant-{entry["code"].lower()}"></a>'
            self.assertEqual(index.count(anchor),1,f['id'])
            body=index.split(anchor,1)[1].split('\n<a id=',1)[0]
            self.assertIn('](../'+prefix+f['script']+')',body,f['id'])
            self.assertIn('](../'+prefix+f['data']+')',body,f['id'])
        self.assertEqual(re.findall(r'!\[[^\]]*\]\(([^)]+)\)',index),[])

if __name__=='__main__':unittest.main()
