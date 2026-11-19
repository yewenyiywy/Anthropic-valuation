import unittest
import numpy as np
from evaluation.competing_risk import estimate, transition, acquisition_npv, run

class CompetingRiskTests(unittest.TestCase):
    def test_five_year_identity(self):
        _,p,_=estimate(['a','b','c'],{'b':{'event':'merger'}})
        np.testing.assert_allclose(np.linalg.matrix_power(transition(p),5)[0],p)
    def test_exit_counts(self):
        r=run()
        self.assertEqual(r['counts'],[8,1,1])
        self.assertEqual(r['external_counts'],[6,1,1])
    def test_deal_cost(self):
        self.assertEqual(acquisition_npv(0,1,.2,2,.1,5),0)
        self.assertLess(acquisition_npv(1,1,.2,2,.1,5),0)
