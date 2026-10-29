import unittest
from fractions import Fraction
from pickal_aggregate_bounds import analyze,_bound,ARM_COUNTS
class TestPublishedAggregate(unittest.TestCase):
 def test_1_arm_counts_and_sample(self):
  x=analyze();self.assertEqual(list(ARM_COUNTS.values()),[86,81,75,95,90]);self.assertEqual(x['sample_in_five_reported_arms'],427)
 def test_2_anova_case_differences(self):
  x=analyze();self.assertEqual(x['performance_anova_cases_inferred_from_df'],427);self.assertEqual(x['interest_motivation_anova_cases_inferred_from_df'],345);self.assertEqual(x['cases_not_in_motivation_anova'],82);self.assertEqual(x['cases_not_in_treatment_check_anova'],83)
 def test_3_published_primary_contrast(self):
  self.assertEqual(analyze()['conditional_interest_high_up_minus_control']['observed_group_mean_difference'],'37/100')
 def test_4_conditional_extrema_exact(self):
  x=analyze()['conditional_interest_high_up_minus_control'];self.assertEqual(Fraction(x['conditional_lower']),Fraction(37,100)+Fraction(82,86)*(1-Fraction(337,100)));self.assertEqual(Fraction(x['conditional_upper']),Fraction(37,100)-Fraction(82,90)*(1-Fraction(3)))
 def test_5_finite_feasible_witnesses(self):
  x=analyze()['conditional_interest_high_up_minus_control'];self.assertEqual(x['lower_witness_missing_higher_up_control_others'],[82,0,0]);self.assertEqual(x['upper_witness_missing_higher_up_control_others'],[0,82,0]);self.assertLess(float(x['conditional_lower']),0);self.assertGreater(float(x['conditional_upper']),0)
 def test_6_competence_secondary_crosses_zero(self):
  x=analyze()['conditional_competence_high_up_minus_control'];self.assertEqual(x['observed_group_mean_difference'],'1/2');self.assertLess(float(x['conditional_lower']),0);self.assertGreater(float(x['conditional_upper']),0)
 def test_7_reject_nonpaper_and_no_ITT_claim(self):
  with self.assertRaises(TypeError):_bound(3.37,Fraction(3),345)
  with self.assertRaises(ValueError):_bound(Fraction(337,100),Fraction(3),-10)
  self.assertIn('not a re-estimated ITT',analyze()['blocked_inferences']);self.assertEqual(analyze()['scientific_grade'],'0/3')
if __name__=='__main__':unittest.main(verbosity=2)
