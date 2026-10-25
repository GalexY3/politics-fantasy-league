from datetime import datetime,timezone
import pytest
from politics_fantasy.rollcall import NominalVote
from politics_fantasy.sociometrics import participation,group_choice_counts,majority_by_group_vote,dissent_report
D=lambda n:datetime(2026,1,n,tzinfo=timezone.utc)

def V(v='v1',p='p1',g='A',choice='YES'):
 return NominalVote(v,p,g,choice,D(1),D(2),D(3),'https://congreso.es/demo','a'*64)

def test_br30_07_missing_row_is_unknown_not_no_vote():
 r=participation([V()],person_id='p1',eligible_vote_ids=['v1','v2'])
 assert (r.unknown,r.no_vote,r.rate,r.status)==(1,0,None,'INCOMPLETE_CENSUS')

def test_br30_08_explicit_denominator_validates_exposure():
 r=participation([V('v1'),V('v2',choice='NO_VOTE')],person_id='p1',eligible_vote_ids=['v1','v2'])
 assert (r.rate,r.no_vote,r.eligible)==(.5,1,2)
 with pytest.raises(ValueError,match='Duplicated'):participation([],person_id='p1',eligible_vote_ids=['v1','v1'])

def test_br30_09_group_counts_member_event_grain_not_person_aggregate():
 x=group_choice_counts([V('v1','p1','A','YES'),V('v1','p2','A','YES'),V('v2','p1','B','NO')])
 assert x['A']['YES']==2 and x['B']['NO']==1

def test_br30_10_majority_is_per_vote_not_global_group():
 r=majority_by_group_vote([V('v1','p1','A','YES'),V('v1','p2','A','YES'),V('v1','p3','A','NO'),
                           V('v2','p1','A','NO'),V('v2','p2','A','NO')])
 assert r[('v1','A')]=='YES' and r[('v2','A')]=='NO'

def test_br30_11_tied_and_mixto_votes_excluded():
 rows=[V('v1','p1','A','YES'),V('v1','p2','A','NO'),V('v2','p1','Mixto','NO'),V('v2','p2','Mixto','YES')]
 r=dissent_report(rows)
 assert r['p1']['eligible_expressed']==0 and r['p1']['dissent']==0 and r['p1']['excluded']==2

def test_br30_12_abstain_counts_as_choice_not_missing():
 rows=[V('v1','p1','A','ABSTAIN'),V('v1','p2','A','ABSTAIN'),V('v1','p3','A','NO'),V('v1','p4','A','NO_VOTE')]
 r=dissent_report(rows)
 assert r['p3']['dissent']==1 and r['p3']['eligible_expressed']==1
 assert r['p4']['rate'] is None and r['p4']['excluded']==1
