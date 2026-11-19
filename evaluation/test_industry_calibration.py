import unittest
from models.industry_calibration import *

class TestIndustryCalibration(unittest.TestCase):
    def test_source_totals(self):
        raw=sector_inputs()
        self.assertAlmostEqual(sum(a for _,a,b in raw),234.6)
        self.assertAlmostEqual(sum(b for _,a,b in raw),631.4)
        self.assertAlmostEqual(sum(sector_budget(0).values()),176.8)

    def test_hazard_conversion(self):
        p=annual_probability(.08,5)
        self.assertAlmostEqual(1-(1-p)**5,.08)
        self.assertLess(p*DISTRESS_EXIT_FRACTION,p)

    def test_caps_and_invoice_reconciliation(self):
        for name,e,c5,c10,rows,ev,eq in run():
            for r in rows:
                self.assertLessEqual(r['revenue'],r['ceiling']+1e-8)
                self.assertAlmostEqual(r['revenue'],sum(r[k] for k in ('startup','trial','mature','personal','enterprise_subscription')))
            self.assertLessEqual(rows[4]['revenue']-rows[4]['personal'],c5+1e-8)
            self.assertLessEqual(rows[9]['revenue']-rows[9]['personal'],c10+1e-8)
