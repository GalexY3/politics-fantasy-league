"""Offline, opt-in field CSV audit: does not fetch political data or score deputies.

Usage: python -m politics_fantasy.field_cli --individual <csv> --aggregate <csv>
       --acquired-at 2026-10-25T08:00:00+01:00 --out <report.json>
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from .field_ingest import ATTRIBUTION, SOURCE_PAGE, read_snapshot,summary_one
from .field_audit import quality_gates,coverage_gate,cluster_inventory,topic_provenance
from .reconcile import reconcile,group_snapshot
from .groupvotes import read_group_snapshot,reconcile_groups
from .groupmetrics import group_period_summary
from .readiness import research_readiness, observed_label_transitions


def make_field_report(*, individual: Path, aggregate: Path, acquired_at:datetime, group:Path|None=None) -> dict:
    i=read_snapshot(individual,kind='individual',acquired_at=acquired_at)
    a=read_snapshot(aggregate,kind='aggregate',acquired_at=acquired_at)
    comp=reconcile(i,a)
    gates=quality_gates(i,a)
    core={
        'schema_version':'1.0', 'mode':'USER_SUPPLIED_CSV_UNCERTIFIED',
        'source_page':SOURCE_PAGE, 'source_attribution':ATTRIBUTION,
        'license':'CC BY 4.0 claimed on source page; review before redistribution',
        'first_original_publication_verified':False,
        'membership_at_vote_certified':False,
        'empirical_findings_validated':False,
        'may_score_real_persons':False,
        'source_snapshots':{
            'individual':{'sha256':i.provenance.sha256,'bytes':i.provenance.input_bytes,
                          'observed_at':i.provenance.acquired_at},
            'aggregate':{'sha256':a.provenance.sha256,'bytes':a.provenance.input_bytes,
                         'observed_at':a.provenance.acquired_at}},
        'coverage':{'individual':summary_one(i),'aggregate':summary_one(a)},
        'reconciliation':{'summary':comp['summary'],'any_unresolved':comp['any_unresolved']},
        'quality':gates,'gate':coverage_gate(gates,roster_verified=False,
                     original_publication_verified=False,license_reviewed=False),
        'clusters':cluster_inventory(i),
        'topics':topic_provenance(i),
        'groups':group_snapshot(i),
        'observed_group_label_changes':observed_label_transitions(i),
        'VSDS':{'grade':1,'scientific_grade':0,'reason':'Offline schema audit, not independently attested field finding'},
        'limitations':['CSV may have been filtered or edited',
                       'No complete historically dated roster',
                       'No certified original publication timestamps',
                       'One file snapshot cannot establish 2023 availability',
                       'Group labels and title keyword topics need independent interpretation',
                       'No validated individual political game scoring']
    }
    if group is not None:
        gs=read_group_snapshot(group,acquired_at=acquired_at)
        evidence=reconcile_groups(gs,a,i)
        periods=group_period_summary(gs)
        core['source_snapshots']['group']={'sha256':gs.provenance.sha256,'bytes':gs.provenance.input_bytes,
                                           'observed_at':gs.provenance.acquired_at}
        core['group_audit']={'group_rows':len(gs.rows),'group_labels':len({r.group for r in gs.rows}),
                             'votations':len({r.vote_id for r in gs.rows}),
                             'years':len({r.day.year for r in gs.rows}),
                             'total_expressed':sum(r.yes+r.no+r.abstain for r in gs.rows),
                             'total_explicit_nonvote':sum(r.no_vote for r in gs.rows),
                             'reconciliation_summary':evidence['summary'],
                             'aggregate_consistent':evidence['aggregate_consistent'],
                             'nominal_group_complete':evidence['nominal_group_complete'],
                             'nominal_group_undercounts':evidence['nominal_group_undercounts'],
                             'nominal_group_overages':evidence['nominal_group_overages'],
                             'group_date_conflicts':evidence['group_votes_with_conflicting_dates'],
                             'interpretation':'RECORDED_GROUP_CHOICES_NOT_PARTY_DISCIPLINE',
                             'group_history':'LABEL_AS_REPORTED_NOT_INDEPENDENTLY_ATTESTED'}
        # No period/group breakdown in API receipts: they can contain small sensitive cells.
    core['research_readiness']=research_readiness(core)
    binary=json.dumps(core,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
    core['report_sha256']=hashlib.sha256(binary).hexdigest()
    return core


def write_report_once(report:dict,out:Path)->None:
    """Atomic, no-clobber creation; a failed/crashed write never replaces prior work."""
    path=Path(out)
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode('utf-8')
    temp_name=None
    try:
        with tempfile.NamedTemporaryFile(mode='wb',prefix='.field-audit-',dir=path.parent,
                                         delete=False) as f:
            temp_name=f.name
            f.write(payload);f.flush();os.fsync(f.fileno())
        # Hard link is atomic (and will refuse to replace an existing report).
        os.link(temp_name,path)
    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)


def main(argv=None):
    p=argparse.ArgumentParser(description='Offline CSV evidence audit; not official certification')
    p.add_argument('--individual',type=Path,required=True)
    p.add_argument('--aggregate',type=Path,required=True)
    p.add_argument('--group',type=Path,help='Optional third-party group-level CSV')
    p.add_argument('--acquired-at',required=True,help='Exact local UTC/offset datetime of file acquisition')
    p.add_argument('--out',type=Path,required=True)
    ns=p.parse_args(argv)
    try:
        acquired_at=datetime.fromisoformat(ns.acquired_at)
        report=make_field_report(individual=ns.individual,aggregate=ns.aggregate,acquired_at=acquired_at,group=ns.group)
        write_report_once(report,ns.out)
    except (OSError,ValueError) as ex:
        p.exit(2,'Audit rejected: '+str(ex)+'\n')
    print('Saved non-certifying audit:',ns.out,'; sha256:',report['report_sha256'])
    return 0

if __name__=='__main__':
    raise SystemExit(main())
