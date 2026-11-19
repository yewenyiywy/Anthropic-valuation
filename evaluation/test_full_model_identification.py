import unittest
import numpy as np
from evaluation.full_model_identification import TRUTH,TRAIN,output,invariances

class FullIdentificationTests(unittest.TestCase):
    def test_exact_and_local_invariances(self):
        for v in invariances().values(): self.assertLess(v,1e-10)
    def test_augmented_information_rank(self):
        z=np.log(TRUTH); h=1e-5
        def rank(aug):
            j=np.column_stack([(output(np.exp(z+h*e),TRAIN,aug)-output(np.exp(z-h*e),TRAIN,aug))/(2*h) for e in np.eye(len(z))])
            s=np.linalg.svd(j,compute_uv=False)
            return sum(s>s[0]*1e-6)
        self.assertEqual(rank(False),6)
        self.assertEqual(rank(True),9)
