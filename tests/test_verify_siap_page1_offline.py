"""Second independent HTML index parser; source original replay is separate CLI."""
from hashlib import sha256
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from verify_siap_page1_offline import (
    GateError, parse_only_pagination_and_source_keys, pinned,
)


def page(html: str) -> bytes:
    return html.encode("utf-8")


def test_replay_parser_only_extracts_unique_source_local_ids():
    raw=page("""<!doctype html><html><head><title>Indice</title></head><body>
      <span>Pàgina 1 de 44</span>
      <a href="/ext/f?p=siap-cerca:expedient:1">202-00001/15</a>
      <a href="https://www.parlament.cat/ext/f?p=siap-cerca:expedient:2">202-00002/14</a>
      <p>Situació: [outcome deliberately hidden]</p>
      <script>let fake="202-00003/15";</script></body></html>""")
    n,pages,ids=parse_only_pagination_and_source_keys(raw)
    assert n==1 and pages==44 and ids==("202-00001/15","202-00002/14")
    assert "outcome" not in " ".join(ids)


@pytest.mark.parametrize("raw,why",[
    ("<a href='/x'>202-00001/15</a>", "BAD_PAGINATION_OR_UNTRUSTED_SOURCE_LINKS"),
    ("Pàgina 2 de 44 <a href='/x'>202-00001/15</a>", "WRONG_PAGE_OR_DUPLICATE_LINKS"),
    ("Pàgina 1 de 44 Pàgina 1 de 45 <a href='/x'>202-00001/15</a>",
     "BAD_PAGINATION_OR_UNTRUSTED_SOURCE_LINKS"),
    ("Pàgina 1 de 44 <a href='/x'>202-00001/15</a> "
     "<a href='/x'>202-00001/15</a>", "WRONG_PAGE_OR_DUPLICATE_LINKS"),
    ("Pàgina 1 de 44 <a href='https://bad.example/exploit'>202-00001/15</a>",
     "BAD_PAGINATION_OR_UNTRUSTED_SOURCE_LINKS"),
    ("Pàgina 1 de 44 <a href='https://foo@www.parlament.cat/x'>202-00001/15</a>",
     "BAD_PAGINATION_OR_UNTRUSTED_SOURCE_LINKS"),
    ("Pàgina 1 de 44 <script>202-00001/15</script>",
     "BAD_PAGINATION_OR_UNTRUSTED_SOURCE_LINKS"),
])
def test_bad_cursor_duplicate_or_external_source_link_quarantined(raw,why):
    with pytest.raises(GateError,match=why):
        parse_only_pagination_and_source_keys(page(raw))


def test_sha_receipt_rejects_unreviewed_byte(tmp_path:Path):
    path=tmp_path/"fixture.html"
    path.write_bytes(b"first")
    check=sha256(b"first").hexdigest()
    assert pinned(path,check,100)==b"first"
    path.write_bytes(b"changed")
    with pytest.raises(GateError,match="ORIGINAL_OR_RECEIPT_HASH_CHANGED"):
        pinned(path,check,100)


def test_invalid_utf8_and_blank_source_blocked():
    with pytest.raises(GateError,match="INVALID_SOURCE_HTML_ENCODING"):
        parse_only_pagination_and_source_keys(b"\xff"*5)
    with pytest.raises(GateError,match="BAD_ORIGINAL_HTML_SIZE"):
        parse_only_pagination_and_source_keys(b"")
