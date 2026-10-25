import pytest
from datetime import datetime,timezone,timedelta
from politics_fantasy.field_ingest import read_snapshot
from politics_fantasy.field_audit import as_of_import,quality_gates,coverage_gate,cluster_inventory,topic_provenance
T=datetime(2026,10,25,tzinfo=timezone.utc)
HI='votacion_id,fecha,temas,diputado_id,grupo,voto\n'
HA='id,fecha,si,no,abstencion,no_vota\n'

def sources(tmp, individuals='s202-v020,2026-09-30,instituciones,001,GR1,Sí\n',aggregates='s202-v020,2026-09-30,1,0,0,0\n'):
 p=tmp/'a.csv';p.write_text(HI+individuals);q=tmp/'b.csv';q.write_text(HA+aggregates)
 return read_snapshot(p,kind='individual',acquired_at=T),read_snapshot(q,kind='aggregate',acquired_at=T)

def test_b30b_13_asof_respects_local_acquisition_not_old_event_date(tmp_path):
 i,_=sources(tmp_path)
 assert as_of_import(i,T-timedelta(minutes=1)) is None
 assert as_of_import(i,T)==i

def test_b30b_14_naive_asof_rejected(tmp_path):
 i,_=sources(tmp_path)
 with pytest.raises(ValueError,match='Naive'):
  as_of_import(i,datetime(2026,10,25))

def test_b30b_15_chamber_capacity_is_warning_not_truth(tmp_path):
 i,a=sources(tmp_path,aggregates='s202-v020,2026-09-30,351,0,0,0\n')
 g=quality_gates(i,a)
 assert g['nominal_exceeds_seats']==['s202-v020'] and g['source_certified'] is False

def test_b30b_16_field_gate_cannot_self_certify_sources(tmp_path):
 i,a=sources(tmp_path);g=quality_gates(i,a)
 report=coverage_gate(g,roster_verified=True,original_publication_verified=True,license_reviewed=True)
 assert report['inference_ready'] is False
 assert report['blockers']==['EXTERNAL_SOURCE_ATTESTATION_REQUIRED']

def test_b30b_17_cluster_inference_not_row_as_independent(tmp_path):
 i,_=sources(tmp_path,individuals='s202-v020,2026-09-30,x,001,GR1,Sí\ns202-v020,2026-09-30,x,002,GR1,No\ns202-v021,2026-09-30,y,001,GR1,Sí\n')
 x=cluster_inventory(i)
 assert (x['nominal_rows'],x['votes'],x['sessions'])==(3,2,1)

def test_b30b_18_topics_are_not_institutional_classification(tmp_path):
 i,_=sources(tmp_path)
 assert topic_provenance(i)['is_institutional_classification'] is False
 assert quality_gates(*sources(tmp_path))['allows_missing_row_as_absence'] is False
