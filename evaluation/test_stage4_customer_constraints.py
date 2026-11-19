import unittest
from evaluation.stage4_customer_constraints import audit

class TestVintageConstraints(unittest.TestCase):
    def test_constraints(self):
        r=audit(); self.assertEqual(r['observations'],20); self.assertEqual(r['companies'],9)
        b={x['company']:x for x in r['bounds']}
        self.assertEqual(b['Fastly']['gross_entries_min'],39)
        self.assertEqual(b['Datadog']['gross_entries_min'],380)
        self.assertIsNone(b['Twilio']['gross_entries_max'])
