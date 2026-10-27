import io
import sys
from pathlib import Path
from hashlib import sha256
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from politics_fantasy.ingest import import_url


class FakeResponse:
    status=200
    headers={'Content-Type':'application/json', 'ETag':'test'}
    def __enter__(self): return self
    def __exit__(self,*args): return None
    def geturl(self): return 'https://www.congreso.es/test.json'
    def read(self,n): return b'{"synthetic": true}'


def test_snapshot_exact_checksum_and_manifest(tmp_path):
    r=import_url(url='https://www.congreso.es/test.json',source='congreso',
                 root=tmp_path,min_interval=1,opener=lambda *args, **kw: FakeResponse())
    assert r['sha256']==sha256(b'{"synthetic": true}').hexdigest()
    assert (tmp_path/r['raw_object']).read_bytes()==b'{"synthetic": true}'
    assert (tmp_path/'manifest.jsonl').is_file()


def test_reject_unapproved_url_before_fetch(tmp_path):
    with pytest.raises(ValueError):
        import_url(url='http://evil.invalid/bad',source='congreso',root=tmp_path,
                   opener=lambda *args,**kw: (_ for _ in ()).throw(AssertionError('network')))

def test_declared_but_short_http_body_fails_before_store(tmp_path):
    class Truncated(FakeResponse):
        headers={'Content-Type':'application/json','Content-Length':'100'}
    with pytest.raises(ValueError,match='TRUNCATED_OR_INCONSISTENT_RESPONSE_LENGTH'):
        import_url(url='https://www.congreso.es/test.json',source='congreso',root=tmp_path,
                   min_interval=1,opener=lambda *args,**kw:Truncated())
    assert not (tmp_path/'manifest.jsonl').exists()
    assert not list((tmp_path/'objects').rglob('*'))


def test_malformed_http_content_length_rejected_before_read(tmp_path):
    class Corrupt(FakeResponse):
        headers={'Content-Length':'-1'}
        def read(self,n): raise AssertionError('body should not be read')
    with pytest.raises(ValueError,match='INVALID_CONTENT_LENGTH'):
        import_url(url='https://www.congreso.es/test.json',source='congreso',root=tmp_path,
                   min_interval=1,opener=lambda *args,**kw:Corrupt())


def test_oversized_declared_http_body_rejected_before_read(tmp_path):
    class TooLarge(FakeResponse):
        headers={'Content-Length':str(20*1024*1024+1)}
        def read(self,n): raise AssertionError('body should not be read')
    with pytest.raises(ValueError,match='RESOURCE_EXCEEDS_20_MIB'):
        import_url(url='https://www.congreso.es/test.json',source='congreso',root=tmp_path,
                   min_interval=1,opener=lambda *args,**kw:TooLarge())


def test_exact_declared_http_content_length_accepts_fake(tmp_path):
    class Exact(FakeResponse):
        headers={'Content-Type':'application/json','Content-Length':str(len(b'{"synthetic": true}'))}
    r=import_url(url='https://www.congreso.es/test.json',source='congreso',root=tmp_path,
                 min_interval=1,opener=lambda *args,**kw:Exact())
    assert (tmp_path/r['raw_object']).read_bytes()==b'{"synthetic": true}'

def test_unsupported_windows_store_fails_before_source_request(tmp_path):
    from unittest.mock import patch
    from politics_fantasy import secure_store
    with patch.object(secure_store.os, 'name', 'nt'):
        with pytest.raises(ValueError, match='SECURE_STORE_UNSUPPORTED_PLATFORM'):
            import_url(url='https://www.congreso.es/test.json', source='congreso',
                       root=tmp_path, min_interval=1,
                       opener=lambda *args, **kwargs: (_ for _ in ()).throw(
                           AssertionError('no network on unsupported OS')))

def test_equal_payload_same_sha_distinct_capture_identifiers(tmp_path, monkeypatch):
    from politics_fantasy import ingest
    monkeypatch.setattr(ingest.time,"sleep",lambda *_:None)
    args=dict(url='https://www.congreso.es/test.json',source='congreso',root=tmp_path,
              min_interval=1,opener=lambda *args, **kw:FakeResponse())
    r1=import_url(**args)
    r2=import_url(**args)
    assert r1['sha256']==r2['sha256']
    assert r1['capture_id']!=r2['capture_id']
    assert len(r1['capture_id'])==len(r2['capture_id'])==32
    records=[__import__('json').loads(x) for x in (tmp_path/'manifest.jsonl').read_text().splitlines()]
    assert [r['capture_id'] for r in records]==[r1['capture_id'],r2['capture_id']]


def test_untrusted_existing_manifest_mode_refused_before_opener(tmp_path):
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_bytes(b'{"synthetic":true}' + bytes([10]))
    manifest.chmod(0o666)
    with pytest.raises(ValueError, match="UNSAFE_STORE_OWNERSHIP_OR_PERMISSIONS"):
        import_url(url="https://www.congreso.es/test.json", source="congreso",
                   root=tmp_path, min_interval=1,
                   opener=lambda *args, **kw: (_ for _ in ()).throw(
                       AssertionError("NETWORK_NOT_ALLOWED_WITH_UNSAFE_MANIFEST")))
    assert manifest.read_bytes() == b'{"synthetic":true}' + bytes([10])
