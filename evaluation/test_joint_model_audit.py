import unittest
from evaluation.joint_model_audit import vintage,train,profile,predict,evaluate
from models.joint_customer_states import forecast_joint

class TestJointAudit(unittest.TestCase):
    def test_no_future_leakage(self):
        rows=vintage()
        a=evaluate(rows)
        b=evaluate([dict(r,r2025='9999',cfo25='9999',cap25='9999') for r in rows])
        self.assertEqual([r['pred'] for r in a['rows']],[r['pred'] for r in b['rows']])
    def test_strict_missing(self):
        p,t=train()
        with self.assertRaises(ValueError): profile(vintage()[0],p,t,strict=True)
    def test_company_specific_cashflow(self):
        p,t=train(); r=vintage()[0]
        self.assertNotEqual(predict(r,p,t)['equity5'],predict(dict(r,operating_income20='0'),p,t)['equity5'])
    def test_engine_default_unchanged(self):
        self.assertAlmostEqual(forecast_joint()[2],249.22,places=1)
