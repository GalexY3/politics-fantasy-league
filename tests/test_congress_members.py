"""Contract tests for official-file projection. Input here is SYNTHETIC."""
import json
import pytest
from politics_fantasy.congress_members import SOURCE_URL,SourceContractError,project

def fixture(**changes):
    a={"NOMBRE":"Apellido, Nombre","CIRCUNSCRIPCION":"Provincia",
       "FORMACIONELECTORAL":"SIGLA_ELECTORAL","GRUPOPARLAMENTARIO":"Grupo X",
       "FECHAALTA":"07/08/2023","FECHACONDICIONPLENA":"17/08/2023",
       "FECHAALTAENGRUPOPARLAMENTARIO":"18/08/2023",
       "BIOGRAFIA":"Private irrelevant biography ignored",
       "unknown_nested_metadata":{"telephone":"do-not-export"}}
    a.update(changes)
    return json.dumps([a],ensure_ascii=False).encode("utf-8")

def test_projection_source_bound_no_scores_no_biography():
    d=project(fixture())
    assert d["dataset_class"]=="OFFICIAL_HISTORICAL_EXTRACT_BOUNDED"
    assert d["status_as_of_october_2026"]=="UNKNOWN_NOT_INFERRED"
    assert d["rpp_id_verified"] is False
    assert d["score_real_people"] is False
    assert d["source_date_is_publisher_certified"] is False
    x=d["people"][0]
    assert x["admission_date_from_official"]=="2023-08-07"
    assert x["first_public_at"] is None
    assert x["continuous_membership_confirmed"] is False
    assert x["eligible_for_real_scoring"] is False
    assert "BIOGRAFIA" not in str(d)
    assert "telephone" not in str(d)
    assert set(x)=={
        "snapshot_row_id","display_name_from_official","constituency_from_official",
        "electoral_label_not_legal_party_id","parliamentary_group_not_party_membership",
        "admission_date_from_official","full_condition_date_from_official",
        "group_joined_date_from_official","first_public_at","end_of_mandate",
        "continuous_membership_confirmed","eligible_for_real_scoring"}

@pytest.mark.parametrize("url",[
    "http://www.congreso.es/webpublica/opendata/diputados/DiputadosActivos__20260725050010.json",
    "https://www.congreso.es.evil.test/webpublica/opendata/diputados/DiputadosActivos__20260725050010.json",
    "https://www.congreso.es@evil.test/webpublica/opendata/diputados/DiputadosActivos__20260725050010.json",
    "https://www.congreso.es/webpublica/opendata/diputados/DiputadosActivos__20260725050010.json?untrusted=1",
    "https://www.congreso.es/opendata/json"]) 
def test_malformed_provenance_rejected(url):
    with pytest.raises(SourceContractError,match="NOT_EXACT_OFFICIAL"):
        project(fixture(),url=url)

def test_unparseable_dates_are_not_silently_accepted():
    with pytest.raises(SourceContractError,match="INVALID_DATE"):
        project(fixture(FECHAALTA="99/99/2023"))

def test_missing_schema_fails_closed():
    x=json.loads(fixture()); del x[0]["GRUPOPARLAMENTARIO"]
    with pytest.raises(SourceContractError,match="MISSING_REQUIRED"):
        project(json.dumps(x).encode())

def test_person_name_alone_not_used_as_cross_snapshot_identifier():
    rows=json.loads(fixture())+[json.loads(fixture())[0]]
    out=project(json.dumps(rows).encode())
    assert out["people"][0]["snapshot_row_id"]!=out["people"][1]["snapshot_row_id"]
    assert out["rpp_id_verified"] is False

def test_sample_bounded():
    with pytest.raises(SourceContractError,match="INVALID_BOUNDED"):
        project(fixture(),max_rows=1001)
    with pytest.raises(SourceContractError,match="INVALID_BOUNDED"):
        project(fixture(),max_rows=True)

def test_bad_upstream_response_rejected():
    with pytest.raises(SourceContractError,match="BAD_JSON"):
        project(b"<html>not data</html>")
