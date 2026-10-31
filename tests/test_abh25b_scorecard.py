"""C03: real SQLite transactional explanation of FICTIONAL scores."""
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from politics_fantasy.product import seed_demo,set_lineup,simulate_round,state,connect,GameError
from politics_fantasy import accounts

NOW=datetime(2026,1,1,tzinfo=timezone.utc)
class ScorecardFunctional(unittest.TestCase):
    def setup_db(self):
        t=tempfile.TemporaryDirectory()
        db=Path(t.name)/'game.sqlite3'
        seed_demo(db,now=NOW)
        return t,db
    def settle(self,path):
        set_lineup(path,club_id='demo',round_id='next',
                   figures=['F01','F02','F03'],when=NOW)
        v=simulate_round(path,round_id='next',when=NOW)
        self.assertFalse(v['already_settled'])
    def test_frozen_components_conserve_score_across_restart_and_event_change(self):
        t,db=self.setup_db()
        try:
            self.settle(db)
            r=next(x for x in state(db,when=NOW)['rounds'] if x['id']=='next')
            detail=r['score_details']['demo']
            self.assertEqual(detail['status'],'FROZEN_COMPONENTS')
            self.assertEqual(len(detail['components']),3)
            self.assertAlmostEqual(sum(x['points'] for x in detail['components']),r['scores']['demo'])
            self.assertTrue(detail['rule_version'].startswith('demo-'))
            with connect(db) as con:
                con.execute("UPDATE demo_event SET kind='speech_recorded' WHERE event_id='SIM:next:F03'")
            restart=next(x for x in state(db,when=NOW)['rounds'] if x['id']=='next')
            self.assertEqual(restart['score_details']['demo'],detail)
            self.assertEqual(restart['scores']['demo'],r['scores']['demo'])
            self.assertTrue(simulate_round(db,round_id='next',when=NOW)['already_settled'])
        finally:t.cleanup()
    def test_corrupted_component_is_not_displayed_as_valid(self):
        t,db=self.setup_db()
        try:
            self.settle(db)
            with connect(db) as con:
                con.execute("UPDATE round_settlement_component SET points=points+1 "
                            "WHERE round_id='next' AND club_id='demo' AND figure_id='F01'")
            with self.assertRaisesRegex(GameError,'Desglose ficticio almacenado inconsistente'):
                state(db,when=NOW)
        finally:t.cleanup()
    def test_existing_settlement_without_component_table_stays_unexplained(self):
        t,db=self.setup_db()
        try:
            self.settle(db)
            with connect(db) as con:
                con.execute("DROP TABLE round_settlement_component")
            s=state(db,when=NOW)
            r=next(x for x in s['rounds'] if x['id']=='next')
            self.assertEqual(r['score_details']['demo']['status'],'LEGACY_UNAVAILABLE')
            with connect(db) as con:
                self.assertFalse(con.execute("SELECT 1 FROM sqlite_master WHERE "
                    "name='round_settlement_component'").fetchone())
        finally:t.cleanup()
    def test_missing_lineup_is_not_zero(self):
        t,db=self.setup_db()
        try:
            simulate_round(db,round_id='next',when=NOW)
            r=next(x for x in state(db,when=NOW)['rounds'] if x['id']=='next')
            self.assertIsNone(r['scores']['demo'])
            self.assertEqual(r['score_details']['demo']['status'],'NO_VALID_LINEUP')
        finally:t.cleanup()
    def test_fictional_accounts_physically_separate_component_tables(self):
        with tempfile.TemporaryDirectory() as root:
            auth=Path(root)/'auth.sqlite3'
            accounts.init_accounts(auth)
            accounts.register(auth,'fic_a123','synthetic-only-passphrase')
            accounts.register(auth,'fic_b123','synthetic-only-passphrase')
            one=accounts.game_path(auth,accounts.authenticate(auth,'fic_a123','synthetic-only-passphrase')[0])
            two=accounts.game_path(auth,accounts.authenticate(auth,'fic_b123','synthetic-only-passphrase')[0])
            self.assertNotEqual(one,two)
            self.settle(one)
            a=next(x for x in state(one,when=NOW)['rounds'] if x['id']=='next')
            b=next(x for x in state(two,when=NOW)['rounds'] if x['id']=='next')
            self.assertEqual(a['score_details']['demo']['status'],'FROZEN_COMPONENTS')
            self.assertEqual(b['score_details']['demo']['status'],'NOT_SETTLED')
if __name__=='__main__':unittest.main()
