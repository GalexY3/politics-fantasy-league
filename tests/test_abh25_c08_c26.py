"""ABH25 C08-C26: 19 frozen, distinct synthetic invariance / adversarial experiments.
These checks are NOT human experiments, real political scores or causal evidence.
"""
import hashlib, http.cookiejar, io, json, sqlite3, tempfile, threading, unittest
import urllib.error, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer

from politics_fantasy import accounts
from politics_fantasy.readiness import yes_share_bounds, research_readiness, as_of_snapshot_gate
from politics_fantasy.structural import simpson_reversal, direct_standardization
from politics_fantasy.evaluation import (session_bootstrap_ci, record_weighted_cluster_bootstrap_ci,
  purged_walk_forward, calibration_bins)
from politics_fantasy.network import VoteRecord, covote_edges
from politics_fantasy.provenance_claim_gate import evaluate_claim_as_of, AUTHORITY
from politics_fantasy.source_eligibility import assess_evidence
from politics_fantasy.quality import audit_jsonl
from politics_fantasy.simulation import gini, simulate_auction
from politics_fantasy.scoring import Rule, person_week_points
from politics_fantasy.events import PoliticalEvent
from politics_fantasy.server import handler_factory
from politics_fantasy.source_capture_guard import inspect_xlsx_bytes
from politics_fantasy.groupvotes import GroupRow
from politics_fantasy.groupmetrics import group_vote_measure
from politics_fantasy.product import seed_demo,simulate_round,set_lineup,state,connect

T0=datetime(2026,1,1,tzinfo=timezone.utc)

