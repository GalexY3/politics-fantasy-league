"""SHA-locked discovery-only Spanish parliamentary source catalogue.

No HTTP, datasets, case identifiers, permission acceptance or science outcomes.
This is a strictly descriptive local inventory, not an authority on whether
the user may accept external terms. A source's catalogue label cannot grant
rights to fetch the underlying original.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

from .procedural_index_contract import utc

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT / 'data/source_manifests/spanish_procedural_candidates_r7_20261031.json'
PINNED_SHA='653607e72a1e294d4cc50eadc10f3b75d308159e6b6847c22c35e22864ee87db'
SAFE_BY=datetime(2026,11,1,0,0,0,tzinfo=timezone.utc)
HOSTS={
    'ASAMBLEA_MADRID_OPENDATA':'ctyp.asambleamadrid.es',
    'CEPC_INICPAR':'www.cepc.gob.es',
    'SENADO_BIBLIOTECA_APCA':'www.senado.es',
    'PARLAMENTO_NAVARRA_INICIATIVAS':'parlamentodenavarra.es',
}
RIGHTS={
    'ASAMBLEA_MADRID_OPENDATA':'TERMS_ACCEPTED_BY_USE_NOT_AUTHORIZED_FOR_AUTOMATED_ORIGINAL_GET',
    'CEPC_INICPAR':'ALL_RIGHTS_RESERVED_NO_BULK_DATASET_REUSE_ATTESTED',
    'SENADO_BIBLIOTECA_APCA':'SOURCE_INOPERATIVE_AND_DATA_REUSE_NOT_ATTESTED',
    'PARLAMENTO_NAVARRA_INICIATIVAS':'NO_SOURCE_SPECIFIC_BULK_REUSE_LICENSE_REVIEWED',
}


def _unique_pairs(pairs):
    values={}
    for k,v in pairs:
        if k in values:
            raise ValueError('DUPLICATED_SOURCE_MATRIX_JSON_KEY')
        values[k]=v
    return values


def _load(path:Path) -> list[dict]:
    if path.is_symlink() or not path.is_file() or not 500 < path.stat().st_size < 15_000:
        raise ValueError('DISCOVERY_MANIFEST_MISSING_OR_WRONG_SIZE')
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=PINNED_SHA:
        raise ValueError('DISCOVERY_MANIFEST_SHA_MISMATCH')
    obj=json.loads(raw.decode('utf8'),object_pairs_hook=_unique_pairs,
                   parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NONFINITE_JSON')))
    if (type(obj)!=dict or set(obj)!={'schema','audited_day_utc','purpose',
             'direct_distribution_GET','new_real_case_records_downloaded',
             'case_outcomes_inspected','complete_registered_population_proven',
             'historical_first_public_at_proven','ABH_cycles',
             'rights_or_terms_accepted_for_user','sources'}
            or obj['schema']!='pfl.spanish_procedural_discovery.v1'
            or obj['audited_day_utc']!='2026-10-31'
            or obj['purpose']!='PUBLIC_DOCUMENTARY_DISCOVERY_NOT_ORIGINAL_DATA_ACQUISITION'
            or type(obj['direct_distribution_GET']) is not int
            or obj['direct_distribution_GET']!=0
            or type(obj['new_real_case_records_downloaded']) is not int
            or obj['new_real_case_records_downloaded']!=0
            or type(obj['ABH_cycles']) is not int or obj['ABH_cycles']!=0
            or any(obj[k] is not False for k in (
                'case_outcomes_inspected','complete_registered_population_proven',
                'historical_first_public_at_proven','rights_or_terms_accepted_for_user'))):
        raise ValueError('UNSUPPORTED_DISCOVERY_PROMOTION')
    sources=obj['sources']
    if not isinstance(sources,list) or len(sources)!=len(HOSTS):
        raise ValueError('UNEXPECTED_DISCOVERY_SOURCES')
    seen=set()
    output=[]
    for s in sources:
        if not isinstance(s,dict) or set(s)!={
            'source_id','institution','official_metadata_url','catalogue_asset',
            'internal_origin','grain','coverage_note','rights_status','general_license_label',
            'legal_evidence','licence_specific_original_downloaded','original_sha256',
            'published_register_entry_denominator','dated_transitions_certified',
            'historical_vintages_verified','first_public_at','eligible_scientific_source'
        }:
            raise ValueError('UNEXPECTED_SOURCE_SCHEMA')
        src=s['source_id']
        if src not in HOSTS or src in seen or s['rights_status']!=RIGHTS[src]:
            raise ValueError('UNAUTHORIZED_SOURCE_OR_RIGHTS_CHANGE')
        seen.add(src)
        url=urlsplit(s['official_metadata_url'])
        if (url.scheme!='https' or url.hostname!=HOSTS[src] or url.username
                or url.password or url.port or url.fragment):
            raise ValueError('UNTRUSTED_DISCOVERY_URL')
        if any(not isinstance(s[key],str) or len(s[key])>1000 for key in (
             'institution','catalogue_asset','internal_origin','grain','coverage_note',
             'general_license_label','legal_evidence')):
            raise ValueError('INVALID_DISCOVERY_TEXT')
        if any(s[key] is not False for key in (
            'licence_specific_original_downloaded','dated_transitions_certified',
            'historical_vintages_verified','eligible_scientific_source')):
            raise ValueError('UNATTESTED_SCIENTIFIC_PROMOTION')
        if any(s[key] is not None for key in (
            'original_sha256','published_register_entry_denominator','first_public_at')):
            raise ValueError('HISTORICAL_OR_CENSUS_FIELD_PROMOTION')
        output.append({
            'source_id':src,'institution':s['institution'],
            'unit':s['grain'],'catalogue_asset':s['catalogue_asset'],
            'access_gate':s['rights_status'],
            'evidence_grade':'OFFICIAL_INDEX_DESCRIPTION_ONLY',
            'original_downloaded':False,
            'source_population_denominator':None,
            'outcomes_or_events_admitted':False,
            'first_public_at':None,
        })
    if seen!=set(HOSTS):
        raise ValueError('SOURCE_DISCOVERY_MISSING')
    return output


def status(*,as_of:str|None=None,path:Path|None=None) -> dict:
    cutoff=utc(as_of) if as_of is not None else None
    base={
        'schema':'pfl.procedural_discovery_r7.status.v1',
        'as_of':as_of,'all_registered_congress_denominator':None,
        'direct_bulk_download_authorized_by_this_inventory':False,
        'new_case_records_admitted':None,'first_public_at':None,
        'case_outcomes_admitted':False,'historical_asof_verified':False,
        'real_person_scoring':False,'ABH_cycles':0,
    }
    if cutoff is not None and cutoff<SAFE_BY:
        return {**base,'status':'DISCOVERY_NOT_KNOWN_AT_CUT',
                'candidate_sources':[],'documentary_sources_count':None,
                'local_audit_safe_by':None,'manifest_sha256':None}
    try:
        sources=_load(path if path is not None else MANIFEST)
    except (OSError,ValueError,TypeError,KeyError,AttributeError):
        return {**base,'status':'DISCOVERY_MANIFEST_QUARANTINED',
                'candidate_sources':[],'documentary_sources_count':None,
                'local_audit_safe_by':None,'manifest_sha256':None}
    return {**base,'status':'DOCUMENTARY_CANDIDATES_BLOCKED_FROM_SOURCE_ADMISSION',
            'candidate_sources':sources,
            'documentary_sources_count':len(sources),
            'local_audit_safe_by':SAFE_BY.isoformat(),
            'manifest_sha256':PINNED_SHA,
            'interpretation':('Descriptions of official indices, with unresolved or binding '
                              'conditions. No download, entry frame, archival revisions or outcomes.')}
