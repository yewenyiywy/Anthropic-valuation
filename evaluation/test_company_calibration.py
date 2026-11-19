import unittest
from evaluation.company_calibration import anchors, vintage, benchmark, anthropic
from models.joint_customer_states import forecast_joint

class CompanyCalibrationTests(unittest.TestCase):
    def test_universe(self):
        self.assertEqual([int(r['rank']) for r in vintage()],list(range(1,11)))
        self.assertEqual(len(benchmark()[0]),5)
    def test_anchors(self):
        a=anchors()
        self.assertAlmostEqual(a['compute_infrastructure']+a['other_opex'],34.502)
        self.assertAlmostEqual(a['adjusted_cash']-a['adjusted_convertibles'],122.609)
        self.assertTrue(a['customers_ge100k']>a['customers_ge1m']>a['customers_ge10m'])
    def test_override(self):
        self.assertLess(forecast_joint(scenario_overrides={'cost_ratio':.60})[1],forecast_joint()[1])
        with self.assertRaises(ValueError): forecast_joint(scenario_overrides={'typo':1})
        a=anthropic(n=4); self.assertGreater(a['mean_equity'][0],a['mean_equity'][1]); self.assertGreater(a['mean_equity'][1],a['mean_equity'][2])
    def test_incomplete_profile_rejected(self):
        with self.assertRaises(ValueError): forecast_joint(profile={})
        with self.assertRaises(ValueError): forecast_joint(profile={},o={'run_rate':10})
