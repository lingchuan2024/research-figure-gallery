"""Regression checks for one complete, nonduplicated editorial gallery."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import hashlib
import json
import re
import unittest
from scripts.catalog_support import ROOT,load_catalog,source_inventory,selected_entries
from scripts.curation_audit import assert_preserved_images

class UnifiedCatalogTests(unittest.TestCase):
    def test_selection_and_supplement_partition_all_available_figures(self):
        catalog=load_catalog();main=[i['id']for i in catalog['selected']];extra=[i['id']for i in catalog['supplement']]
        self.assertEqual(len(main),len(set(main)));self.assertEqual(len(extra),len(set(extra)));self.assertFalse(set(main)&set(extra))
        self.assertEqual(set(main)|set(extra),set(source_inventory()))
        self.assertTrue(all(i['reason']for i in catalog['supplement']))

    def test_existing_images_are_unchanged_after_reorganization(self):
        baseline=json.loads((ROOT/'curation/2026-11-02/image_baseline.json').read_text())
        assert_preserved_images(baseline)

    def test_detailed_gallery_has_one_purpose_structure(self):
        content=(ROOT/'docs/GALLERY.md').read_text();items=selected_entries()
        actual=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',content)
        self.assertEqual(actual,['../'+i['image']for i in items]);self.assertEqual(len(actual),len(set(actual)))
        for section in dict.fromkeys(i['section']for i in items):
            body=content.split('## '+section+'\n',1)[1].split('\n## ',1)[0]
            images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',body)
            self.assertEqual(images,['../'+i['image']for i in items if i['section']==section])
        self.assertNotIn('## 新增',content);self.assertNotIn('原有模板',content)
        supplemental=(ROOT/'SUPPLEMENT.md').read_text();inventory=source_inventory()
        for item in load_catalog()['supplement']:
            self.assertIn(']('+inventory[item['id']]['image']+')',supplemental)

    def test_entrypoint_and_complete_index_have_working_source_links(self):
        readme=(ROOT/'README.md').read_text()
        self.assertIn('](docs/FIGURE_INDEX.md)',readme)
        self.assertIn('](docs/GALLERY.md)',readme)
        images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',readme)
        self.assertEqual(len(images),34)
        self.assertEqual(len(set(images)),34)
        index=(ROOT/'docs/FIGURE_INDEX.md').read_text()
        codes=re.findall(r'^\| ([TMSG]\d{2}) \|',index,re.M)
        expected=[f'T{i:02d}'for i in range(1,4)]+[f'M{i:02d}'for i in range(1,16)]+[f'S{i:02d}'for i in range(1,9)]+[f'G{i:02d}'for i in range(1,9)]
        self.assertEqual(codes,expected)
        self.assertEqual(re.findall(r'^### ([TMSG]\d{2}) ·',readme,re.M),expected)
        for label in ['这张图怎么看','适合放在论文哪里','换成我们的实验需要','使用边界']:
            self.assertEqual(readme.count('**'+label+'：**'),34,label)
        for name in ['README.md','docs/GALLERY.md','docs/FIGURE_INDEX.md','SUPPLEMENT.md']:
            document=ROOT/name
            for target in re.findall(r'\]\(([^)]+)\)',document.read_text()):
                if target.startswith(('http:','https:','#')):continue
                self.assertTrue((document.parent/target.split('#')[0]).is_file(),f'{name}: {target}')

if __name__=='__main__':unittest.main()
