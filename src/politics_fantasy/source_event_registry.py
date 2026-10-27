"""Read-only, source-scoped event stages: not independent attestation."""
from __future__ import annotations
from types import MappingProxyType
from .provenance_claim_gate import AUTHORITY, evaluate_claim_as_of

_RECORDS = MappingProxyType({
 'ESE/000002-01': MappingProxyType({'authority': AUTHORITY,'evidence_ref':'ESE/000002-01','record_family':'BOCCL_CANDIDATE_ACCEPTANCE','claim_kind':'NOMINATED_AND_ACCEPTED_CANDIDATES','act_day':'2026-09-03','bulletin_day':'2026-09-10','first_public_at':None}),
 'ESE/000002-02': MappingProxyType({'authority': AUTHORITY,'evidence_ref':'ESE/000002-02','record_family':'BOCCL_PLENARY_DESIGNATION','claim_kind':'DESIGNATED_SENATORS','act_day':'2026-09-10','bulletin_day':'2026-09-16','first_public_at':None}),
 'SENADO-XV-P82-20260915': MappingProxyType({'authority':'Senado de Espana','evidence_ref':'SENADO-XV-P82-20260915','record_family':'SENATE_PLENARY_OATH','claim_kind':'OATH_CONSTITUTION_FULFILLED','act_day':'2026-09-15','bulletin_day':None,'first_public_at':None})
})

def public_stage_catalog():
 return {'mode':'UNATTESTED_OFFICIAL_DOCUMENT_INDEX','records':[dict(r) for r in _RECORDS.values()],'full_senator_status_certified':False,'legal_requirements':['CREDENTIAL','DECLARATIONS','OATH'],'original_publication_timestamps_verified':0,'real_person_scoring':False,'release_ready':False}

def evaluate_server_claim(*,evidence_ref:str,desired_claim:str,as_of:str):
 record = _RECORDS.get(evidence_ref) if isinstance(evidence_ref,str) else None
 if record is None: return {'eligible':False,'reason':'UNKNOWN_SERVER_EVIDENCE_REF','release_grade':False}
 if desired_claim=='FULL_SENATOR_STATUS':return {'eligible':False,'reason':'THREE_LEGAL_PREREQUISITES_UNVERIFIED','release_grade':False}
 if record['record_family']=='SENATE_PLENARY_OATH':return {'eligible':False,'reason':'OATH_FIRST_PUBLIC_AT_UNVERIFIED','release_grade':False}
 return evaluate_claim_as_of(authority=record['authority'],record_family=record['record_family'],evidence_ref=record['evidence_ref'],desired_claim=desired_claim,as_of=as_of,trusted_registry=_RECORDS)
