import unittest
from models.accounting import anthropic_anchor,cashflow,ratios
from models.joint_customer_states import forecast_joint
from models.valuation import SCENARIOS

class AccountingTests(unittest.TestCase):
    def test_anchor_ebit(self):
        r=anthropic_anchor();self.assertAlmostEqual(1-r['compute']-r['other'],r['ebit'])
    def test_capex_not_tax_deductible(self):
        a=dict(compute=.4,other=.3,da=.05,capex=.1)
        r=cashflow(100,90,0,a);s=cashflow(100,90,0,dict(a,capex=.2))
        self.assertEqual(r['tax'],s['tax']);self.assertAlmostEqual(r['fcf']-s['fcf'],10)
    def test_commitment_floor_no_double_count(self):
        r=cashflow(100,100,50,dict(compute=.4,other=.3,da=.04,capex=.1))
        self.assertAlmostEqual(r['compute_cash'],50);self.assertAlmostEqual(r['commitment_shortfall'],12)
    def test_full_engine_candidate(self):
        a=anthropic_anchor();r,_,_=forecast_joint(accounting=dict(anchor=a));self.assertAlmostEqual(r[0]['accounting']['ebit']/r[0]['revenue'],a['ebit'])
        self.assertAlmostEqual(r[0]['fcf'],r[0]['accounting']['fcf']);self.assertEqual(len(r),10)
