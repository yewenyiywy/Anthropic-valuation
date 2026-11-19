import unittest
import numpy as np
from evaluation.structural_factors import dataset, features, design, fit, anthropic_diagnostics

class StructuralFactorTests(unittest.TestCase):
    def test_cash_burn_pressure(self):
        train,_=dataset()
        amazon=next(r for r in train if r['company']=='Amazon')
        self.assertAlmostEqual(np.expm1(features(amazon)[7]),(.287055+.090875)/.133309)
    def test_missing_factors_neutral(self):
        train,ext=dataset()
        r=next(r for r in ext if r['company']=='CMGI')
        _,z,_=design(train,r,('investment','liquidity'),.5)
        np.testing.assert_allclose(z,0)
    def test_outcome_invariance(self):
        train,ext=dataset(); r=ext[0]
        np.testing.assert_allclose(fit(train,r,('investment',),16,.5),
                                   fit(train,dict(r,r2004='99999'),('investment',),16,.5))
    def test_concentration_bound(self):
        self.assertAlmostEqual(anthropic_diagnostics()['top5_hhi_lower_bound'],.0125)
