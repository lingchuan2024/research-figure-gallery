"""Boundary checks for paired scientific comparisons, not rendering internals."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

import numpy as np

BUNDLE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BUNDLE))
from common import (validate_config,validate_rows,paired_differences,
                    bootstrap_ci,select_metric_cohort,pareto_mask)


def config(kind='binary'):
    return {
        'schema_version':1,
        'data_kind':'synthetic',
        'experiment':'Hand-constructed boundary fixtures; not experiment results',
        'baseline':'baseline',
        'methods':[
            {'id':'baseline','label':'Baseline','color':'#607D8B'},
            {'id':'rerank','label':'Rerank','color':'#00897B'},
        ],
        'score':{'label':'Accuracy' if kind=='binary' else 'nDCG@10',
                 'kind':kind,'scale':100,'unit':'%','delta_unit':'pp'},
        'conditions':{
            'question_set':'fixed fixture questions',
            'generator_model':'fixed fixture model',
            'retrieval_policy':'same candidate pool',
            'hardware':'same device',
            'concurrency':'one worker',
            'stopping_rule':'same turn and wall-clock limits',
            'run_selection':'one prespecified run per question and method',
        },
    }


def fixture_rows():
    # q01 is the only outcome improvement; removing it must remove the gain.
    return [
        {'benchmark':'bench-a','question_id':'q01','subset':'general',
         'method':'baseline','status':'complete','score':'0','wall_seconds':'4'},
        {'benchmark':'bench-a','question_id':'q01','subset':'general',
         'method':'rerank','status':'complete','score':'1','wall_seconds':'3'},
        {'benchmark':'bench-a','question_id':'q02','subset':'general',
         'method':'baseline','status':'complete','score':'1','wall_seconds':'6'},
        {'benchmark':'bench-a','question_id':'q02','subset':'general',
         'method':'rerank','status':'complete','score':'1','wall_seconds':'5'},
    ]


class IdentityAndScoreTests(unittest.TestCase):
    def test_duplicate_question_method_is_rejected(self):
        rows=fixture_rows()
        rows.append(deepcopy(rows[0]))
        with self.assertRaises(ValueError):
            validate_rows(rows,config())

    def test_missing_method_question_is_rejected(self):
        rows=fixture_rows()[:-1]
        with self.assertRaises(ValueError):
            validate_rows(rows,config())

    def test_subset_cannot_change_between_methods(self):
        rows=fixture_rows()
        rows[1]['subset']='different difficulty stratum'
        with self.assertRaises(ValueError):
            validate_rows(rows,config())

    def test_scores_must_be_finite_and_within_zero_one(self):
        for score in ('nan','inf','-inf','-0.001','1.001'):
            with self.subTest(score=score):
                rows=fixture_rows()
                rows[0]['score']=score
                with self.assertRaises(ValueError):
                    validate_rows(rows,config('bounded'))

    def test_binary_score_cannot_be_a_fraction(self):
        rows=fixture_rows()
        rows[0]['score']='0.5'
        with self.assertRaises(ValueError):
            validate_rows(rows,config('binary'))

    def test_failed_binary_outcomes_cannot_be_counted_correct(self):
        for status in ('timeout','no_final','error'):
            with self.subTest(status=status):
                rows=fixture_rows()
                rows[1]['status']=status
                with self.assertRaises(ValueError):
                    validate_rows(rows,config())

    def test_failed_rows_are_retained_with_zero_score_and_observed_cost(self):
        rows=fixture_rows()
        rows[1].update(status='timeout',score='0',wall_seconds='3601.4')
        parsed=validate_rows(rows,config())
        failed=next(r for r in parsed if r['question_id']=='q01' and r['method']=='rerank')
        self.assertEqual(len(parsed),4)
        self.assertEqual(failed['score'],0)
        self.assertAlmostEqual(failed['wall_seconds'],3601.4)

    def test_required_condition_and_positive_scale_are_enforced(self):
        cfg=config()
        cfg['conditions']['run_selection']=''
        with self.assertRaises(ValueError):
            validate_config(cfg)
        for value in (0,-1,float('nan'),float('inf')):
            with self.subTest(scale=value):
                cfg=config()
                cfg['score']['scale']=value
                with self.assertRaises(ValueError):
                    validate_config(cfg)


class CostAndCohortTests(unittest.TestCase):
    def test_missing_cost_remains_missing_and_default_policy_rejects_it(self):
        for missing in ('',None):
            with self.subTest(missing=missing):
                rows=fixture_rows()
                rows[1]['wall_seconds']=missing
                parsed=validate_rows(rows,config())
                absent=next(r for r in parsed if r['question_id']=='q01' and r['method']=='rerank')
                self.assertIsNone(absent.get('wall_seconds'))
                with self.assertRaises(ValueError):
                    select_metric_cohort(parsed,'wall_seconds','error')

    def test_absent_cost_column_is_not_inferred_as_zero(self):
        rows=fixture_rows()
        for row in rows:
            row.pop('wall_seconds')
        parsed=validate_rows(rows,config())
        self.assertTrue(all(row.get('wall_seconds') is None for row in parsed))
        with self.assertRaises(ValueError):
            select_metric_cohort(parsed,'wall_seconds','error')

    def test_complete_case_removes_whole_question_and_recomputes_score_cohort(self):
        rows=fixture_rows()
        rows[1]['wall_seconds']=''
        parsed=validate_rows(rows,config())
        before=paired_differences(parsed,'baseline','rerank')
        self.assertAlmostEqual(float(np.mean(before)),.5)
        kept,audit=select_metric_cohort(parsed,'wall_seconds','complete-case')
        self.assertEqual(len(kept),2)
        self.assertEqual({row['question_id'] for row in kept},{'q02'})
        self.assertEqual({row['method'] for row in kept},{'baseline','rerank'})
        self.assertEqual([row['score'] for row in kept],[1,1])
        np.testing.assert_array_equal(paired_differences(kept,'baseline','rerank'),[0])
        self.assertEqual(audit['questions_before'],{'bench-a':2})
        self.assertEqual(audit['questions_after'],{'bench-a':1})
        self.assertEqual(audit['excluded_question_count'],1)
        self.assertEqual(audit['excluded_questions'],[
            {'benchmark':'bench-a','question_id':'q01','missing_methods':['rerank']}])

    def test_missing_question_removal_is_scoped_to_benchmark(self):
        rows=fixture_rows()
        other=[{**deepcopy(row),'benchmark':'bench-b'} for row in rows[:2]]
        rows[1]['wall_seconds']=''
        parsed=validate_rows(rows+other,config())
        kept,_=select_metric_cohort(parsed,'wall_seconds','complete-case')
        keys={(row['benchmark'],row['question_id']) for row in kept}
        self.assertEqual(keys,{('bench-a','q02'),('bench-b','q01')})
        self.assertEqual(len(kept),4)

    def test_zero_cost_is_observed_not_missing(self):
        rows=fixture_rows()
        for row in rows:
            row['rerank_seconds']='0' if row['method']=='baseline' else '2'
        parsed=validate_rows(rows,config())
        for policy in ('error','complete-case'):
            with self.subTest(policy=policy):
                kept,_=select_metric_cohort(parsed,'rerank_seconds',policy)
                self.assertEqual(len(kept),4)
                self.assertEqual([r['rerank_seconds'] for r in kept if r['method']=='baseline'],[0,0])

    def test_invalid_costs_and_fractional_token_counts_are_rejected(self):
        for field,value in [('wall_seconds','-1'),('wall_seconds','nan'),
                            ('rerank_seconds','inf'),('main_input_tokens','2.5'),
                            ('rerank_events','-1'),('scored_passages','1.5')]:
            with self.subTest(field=field,value=value):
                rows=fixture_rows()
                rows[0][field]=value
                with self.assertRaises(ValueError):
                    validate_rows(rows,config())


class PairedStatisticsTests(unittest.TestCase):
    def test_pairing_uses_question_identity_and_is_invariant_to_row_order(self):
        rows=fixture_rows()
        # Two bounded-score pairs: q01=-0.25, q02=+0.5.
        for row,value in zip(rows,('.5','.25','.2','.7')):
            row['score']=value
        parsed=validate_rows(rows,config('bounded'))
        permuted=[parsed[i] for i in (3,0,2,1)]
        expected=np.array([-.25,.5])
        actual=paired_differences(parsed,'baseline','rerank')
        reordered=paired_differences(permuted,'baseline','rerank')
        np.testing.assert_allclose(actual,expected,rtol=0,atol=1e-12)
        np.testing.assert_array_equal(actual,reordered)
        self.assertEqual(tuple(bootstrap_ci(actual,draws=2000,seed=42)),
                         tuple(bootstrap_ci(reordered,draws=2000,seed=42)))

    def test_constant_paired_gain_has_degenerate_interval(self):
        low,high=bootstrap_ci(np.array([.25,.25,.25,.25]),draws=2000,seed=7)
        self.assertAlmostEqual(float(low),.25)
        self.assertAlmostEqual(float(high),.25)

    def test_pareto_requires_weak_improvement_in_both_and_strict_in_one(self):
        # Minimize x, maximize y. The duplicated (2,.7) point stays nondominated.
        costs=np.array([1,2,2,3,0,2],dtype=float)
        scores=np.array([.5,.5,.7,.6,.3,.7])
        actual=pareto_mask(costs,scores)
        np.testing.assert_array_equal(actual,[True,False,True,False,True,True])


if __name__=='__main__':
    unittest.main()
