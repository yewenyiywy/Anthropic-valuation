import unittest
from evaluation.five_year import evaluate
from models.joint_customer_states import forecast_joint

class TestFiveYear(unittest.TestCase):
    def test_endpoint(self):
        r=evaluate()
        self.assertEqual(r['scores']['original']['n'],8)
        self.assertEqual(set(r['censored']),{'AOL','Excite@Home'})
        self.assertLess(r['scores']['calibrated']['wape'],r['scores']['original']['wape'])
    def test_sensitivity(self):
        self.assertNotEqual(forecast_joint()[2],forecast_joint(growth_half_life=1)[2])
