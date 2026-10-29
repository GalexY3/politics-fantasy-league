import unittest
from kloc_aggregate_ci import analyze,TABLE
class TestKloc(unittest.TestCase):
 def test_exact_table_3_all_five_outcomes(self):
  self.assertEqual(tuple(TABLE),('login','active_time','learning','practice','hardest_subject'))
  self.assertEqual(tuple(v['beta'] for v in TABLE.values()),(.008,.009,.008,.002,.007))
  self.assertEqual(tuple(v['se'] for v in TABLE.values()),(.006,.016,.014,.020,.015))
 def test_panel_rows_not_n_users(self):
  x=analyze();self.assertEqual(x['eligible_users_reported'],3762)
  self.assertEqual(x['rows']['active_time']['n_panel'],108171)
  self.assertEqual(x['rows']['hardest_subject']['n_panel'],79956)
 def test_primary_95_interval_precise(self):
  x=analyze()['rows']['active_time']['ci95_normal'];self.assertAlmostEqual(x[0],-.02235942,places=6);self.assertAlmostEqual(x[1],.04035942,places=6)
 def test_bonf_multiple_endpoint_reverses_threshold(self):
  x=analyze();self.assertTrue(x['primary_active_time']['single_endpoint_upper_below_0_05_SD'])
  self.assertFalse(x['primary_active_time']['five_endpoint_bonf_upper_below_0_05_SD'])
 def test_no_false_equivalence_or_full_population_ITT(self):
  x=analyze()['interpretation'];self.assertTrue(any('not evidence of null' in s for s in x))
  self.assertTrue(any('does not establish ITT for all registered' in s for s in x))
 def test_no_causal_promotion_of_dispersion(self):
  x=analyze();self.assertTrue(any('post-allocation association' in s for s in x['interpretation']))
 def test_all_five_95_ci_cover_zero(self):
  for v in analyze()['rows'].values():self.assertLess(v['ci95_normal'][0],0);self.assertGreater(v['ci95_normal'][1],0)
 def test_precommitted_five_endpoint_familywise_interval_wider(self):
  for v in analyze()['rows'].values():
   self.assertLess(v['ci_bonferroni_95_family'][0],v['ci95_normal'][0])
   self.assertGreater(v['ci_bonferroni_95_family'][1],v['ci95_normal'][1])
if __name__=='__main__':unittest.main(verbosity=2)
