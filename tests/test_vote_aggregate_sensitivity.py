import unittest
from politics_fantasy.vote_aggregate_sensitivity import analyze_vote_sample

ROWS=[
 {'expediente':'130/000049','vote':'convalidación','yes':175,'no':33,'abstain':140,'total':348},
 {'expediente':'130/000049','vote':'urgencia','yes':344,'no':0,'abstain':0,'total':344},
 {'expediente':'130/000050','vote':'convalidación','yes':167,'no':37,'abstain':144,'total':348},
 {'expediente':'130/000050','vote':'urgencia','yes':347,'no':0,'abstain':0,'total':347},
]
class VoteSensitivity(unittest.TestCase):
 def test_four_ballots_two_exp(self):
  x=analyze_vote_sample(ROWS)
  self.assertEqual((x['observed_ballots'],x['distinct_expedientes']),(4,2))
  self.assertEqual(x['expedientes'][0]['ballots'],2)
  self.assertEqual(x['expedientes'][1]['ballots'],2)
 def test_first_exp_pool_hides_within_ballot_variation(self):
  e=analyze_vote_sample(ROWS)['expedientes'][0]
  self.assertEqual(e['naive_collapsed_yes_pct'],75.)
  self.assertAlmostEqual(e['range_pp'],49.712644,places=5)
  self.assertEqual([x['total'] for x in e['per_ballot']],[348,344])
 def test_second_exp_pool_hides_within_ballot_variation(self):
  e=analyze_vote_sample(ROWS)['expedientes'][1]
  self.assertAlmostEqual(e['naive_collapsed_yes_pct'],73.956835,places=5)
  self.assertAlmostEqual(e['range_pp'],52.011494,places=5)
 def test_duplicate_vote_within_expediente_rejected(self):
  with self.assertRaisesRegex(ValueError,'DUPLICATE_BALLOT_KEY'):analyze_vote_sample(ROWS+[ROWS[0]])
 def test_tally_inconsistency_and_missing_id_rejected(self):
  with self.assertRaisesRegex(ValueError,'INVALID_BALLOT_DENOMINATOR'):analyze_vote_sample([{**ROWS[0],'total':349}])
  with self.assertRaisesRegex(ValueError,'INVALID_BALLOT_ID'):analyze_vote_sample([{**ROWS[0],'vote':''}])
 def test_no_boolean_counts_or_zero_denominator(self):
  with self.assertRaisesRegex(ValueError,'INVALID_TALLY'):analyze_vote_sample([{**ROWS[0],'yes':True}])
  with self.assertRaisesRegex(ValueError,'INVALID_BALLOT_DENOMINATOR'):analyze_vote_sample([{**ROWS[0],'yes':0,'no':0,'abstain':0,'total':0}])
if __name__=='__main__':unittest.main()
