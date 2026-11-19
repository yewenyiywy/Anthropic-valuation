import unittest
import numpy as np
from evaluation.fundamental_growth import panel, fit, compare

class TestFundamentalGrowth(unittest.TestCase):
    def test_holdout(self):
        rows=panel(); target=rows[0].copy(); train=[r.copy() for r in rows[1:]]
        p=fit(train,target,'margin_size')
        for r in train: r.update(r2004='999',r2005='999')
        target.update(r2000='999',r2001='999',r2002='999',r2003='999',r2004='999',r2005='999')
        np.testing.assert_allclose(p,fit(train,target,'margin_size'))
    def test_endpoints(self):
        r=compare(); self.assertEqual(r['scores']['2005']['size']['n'],8)
        self.assertLess(r['scores']['2004']['size']['wape'],r['scores']['2004']['blend']['wape'])
