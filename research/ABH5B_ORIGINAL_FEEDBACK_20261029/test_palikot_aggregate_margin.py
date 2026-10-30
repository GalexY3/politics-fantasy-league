import unittest
from fractions import Fraction as F
from palikot_aggregate_margin import analyze,decompose,PUBLISHED
class PublishedMarginalDecompositionTests(unittest.TestCase):
 def test_reconstructed_mean_and_original_rct_differences(self):
  x=analyze()['periods'];self.assertAlmostEqual(x['4_weeks']['treatment_mean_reconstructed'],.324);self.assertAlmostEqual(x['12_weeks']['treatment_mean_reconstructed'],.696)
 def test_four_week_active_difference(self):
  x=analyze()['periods']['4_weeks'];self.assertAlmostEqual(x['activity_percentage_point_difference'],3.1)
 def test_twelve_week_active_difference_is_not_four_week(self):
  x=analyze()['periods']['12_weeks'];self.assertAlmostEqual(x['activity_percentage_point_difference'],2.1)
 def test_exact_decomposition_both_periods(self):
  for v in PUBLISHED.values():
   a=decompose(v);self.assertTrue(a['exact_algebra_check']);self.assertAlmostEqual(a['symmetric_extensive_component']+a['symmetric_intensive_component'],a['difference'])
 def test_components_not_causal_and_different_periods(self):
  a=analyze();self.assertTrue(any('POST-TREATMENT SELECTED' in s for s in a['critical_assumptions']));self.assertTrue(any('windows differ' in s for s in a['critical_assumptions']));self.assertIn('not isolated leaderboard impact',a['no_claims'])
 def test_falsifiers_invalid_and_missing_rates(self):
  with self.assertRaises(ValueError):decompose({**PUBLISHED['4_weeks'],'control_active':F(0)})
  with self.assertRaises(ValueError):decompose({'control_stories':F(1)})
 def test_source_is_original_and_uncertainty_undetermined(self):
  a=analyze();self.assertEqual(a['grade'],'0/3');self.assertIn('joint covariance',a['critical_assumptions'][2]);self.assertIn('9327',a['design'])
if __name__=='__main__':unittest.main(verbosity=2)
