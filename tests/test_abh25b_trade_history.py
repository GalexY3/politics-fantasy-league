"""ABH25B C07 — real persistent SQLite transaction log, no fabricated seed transfers."""
import tempfile,unittest
from pathlib import Path
from datetime import datetime,timezone
from politics_fantasy.product import seed_demo,add_club,transfer,state
NOW=datetime(2026,1,1,tzinfo=timezone.utc)
class TradeHistory(unittest.TestCase):
    def test_real_buy_sell_ledger_survives_reopen_without_fabrication(self):
        with tempfile.TemporaryDirectory() as root:
            db=Path(root)/'game.db';seed_demo(db,now=NOW)
            self.assertEqual(state(db,when=NOW)['trades'],[])
            club=add_club(db,'Testers')["id"]
            bought=transfer(db,club_id=club,figure_id='F04',action='buy',when=NOW)
            sold=transfer(db,club_id=club,figure_id='F04',action='sell',when=NOW)
            self.assertEqual(bought['credits_delta'],-sold['credits_delta'])
            saved=state(db,when=NOW)
            rows=[x for x in saved['trades'] if x['club_id']==club]
            self.assertEqual(len(rows),2)
            self.assertEqual([x['action'] for x in rows],['sell','buy'])
            self.assertEqual(sum(x['credits_delta'] for x in rows),0)
            again=state(db,when=NOW)
            self.assertEqual(saved['trades'],again['trades'])
            self.assertEqual(saved['clubs'],again['clubs'])
    def test_invalid_sale_does_not_enter_ledger(self):
        with tempfile.TemporaryDirectory() as root:
            db=Path(root)/'game.db';seed_demo(db,now=NOW)
            from politics_fantasy.product import GameError
            with self.assertRaises(GameError):
                transfer(db,club_id='demo',figure_id='F04',action='sell',when=NOW)
            self.assertEqual(state(db,when=NOW)['trades'],[])
if __name__=='__main__':unittest.main()
