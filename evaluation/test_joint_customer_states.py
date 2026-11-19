import unittest
import numpy as np
from models.joint_customer_states import *

class TestJoint(unittest.TestCase):
    def test_probabilities(self):
        for p in (MACRO,HEALTH_P,*[health_matrix(k) for k in range(3)]):
            self.assertTrue(np.all(p>=0)); np.testing.assert_allclose(p.sum(1),1)
        for k in range(3):
            for g in range(4):
                p=vendor_matrix('base',g,k); self.assertTrue(np.all(p>=0)); np.testing.assert_allclose(p.sum(1),1)
    def test_posterior_and_revenue(self):
        self.assertAlmostEqual(posterior(PRIOR[0],True).sum(),1)
        self.assertAlmostEqual(reward(initial_tensor([1]*8)),8)
    def test_baseline(self):
        self.assertAlmostEqual(forecast_joint(health=False,duration=False,competition=False)[2],forecast_markov('base')[2],places=8)
    def test_reproducible(self):
        self.assertEqual(simulate(n=4),simulate(n=4))
    def test_winter(self):
        self.assertLess(forecast_joint(regime_path=[0]*10)[2],forecast_joint()[2])

if __name__=='__main__': unittest.main()
