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
