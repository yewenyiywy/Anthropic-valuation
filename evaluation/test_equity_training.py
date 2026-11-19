import unittest
from evaluation.equity_training import training_rows, transfer_rows, fit, predict, run, BASE

class EquityTrainingTests(unittest.TestCase):
    def test_disjoint_issuers(self):
        self.assertFalse({r['company'] for r in training_rows()} & {r['company'] for r in transfer_rows()})
    def test_prediction_ignores_future_labels(self):
        r=training_rows()[0]
        self.assertEqual(predict(r,BASE),predict(dict(r,cap5=999999,revenue5=999999),BASE))
    def test_trials_and_status(self):
        r=run()
        self.assertEqual(len(r['trials']),60)
        self.assertEqual(len(r['premium_trials']),11)
        self.assertIn('blocked',r['status'])
        self.assertLessEqual(r['train_fitted']['logmae'],r['train_baseline']['logmae'])
