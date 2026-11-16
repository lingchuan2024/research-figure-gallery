"""Check statistical edge cases and cross-table invariants, not plot internals."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import csv
import json
import re
import unittest
from collections import Counter, defaultdict
from gallerylib import ROOT, METHODS, TOOLS, np, normalize_rows, wilson_interval, paired_bootstrap_ci, pair_by_id, pareto_frontier

def read(name):
    with (ROOT/'data/demo'/name).open(newline='')as f:return list(csv.DictReader(f))

class StatisticsTests(unittest.TestCase):
    def test_normalization_and_unobserved_state(self):
        actual=normalize_rows([[1,3],[0,0]])
        np.testing.assert_allclose(actual[0],[.25,.75]);self.assertTrue(np.isnan(actual[1]).all())

    def test_negative_counts_rejected(self):
        with self.assertRaises(ValueError):normalize_rows([[1,-1]])

    def test_wilson_extremes(self):
        lo,hi=wilson_interval(0,10);self.assertAlmostEqual(lo,0);self.assertGreater(hi,0)
        lo,hi=wilson_interval(10,10);self.assertLess(lo,1);self.assertAlmostEqual(hi,1)
        with self.assertRaises(ValueError):wilson_interval(0,0)

    def test_bootstrap_constant_difference(self):
        np.testing.assert_allclose(paired_bootstrap_ci([.2,.2,.2]),[.2,.2])
        np.testing.assert_allclose(paired_bootstrap_ci([1,2,3]),paired_bootstrap_ci([1,2,3]))
        with self.assertRaises(ValueError):paired_bootstrap_ci([np.nan])

    def test_pairing_does_not_follow_row_order(self):
        a=[{'question_id':'b','value':2},{'question_id':'a','value':1}];b=list(reversed(a))
        self.assertEqual([x['question_id']for x,y in pair_by_id(a,b)],['a','b'])

    def test_unmatched_and_duplicate_pairs_rejected(self):
        with self.assertRaises(ValueError):pair_by_id([{'question_id':'a'}],[{'question_id':'b'}])
        with self.assertRaises(ValueError):pair_by_id([{'question_id':'a'}]*2,[{'question_id':'a'}])

    def test_pareto_uses_both_objectives(self):
        self.assertEqual(set(pareto_frontier([1,2,2,3,4],[1,1,2,1,3])),{0,2,4})
        with self.assertRaises(ValueError):pareto_frontier([1],[np.inf])

class DataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.q=read('questions.csv');cls.index={(r['question_id'],r['method']):r for r in cls.q}

    def test_question_identity_and_complete_pairing(self):
        self.assertEqual(len(self.index),len(self.q));ids=[]
        for m in METHODS:ids.append({r['question_id']for r in self.q if r['method']==m})
        self.assertGreater(len(ids[0]),0);self.assertTrue(all(s==ids[0]for s in ids))

    def test_token_accounting(self):
        totals=Counter()
        for r in read('context.csv'):totals[r['question_id'],r['method']]+=int(r['input_tokens'])
        for key,r in self.index.items():
            self.assertEqual(int(r['main_uncached_tokens'])+int(r['main_cached_tokens']),int(r['main_input_tokens']))
            self.assertEqual(totals[key],int(r['main_input_tokens']))

    def test_explicit_call_ledger_matches_actions(self):
        count=Counter();turns=defaultdict(set)
        for r in read('actions.csv'):
            key=(r['question_id'],r['method']);t=int(r['turn']);self.assertNotIn(t,turns[key]);turns[key].add(t)
            count[(*key,r['tool'])]+=1
        for r in read('tool_calls.csv'):
            self.assertEqual(count[r['question_id'],r['method'],r['tool']],int(r['calls']))
            if r['tool']in {'search','rerank'}:self.assertEqual(int(r['returned_chars']),100*int(r['calls']))
        for key,r in self.index.items():self.assertEqual(len(turns[key]),int(r['turns']))

    def test_evidence_and_outcome_contracts(self):
        for r in self.q:
            self.assertTrue(0<=int(r['gold_located'])<=int(r['gold_shown'])<=int(r['gold_in_pool'])<=1)
            self.assertEqual(int(r['correct']),int(r['outcome']=='Correct'))
            self.assertIn(r['outcome'],['Correct','Wrong answer','Abstain','No final'])
            self.assertIn(r['stop_reason'],['Completed','Turn limit','Timeout'])
            self.assertGreater(float(r['wall_seconds']),0)

    def test_ranking_candidate_universe(self):
        rr=read('ranks.csv');self.assertEqual(len({r['snapshot_id']for r in rr}),len(rr))
        for r in rr:
            if int(r['in_candidates']):
                self.assertTrue(1<=int(r['before_rank'])<=1000);self.assertTrue(1<=int(r['after_rank'])<=1000)
            else:self.assertEqual((r['before_rank'],r['after_rank']),('',''))

    def test_all_ablations_and_budgets_are_paired(self):
        ids={r['question_id']for r in self.q};groups=defaultdict(list)
        for r in read('budget_runs.csv'):groups[r['method'],r['budget']].append(r['question_id'])
        for r in read('ablations.csv'):groups[r['variant']].append(r['question_id'])
        for group in groups.values():self.assertEqual(set(group),ids);self.assertEqual(len(group),len(ids))

    def test_manifest_code_and_data_exist(self):
        items=json.loads((ROOT/'gallery.json').read_text());ids=[i['id']for i in items]
        self.assertEqual(len(ids),len(set(ids)));self.assertGreater(len(ids),0)
        self.assertEqual({i['script']for i in items},{str(p.relative_to(ROOT))for p in (ROOT/'examples').glob('*/plot.py')})
        for fmt,key in [('png','image'),('svg','vector')]:
            self.assertEqual({i[key]for i in items},{str(p.relative_to(ROOT))for p in (ROOT/'assets').glob('*.'+fmt)if p.stem!='overview'})
        for item in items:
            self.assertTrue((ROOT/item['script']).is_file());self.assertIn(item['id'],(ROOT/item['script']).read_text())
            for path in item['data']:self.assertTrue((ROOT/path).is_file())

    def test_documentation_local_links_resolve_when_present(self):
        for name in ['README.md','SUPPLEMENT.md','docs/GALLERY.md','docs/FIGURE_INDEX.md']:
            path=ROOT/name
            if not path.exists():self.skipTest('First build generates documentation after rendering')
            for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                if not link.startswith(('http:','https:','#')):self.assertTrue((path.parent/link.split('#')[0]).exists(),f'{name}: {link}')

    def test_detailed_gallery_coverage_when_present(self):
        path=ROOT/'docs/GALLERY.md'
        if not path.exists():self.skipTest('First build generates gallery documentation after rendering')
        content=path.read_text()
        items=json.loads((ROOT/'gallery.json').read_text())
        selected={i['id']for i in json.loads((ROOT/'catalog.json').read_text())['selected']}
        for item in items:
            expected=int(item['id']in selected)
            self.assertEqual(content.count('](../'+item['image']+')'),expected,item['id']+' image selection mismatch')
            self.assertEqual(content.count('](../'+item['script']+')'),expected,item['id']+' source link selection mismatch')

if __name__=='__main__':unittest.main()
