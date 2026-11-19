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
