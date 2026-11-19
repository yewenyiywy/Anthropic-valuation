import unittest
from evaluation.company_oos import panel, predict, run, calibrated

class TestCompanyOOS(unittest.TestCase):
    def test_panel(self):
        self.assertEqual(len(panel()),10)
        self.assertEqual(len({r['company'] for r in panel()}),10)
    def test_company_specific(self):
        self.assertNotEqual(predict(1,2),predict(1,3))
        self.assertAlmostEqual(predict(1,2)[0],2*2**.5)
    def test_holdouts(self):
        r=run()
        self.assertEqual(r['fy2000']['n'],10)
        self.assertEqual(r['available_2001_04']['n'],23)
        self.assertLess(r['fy2000']['mape'],r['flat2000']['mape'])
        self.assertGreater(r['available_2001_04']['mape'],1)
    def test_preperiod(self):
        self.assertEqual(calibrated()['fy2000']['n'],10)