class FormalCrossDomain(unittest.TestCase):
    def test_c08_missing_roster_bounds_are_not_imputed_zero(self):
        full=yes_share_bounds(yes=5,observed=10,eligible_roster=10)
        partial=yes_share_bounds(yes=5,observed=10,eligible_roster=20)
        unknown=yes_share_bounds(yes=5,observed=10,eligible_roster=None)
        self.assertEqual(full['lower'],full['upper'])
        self.assertAlmostEqual(partial['upper']-partial['lower'],0.5)
        self.assertIsNone(unknown['upper'])
        with self.assertRaises(ValueError):yes_share_bounds(yes=11,observed=10,eligible_roster=20)

    def test_c09_simpson_reversal_and_external_standardization(self):
        a={'high':(9,10),'low':(20,50)}
        b={'high':(80,100),'low':(1,5)}
        o=simpson_reversal(a,b)
        self.assertTrue(o['reversal'])
        self.assertLess(o['pooled_difference'],0)
        w={'high':.5,'low':.5}
        self.assertGreater(direct_standardization(a,w),direct_standardization(b,w))
        with self.assertRaises(ValueError):direct_standardization(a,{'high':1.0})

    def test_c10_clusters_are_not_pseudoreplicated(self):
        samples={'one':[0.0],'nine':[1.0]*9}
        s=session_bootstrap_ci(samples,replicates=100,seed=29)
        v=record_weighted_cluster_bootstrap_ci(samples,replicates=100,seed=29)
        self.assertAlmostEqual(s['mean'],0.5)
        self.assertAlmostEqual(v['mean'],0.9)
        self.assertNotEqual(s['mean'],v['mean'])
        self.assertEqual(s,session_bootstrap_ci(samples,replicates=100,seed=29))

    def test_c11_purged_chronology_has_strict_disjoint_folds(self):
        weeks=[f'w{i:02}' for i in range(1,13)]
        folds=list(purged_walk_forward(weeks,min_train=3,gap=2,horizon=2))
        self.assertGreater(len(folds),0)
        for f in folds:
            self.assertEqual(len(f['purged']),2)
            self.assertEqual(len(f['test']),2)
            self.assertLess(f['train'][-1],f['purged'][0])
            self.assertLess(f['purged'][-1],f['test'][0])
            self.assertFalse(set(f['train'])&set(f['test']))
        with self.assertRaises(ValueError):list(purged_walk_forward(weeks[::-1],min_train=3,gap=2))

    def test_c12_covoing_requires_joint_public_exposure(self):
        votes=[]
        for i in range(3):
            for person,choice in [('A','YES'),('B','YES' if i<2 else 'NO')]:
                votes.append(VoteRecord(f'V{i}',person,choice,T0+timedelta(days=i),
                                        T0+timedelta(days=1 if i<2 else 10)))
        early=covote_edges(votes,as_of=T0+timedelta(days=5),min_joint=2)
        late=covote_edges(votes,as_of=T0+timedelta(days=11),min_joint=2)
        self.assertEqual(early[0]['joint_votes'],2)
        self.assertEqual(late[0]['joint_votes'],3)
        self.assertGreater(early[0]['agreement_smoothed'],late[0]['agreement_smoothed'])
        self.assertEqual(early[0]['status'],'DESCRIPTIVE_NOT_CAUSAL')

    def test_c13_claim_requires_type_and_earliest_publication(self):
        k={'authority':AUTHORITY,'record_family':'BOCCL_CANDIDATE_ACCEPTANCE',
           'evidence_ref':'SYN-C13','first_public_at':'2026-01-03T00:00:00Z'}
        opts=dict(authority=AUTHORITY,record_family='BOCCL_CANDIDATE_ACCEPTANCE',
          evidence_ref='SYN-C13',desired_claim='NOMINATED_AND_ACCEPTED_CANDIDATES',
          trusted_registry={'SYN-C13':k})
        before=evaluate_claim_as_of(as_of='2026-01-02T00:00:00Z',**opts)
        after=evaluate_claim_as_of(as_of='2026-01-04T00:00:00Z',**opts)
        self.assertEqual(before['reason'],'NOT_PUBLIC_BY_CUTOFF')
        self.assertTrue(after['eligible'])
        self.assertFalse(after['release_grade'])
        bad=dict(opts,desired_claim='DESIGNATED_SENATORS')
        self.assertFalse(evaluate_claim_as_of(as_of='2026-01-04T00:00:00Z',**bad)['eligible'])

    def test_c14_caller_claims_cannot_certify_real_scoring(self):
        base=dict(scope='AGGREGATE',official_url='https://www.congreso.es/docs',
          raw_sha256='a'*64,sha_replayed=True,reuse_adjudicated=True)
        first=assess_evidence(base)
        self.assertEqual(first['status'],'QUARANTINED')
        self.assertIn('CLAIMS_NOT_INDEPENDENTLY_ATTESTED',first['reasons'])
        self.assertFalse(first['real_person_scoring'])
        spoof=assess_evidence(dict(base,official_url='https://www.congreso.es.evil.example/docs'))
        self.assertIn('UNVERIFIED_SOURCE_URL',spoof['reasons'])

    def test_c15_jsonl_duplicate_and_absent_are_not_coverage(self):
        row=dict(event_id='SYN-C15',source_id='fictional',event_kind='speech_recorded',
                 occurred_at=T0.isoformat(),first_public_at=(T0+timedelta(days=1)).isoformat(),
                 source_url='synthetic://test',raw_sha256='b'*64,person_ids=['FIG-01'])
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'audit.jsonl'
            path.write_text('\n'.join([json.dumps(row),json.dumps(row),
                          json.dumps({k:v for k,v in row.items() if k!='first_public_at'})])+'\n')
            o=audit_jsonl(path)
        self.assertEqual(o['counts']['duplicate_same_revision'],1)
        self.assertEqual(o['counts']['missing_required'],1)
        self.assertEqual(o['counts']['parseable'],2)
        self.assertEqual(o['coverage_status'],'NOT_INFERABLE_WITHOUT_SOURCE_CENSUS')

    def test_c16_market_concentration_is_synthetic_seeded(self):
        self.assertAlmostEqual(gini([0,0,10]),2/3)
        self.assertAlmostEqual(gini([0,0,10]),gini([0,0,100]))
        x=simulate_auction(seed=31,clubs=4,assets=10,rounds=3)
        y=simulate_auction(seed=31,clubs=4,assets=10,rounds=3)
        self.assertEqual(x,y)
        self.assertGreater(x.mean_value,0)
        self.assertEqual(x.note,'SYNTHETIC_RULE_DEPENDENT')

    def test_c17_internal_completeness_cannot_certify_origins(self):
        report={'reconciliation':{'any_unresolved':False},
                'group_audit':{'aggregate_consistent':True,'nominal_group_complete':True}}
        v=research_readiness(report)
        self.assertEqual(v['status'],'NOT_READY_FOR_EMPIRICAL_CLAIMS')
        self.assertIn('ORIGINAL_PUBLICATION_TIMES_UNVERIFIED',v['discriminating_blockers'])
        self.assertIn('OFFICIAL_SOURCE_NOT_INDEPENDENTLY_ATTESTED',v['discriminating_blockers'])

    def test_c18_immutable_rule_snapshots_and_caps(self):
        weights={'speech_recorded':2.0}
        rule=Rule('SYN-C18',weights,{'speech_recorded':3})
        weights['speech_recorded']=99.0
        evs=[PoliticalEvent(f'C18-{i}','speech_recorded',T0,T0+timedelta(days=1),
              ('FIG-01',),'synthetic://c18',f'{i:064x}','v1',{}) for i in range(5)]
        s=person_week_points(evs,person_id='FIG-01',start=T0,end=T0+timedelta(days=2),
                knowledge_cutoff=T0+timedelta(days=3),rule=rule)
        self.assertEqual(s,6.0)
        with self.assertRaises(TypeError):rule.weights['speech_recorded']=7

    def test_c19_expired_cookie_does_not_resurrect_session(self):
        with tempfile.TemporaryDirectory() as d:
            auth=Path(d)/'auth.db';accounts.init_accounts(auth)
            accounts.register(auth,'fiction_c19','synthetic-only-password')
            token,sess=accounts.login(auth,'fiction_c19','synthetic-only-password')
            self.assertIsNotNone(accounts.lookup(auth,token))
            import time
            now=time.time()
            with patch('politics_fantasy.accounts.time.time',return_value=now+accounts.SESSION_TTL+2):
                self.assertIsNone(accounts.lookup(auth,token))
                accounts.revoke(auth,token)
            self.assertIsNone(accounts.lookup(auth,token))

    def test_c20_simultaneous_username_registration_one_db(self):
        with tempfile.TemporaryDirectory() as d:
            auth=Path(d)/'auth.db';accounts.init_accounts(auth)
            def once(_):
                try:return accounts.register(auth,'fiction_c20','synthetic-only-password')
                except accounts.AccountError as e:return e.code
            with ThreadPoolExecutor(max_workers=2) as pool:
                result=list(pool.map(once,range(2)))
            self.assertEqual(result.count('fiction_c20'),1)
            self.assertEqual(result.count('USERNAME_TAKEN'),1)
            with sqlite3.connect(auth) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM account').fetchone()[0],1)
            self.assertEqual(len(list((Path(d)/'accounts').glob('*.sqlite3'))),1)

    def test_c21_ambiguous_http_json_does_not_register(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);auth=root/'auth.db';accounts.init_accounts(auth)
            srv=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(root/'legacy.db',None,None,auth))
            t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
            try:
                base=f'http://127.0.0.1:{srv.server_port}'
                def send(raw):
                    req=urllib.request.Request(base+'/api/register',data=raw,
                      headers={'Content-Type':'application/json','X-PFL-Request':'1'},method='POST')
                    try:
                        with urllib.request.urlopen(req,timeout=8) as resp:return resp.status
                    except urllib.error.HTTPError as err:
                        with err:err.read()
                        return err.code
                self.assertEqual(send(b'{"username":"a_one","username":"a_two","password":"synthetic-passphrase"}'),400)
                with sqlite3.connect(auth) as db:
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM account').fetchone()[0],0)
                self.assertEqual(send(b'{"username":"a_two","password":"synthetic-passphrase"}'),201)
            finally:
                srv.shutdown();srv.server_close();t.join(timeout=4)

    def test_c22_ooxml_guard_never_attests_source(self):
        def archive(extra=None):
            out=io.BytesIO()
            with zipfile.ZipFile(out,'w') as z:
                for p in ('[Content_Types].xml','_rels/.rels','xl/workbook.xml',
                          'xl/worksheets/sheet1.xml'):
                    z.writestr(p,'<synthetic/>')
                if extra:z.writestr(extra,'fake')
            return out.getvalue()
        url='https://descargas.interior.gob.es/datasets/paridad_electoral/sample.xlsx'
        data=archive()
        s=inspect_xlsx_bytes(url,data,declared_sha256=hashlib.sha256(data).hexdigest())
        self.assertFalse(s['origin_authenticated'])
        self.assertIsNone(s['first_public_at'])
        with self.assertRaisesRegex(ValueError,'UNSAFE_ZIP_MEMBER'):
            inspect_xlsx_bytes(url,archive('../outside.xml'))
        with self.assertRaisesRegex(ValueError,'UNSAFE_SOURCE_URL'):
            inspect_xlsx_bytes('https://descargas.interior.gob.es.evil.example/datasets/paridad_electoral/a.xlsx',data)

    def test_c23_early_archive_not_first_publication(self):
        early={'source_snapshots':{'x':{'observed_at':(T0+timedelta(days=1)).isoformat()}}}
        late={'source_snapshots':{'x':{'observed_at':(T0+timedelta(days=9)).isoformat()}}}
        a=as_of_snapshot_gate(early,T0+timedelta(days=5))
        b=as_of_snapshot_gate(late,T0+timedelta(days=5))
        self.assertFalse(a['eligible_for_historical_prediction'])
        self.assertEqual(a['reason'],'ORIGINAL_PUBLICATION_UNVERIFIED_EVEN_WHEN_ACQUIRED_EARLY')
        self.assertEqual(b['reason'],'SNAPSHOT_ACQUIRED_AFTER_PREDICTION_CUTOFF')

    def test_c24_modal_plurality_is_not_strict_majority(self):
        weak=GroupRow('SYN-C24',T0.date(),'Fictional',4,3,2,1,1)
        strong=GroupRow('SYN-C24B',T0.date(),'Fictional',6,2,1,1,2)
        a=group_vote_measure(weak);b=group_vote_measure(strong)
        self.assertEqual(a['majority_kind'],'MODAL_EXPRESSED_NOT_STRICT')
        self.assertEqual(a['strict_majority'],'NO_ABSOLUTE_MAJORITY')
        self.assertIsNone(a['dissent_from_group_majority'])
        self.assertEqual(b['strict_majority'],'YES')
        self.assertEqual(b['dissent_from_group_majority'],3)
        self.assertEqual(a['denominator'],'RECORDED_GROUP_COUNTS_NOT_CERTIFIED_ELIGIBILITY')

    def test_c25_eight_round_lifecycle_no_score_rewrite(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'game.db';seed_demo(path,now=T0)
            rid='next';scores={}
            for i in range(8):
                set_lineup(path,club_id='demo',round_id=rid,
                           figures=['F01','F02','F03'],when=T0)
                result=simulate_round(path,round_id=rid,when=T0)
                self.assertFalse(result['already_settled'])
                after=state(path,when=T0)
                scores[rid]=next(q for q in after['rounds'] if q['id']==rid)['scores']['demo']
                self.assertIsNotNone(scores[rid])
                rid=result['next_round_id']
            with connect(path) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM round_settlement').fetchone()[0],8)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM demo_event WHERE event_id LIKE 'SIM:%'").fetchone()[0],80)
            final=state(path,when=T0)
            for old,score in scores.items():
                self.assertEqual(next(q for q in final['rounds'] if q['id']==old)['scores']['demo'],score)

    def test_c26_sparse_calibration_never_zeros_unobserved(self):
        bins=calibration_bins([(0,0.1),(1,0.2),(2,2.0)],edges=(1.0,),min_n=2)
        self.assertEqual(bins[0]['n'],2)
        self.assertAlmostEqual(bins[0]['observed'],0.5)
        self.assertEqual(bins[1]['status'],'LOW_SUPPORT')
        self.assertIsNone(bins[1]['observed'])
        self.assertIsNone(bins[1]['predicted'])

if __name__=='__main__':unittest.main()
