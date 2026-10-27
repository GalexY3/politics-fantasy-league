"""Offline original-shaped fictional data path, never real names/votes or HTTP route."""
import json
from pathlib import Path
from unittest.mock import patch

from politics_fantasy import ingest, quarantine_ingest
from politics_fantasy.private_audit import audit_private_root
from politics_fantasy.private_audit_cli import main as audit_cli


def fake_original(*, corrupt=False):
    source={"votaciones":[{"asiento":"17","voto":"Sí"}],
            "totales":{"afavor":0 if corrupt else 1,"enContra":0,
                       "abstenciones":0,"noVotan":0,"presentes":1}}
    return json.dumps(source,ensure_ascii=False).encode()


class SyntheticResponse:
    status=200
    headers={'Content-Type':'application/json'}
    def __init__(self,url,data): self.url,self.data=url,data
    def __enter__(self): return self
    def __exit__(self,*args): return None
    def geturl(self): return self.url
    def read(self,n): return self.data[:n]


def capture(root, data):
    with patch.object(ingest.time,'sleep',return_value=None):
        return quarantine_ingest.capture_validate_quarantine(
            url='https://www.congreso.es/fictional-document',source='congreso',
            document_kind='congreso_vote',root=root,min_interval=1,
            opener=lambda req,timeout:SyntheticResponse(req.full_url,data))


def test_fictional_valid_capture_schema_quarantine_audit_cli(tmp_path,capsys):
    result=capture(tmp_path,fake_original())
    assert result['quarantine_state']=='QUARANTINED_SCHEMA_PASSED'
    assert result['release_grade'] is False
    agg=audit_private_root(tmp_path)
    assert agg['object_integrity']=={'VALID_OBJECT':1}
    assert agg['quarantine_states']=={'QUARANTINED_SCHEMA_PASSED':1}
    assert agg['unreviewed_captures']==0
    assert audit_cli(['--root',str(tmp_path)])==0
    output=capsys.readouterr().out
    assert 'fictional-document' not in output
    assert result['capture_id'] not in output
    assert result['sha256'] not in output


def test_fictional_corrupted_schema_never_released(tmp_path):
    result=capture(tmp_path,fake_original(corrupt=True))
    assert result['quarantine_state']=='QUARANTINED_SCHEMA_FAILED'
    assert result['validator_result'] is None
    assert result['real_person_scoring'] is False
    agg=audit_private_root(tmp_path)
    assert agg['object_integrity']=={'VALID_OBJECT':1}  # captured bytes, not proof of schema
    assert agg['quarantine_states']=={'QUARANTINED_SCHEMA_FAILED':1}
    assert audit_cli(['--root',str(tmp_path)])==0  # operationally reviewed, not releasable


def test_same_sha_duplicate_capture_without_review_stays_pending(tmp_path):
    result=capture(tmp_path,fake_original())
    with patch.object(ingest.time,'sleep',return_value=None):
        ingest.import_url(url='https://www.congreso.es/fictional-document',source='congreso',root=tmp_path,min_interval=1,
                          opener=lambda req,timeout:SyntheticResponse(req.full_url,fake_original()))
    agg=audit_private_root(tmp_path)
    assert agg['manifest_rows']==2
    assert agg['review_rows']==1
    assert agg['unreviewed_captures']==1
    assert audit_cli(['--root',str(tmp_path)])==2
