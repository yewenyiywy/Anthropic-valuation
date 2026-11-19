import unittest
import numpy as np
from evaluation.covariance_factors import data, transform, fit, anchored

class CovarianceTest(unittest.TestCase):
    def test_residual_orthogonality(self):
        train,ext=data()
        X,_,_=transform(train,ext[0],'residual',4)
        G=X.T@X
        np.testing.assert_allclose(G,np.diag(np.diag(G)),atol=1e-9)
    def test_future_endpoint_invariance(self):
        train,ext=data(); r=ext[0]
        for fn in (lambda x:fit(train,x,'ridge',4),lambda x:anchored(train,x,16)):
            np.testing.assert_allclose(fn(r),fn(dict(r,r2004='100000')))
    def test_shrink_whitening(self):
        train,ext=data()
        X,_,C=transform(train,ext[0],'shrink_cov',.5)
        self.assertTrue(np.isfinite(X).all())
        self.assertGreater(np.linalg.eigvalsh(.5*C+.5*np.eye(4)).min(),0)
