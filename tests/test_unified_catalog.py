"""Regression checks for one complete, nonduplicated editorial gallery."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import re
import unittest
from scripts.catalog_support import ROOT,load_catalog,source_inventory
from scripts.curation_audit import assert_preserved_images
from scripts.family_support import load_families
from scripts.render_readme import index_entries

class UnifiedCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries=index_entries()
        cls.by_code={entry['code']:entry for entry in cls.entries}
        cls.families=load_families(cls.by_code)

    def test_selection_and_supplement_partition_all_available_figures(self):
        catalog=load_catalog();main=[i['id']for i in catalog['selected']];extra=[i['id']for i in catalog['supplement']]
        self.assertEqual(len(main),len(set(main)));self.assertEqual(len(extra),len(set(extra)));self.assertFalse(set(main)&set(extra))
        self.assertEqual(set(main)|set(extra),set(source_inventory()))
        self.assertTrue(all(i['reason']for i in catalog['supplement']))

    def test_existing_images_are_unchanged_after_reorganization(self):
        baseline=json.loads((ROOT/'curation/2026-11-02/image_baseline.json').read_text())
        assert_preserved_images(baseline)

    def test_families_partition_all_34_variants_and_cover_their_uses(self):
        registry=json.loads((ROOT/'figure_families.json').read_text())
        self.assertEqual(registry['version'],1)
        self.assertEqual(len(self.entries),34)
        self.assertEqual(len(self.by_code),34)
        self.assertEqual([f['id']for f in self.families],[f'F{i:02d}'for i in range(1,12)])
        members=[code for family in self.families for code in family['members']]
        self.assertEqual(len(members),len(set(members)))
        self.assertEqual(set(members),set(self.by_code))
        self.assertEqual(sum(len(f['uses'])for f in self.families),28)
        for family in self.families:
            self.assertIn(family['representative'],family['members'])
            self.assertTrue(family['title'].strip())
            self.assertTrue(family['caution'].strip())
            covered=set()
            for use in family['uses']:
                for key in ('purpose','placement','data'):
                    self.assertTrue(isinstance(use[key],str) and use[key].strip(),(family['id'],key))
                self.assertTrue(use['source_codes'])
                self.assertTrue(set(use['source_codes'])<=set(family['members']))
                covered.update(use['source_codes'])
            self.assertEqual(covered,set(family['members']))

    def test_readme_has_one_representative_and_all_uses_per_family(self):
        content=(ROOT/'README.md').read_text()
        actual=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',content)
        expected=[self.by_code[f['representative']]['image']for f in self.families]
        self.assertEqual(actual,expected)
        self.assertEqual(len(actual),11)
        self.assertEqual(len(set(actual)),11)
        self.assertEqual(re.findall(r'^## (F\d{2}) ·',content,re.M),[f['id']for f in self.families])
        self.assertEqual(content.count('建议位置：'),28)
        for family in self.families:
            body=content.split(f"## {family['id']} · {family['title']}\n",1)[1].split('\n## ',1)[0]
            self.assertEqual(re.findall(r'!\[[^\]]*\]\(([^)]+)\)',body),
                             [self.by_code[family['representative']]['image']])
            for use in family['uses']:
                for field in ('purpose','placement','data'):
                    self.assertIn(use[field],body)
                for code in use['source_codes']:
                    self.assertIn(f'](docs/FIGURE_INDEX.md#variant-{code.lower()})',body)
            self.assertIn(family['caution'],body)
        self.assertNotIn('docs/GALLERY.md',content)
        self.assertNotIn('SUPPLEMENT.md',content)

    def test_entrypoint_and_complete_index_have_working_source_links(self):
        readme=(ROOT/'README.md').read_text()
        self.assertIn('](docs/FIGURE_INDEX.md)',readme)
        index=(ROOT/'docs/FIGURE_INDEX.md').read_text()
        self.assertEqual(re.findall(r'!\[[^\]]*\]\(([^)]+)\)',index),[])
        expected=[code.lower()for family in self.families for code in family['members']]
        self.assertEqual(re.findall(r'<a id="variant-([tmsg]\d{2})"></a>',index),expected)
        self.assertEqual(re.findall(r'^## (F\d{2}) ·',index,re.M),[f['id']for f in self.families])
        headings=[f"{family['id']}.{number}"for family in self.families
                  for number in range(1,len(family['members'])+1)]
        self.assertEqual(re.findall(r'^### (F\d{2}\.\d+) ·',index,re.M),headings)
        for entry in self.entries:
            anchor=f'<a id="variant-{entry["code"].lower()}"></a>'
            body=index.split(anchor,1)[1].split('\n<a id=',1)[0]
            paths=[entry['script'],*(path for _,path in entry['inputs'])]
            paths.extend(entry[key]for key in ('helper','source','license')if entry.get(key))
            for path in paths:
                self.assertIn('](../'+path+')',body,(entry['code'],path))
                self.assertTrue((ROOT/path).is_file(),path)
            self.assertIn(entry['status'],body)
            self.assertIn(entry['reference'],body)
        for name in ['README.md','docs/FIGURE_INDEX.md']:
            document=ROOT/name
            for target in re.findall(r'\]\(([^)]+)\)',document.read_text()):
                if target.startswith(('http:','https:')):continue
                path,_,fragment=target.partition('#')
                resolved=document.parent/path if path else document
                self.assertTrue(resolved.is_file(),f'{name}: {target}')
                if fragment and re.fullmatch(r'(?:variant-[tmsg]\d{2}|f\d{2})',fragment):
                    self.assertIn(f'<a id="{fragment}"></a>',resolved.read_text(),f'{name}: {target}')

if __name__=='__main__':unittest.main()
