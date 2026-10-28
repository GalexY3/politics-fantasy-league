"""C17 red/green duplicate JSON member controls, synthetic only."""
import pytest
from politics_fantasy.congress_members import project, SourceContractError


def fixture():
    import json
    return json.dumps([{
        "NOMBRE":"Apellido, Nombre", "CIRCUNSCRIPCION":"Provincia",
        "FORMACIONELECTORAL":"SIGLA_ELECTORAL", "GRUPOPARLAMENTARIO":"Grupo X",
        "FECHAALTA":"07/08/2023", "FECHACONDICIONPLENA":"17/08/2023",
        "FECHAALTAENGRUPOPARLAMENTARIO":"18/08/2023",
        "unknown_nested_metadata":{"telephone":"do-not-export"}
    }],ensure_ascii=False).encode("utf-8")


def test_duplicate_named_field_rejected():
    raw=fixture().replace(b'"NOMBRE": "Apellido, Nombre"',b'"NOMBRE":"Primero","NOMBRE":"Segundo"')
    with pytest.raises(SourceContractError,match="DUPLICATE_JSON_MEMBER"):
        project(raw)


def test_nested_duplicate_unknown_field_rejected():
    raw=fixture().replace(b'"telephone": "do-not-export"',b'"telephone":"A","telephone":"B"')
    with pytest.raises(SourceContractError,match="DUPLICATE_JSON_MEMBER"):
        project(raw)


def test_normal_source_remains_synthetic_non_score_eligible():
    out=project(fixture())
    assert out["people"][0]["eligible_for_real_scoring"] is False
    assert out["people"][0]["first_public_at"] is None
