"""No-network private snapshot/schema/quarantine integration with fictional rows."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from politics_fantasy import quarantine_ingest as pipeline
from politics_fantasy import ingest


def congress_bytes(*, broken=False):
    x = {
        "votaciones": [{"asiento": "11", "voto": "Sí"},
                       {"asiento": "-1", "voto": "No vota"}],
        "totales": {"afavor": 1 if not broken else 2, "enContra": 0,
                   "abstenciones": 0, "noVotan": 1, "presentes": 1},
    }
    return json.dumps(x, ensure_ascii=False).encode()


def senate_bytes():
    return (b"<main><sesion><fecha_sesion>07/10/2025</fecha_sesion>"
            b"<votacion><num_vot>1</num_vot><CodVotacion>101</CodVotacion>"
            b"<fecha_v>08-OCT-2025</fecha_v>"
            b"<tot_afirmativos>0</tot_afirmativos><tot_negativos>0</tot_negativos>"
            b"<tot_abstenciones>0</tot_abstenciones><tot_novotan>1</tot_novotan>"
            b"<tot_presentes>1</tot_presentes><tot_ausentes>0</tot_ausentes>"
            b"<resultado><VotoSenador><escano>11</escano>"
            b"<voto>NO VOTAN</voto></VotoSenador></resultado>"
            b"<ausentes/></votacion></sesion></main>")


class MockResponse:
    status = 200
    headers = {"Content-Type": "application/json"}
    def __init__(self, url, payload): self.url, self.payload = url, payload
    def __enter__(self): return self
    def __exit__(self, *args): return None
    def geturl(self): return self.url
    def read(self, n): return self.payload[:n]


class QuarantinePipelineTests(unittest.TestCase):
    def capture(self, root, *, source, kind, content, opener=None):
        url = f"https://www.{source}.es/fake-original"
        responder = opener or (lambda request, timeout: MockResponse(request.full_url,content))
        with patch.object(ingest.time, "sleep", return_value=None):
            return pipeline.capture_validate_quarantine(
                url=url, source=source, document_kind=kind, root=root,
                opener=responder, min_interval=1,
            )

    def test_congress_valid_structure_always_quarantined(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            result=self.capture(root,source="congreso",kind="congreso_vote",content=congress_bytes())
            self.assertEqual(result["quarantine_state"],"QUARANTINED_SCHEMA_PASSED")
            self.assertEqual(result["validator_result"]["nominal_rows"],2)
            self.assertFalse(result["real_person_scoring"])
            self.assertFalse(result["release_grade"])
            self.assertIsNone(result["first_public_at"])
            self.assertFalse(result["http_ingest_endpoint_connected"])
            self.assertEqual(len((root/"manifest.jsonl").read_text().splitlines()),1)
            self.assertEqual(len((root/"quarantine_reviews.jsonl").read_text().splitlines()),1)

    def test_corrupted_congress_totals_stay_quarantined(self):
        with tempfile.TemporaryDirectory() as td:
            result=self.capture(Path(td),source="congreso",kind="congreso_vote",content=congress_bytes(broken=True))
            self.assertEqual(result["quarantine_state"],"QUARANTINED_SCHEMA_FAILED")
            self.assertIsNone(result["validator_result"])
            self.assertFalse(result["real_person_scoring"])

    def test_senate_valid_xml_schema_without_semantic_publication_claim(self):
        with tempfile.TemporaryDirectory() as td:
            result=self.capture(Path(td),source="senado",kind="senado_session",content=senate_bytes())
            self.assertEqual(result["quarantine_state"],"QUARANTINED_SCHEMA_PASSED")
            self.assertEqual(result["validator_result"]["votes_verified"],1)
            self.assertFalse(result["senate_no_votan_institutional_semantics_verified"])
            self.assertIsNone(result["first_public_at"])

    def test_wrong_source_kind_denied_before_any_open(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"SOURCE_DOCUMENT_KIND_MISMATCH"):
                self.capture(Path(td),source="congreso",kind="senado_session",
                             content=b"{}",opener=lambda *x,**kw:self.fail("network"))
            self.assertFalse((Path(td)/"manifest.jsonl").exists())

    def test_unsupported_kind_denied_before_any_open(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"UNSUPPORTED_DOCUMENT_KIND"):
                self.capture(Path(td),source="boe",kind="rpp_party",content=b"{}",
                             opener=lambda *x,**kw:self.fail("network"))

    def test_quarantine_ledger_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            outside=root.parent / (root.name + "_outside_review")
            outside.write_bytes(b"DO_NOT_MODIFY")
            (root / "quarantine_reviews.jsonl").symlink_to(outside)
            with self.assertRaisesRegex(ValueError,"UNSAFE_PRIVATE_LEDGER"):
                self.capture(root,source="congreso",kind="congreso_vote",content=congress_bytes())
            self.assertEqual(outside.read_bytes(),b"DO_NOT_MODIFY")

    def test_tampered_snapshot_hash_is_quarantined(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            original=pipeline.import_url
            def tampering_import(**kwargs):
                record=original(**kwargs)
                (root/record["raw_object"]).write_bytes(b"tampered after download")
                return record
            with patch.object(pipeline,"import_url",side_effect=tampering_import):
                result=self.capture(root,source="congreso",kind="congreso_vote",content=congress_bytes())
            self.assertEqual(result["quarantine_state"],"QUARANTINED_INTEGRITY_FAILED")
            self.assertEqual(result["error_code"],"RAW_SHA_MISMATCH")
            self.assertFalse(result["release_grade"])


if __name__=="__main__":
    unittest.main()
