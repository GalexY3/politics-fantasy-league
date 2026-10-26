"""BR10P real Python negative controls. All names in fixtures are invented."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_boe_nominations_all as N

def fixture():
    return """
JUNTA ELECTORAL DE ALBACETE
CONGRESO DE LOS DIPUTADOS
1. PARTIDO SOCIALISTA OBRERO ESPAÑOL (PSOE)
1. Persona Inventada.
2. FRENTE OBRERO (FO)
1. Otra Persona.
SENADO
1. FAKE SENATE PARTY (SENATE)
JUNTA ELECTORAL DE BURGOS
CONGRESO DE LOS DIPUTADOS
1. FRENTE OBRERO (FO)
1. Persona Inventada.
2. PARTIDO COMUNISTA DE LOS TRABAJADORES (PCTE)
SENADO
1. FAKE SENATE PARTY (SENATE)
"""
def fake_pdf(tmp_path):
    p=tmp_path/"fake.pdf";p.write_bytes(b"%PDF-1.5\n"+b"x"*120+b"%%EOF\n");return p
def test_two_provinces_and_four_DISTINCT_NOMINATIONS():
    a=N.extract(fixture())
    assert a["province_sections_detected"]==2
    assert a["province_sections_parsed"]==2
    assert a["list_headings_extracted"]==4
    assert a["distinct_label_acronyms"]==3
    assert a["official_population_denominator_confirmed"] is False
    assert a["people_public_roles_joined"]==0
def test_repeated_acronym_not_same_candidacy_identity():
    a=N.extract(fixture())
    x=a["provinces"][0]["lists"][1];y=a["provinces"][1]["lists"][0]
    assert x["acronym"]==y["acronym"]=="FO"
    assert x["candidacy_id"]!=y["candidacy_id"]
    assert x["legal_party_registration_id"] is None
def test_senate_excluded_and_no_person_names_exported():
    a=N.extract(fixture())
    js=str(a)
    assert "Persona Inventada" not in js
    assert "SENATE" not in js
    assert a["no_candidate_person_names_exported"] is True
def test_out_of_order_list_excluded_and_issue_visible():
    t=fixture().replace("2. PARTIDO COMUNISTA","7. PARTIDO COMUNISTA")
    a=N.extract(t)
    assert a["province_sections_detected"]==2
    assert a["province_sections_parsed"]==1
    assert any(z["code"]=="NON_SEQUENTIAL_LIST_POSITIONS" for z in a["issues"])
def test_missing_senate_fail_closed():
    t=fixture().replace("SENADO","NOT SENADO",1)
    a=N.extract(t)
    assert a["province_sections_parsed"]==1
    assert any(z["code"]=="SENADO_HEADING_MISSING" for z in a["issues"])
def test_empty_pdf_rejected(tmp_path):
    p=tmp_path/"raw.pdf";p.write_bytes(b"NOT A PDF")
    with pytest.raises(ValueError,match="INVALID_PDF_BYTES"):
        N.audit(p,text_override=fixture())
def test_sha_mismatch_rejected(tmp_path):
    with pytest.raises(ValueError,match="SHA256_CHANGED"):
        N.audit(fake_pdf(tmp_path),text_override=fixture())
def test_parse_with_supplied_fake_pdf_marks_digest_unverified(tmp_path):
    a=N.audit(fake_pdf(tmp_path),text_override=fixture(),verify_sha=False)
    assert a["hash_matches_known_original"] is False
    assert len(a["sha256"])==64
    assert a["province_sections_parsed"]==2
def test_duplicate_province_heading_is_not_valid_unique_coverage():
    a=N.extract(fixture()+"\n"+fixture())
    assert any(x["code"]=="DUPLICATED_PROVINCE_HEADING" for x in a["issues"])
def test_without_junta_no_records():
    with pytest.raises(ValueError,match="NO_PROVINCIAL_JUNTAS"):
        N.extract("ONE GREAT POLITICAL PARTY LIST\n")
