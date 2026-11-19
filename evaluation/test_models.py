import unittest
from models.valuation import *

class TestModels(unittest.TestCase):
    def test_source_integrity(self):
        with (ROOT/"data/observations.csv").open() as file:
            rows=list(csv.DictReader(file))
        self.assertEqual(len(rows),len({r["id"] for r in rows}))
        for r in rows:
            self.assertTrue(r["source_url"].startswith("https://"))
            self.assertTrue(math.isfinite(float(r["value"])))
    def test_income_reconciliation(self):
        o=observations()
        self.assertAlmostEqual(o["consumption_9m26"]/o["revenue_9m26"],.79,places=2)
        self.assertAlmostEqual(o["cfo_9m26"]-o["capex_9m26"],5.644)
    def test_survival_holdouts(self):
        o=observations()
        data=[v for k,v in o.items() if k.startswith("survival_")]
        errors=[abs(y-sum(data[:i]+data[i+1:])/(len(data)-1)) for i,y in enumerate(data)]
        self.assertLess(sum(errors)/len(errors),.05)
    def test_pilot_break_even(self):
        self.assertEqual(pilot(100,.25,4),100)
    def test_price_volume_break_even(self):
        self.assertEqual(cohort(100,1,2,.5,1),100)
    def test_scenarios(self):
        vals=[]
        for p in SCENARIOS.values():
            rows,ev,equity=forecast(p)
            vals.append(equity)
            for r in rows:
                self.assertGreaterEqual(r["compute"],r["commitment_floor"])
                self.assertAlmostEqual(r["revenue"],sum(r[k] for k in ("startup","trial","mature","subscription")))
        self.assertEqual(vals,sorted(vals))
    def test_reproducibility(self):
        self.assertEqual(monte_carlo(20),monte_carlo(20))
    def test_overlap_and_ceiling(self):
        self.assertAlmostEqual(overlap_factor(.6,.5),.7)
        for p in SCENARIOS.values():
            rows,_,_=forecast(p)
            for r in rows:
                self.assertLessEqual(r['revenue'],r['ceiling']+1e-8)
                self.assertAlmostEqual(r['subscription'],r['personal']+r['enterprise_subscription'])
    def test_commitment_reconciliation(self):
        o=observations()
        self.assertAlmostEqual(sum(commitment_floor(t,o) for t in range(1,20)),o['commit_total'])
    def test_lifecycle_exit(self):
        p=SCENARIOS['base']; o=observations()
        _,tail=lifecycle_tail(100,p,o)
        self.assertAlmostEqual(tail[-1]['alive'],(1-p['exit'])**20)
        self.assertEqual(tail[-1]['year'],30)

if __name__=="__main__":
    unittest.main()
