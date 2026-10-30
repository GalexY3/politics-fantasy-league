"""ABH25 C05 + C06. Synthetic-only adversarial temporal integration."""
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from politics_fantasy.product import seed_demo, simulate_round, connect, set_lineup, state
from politics_fantasy.scoring import person_week_points
from politics_fantasy.events import PoliticalEvent, observable_event_revisions

UTC=timezone.utc
T0=datetime(2026,1,1,tzinfo=UTC)

class C05AtomicSettlement(unittest.TestCase):
    def test_six_concurrent_settlements_are_unique_and_repeatable(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'game.sqlite3'
            seed_demo(path,now=T0)
            set_lineup(path,club_id='demo',round_id='next',figures=['F01','F02','F03'],when=T0)
            with ThreadPoolExecutor(max_workers=6) as pool:
                outcomes=list(pool.map(lambda _: simulate_round(path,round_id='next',when=T0),range(6)))
            self.assertEqual(sum(not x['already_settled'] for x in outcomes),1)
            self.assertEqual(len({x['next_round_id'] for x in outcomes}),1)
            with connect(path) as db:
                self.assertEqual(db.execute("SELECT count(*) FROM round_settlement WHERE round_id='next'").fetchone()[0],1)
                self.assertEqual(db.execute("SELECT count(*) FROM demo_event WHERE event_id LIKE 'SIM:next:%'").fetchone()[0],10)
                self.assertEqual(db.execute("SELECT count(*) FROM fantasy_round").fetchone()[0],3)
            s=state(path,when=T0)
            nxt=next(r for r in s['rounds'] if r['id']=='next')
            self.assertIsInstance(nxt['scores']['demo'],float)
            self.assertEqual(nxt['scores']['demo'],state(path,when=T0)['rounds'][1]['scores']['demo'])

class C06KnowledgeCutoff(unittest.TestCase):
    def event(self,version,kind,publication):
        return PoliticalEvent('SYN-C06',kind,T0,publication,('FICTION-01',),
            'synthetic://abh25','0'*64,version,{'evidence':'SYNTHETIC_ONLY'})

    def test_late_revision_never_leaks_or_doubles(self):
        first=self.event('base','speech_recorded',T0+timedelta(days=1))
        later=self.event('amended','initiative_registered',T0+timedelta(days=8))
        events=[first,later]
        kw=dict(person_id='FICTION-01',start=T0,end=T0+timedelta(days=2))
        initial=person_week_points(events,knowledge_cutoff=T0+timedelta(days=4),**kw)
        recent=person_week_points(events,knowledge_cutoff=T0+timedelta(days=9),**kw)
        self.assertEqual(initial,2.0)
        self.assertEqual(recent,3.0)
        self.assertEqual(person_week_points(events+[first],knowledge_cutoff=T0+timedelta(days=9),**kw),recent)
        with self.assertRaisesRegex(ValueError,'Ambiguous public revisions'):
            person_week_points([first,self.event('equal','question_registered',T0+timedelta(days=1))],
              knowledge_cutoff=T0+timedelta(days=4),**kw)
        with self.assertRaisesRegex(ValueError,'Conflicting source revision'):
            observable_event_revisions([first,self.event('base','question_registered',T0+timedelta(days=2))],
                as_of=T0+timedelta(days=4))

if __name__=='__main__':
    unittest.main()
