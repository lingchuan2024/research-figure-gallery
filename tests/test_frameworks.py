"""Check source-to-artifact traceability, portable rendering and old-image preservation."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'frameworks/2026-11-02'

class FrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=json.loads((FOLDER/'manifest.json').read_text())
        cls.sources={s['id']:s for s in json.loads((FOLDER/'sources.json').read_text())}

    def test_all_preexisting_images_keep_their_bytes(self):
        baseline=json.loads((FOLDER/'preservation-baseline.json').read_text())
        self.assertEqual(len(baseline),39)
        for name,digest in baseline.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)

    def test_each_framework_has_code_editable_structure_and_source_scope(self):
        self.assertEqual(len(self.items),4)
        for item in self.items:
            for key in ['script','spec','image','vector','editable']:
                self.assertTrue((FOLDER/item[key]).is_file(),item[key])
            self.assertTrue(item['scope']);self.assertTrue(item['code_provenance'])
            if item['origin']=='paper_framework':
                source=self.sources[item['source']]
                self.assertIn(source['version'],source['pdf'])
                self.assertGreater(source['pdf_page'],0)
                self.assertRegex(source['pdf_sha256'],r'^[a-f0-9]{64}$')
            else:self.assertEqual(item['origin'],'design_framework')

    def test_editable_exports_retain_every_module_and_route(self):
        for item in self.items:
            spec=json.loads((FOLDER/item['spec']).read_text())
            xml=ET.parse(FOLDER/item['editable'])
            cells=xml.findall('.//mxCell');vertices={c.attrib['id']for c in cells if c.get('vertex')=='1'}
            self.assertTrue({n['id']for n in spec['nodes']}<=vertices)
            self.assertEqual(sum(c.get('edge')=='1'for c in cells),len(spec['edges']))
            svg=ET.parse(FOLDER/item['vector'])
            self.assertTrue(svg.findall('.//{http://www.w3.org/2000/svg}text'),'SVG text should remain editable')
            self.assertEqual(len(spec['nodes']),len({n['id']for n in spec['nodes']}))
            for n in spec['nodes']:
                self.assertTrue(0<=n['x']<n['x']+n['w']<=spec['width'],n['id'])
                self.assertTrue(0<=n['y']<n['y']+n['h']<=spec['height'],n['id'])

    def test_unverified_design_and_paper_mode_are_visible_in_exports(self):
        design=(FOLDER/'figures/F04_rerank_control.svg').read_text()
        for phrase in ['Experiment-design sketch','verify configuration','Search','response','additional rerank observation','B caps each tool response']:
            self.assertIn(phrase,design)
        explorer=(FOLDER/'figures/F03_webthinker_nested.svg').read_text()
        self.assertIn('problem-solving mode',explorer)
        self.assertIn('Report drafting, document memory and RL training omitted',explorer)

    def test_scripts_render_from_an_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory()as temp:
            for item in self.items:
                result=subprocess.run([sys.executable,str(FOLDER/item['script']),'--output-dir',temp],cwd=temp,capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                for suffix in ['svg','drawio']:ET.parse(Path(temp)/(item['id']+'.'+suffix))
                with Image.open(Path(temp)/(item['id']+'.png'))as im:
                    self.assertGreater(min(im.size),1000)
                    self.assertTrue(any(lo!=hi for lo,hi in im.convert('RGB').getextrema()))

    def test_framework_notes_and_root_links_resolve(self):
        for path in [ROOT/'README.md',FOLDER/'NOTES.md',FOLDER/'VISUAL_REVIEW.md']:
            for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                if not link.startswith(('https:','http:','#')):
                    self.assertTrue((path.parent/link).exists(),str(path)+': '+link)

if __name__=='__main__':unittest.main()
