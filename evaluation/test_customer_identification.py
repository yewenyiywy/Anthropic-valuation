import unittest
from evaluation.customer_identification import stock_flow_bounds, evidence, report

class TestCustomerIdentification(unittest.TestCase):
    def test_account_bounds(self):
        b=stock_flow_bounds(295,361)
        self.assertEqual(b['gross_entries_min'],66)
        self.assertEqual(b['gross_entries_max'],361)
        self.assertEqual(b['retention_max'],1)
    def test_decrease(self):
        self.assertEqual(stock_flow_bounds(100,70)['retention_max'],.7)
    def test_vintage_and_gate(self):
        self.assertEqual(len(evidence()),5)
        r=report();self.assertEqual(r['eligible'],0);self.assertIsNone(r['equity_wape'])
        self.assertEqual(r['status'],'BLOCKED')
