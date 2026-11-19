import csv
import unittest
from evaluation import margin_path as mp

class MarginPath(unittest.TestCase):
    def test_freeze_record_matches_artifacts(self):
        rec=mp.verify(); self.assertEqual(rec['selected'],'leverage')
    def test_inputs_are_origin_known(self):
        for r in mp.read(mp.INPUTS)+mp.read(mp.DEV):
            self.assertLessEqual(r['filed'],r['origin']); self.assertLess(r['fy_end'],r['origin'])
    def test_stage4_rows_carry_no_outcomes(self):
        self.assertFalse([k for k in mp.read(mp.INPUTS)[0] if k.startswith('target')])
        self.assertEqual(len(mp.read(mp.INPUTS)),17)
    def test_development_is_exposed_families_only(self):
        from evaluation.validation_gate import EXPOSED
        self.assertTrue(all(r['family'] in EXPOSED for r in mp.read(mp.DEV)))
        roster={r['family'] for r in csv.DictReader(open(mp.ROOT/'data/stage4_candidate_universe.csv')) if r['eligibility']=='candidate'}
        self.assertEqual(roster,{r['family'] for r in mp.read(mp.INPUTS)})
    def test_selection_rule_reproducible(self):
        d=mp.development(); self.assertEqual(d['selected'],'leverage'); self.assertEqual(d['families'],5)
        self.assertGreaterEqual(d['candidates']['hold']['loo_mae_pp']-d['candidates']['leverage']['loo_mae_pp'],mp.SIMPLICITY_PP)
    def test_models(self):
        x=dict(m0=.1,g0=.5,h=6)
        self.assertEqual(mp.predict('hold',None,x),.1); self.assertAlmostEqual(mp.predict('leverage',.4,x),.3)
        self.assertAlmostEqual(mp.predict('converge',.3,dict(x,h=3)),.2)

if __name__=='__main__': unittest.main()

class Stage4Scored(unittest.TestCase):
    def test_score_reproduces_record(self):
        import json
        rec=json.load(open(mp.ROOT/'evaluation/stage4_margin_score.json'))
        self.assertEqual(mp.score(mp.ROOT/'data/stage4_margin_labels.csv'),rec)
        self.assertFalse(rec['promoted']); self.assertEqual(rec['scores']['all']['n'],11)
    def test_acquired_issuers_unlabelled(self):
        lab={r['family']:r for r in mp.read(mp.ROOT/'data/stage4_margin_labels.csv')}
        for f in ('linkedin','netsuite','ultimate software group','athenahealth','medidata solutions','coupa'):
            self.assertEqual(lab[f]['target_margin'],'')
    def test_development_panel_pooled(self):
        from evaluation.margin_development import run
        d=run(); self.assertEqual((d['n'],d['families']),(18,16))
        self.assertLess(d['econ']['loo']['converge3']['loo_mae_pp'],d['econ']['loo']['hold']['loo_mae_pp'])
