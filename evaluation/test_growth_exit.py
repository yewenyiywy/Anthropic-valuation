import os
import unittest
from evaluation import growth_persistence as gp, saas_exit as se
from evaluation.cloud_equity import inputs, predict_value
from evaluation.external_validation import calibrate
from evaluation.fundamental_growth import panel as dotcom_panel
from models.valuation import ROOT

class GrowthPersistence(unittest.TestCase):
    def test_panel_and_fit(self):
        d=gp.run(); self.assertEqual((d['n'],d['families']),(18,16))
        self.assertEqual(d['fit'],dict(half_life=4.0,g_inf=0.065))
        self.assertLess(d['loo']['decay_fit']['loo_mae_log'],d['loo']['hold_growth']['loo_mae_log'])
    def test_engine_equivalent_g0_inside_panel(self):
        e=gp.engine_equivalent_g0(); lo,hi=gp.run()['g0_range']
        for v in e['equivalent_g0'].values(): self.assertTrue(lo<=v<=hi)
        self.assertGreater(e['anthropic_observed_g0'],hi)
    def test_cum_matches_constant_growth(self):
        self.assertAlmostEqual(gp.cum(.1,5,.1,3),.5)

class SaasExit(unittest.TestCase):
    def test_universe_counts(self):
        d=se.run()
        self.assertEqual(d['episodes']['cloud2015']['counts'],dict(standalone=5,acquired=5,bankrupt=0))
        self.assertEqual(d['episodes']['cloud2020']['counts'],dict(standalone=13,acquired=1,bankrupt=0))
        self.assertEqual(d['pooled']['n'],24)
    def test_acquired_value_not_zero(self):
        for r in se.read('stage4_exit_events.csv'):
            self.assertGreater(float(r['headline_value_usd_b']),0); self.assertTrue(r['source'].startswith('https://'))
    def test_policy_documented(self):
        self.assertTrue(os.path.exists(ROOT/'evaluation/acquisition_endpoint_policy.md'))

class HorizonEquity(unittest.TestCase):
    def test_default_horizon_is_five(self):
        t=dotcom_panel(); th=calibrate(t); r=inputs()[0]
        self.assertEqual(predict_value(r,t,th)['dcf'],predict_value(r,t,th,horizon=5)['dcf'])
        with self.assertRaises(ValueError): predict_value(r,t,th,horizon=0)

if __name__=='__main__': unittest.main()
