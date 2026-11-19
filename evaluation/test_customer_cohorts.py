import unittest
from models.customer_cohorts import *

class TestCustomerCohorts(unittest.TestCase):
    def test_hazards(self):
        h=hazards(); d=risk_data()
        self.assertAlmostEqual((1-h[0])**5,d['information_new_survival5'])
        self.assertAlmostEqual((1-h[1])**5,d['information_survival10']/d['information_new_survival5'])
        for name in INPUTS:
            self.assertAlmostEqual(sum(INPUTS[name]['weights']),1)
            for s,p in zip(customer_retention(name),h):
                self.assertGreaterEqual(s,0)
                self.assertLessEqual(s,1-p+1e-10)

    def test_invoice_and_caps(self):
        for name in INPUTS:
            rows,_,_=forecast_cohorts(name)
            for row in rows:
                self.assertAlmostEqual(sum(row['group'].values()),row['enterprise'])
                self.assertAlmostEqual(row['enterprise']+row['personal'],row['revenue'])
                self.assertLessEqual(row['enterprise'],row['cap']+1e-8)
            self.assertGreater(rows[-1]['new'],0)

    def test_cancellation_comparative_statics(self):
        for name in INPUTS:
            self.assertLessEqual(forecast_cohorts(name)[2],forecast_cohorts(name,no_commercial_loss=True)[2])
