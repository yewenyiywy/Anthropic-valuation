import unittest
import numpy as np
from evaluation.growth_comparison import compare, fit_predict
from evaluation.five_year import complete_panel

class TestGrowthComparison(unittest.TestCase):
    def test_no_target_or_terminal_leakage(self):
        rows=complete_panel(); target=rows[0].copy(); train=[r.copy() for r in rows[1:]]
        p=fit_predict(train,target,'ridge_growth')
        for r in train: r['r2004']='99999'
        for year in range(2000,2005): target[f'r{year}']='99999'
        np.testing.assert_allclose(p,fit_predict(train,target,'ridge_growth'))
    def test_scores(self):
        r=compare(); self.assertEqual(len(r['rows']),8)
        self.assertEqual(r['scores']['calibrated']['under'],6)
        self.assertLess(r['scores']['saturation_recovery']['wape'],r['scores']['calibrated']['wape'])
