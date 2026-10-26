"""Contract tests for a bounded BOE 2023 original PDF candidacy heading parser.

No person names are fixtures. Original PDF bytes used in separate CI job.
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_proclaimed_candidates import audit,extract_albacete_lists,EXPECTED_LABELS

LABELS=[
 "PARTIDO SOCIALISTA OBRERO ESPAÑOL (PSOE)",
 "FRENTE OBRERO (FO)",
 "PARTIDO POPULAR (PP)",
 "PARTIDO ANIMALISTA CON EL MEDIO AMBIENTE (PACMA)",
 "POR UN MUNDO MÁS JUSTO (PUM+J)",
 "SUMAR (SUMAR)",
 "VOX (VOX)",
 "RECORTES CERO (RECORTES CERO)",
]

def text():
    p=["JUNTA ELECTORAL DE ALBACETE","CONGRESO DE LOS DIPUTADOS"]
    for i,label in enumerate(LABELS,1):
        p.extend([f"{i}. {label}","1. Persona inventada (persona no exportada)","Suplentes:"])
    p.extend(["SENADO","1. PARTIDO FICTICIO (FAKE)"])
    return "\n".join(p)

def fake_pdf(tmp_path):
    p=tmp_path/"sample.pdf"
    p.write_bytes(b"%PDF-1.5\n"+b" "*48+b"%%EOF\n")
    return p

def test_eight_proclaimed_2023_candidacies_are_lists_not_parties():
    records=extract_albacete_lists(text())
    assert len(records)==8
    assert [x["acronym"] for x in records]==list(EXPECTED_LABELS)
    assert all(x["legal_party_registry_id"] is None for x in records)
    assert all(x["people_records_exported"]==0 for x in records)

def test_not_proclaimed_extra_not_silently_included():
    misleading=text().replace("SENADO","9. NO PROCLAMADA (NPRO)\nSENADO")
    with pytest.raises(ValueError,match="NOT_THE_EIGHT_ORDERED"):
        extract_albacete_lists(misleading)

def test_senate_is_never_counted():
    records=extract_albacete_lists(text())
    assert len(records)==8 and "FAKE" not in [x["acronym"] for x in records]

def test_candidate_names_are_not_list_headings():
    names=extract_albacete_lists(text())
    assert all("Persona inventada" not in x["electoral_candidacy_label"] for x in names)

def test_page_extraction_fail_closed():
    with pytest.raises(ValueError,match="SENATE_BOUNDARY_MISSING"):
        extract_albacete_lists(text().split("SENADO")[0])

def test_pdf_adversarial_cannot_claim_legal_party_id(tmp_path):
    p=fake_pdf(tmp_path)
    result=audit(p,text_override=text())
    assert result["legal_parties_validated"]==0
    assert result["real_people_identified_and_joined"]==0
    assert result["n_candidacy_lists"]==8
