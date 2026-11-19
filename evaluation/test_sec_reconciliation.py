import csv
import unittest
from models.valuation import ROOT

def rows(name): return list(csv.DictReader(open(ROOT/'data'/name)))

class SecReconciliation(unittest.TestCase):
    """Every SEC figure used by the margin/growth/exit components must be
    reconciled to the filed document, not only to XBRL."""
    def setUp(self):
        self.rec={(r['accn'],r['family'],r['field']):r for r in rows('sec_reconciliation.csv')}
    def check(self,accn,family,field,value):
        if value in ('',None) or float(value)==0: return
        r=self.rec.get((accn,family,field)); self.assertIsNotNone(r,(accn,family,field))
        self.assertAlmostEqual(float(r['xbrl_value_usd_b']),abs(float(value)),places=6)
        self.assertTrue(r['status'].startswith('reconciled'))
        reported=int(r['reported_figure'].replace(',',''))
        scale=1e6 if r['reported_unit']=='USD thousands' else 1e3
        self.assertEqual(reported,round(abs(float(value))*scale))
    def test_stage4_inputs(self):
        for r in rows('stage4_origin_inputs.csv'):
            for f in ('revenue','revenue_prior','cfo','capex_ppe','capex_software','sbc'): self.check(r['accn'],r['family'],f,r[f])
    def test_stage4_labels(self):
        for r in rows('stage4_margin_labels.csv'):
            if r['endpoint']!='standalone': continue
            for f in ('revenue','cfo','capex_software','sbc'): self.check(r['accn'],r['family'],f,r[f])
            if r['family']=='workday':
                self.check(r['accn'],'workday','capex_other_productive','0.243694'); self.check(r['accn'],'workday','capex_owned_real_estate','0.099308')
                self.assertAlmostEqual(float(r['capex_ppe']),0.243694+0.099308)
            else: self.check(r['accn'],r['family'],'capex_ppe',r['capex_ppe'])
    def test_dev_panel(self):
        for r in rows('margin_dev_panel.csv'):
            fam=r['family']+'@'+r['origin'][:4]
            for f in ('revenue','revenue_prior','cfo','capex_ppe','capex_software','sbc'): self.check(r['accn'],fam,f,r[f])
            for f in ('revenue','cfo','capex_ppe','capex_software','sbc'): self.check(r['target_accn'],fam,f,r['target_'+f])
    def test_exit_events_two_sources(self):
        for r in rows('stage4_exit_events.csv'):
            self.assertTrue(r['source'].startswith('https://') and r['second_source'].startswith('https://'))
            self.assertNotEqual(r['source'],r['second_source'])

if __name__=='__main__': unittest.main()
