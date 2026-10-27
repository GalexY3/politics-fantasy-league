"""Synthetic controls preserve unknown, missing, duplicate and absence semantics."""
import importlib.util
from pathlib import Path
from xml.etree import ElementTree as ET

script=Path(__file__).resolve().parents[1]/'scripts/audit_senate_vote_consistency.py'
spec=importlib.util.spec_from_file_location('senate_consistency',script)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def vote(value='Sí', seat='1', total='1', extra=''):
    return ET.fromstring(f'<votacion><num_vot>1</num_vot><CodVotacion>A</CodVotacion>'
        f'<tot_afirmativos>{total}</tot_afirmativos><tot_negativos>0</tot_negativos>'
        f'<tot_abstenciones>0</tot_abstenciones><tot_novotan>0</tot_novotan>'
        f'<tot_nulos>0</tot_nulos><tot_ausentes>1</tot_ausentes><tot_presentes>1</tot_presentes>'
        f'<resultado><VotoSenador><escano>{seat}</escano><voto>{value}</voto></VotoSenador>{extra}</resultado>'
        f'<ausentes><ausencia><escano>2</escano></ausencia></ausentes></votacion>')


def test_unknown_label_is_not_silently_assigned():
    result=audit.audit_vote(vote(value='Desconocido'),audit.STRICT_LABELS)
    assert result['unknown_labels']=={'DESCONOCIDO':1}
    assert all(v is None for v in result['candidate_category_matches'].values())


def test_different_total_and_duplicate_seat_are_detected():
    r=audit.audit_vote(vote(total='2',extra='<VotoSenador><escano>1</escano><voto>No</voto></VotoSenador>'),audit.STRICT_LABELS)
    assert r['candidate_category_matches']['yes'] is False
    assert r['candidate_category_matches']['no'] is False
    assert r['duplicate_seat_rows']==1


def test_absence_is_not_counted_as_no_vote():
    r=audit.audit_vote(vote(),audit.STRICT_LABELS)
    assert r['absence_rows']==1 and r['absence_count_match'] is True
    assert r['known_vote_counts']['no_vote']==0


def test_missing_total_is_unknown_not_zero():
    r=audit.audit_vote(vote(total=''),audit.STRICT_LABELS)
    assert r['declared_totals']['yes'] is None
    assert r['candidate_category_matches']['yes'] is None


def test_observed_plural_requires_explicit_posthoc_mapping():
    v=vote(value='NO VOTAN',total='0')
    assert audit.audit_vote(v,audit.STRICT_LABELS)['unknown_labels']=={'NO VOTAN':1}
    assert audit.audit_vote(v,{**audit.STRICT_LABELS,'NO VOTAN':'no_vote'})['known_vote_counts']['no_vote']==1
