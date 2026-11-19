import csv, unittest
from pathlib import Path

D = Path(__file__).resolve().parents[1] / 'data'
OK = {'matched', 'matched_targeted', 'matched_derived', 'matched_replacement_doc', 'matched_second_doc',
      'matched_second_source', 'corrected', 'corrected_precision', 'redefined', 'not_reproducible', 'pending', 'partial'}


def rows():
    return list(csv.DictReader(open(D / 'legacy_reconciliation.csv')))


class LegacyReconciliation(unittest.TestCase):
    def test_statuses(self):
        self.assertTrue(all(x['status'] in OK for x in rows()))

    def test_no_unreconciled_sec_value(self):
        sec = [x for x in rows() if x['cited_source'].startswith('https://www.sec.gov/') and x['field']]
        self.assertGreaterEqual(len(sec), 295)
        self.assertFalse([x for x in sec if x['status'] in ('pending', 'not_reproducible')])

    def test_corrections_applied(self):
        eq = {r['company']: r for r in csv.DictReader(open(D / 'cloud_equity_cohort.csv'))}
        self.assertAlmostEqual(float(eq['PayPal']['cash20']), 13.083)
        self.assertAlmostEqual(float(eq['ServiceNow']['cash20']), 3.092036)
        self.assertAlmostEqual(float(eq['Shopify']['cash20']), 6.387967)
        cv = {r['company']: r for r in csv.DictReader(open(D / 'cloud_company_vintage.csv'))}
        self.assertAlmostEqual(float(cv['Salesforce']['da20']), 2.135)

    def test_no_dead_links(self):
        for f in D.glob('*.csv'):
            t = f.read_text()
            if f.name == 'legacy_reconciliation.csv':
                continue
            self.assertNotIn('/Archives/edgar/data/110852425000006/', t, f.name)
            self.assertNotIn('/Archives/edgar/vprr/', t, f.name)


if __name__ == '__main__':
    unittest.main()
