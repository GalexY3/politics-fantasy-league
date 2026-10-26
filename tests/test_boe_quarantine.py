"""FOCUS20R: quarantined headings are observations, never approved lists."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_boe_nominations_all import extract

def fixture():
    return """
JUNTA ELECTORAL DE ALBACETE
CONGRESO DE LOS DIPUTADOS
1. PARTIDO SOCIALISTA OBRERO ESPAÑOL (PSOE)
2. FRENTE OBRERO (FO)
3. VOX (VOX)
SENADO
1. SENATE ONLY (SEN)
JUNTA ELECTORAL DE BURGOS
CONGRESO DE LOS DIPUTADOS
1. PARTIDO SOCIALISTA OBRERO ESPAÑOL (PSOE)
3. FRENTE OBRERO (FO)
SENADO
1. SENATE ONLY (SEN)
"""
def test_quarantine_keeps_partial_observed_headings_not_certified():
    d=extract(fixture())
    assert d["province_sections_detected"]==2
    assert d["province_sections_parsed"]==1
    assert d["list_headings_extracted"]==3
    assert d["quarantined_observed_list_headings"]==2
    q=d["quarantined_provinces"][0]
    assert q["province_id"]=="BURGOS"
    assert q["missing_ordinal_positions"]==[2]
    assert q["not_a_complete_candidacy_list"] is True
    assert [x["position"] for x in q["observed_labels_only"]]==[1,3]
    assert all(x["legal_party_registration_id"] is None for x in q["observed_labels_only"])

def test_short_uppercase_vox_remains_valid():
    d=extract(fixture())
    assert [x["acronym"] for x in d["provinces"][0]["lists"]]==["PSOE","FO","VOX"]
def test_public_personal_names_not_stored_in_quarantine():
    s=fixture().replace("3. FRENTE OBRERO (FO)","2. Persona Privada.\n3. FRENTE OBRERO (FO)")
    d=extract(s)
    assert "Persona Privada" not in str(d)
    assert d["people_public_roles_joined"]==0
def test_missing_ordinal_is_not_auto_created():
    d=extract(fixture())
    q=d["quarantined_provinces"][0]
    assert 2 not in q["observed_positions"]
    assert q["observed_list_headings"]==2
    assert q["legal_registered_parties_confirmed"]==0
