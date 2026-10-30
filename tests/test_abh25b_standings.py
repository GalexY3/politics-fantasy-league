"""ABH25B C04: cumulated fictional standings, no zero imputation."""
import tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from politics_fantasy.product import (
    seed_demo,add_club,transfer,set_lineup,simulate_round,state)
T=datetime(2026,1,1,tzinfo=timezone.utc)
class C04Standings(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db=Path(self.temp.name)/'fictional.sqlite3'
        seed_demo(self.db,now=T)
    def tearDown(self): self.temp.cleanup()
    def test_prior_round_without_settlement_is_not_aggregated(self):
        s=state(self.db,when=T)
        self.assertEqual(len(s['season_standings']),1)
        row=s['season_standings'][0]
        self.assertEqual(row['status'],'NO_SETTLED_ROUNDS')
        self.assertIsNone(row['rank'])
        self.assertIsNone(row['total_points'])
        self.assertEqual(row['rounds_settled'],0)
    def test_missing_lineup_does_not_become_a_zero_or_rank(self):
        other=add_club(self.db,'Equipo B')
        set_lineup(self.db,club_id='demo',round_id='next',figures=['F01','F02','F03'],when=T)
        simulate_round(self.db,round_id='next',when=T)
        s=state(self.db,when=T)['season_standings']
        top=next(x for x in s if x['club_id']=='demo')
        missing=next(x for x in s if x['club_id']==other['id'])
        self.assertEqual(top['rank'],1)
        self.assertEqual(top['rounds_scored'],1)
        self.assertGreater(top['total_points'],0)
        self.assertEqual(missing['status'],'INCOMPLETE_COVERAGE')
        self.assertEqual(missing['rounds_unknown'],1)
        self.assertIsNone(missing['total_points'])
        self.assertIsNone(missing['rank'])
    def test_equal_clubs_share_rank_and_sum_is_frozen_across_two_rounds(self):
        other=add_club(self.db,'Equipo B')
        for fig in ['F04','F05','F06']:
            transfer(self.db,club_id=other['id'],figure_id=fig,action='buy',when=T)
        for club,figs in [('demo',['F01','F02','F03']),(other['id'],['F04','F05','F06'])]:
            set_lineup(self.db,club_id=club,round_id='next',figures=figs,when=T)
        settled=simulate_round(self.db,round_id='next',when=T)
        rows=state(self.db,when=T)['season_standings']
        self.assertEqual([r['rank'] for r in rows],[1,1])
        self.assertEqual(rows[0]['total_points'],rows[1]['total_points'])
        for club,figs in [('demo',['F01','F02','F03']),(other['id'],['F04','F05','F06'])]:
            set_lineup(self.db,club_id=club,round_id=settled['next_round_id'],figures=figs,when=T)
        simulate_round(self.db,round_id=settled['next_round_id'],when=T)
        season=state(self.db,when=T)
        for x in season['season_standings']:
            self.assertEqual(x['rounds_settled'],2)
            self.assertEqual(x['rounds_unknown'],0)
            expected=sum(rr['scores'][x['club_id']] for rr in season['rounds'] if rr['is_settled'])
            self.assertEqual(x['total_points'],expected)
            self.assertEqual(x['rank'],1)
if __name__=='__main__':unittest.main()
