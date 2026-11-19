import unittest
from models.customer_markov import PARAM, transition, step_count, seed_birth, forecast_markov

class TestMarkov(unittest.TestCase):
    def test_stochastic(self):
        for name in PARAM:
            for row in transition(name):
                self.assertAlmostEqual(sum(row),1)
                self.assertTrue(all(0<=x<=1 for x in row))
    def test_cumulative_incidence(self):
        for name,a in PARAM.items():
            P=transition(name); n=[1.]+[0.]*8; cumulative=0.
            for i,target in enumerate(a['seed_cif']):
                cumulative+=n[i]*P[i][5]
                self.assertAlmostEqual(cumulative,target)
                n=step_count(n,P)
    def test_open_chain(self):
        P=transition('base'); n=[1000]+[0]*8
        for t in range(10):
            n=step_count(n,P,100)
            self.assertAlmostEqual(sum(n),1000+100*(t+1))
        self.assertGreater(n[7],0)
    def test_birth_budget(self):
        for name in PARAM:
            rows,_,_=forecast_markov(name)
            self.assertTrue(all(0<=x['birth_revenue']<=x['birth_budget']+1e-10 for x in rows))
            self.assertTrue(all(x['birth_revenue']==0 for x in forecast_markov(name,birth_multiplier=0)[0]))
    def test_no_migration(self):
        P=transition('base',False)
        self.assertEqual(P[0][5],0)
        self.assertEqual(P[5][7],0)

if __name__=='__main__': unittest.main()
