"""ABH25B C17–C26: ten distinct new fictional-game insight acceptance tests."""
import copy
import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from politics_fantasy.product import seed_demo,state,transfer,set_lineup,simulate_round,add_club
from politics_fantasy.insights import (
 c17_valuation,c18_affordability,c19_role_entropy,c20_group_hhi,
 c21_starter_bench,c22_bounded_cash_flow,c23_churn,
 c24_lineup_readiness,c25_settled_mean,c26_component_concentration,derive_all)
NOW=datetime(2026,1,1,tzinfo=timezone.utc)
class RealFictionalFixture(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.path=Path(self.temp.name)/'g.sqlite3'
  seed_demo(self.path,now=NOW)
  self.data=state(self.path,when=NOW)
 def tearDown(self):self.temp.cleanup()
 def get(self):return state(self.path,when=NOW)
 def test_c17_portfolio_book_value_conserves_static_credits(self):
  v=c17_valuation(self.data,'demo')
  self.assertEqual(v['portfolio_book_value'],100)
  self.assertEqual(v['asset_book_value'],68)
  transfer(self.path,club_id='demo',figure_id='F04',action='buy',when=NOW)
  self.assertEqual(c17_valuation(self.get(),'demo')['portfolio_book_value'],100)
  self.assertFalse(v['market_revaluation'])
 def test_c18_affordability_requires_all_three_resources(self):
  x=c18_affordability(self.data,'demo')
  self.assertEqual(x['vacant_roster_slots'],2)
  self.assertTrue(x['affordable_unowned_count']>=2)
  transfer(self.path,club_id='demo',figure_id='F04',action='buy',when=NOW)
  transfer(self.path,club_id='demo',figure_id='F07',action='buy',when=NOW)
  self.assertEqual(c18_affordability(self.get(),'demo')['affordable_unowned_count'],0)
 def test_c19_role_entropy_uniform_and_single_role(self):
  x=c19_role_entropy(self.data,'demo')
  self.assertAlmostEqual(x['entropy_normalized'],1.0)
  temp=copy.deepcopy(self.data)
  for fig in temp['figures']:fig['role']='FICTIONAL_SAME'
  self.assertEqual(c19_role_entropy(temp,'demo')['entropy_normalized'],0.0)
 def test_c20_group_hhi_is_not_score_or_influence(self):
  x=c20_group_hhi(self.data,'demo')
  self.assertAlmostEqual(x['hhi'],5/9)
  temp=copy.deepcopy(self.data)
  for f in temp['figures']:f['group_name']='ONE'
  self.assertEqual(c20_group_hhi(temp,'demo')['hhi'],1.0)
 def test_c21_saved_starters_versus_bench_before_settlement(self):
  self.assertEqual(c21_starter_bench(self.data,'demo')['status'],'NO_VALID_SAVED_LINEUP')
  set_lineup(self.path,club_id='demo',round_id='next',figures=['F01','F02','F03'],when=NOW)
  transfer(self.path,club_id='demo',figure_id='F04',action='buy',when=NOW)
  v=c21_starter_bench(self.get(),'demo')
  self.assertEqual(v['status'],'SAVED_VALID_LINEUP')
  self.assertEqual(v['starter_value'],68)
  self.assertEqual(v['bench_value'],12)
 def test_c22_recent_cash_flow_not_historic_baseline(self):
  transfer(self.path,club_id='demo',figure_id='F04',action='buy',when=NOW)
  transfer(self.path,club_id='demo',figure_id='F04',action='sell',when=NOW)
  v=c22_bounded_cash_flow(self.get(),'demo')
  self.assertEqual(v['observed_buys'],1)
  self.assertEqual(v['observed_sells'],1)
  self.assertEqual(v['cash_delta_bounded'],0)
  self.assertFalse(v['baseline_credits_attested'])
 def test_c23_repeat_trades_distinct_from_figure_count(self):
  transfer(self.path,club_id='demo',figure_id='F04',action='buy',when=NOW)
  transfer(self.path,club_id='demo',figure_id='F04',action='sell',when=NOW)
  v=c23_churn(self.get(),'demo')
  self.assertEqual(v['observed_transactions'],2)
  self.assertEqual(v['distinct_figures_traded'],1)
  self.assertEqual(v['figures_traded_multiple_times'],1)
  self.assertTrue(v['not_all_time_churn'])
 def test_c24_lineup_readiness_is_not_a_forecast(self):
  self.assertEqual(c24_lineup_readiness(self.data,'demo')['status'],'INCOMPLETE')
  set_lineup(self.path,club_id='demo',round_id='next',figures=['F01','F02','F03'],when=NOW)
  self.assertEqual(c24_lineup_readiness(self.get(),'demo')['status'],'READY')
  simulate_round(self.path,round_id='next',when=NOW)
  self.assertEqual(c24_lineup_readiness(self.get(),'demo')['status'],'INCOMPLETE')
 def test_c25_realized_mean_excludes_null_and_pending(self):
  self.assertIsNone(c25_settled_mean(self.data,'demo')['mean_scored'])
  add_club(self.path,'Club Nuevo')
  set_lineup(self.path,club_id='demo',round_id='next',figures=['F01','F02','F03'],when=NOW)
  simulate_round(self.path,round_id='next',when=NOW)
  v=c25_settled_mean(self.get(),'demo')
  self.assertEqual(v['scored_rounds'],1)
  self.assertEqual(v['coverage'],1.0)
  other=next(c['id'] for c in self.get()['clubs'] if c['id']!='demo')
  o=c25_settled_mean(self.get(),other)
  self.assertEqual(o['scored_rounds'],0)
  self.assertIsNone(o['mean_scored'])
  self.assertEqual(o['unscored_settled_rounds'],1)
 def test_c26_concentration_requires_frozen_component_receipt(self):
  self.assertEqual(c26_component_concentration(self.data,'demo')['status'],'NO_SETTLED_ROUND')
  set_lineup(self.path,club_id='demo',round_id='next',figures=['F01','F02','F03'],when=NOW)
  simulate_round(self.path,round_id='next',when=NOW)
  v=c26_component_concentration(self.get(),'demo')
  self.assertEqual(v['status'],'CONCENTRATION_OF_FICTIONAL_SCORES')
  self.assertGreaterEqual(v['hhi'],1/3)
  self.assertLessEqual(v['hhi'],1.0)
  self.assertEqual(len(derive_all(self.get())['demo']),10)
if __name__=='__main__':unittest.main()
