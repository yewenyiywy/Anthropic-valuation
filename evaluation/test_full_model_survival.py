import unittest
import numpy as np
from evaluation.full_model_survival import fit, run
from models.customer_markov import transition
from models.joint_customer_states import forecast_joint

class FullModelSurvivalTests(unittest.TestCase):
    def test_component_fit(self):
        r=fit()
        self.assertLess(r['weibull']['mae'],r['constant']['mae'])
        self.assertTrue(all(a>b for a,b in zip(r['seed_hazards'],r['seed_hazards'][1:])))
    def test_competing_risk_probability_mass(self):
        r=fit(); p=np.asarray(transition('base',seed_hazards=r['seed_hazards'],seed_cif=r['seed_cif']))
        self.assertTrue(np.all(p>=0)); np.testing.assert_allclose(p.sum(axis=1),1)
        risk=1.; graduated=0.
        for i in range(4):
            graduated+=risk*p[i,5]; risk*=p[i,i+1]
            self.assertAlmostEqual(graduated,r['seed_cif'][i])
    def test_full_engine(self):
        r=fit(); rows,ev,eq=forecast_joint(seed_hazards=r['seed_hazards'],seed_cif=r['seed_cif'])
        self.assertEqual(len(rows),10)
        self.assertTrue(all(np.isfinite([ev,eq])))
        self.assertGreater(rows[0]['vendor_mass'][2],0)
        self.assertNotEqual(rows,forecast_joint()[0])
    def test_reproducible(self):
        self.assertEqual(run(2),run(2))
