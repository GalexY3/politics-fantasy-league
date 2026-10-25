"""Descriptive sociology of observed *group tallies*, never inferred party discipline.

NO_VOTE is only the explicit category in the source; no unobserved deputy is added.
"""
from __future__ import annotations
from collections import defaultdict
from .groupvotes import GroupSnapshot, GroupRow, majority


def group_vote_measure(row:GroupRow)->dict:
    expressed=row.yes+row.no+row.abstain
    counted=expressed+row.no_vote
    leader=majority(row)
    modal=max(row.yes,row.no,row.abstain)
    return {'vote_id':row.vote_id,'day':row.day.isoformat(),'group':row.group,
            'known_counted':counted,'expressed':expressed,
            'explicit_no_vote':row.no_vote,
            'no_vote_rate_among_recorded':row.no_vote/counted if counted else None,
            'modal_share_expressed':modal/expressed if expressed else None,
            'nonmodal_choices':expressed-modal if expressed else None,
            'majority':leader,
            'dissent_from_group_majority':None if leader in ('TIE','NO_EXPRESSED_CHOICE') else expressed-modal,
            'denominator':'RECORDED_GROUP_COUNTS_NOT_CERTIFIED_ELIGIBILITY',
            'interpretation':'DISPERSION_NOT_PARTY_DISCIPLINE'}


def group_period_summary(snapshot:GroupSnapshot)->list[dict]:
    by_key=defaultdict(list)
    for row in snapshot.rows:by_key[(row.day.year,row.group)].append(row)
    result=[]
    for year,group in sorted(by_key):
        rows=by_key[year,group]
        expressed=sum(r.yes+r.no+r.abstain for r in rows)
        counted=expressed+sum(r.no_vote for r in rows)
        modal=sum(max(r.yes,r.no,r.abstain) for r in rows)
        ties=sum(majority(r)=='TIE' for r in rows)
        result.append({'year':year,'group':group,'vote_opportunities_observed':len(rows),
                       'expressed_ballots':expressed,'recorded_ballots':counted,
                       'weighted_modal_share':modal/expressed if expressed else None,
                       'explicit_nonvote_rate':(counted-expressed)/counted if counted else None,
                       'tied_votes':ties,'unobserved_eligibility':'UNKNOWN',
                       'historical_group':'AS_LISTED_PER_VOTE_UNCERTIFIED',
                       'mode':'DESCRIPTIVE_UNVALIDATED'})
    return result
