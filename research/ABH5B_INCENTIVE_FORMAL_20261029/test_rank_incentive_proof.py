import unittest
from fractions import Fraction as F
from rank_incentive_proof import (probability,score,deterministic_win,
    lottery_win,expected_win,exact_truthfulness_gap,audit)

class IncentiveFormalAudit(unittest.TestCase):
    def test_01_counterexample_to_deterministic_truthfulness(self):
        p,q=F(11,20),F(3,5)
        self.assertEqual(expected_win(p,p,q,deterministic_win),F(9,20))
        self.assertEqual(expected_win(p,F(61,100),q,deterministic_win),F(11,20))

    def test_02_truthful_scoring_expected_score_advantage(self):
        p,q,r=F(11,20),F(3,5),F(61,100)
        truth=(1-p)*score(p,0)+p*score(p,1)
        dev=(1-p)*score(r,0)+p*score(r,1)
        self.assertEqual(truth-dev,F(9,2500))

    def test_03_lottery_probabilities_are_bounded_and_sum_to_one(self):
        for r in [F(0),F(1,5),F(1,2),F(4,5),F(1)]:
            for q in [F(0),F(2,5),F(1)]:
                for y in (0,1):
                    x=lottery_win(r,q,y)
                    self.assertLessEqual(F(0),x)
                    self.assertLessEqual(x,F(1))
                    self.assertEqual(x+lottery_win(q,r,y),F(1))

    def test_04_lottery_has_proper_truthful_gap_in_selected_case(self):
        p,q,r=F(11,20),F(3,5),F(61,100)
        self.assertEqual(exact_truthfulness_gap(p,r,q),F(9,5000))
        self.assertEqual(expected_win(p,p,q,lottery_win)-expected_win(p,r,q,lottery_win),F(9,5000))

    def test_05_identity_grid_is_checks_not_proof_of_continuum(self):
        for i in range(11):
            for j in range(11):
                p,q=F(i,10),F(j,10)
                for r in [F(0),F(1,4),F(1,2),F(3,4),F(1)]:
                    self.assertEqual(exact_truthfulness_gap(p,r,q),F(1,2)*(r-p)**2)

    def test_06_ties_are_not_automatic_wins(self):
        self.assertEqual(deterministic_win(F(1,2),F(1,2),0),F(1,2))
        self.assertEqual(deterministic_win(F(1,2),F(1,2),1),F(1,2))
        self.assertEqual(lottery_win(F(1,2),F(1,2),0),F(1,2))

    def test_07_invalid_inputs_fail_closed(self):
        for bad in (-0.1, F(-1,2),F(3,2),.5,True,0,1):
            with self.assertRaises(ValueError):probability(bad)
        with self.assertRaises(ValueError):score(F(1,2),2)
        with self.assertRaises(ValueError):score(F(1,2),True)

    def test_08_exact_scope_flags_no_human_or_deployed_pfl_claim(self):
        r=audit()
        self.assertEqual(r['scientific_grade'],'0/3')
        self.assertEqual(r['real_human_rows'],0)
        self.assertIn('not a PFL implemented prize scheme',r['no_claims'])
        self.assertEqual(r['deviation_gain_in_deterministic_win_probability'],'1/10')
        self.assertEqual(r['truthful_advantage_in_lottery'],'9/5000')

if __name__=='__main__':unittest.main(verbosity=2)
