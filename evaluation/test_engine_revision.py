import unittest
import numpy as np
from models.valuation import SCENARIOS, lifecycle_tail, EXIT_HAZARD
from models.joint_customer_states import forecast_joint, simulate, draw_parameters, initial_capture, INPUTS
from evaluation.validation_gate import spearman
from evaluation.reverse_dcf import solve

Z=dict(commit_total=0,commit_to_2030=0,commit_next12m=0)

class EngineRevision(unittest.TestCase):
    def test_tail_recentered_drift(self):
        # Survivor long-run growth equals the stated terminal growth.
        p=dict(SCENARIOS['base']); _,t=lifecycle_tail(1.,p,Z,horizon=300,continuation=False)
        g=(t[-1]['revenue']/t[-1]['alive'])/(t[-2]['revenue']/t[-2]['alive'])-1
        self.assertAlmostEqual(g,p['terminal_growth'],places=3)
    def test_continuation_matches_long_explicit_sum(self):
        p=dict(SCENARIOS['base'])
        a,_=lifecycle_tail(1.,p,Z); b,_=lifecycle_tail(1.,p,Z,horizon=600,continuation=False)
        self.assertAlmostEqual(a,b,places=6)
    def test_tail_margin_follows_scenario_costs(self):
        p=dict(SCENARIOS['base'],cost_ratio=.9)
        self.assertLess(lifecycle_tail(1.,p,Z)[0],0)
    def test_shared_exit_hazards(self):
        for n in ('bear','base','bull'): self.assertEqual(SCENARIOS[n]['exit'],EXIT_HAZARD[n])
    def test_base_capture_held(self):
        self.assertIsNone(INPUTS['base']['capture'])
        self.assertAlmostEqual(draw_parameters(0.)[1]['capture'],initial_capture())
    def test_commitment_diagnostics(self):
        for r in forecast_joint()[0]:
            self.assertGreaterEqual(r['idle_commitment_cost'],0)
            self.assertAlmostEqual(max(r['commitment_floor'],r['revenue']*r['cost_ratios'][0]),r['compute_cost'])
    def test_cost_path_converges_from_reported_ratios(self):
        from models.accounting import anthropic_anchor
        a=anthropic_anchor(); rows=forecast_joint()[0]; p=SCENARIOS['base']
        self.assertAlmostEqual(rows[0]['cost_ratios'][0],p['cost_ratio']+(a['compute']-p['cost_ratio'])*2**(-1/3))
        self.assertLess(abs(rows[-1]['cost_ratios'][1]-p['other_ratio']),abs(rows[0]['cost_ratios'][1]-p['other_ratio']))
        self.assertEqual(forecast_joint(cost_half_life=None)[0][0]['cost_ratios'],(p['cost_ratio'],p['other_ratio'],p['capex']))
    def test_parameter_uncertainty_widens(self):
        a=simulate(n=64,parameters=False); b=simulate(n=64)
        self.assertGreater(b['p95']-b['p05'],a['p95']-a['p05'])
        self.assertEqual(simulate(n=8),simulate(n=8))
    def test_spearman(self):
        self.assertAlmostEqual(spearman([1,2,3],[10,20,30]),1)
        self.assertAlmostEqual(spearman([1,2,3],[3,2,1]),-1)
    def test_reverse_dcf_wacc_roundtrip(self):
        x=forecast_joint(scenario_overrides=dict(wacc=.10))[2]
        self.assertAlmostEqual(solve(x,'wacc')['implied'],.10,places=3)

if __name__=='__main__': unittest.main()
