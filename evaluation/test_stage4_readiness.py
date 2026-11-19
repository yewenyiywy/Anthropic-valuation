import unittest
from evaluation.stage4_readiness import audit

class TestStage4(unittest.TestCase):
    def test_roster(self):
        r=audit()
        self.assertEqual((r['total'],r['candidates'],r['excluded']),(20,17,3))
        self.assertEqual(r['episodes'],{'cloud2015':8,'cloud2020':9})
        self.assertEqual(r['status'],'BLOCKED')
        self.assertIsNone(r['equity_wape'])
