import hashlib, unittest
from pathlib import Path
from evaluation import margin_scale as M
from models.valuation import SCENARIOS

ROOT = Path(__file__).resolve().parents[1]


class MarginScale(unittest.TestCase):
    def test_frozen_inputs(self):
        for line in (ROOT / 'evaluation' / 'margin_scale_freeze.sha256').read_text().split('\n'):
            if not line.strip(): continue
            h, p = line.split()
            self.assertEqual(hashlib.sha256((ROOT / p).read_bytes()).hexdigest(), h, p)

    def test_scenarios_match_estimator(self):
        est = M.estimates()
        for n in ('bear', 'base', 'bull'):
            for k in ('cost_ratio', 'other_ratio', 'wacc'):
                self.assertAlmostEqual(SCENARIOS[n][k], est[n][k], places=3, msg=(n, k))

    def test_ordering(self):
        e = M.estimates()
        self.assertTrue(e['bear']['m_star'] < e['base']['m_star'] < e['bull']['m_star'])
        self.assertTrue(e['bull']['wacc'] < e['base']['wacc'] < e['bear']['wacc'])
        for n in e: self.assertGreater(e[n]['wacc'], SCENARIOS[n]['terminal_growth'])


if __name__ == '__main__':
    unittest.main()


class BlockDraws(unittest.TestCase):
    def test_revenue_bounds_match_comparables(self):
        import models.joint_customer_states as J
        q = M.target_d(M.load())['revenue_multiple']; lo, hi = J.revenue_bounds(); m0 = J._rev_multiple(0.)
        self.assertAlmostEqual(J._rev_multiple(hi), m0 * q['q90'] / q['q50'], places=3)
        self.assertAlmostEqual(J._rev_multiple(lo), m0 * q['q10'] / q['q50'], places=3)

    def test_median_cost_draw_is_base(self):
        d = M.draw_costs(.5, .5); e = M.estimates()['base']
        self.assertAlmostEqual(1 - d['cost_ratio'] - d['other_ratio'], e['m_star'], places=6)
        q = M.empirical()
        self.assertGreaterEqual(1 - M.draw_costs(.999, .5)['cost_ratio'] - M.draw_costs(.999, .5)['other_ratio'], q['m'].max() - 1e-9)
