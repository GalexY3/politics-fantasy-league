from datetime import date,datetime,timezone
from pathlib import Path
from politics_fantasy.groupvotes import GroupRow,GroupSnapshot,read_group_snapshot
from politics_fantasy.groupmetrics import group_vote_measure,group_period_summary

T=datetime(2026,10,25,tzinfo=timezone.utc)
def r(yes,no,abstain,no_vote,grp='A',day=date(2026,9,30),vote='s202-v01'):
 return GroupRow(vote,day,grp,yes,no,abstain,no_vote,1)
def snapshot(tmp_path,rows):
 p=tmp_path/'groups.csv';p.write_text('votacion_id,fecha,grupo,si,no,abstencion,no_vota\n'+''.join(f'{x.vote_id},{x.day.isoformat()},{x.group},{x.yes},{x.no},{x.abstain},{x.no_vote}\n' for x in rows),encoding='utf-8')
 return read_group_snapshot(p,acquired_at=T)

def test_br30c_07_nonvote_denominator_explicit():
 a=group_vote_measure(r(2,1,0,1));assert a['no_vote_rate_among_recorded']==0.25
 assert a['denominator']!='ALL_ELIGIBLE_DEPUTIES'

def test_br30c_08_modal_concentration_and_undefined():
 assert group_vote_measure(r(3,1,0,0))['modal_share_expressed']==0.75
 assert group_vote_measure(r(0,0,0,4))['modal_share_expressed'] is None

def test_br30c_09_tie_not_dissent():
 a=group_vote_measure(r(2,2,0,0));assert a['majority']=='TIE'
 assert a['dissent_from_group_majority'] is None

def test_br30c_10_abstention_counts_as_expressed():
 a=group_vote_measure(r(1,0,3,2));assert a['expressed']==4
 assert a['modal_share_expressed']==0.75 and a['majority']=='ABSTAIN'

def test_br30c_11_order_permutation_invariant(tmp_path):
 rows=[r(2,1,0,0),r(0,1,1,2,grp='B'),r(1,0,0,0,day=date(2025,10,1),vote='s101-v01')]
 a=group_period_summary(snapshot(tmp_path,rows));b=group_period_summary(snapshot(tmp_path,list(reversed(rows))))
 assert a==b

def test_br30c_12_group_year_cohorts_not_overwritten(tmp_path):
 rows=[r(5,0,0,0,grp='A',day=date(2025,12,31),vote='s101-v01'),r(0,5,0,0,grp='B',day=date(2026,1,1),vote='s102-v01')]
 s=group_period_summary(snapshot(tmp_path,rows));assert [(x['year'],x['group']) for x in s]==[(2025,'A'),(2026,'B')]
 assert all(x['historical_group']=='AS_LISTED_PER_VOTE_UNCERTIFIED' for x in s)
