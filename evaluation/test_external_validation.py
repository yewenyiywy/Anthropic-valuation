import unittest
from evaluation.external_validation import evaluate, load

class ExternalValidationTest(unittest.TestCase):
    def test_endpoints_do_not_change_forecasts(self):
        a=evaluate()
        rows=load()
        for r in rows:
            if r['status']=='observed': r['r2004']=str(float(r['r2004'])*10)
        b=evaluate(rows)
        self.assertEqual([r['pred'] for r in a['rows']],[r['pred'] for r in b['rows']])
    def test_censoring(self):
        a=evaluate()
        self.assertEqual(len(a['rows']),6)
        self.assertEqual(len(a['censored']),2)
