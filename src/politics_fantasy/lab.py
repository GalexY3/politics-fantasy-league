"""Isolated, explicitly SYNTHETIC sociology laboratory for the local application.

No individual from the real Congress, no attribution, no real game scoring.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime,timezone
from .rollcall import NominalVote,rollcall_as_of
from .sociometrics import participation,dissent_report
from .structural import pair_agreement,expressed_diversity

T=datetime(2026,1,1,tzinfo=timezone.utc)
SRC='https://example.org/SYNTHETIC_NOT_REAL_PARLIAMENT'
H='0'*64


def synthetic_rollcalls() -> tuple[NominalVote,...]:
    """No randomness, no resemblance to named real persons. Includes incomplete cases."""
    rows=[
      ('V01','SYN-P01','SYN-G1','YES'),('V01','SYN-P02','SYN-G1','YES'),
      ('V01','SYN-P03','SYN-G2','NO'),('V01','SYN-P04','SYN-G2','NO_VOTE'),
      ('V02','SYN-P01','SYN-G1','NO'),('V02','SYN-P02','SYN-G1','NO'),
      ('V02','SYN-P03','SYN-G2','YES'),('V02','SYN-P04','SYN-G2','YES'),
      ('V03','SYN-P01','SYN-G1','ABSTAIN'),('V03','SYN-P02','SYN-G1','YES'),
      ('V03','SYN-P03','SYN-G2','NO'),
    ]
    return tuple(NominalVote(v,p,g,c,T,T,T,SRC,H) for v,p,g,c in rows)


def project_value_grade(*, artifact_valid:bool, source_certified:bool=False,
                        semantics_audited:bool=False, baseline_competent:bool=False,
                        coverage_certified:bool=False, independently_replicated:bool=False,
                        utility_demonstrated:bool=False) -> dict:
    """VSDS 0–3 local VALUE scale; scientific novelty grading is independent."""
    if not artifact_valid: grade=0
    elif not (source_certified and semantics_audited and baseline_competent and coverage_certified):grade=1
    elif not (independently_replicated and utility_demonstrated): grade=2
    else:grade=3
    return {'grade':grade,'scale':'VSDS_PROJECT_ONLY_VALUE_NOT_NOVELTY','scientific_novelty_grade':0,
            'evidence_level':('UNUSABLE','ENGINEERING_LOCAL','FIELD_ANALYTICAL','EXTERNALLY_VALIDATED_VALUE')[grade]}


def local_lab_report() -> dict:
    votes=rollcall_as_of(synthetic_rollcalls(),T)
    census=('V01','V02','V03')  # synthetic roster opportunities, not real calendar
    coverage=[]
    for p in sorted({x.person_id for x in votes}):
        x=participation(votes,person_id=p,eligible_vote_ids=census)
        coverage.append({'actor':p,'eligible':x.eligible,'expressed':x.expressed,
                         'explicit_no_vote':x.no_vote,'unknown':x.unknown,
                         'participation':x.rate,'status':x.status})
    pair=pair_agreement(votes,left='SYN-P01',right='SYN-P02')
    dissent=dissent_report(votes,exclude_groups=frozenset({'Mixto','SYN-HETEROGENEOUS'}))
    diversity=expressed_diversity([v.choice for v in votes])
    grade=project_value_grade(artifact_valid=True)
    data={'mode':'SYNTHETIC_NOT_SPANISH_PARLIAMENT','source_status':'FICTIONAL_NO_SOURCE_CLAIM',
          'real_politician_scoring':False,'records':len(votes),'opportunities':len(census),
          'participation':coverage,'pair_comparison':pair,'expressed_diversity':diversity,
          'dissent':{k:{'numerator':v['dissent'],'denominator':v['eligible_expressed'],'rate':v['rate']}
                    for k,v in dissent.items()},
          'value_grade':grade,'warn':'Fixture SINTÉTICA: No es comportamiento político real ni ideología o influencia; el no-voto no se infiere de ausencias.'}
    payload=json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    data['report_sha256']=hashlib.sha256(payload).hexdigest()
    return data
