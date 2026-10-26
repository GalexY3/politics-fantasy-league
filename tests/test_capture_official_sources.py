"""Native adversarial source-capture tests; NO live requests or personal data."""
import io
import json
from pathlib import Path
import zipfile
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'scripts'))
import capture_official_sources as C

def xlsx():
    output=io.BytesIO()
    with zipfile.ZipFile(output,"w") as z:
        z.writestr("[Content_Types].xml","<Types/>")
        z.writestr("xl/workbook.xml",'<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Datos" sheetId="1"/></sheets></workbook>')
    return output.getvalue()

class FakeResponse:
    status=200
    headers={"content-type":"application/json"}
    def __init__(self,data,final_url):
        self.data,self.final_url=data,final_url
    def geturl(self):return self.final_url
    def read(self,n=-1):return self.data if n<0 else self.data[:n]
    def __enter__(self):return self
    def __exit__(self,*args):return False

def mock_bytes(body,url):
    def opener(request,timeout,context):
        return FakeResponse(body,url)
    return opener

def test_json_keys_no_private_person_values():
    shape=C.introspect(json.dumps([{"NOMBRE":"Persona Ficticia","FORMACIONELECTORAL":"Grupo ficticio"}]).encode(),"json")
    assert shape["root"]=="array"
    assert shape["first_object_keys"]==["FORMACIONELECTORAL","NOMBRE"]
    assert "Persona Ficticia" not in json.dumps(shape)

def test_valid_xlsx_workbook_structure():
    shape=C.introspect(xlsx(),"xlsx")
    assert shape["sheets_count"]==1
    assert shape["sheets_shape"][0]["name_length"]==5
    assert shape["contains_workbook_xml"] is True

def test_reject_non_office_file():
    with pytest.raises(ValueError,match="WRONG_OFFICE_SIGNATURE"):
        C.introspect(b"<html>not a spreadsheet</html>","xlsx")

def test_capture_sha256_only_with_correct_institution_domain(monkeypatch,tmp_path:Path):
    monkeypatch.setattr(C,"ROOT",tmp_path)
    url="https://www.congreso.es/example.json"
    reply=C.fetch_target("test",url,"json","www.congreso.es",
        opener=mock_bytes(b'[{"PUBLIC":"DATO_PUBLICO_DEMO"}]',url))
    assert reply["original_binary_captured"] is True
    assert reply["capture_status"]=="RAW_BYTES_CAPTURED"
    assert reply["bytes"]==len(b'[{"PUBLIC":"DATO_PUBLICO_DEMO"}]')
    assert len(reply["sha256"])==64
    assert (tmp_path/"test.json").read_bytes()==b'[{"PUBLIC":"DATO_PUBLICO_DEMO"}]'

def test_redirect_to_third_party_rejected(monkeypatch,tmp_path):
    monkeypatch.setattr(C,"ROOT",tmp_path)
    result=C.fetch_target("s","https://www.congreso.es/example.json","json","www.congreso.es",
        opener=mock_bytes(b'[{"PUBLIC":"DATO"}]',"https://unexpected.example/download.json"))
    assert result["original_binary_captured"] is False
    assert result["capture_status"]=="STOP_R5_NETWORK_OR_FORMAT"
    assert result["error"]=="HTTPS_REDIRECT_OUTSIDE_OFFICIAL_HOST"
    assert not list(tmp_path.iterdir())

def test_fake_html_content_with_json_extension_is_blocked(monkeypatch,tmp_path):
    monkeypatch.setattr(C,"ROOT",tmp_path)
    url="https://www.congreso.es/a.json"
    result=C.fetch_target("bad",url,"json","www.congreso.es",opener=mock_bytes(b"<html><body>error</body></html>",url))
    assert result["original_binary_captured"] is False
    assert result["error_type"]=="JSONDecodeError"
    assert not list(tmp_path.iterdir())


def test_pdf_signatures_with_embedded_fake_pdf_bytes():
    fake=b"%PDF-1.4\\n"+b" " * 100+b"%%EOF\\n"
    val=C.introspect(fake,"pdf")
    assert val["signature_valid"] is True
    assert val["format"] == "pdf"
    with pytest.raises(ValueError,match="INVALID_PDF_MAGIC_OR_FOOTER"):
        C.introspect(b"<html>wrong PDF</html>","pdf")
