"""Verify authorized removal, canonical source copies, and retained image bytes."""
from pathlib import Path
import csv
import hashlib
import json
import sys
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.catalog_support import source_inventory
from scripts.curation_audit import assert_preserved_images


class DeduplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt=json.loads((ROOT/'curation/2026-11-15-dedup/deletions.json').read_text())

    def test_only_recorded_files_removed_and_canonical_copies_match(self):
        self.assertEqual(len({r['path'] for r in self.receipt['deleted_files']}),len(self.receipt['deleted_files']))
        for item in self.receipt['deleted_files']:
            self.assertFalse((ROOT/item['path']).exists(),item['path'])
            self.assertTrue((ROOT/item['replacement']).is_file(),item['replacement'])
            if item['path'].endswith('.csv'):
                self.assertEqual(hashlib.sha256((ROOT/item['replacement']).read_bytes()).hexdigest(),item['sha256_before'])

    def test_retained_figures_are_unchanged_and_not_pixel_duplicates(self):
        inventory=source_inventory()
        expected={entry[key] for entry in inventory.values() for key in ('image','vector')}
        self.assertEqual(set(self.receipt['retained_image_sha256']),expected)
        for name,digest in self.receipt['retained_image_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
        seen=set()
        for item in inventory.values():
            with Image.open(ROOT/item['image']) as image:
                rgb=image.convert('RGB');key=(rgb.size,hashlib.sha256(rgb.tobytes()).hexdigest())
            self.assertNotIn(key,seen,item['id']);seen.add(key)

    def test_historical_rerank_preservation_receipt_still_holds(self):
        baseline=json.loads((ROOT/'rerank_expansion/2026-11-15/preservation-baseline.json').read_text())
        assert_preserved_images(baseline)

    def test_retained_budget_template_still_has_source_data(self):
        # The removed example has the same outcomes, with no independent cost data.
        with (ROOT/'data/demo/budget_runs.csv').open(newline='') as handle:
            rows=list(csv.DictReader(handle))
        for row in rows:
            multiplier=1.25 if row['method']=='Auto rerank' else 1.0
            self.assertAlmostEqual(float(row['cost_units']),multiplier*float(row['budget']))


if __name__=='__main__':
    unittest.main()
