"""Regression checks for one complete, nonduplicated editorial gallery."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import hashlib
import json
import re
import unittest
from scripts.catalog_support import ROOT,load_catalog,source_inventory,selected_entries

class UnifiedCatalogTests(unittest.TestCase):
    def test_selection_and_supplement_partition_all_available_figures(self):
        catalog=load_catalog();main=[i['id']for i in catalog['selected']];extra=[i['id']for i in catalog['supplement']]
        self.assertEqual(len(main),len(set(main)));self.assertEqual(len(extra),len(set(extra)));self.assertFalse(set(main)&set(extra))
        self.assertEqual(set(main)|set(extra),set(source_inventory()))
        self.assertTrue(all(i['reason']for i in catalog['supplement']))

    def test_existing_images_are_unchanged_after_reorganization(self):
        baseline=json.loads((ROOT/'curation/2026-11-02/image_baseline.json').read_text())
        for name,digest in baseline.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)

    def test_whole_readme_has_one_purpose_structure(self):
        content=(ROOT/'README.md').read_text();items=selected_entries()
        actual=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',content)
        self.assertEqual(actual,[i['image']for i in items]);self.assertEqual(len(actual),len(set(actual)))
        for section in dict.fromkeys(i['section']for i in items):
            body=content.split('## '+section+'\n',1)[1].split('\n## ',1)[0]
            images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',body)
            self.assertEqual(images,[i['image']for i in items if i['section']==section])
        self.assertNotIn('## 新增',content);self.assertNotIn('原有模板',content)
        supplemental=(ROOT/'SUPPLEMENT.md').read_text();inventory=source_inventory()
        for item in load_catalog()['supplement']:
            self.assertIn(']('+inventory[item['id']]['image']+')',supplemental)

if __name__=='__main__':unittest.main()
