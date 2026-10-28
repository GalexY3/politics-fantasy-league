import io
import unittest
from zipfile import ZipFile, ZIP_DEFLATED
from politics_fantasy.source_capture_guard import inspect_xlsx_bytes

OFFICIAL_URL='https://descargas.interior.gob.es/datasets/paridad_electoral/Paridad-cargos-electos.xlsx'

def fixture_xlsx():
    b=io.BytesIO()
    with ZipFile(b,'w',ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<Types/>')
        z.writestr('_rels/.rels','<Relationships/>')
        z.writestr('xl/workbook.xml','<workbook/>')
        z.writestr('xl/worksheets/sheet1.xml','<worksheet/>')
    return b.getvalue()

class TestOriginalSourceGuard(unittest.TestCase):
    def test_valid_minimal_synthetic_workbook(self):
        x=inspect_xlsx_bytes(OFFICIAL_URL,fixture_xlsx())
        self.assertEqual(x['structure'],'OOXML_XLSX_ZIP_VALID_SYNTHETIC_OR_UNVERIFIED_ORIGIN')
        self.assertEqual(x['sheets'],1)
        self.assertEqual(x['byte_length'],len(fixture_xlsx()))
        self.assertEqual(len(x['sha256']),64)
        self.assertFalse(x['origin_authenticated'])
        self.assertIsNone(x['first_public_at'])
    def test_missing_payload_and_metadata_only(self):
        for b in (None,b'', 'not bytes'):
            with self.assertRaisesRegex((TypeError,ValueError),'BYTES_REQUIRED'):
                inspect_xlsx_bytes(OFFICIAL_URL,b)
    def test_reject_wrong_scheme_and_userinfo(self):
        for url in ('http://descargas.interior.gob.es/a.xlsx','https://evil@descargas.interior.gob.es/a.xlsx',
                    'https://descargas.interior.gob.es/a.xlsx#trick', 'https://descargas.interior.gob.es.evil.invalid/a.xlsx'):
            with self.assertRaisesRegex(ValueError,'UNSAFE_SOURCE_URL'):
                inspect_xlsx_bytes(url,fixture_xlsx())
    def test_reject_html_renamed_to_xlsx(self):
        with self.assertRaisesRegex(ValueError,'NOT_XLSX_ARCHIVE'):
            inspect_xlsx_bytes(OFFICIAL_URL,b'<html>403 forbidden</html>')
    def test_reject_incomplete_zip(self):
        b=io.BytesIO()
        with ZipFile(b,'w') as z:z.writestr('random.txt','not a workbook')
        with self.assertRaisesRegex(ValueError,'MISSING_XLSX_PART'):
            inspect_xlsx_bytes(OFFICIAL_URL,b.getvalue())
    def test_reject_hash_mismatch(self):
        with self.assertRaisesRegex(ValueError,'HASH_MISMATCH'):
            inspect_xlsx_bytes(OFFICIAL_URL,fixture_xlsx(),declared_sha256='a'*64)
    def test_reject_path_traversal_zip_member(self):
        b=io.BytesIO()
        with ZipFile(b,'w') as z:
            z.writestr('[Content_Types].xml','<Types/>')
            z.writestr('_rels/.rels','<Relationships/>')
            z.writestr('xl/workbook.xml','<workbook/>')
            z.writestr('xl/worksheets/sheet1.xml','<worksheet/>')
            z.writestr('../traversal.txt','bad')
        with self.assertRaisesRegex(ValueError,'UNSAFE_ZIP_MEMBER'):
            inspect_xlsx_bytes(OFFICIAL_URL,b.getvalue())
    def test_reject_trailing_garbage(self):
        with self.assertRaisesRegex(ValueError,'TRAILING_ZIP_BYTES'):
            inspect_xlsx_bytes(OFFICIAL_URL,fixture_xlsx()+b'<html>stuff')

if __name__=='__main__':unittest.main()
